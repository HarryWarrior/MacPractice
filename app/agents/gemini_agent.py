"""
Agente de Gemini — Motor de IA Principal.

Usa google-generativeai SDK con Google Search Retrieval (Search Grounding)
para investigación web nativa sin scrapers.

Migrado de google-genai a google-generativeai para compatibilidad con
Hugging Face Spaces (conflicto de websockets resuelto).
"""

from typing import Generator

import warnings
warnings.simplefilter("ignore", FutureWarning)
import google.generativeai as genai

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.agents.prompts import RESEARCH_PROMPT, OUTREACH_PROMPT, EXECUTIVE_SUMMARY_PROMPT
from app.utils.logger import LogAccumulator


def _configure():
    """Configura el SDK con la API key."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not configured. "
            "Add it to your .env file"
        )
    genai.configure(api_key=GEMINI_API_KEY)


def call_gemini_research(
    query: str,
    log: LogAccumulator,
) -> Generator[tuple[str, str | None], None, None]:
    """
    Llama a Gemini con Search Grounding para investigar una clínica.

    Yields:
        (log_text, raw_response | None)
        - raw_response solo se produce al final cuando hay respuesta.

    Raises:
        Exception: Si la API falla (para activar el fallback).
    """
    _configure()

    print(f"\n{'='*60}")
    print(f"[GEMINI SEARCH] Query enviado a Google:")
    print(f"  {query}")
    print(f"{'='*60}")

    yield log.add(
        "search",
        "Querying Google Search via Gemini Grounding..."
    ), None

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=RESEARCH_PROMPT,
        tools=[{"google_search_retrieval": {}}],
    )

    response = model.generate_content(query)

    if not response or not response.text:
        raise ValueError(
            "Gemini no devolvió contenido en la respuesta."
        )

    raw_text = response.text

    # ── Imprimir metadata de grounding (fuentes usadas) ──────
    try:
        for candidate in (response.candidates or []):
            gm = getattr(candidate, "grounding_metadata", None)
            if not gm:
                print("[GEMINI] Sin grounding metadata en esta respuesta.")
                continue

            search_queries = getattr(gm, "web_search_queries", None) or []
            if search_queries:
                print(f"\n[GEMINI] Google Search queries ejecutadas ({len(search_queries)}):")
                for q in search_queries:
                    print(f"  🔍 {q}")

            chunks = getattr(gm, "grounding_chunks", None) or []
            print(f"\n[GEMINI] Páginas analizadas por Gemini: {len(chunks)}")
            for i, chunk in enumerate(chunks, 1):
                web = getattr(chunk, "web", None)
                if web:
                    title = getattr(web, "title", "") or "(sin título)"
                    uri = getattr(web, "uri", "") or ""
                    print(f"  [{i:02d}] {title}")
                    print(f"        {uri}")

            supports = getattr(gm, "grounding_supports", None) or []
            if supports:
                print(f"\n[GEMINI] Fragmentos respaldados por fuentes: {len(supports)}")
    except Exception as meta_err:
        print(f"[GEMINI] Error leyendo grounding metadata: {meta_err}")

    print(f"\n[GEMINI] Respuesta generada: {len(raw_text)} caracteres")
    print(f"{'='*60}\n")

    yield log.add(
        "success",
        f"Gemini responded ({len(raw_text)} chars)."
    ), raw_text


def call_gemini_outreach(
    prospect_json: str,
    log: LogAccumulator,
) -> Generator[tuple[str, str | None], None, None]:
    """
    Llama a Gemini para generar un email de outreach personalizado.
    NO usa Search Grounding (no necesita buscar en la web).

    Yields:
        (log_text, raw_response | None)
    """
    _configure()

    yield log.add(
        "write",
        "Generating personalized email with Gemini..."
    ), None

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=OUTREACH_PROMPT,
    )

    response = model.generate_content(prospect_json)

    if not response or not response.text:
        raise ValueError(
            "Gemini no devolvió contenido para el outreach."
        )

    raw_text = response.text

    yield log.add(
        "success",
        f"Email generated ({len(raw_text)} chars)."
    ), raw_text


def call_gemini_summary(
    pipeline_json: str,
    log: LogAccumulator,
) -> Generator[tuple[str, str | None], None, None]:
    """
    Llama a Gemini para generar el resumen ejecutivo del pipeline.
    NO usa Search Grounding — los datos ya están en el JSON.

    Yields:
        (log_text, raw_response | None)
    """
    _configure()

    yield log.add(
        "search",
        "Analyzing pipeline with Gemini..."
    ), None

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=EXECUTIVE_SUMMARY_PROMPT,
    )

    response = model.generate_content(pipeline_json)

    if not response or not response.text:
        raise ValueError(
            "Gemini no devolvió contenido para el resumen ejecutivo."
        )

    raw_text = response.text

    yield log.add(
        "success",
        f"Executive summary generated ({len(raw_text)} chars)."
    ), raw_text
