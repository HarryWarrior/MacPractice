"""
Agente de Gemini — Motor de IA Principal.
Ref: SPEC.md § 4.3, § 16.1.

Usa Google GenAI SDK (google-genai) con Search Grounding (GoogleSearch)
para investigación web nativa sin scrapers.

Migrado del SDK deprecado (google-generativeai) al nuevo SDK oficial
(google-genai) siguiendo: https://ai.google.dev/gemini-api/docs/migrate
"""

from typing import Generator

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.agents.prompts import RESEARCH_PROMPT, OUTREACH_PROMPT, EXECUTIVE_SUMMARY_PROMPT
from app.utils.logger import LogAccumulator


def _get_client() -> genai.Client:
    """Crea un cliente de Gemini con la API key."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY no está configurada. "
            "Agrégala a tu archivo .env"
        )
    return genai.Client(api_key=GEMINI_API_KEY)


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
    client = _get_client()

    print(f"\n{'='*60}")
    print(f"[GEMINI SEARCH] Query enviado a Google:")
    print(f"  {query}")
    print(f"{'='*60}")

    yield log.add(
        "search",
        "Consultando Google Search via Gemini Grounding..."
    ), None

    # Nuevo SDK: Search Grounding con GoogleSearch tool
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=query,
        config=types.GenerateContentConfig(
            system_instruction=RESEARCH_PROMPT,
            tools=[
                types.Tool(
                    google_search=types.GoogleSearch()
                )
            ],
        ),
    )

    # Extraer el texto de la respuesta
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

            # Queries que Google ejecutó internamente
            search_queries = getattr(gm, "web_search_queries", None) or []
            if search_queries:
                print(f"\n[GEMINI] Google Search queries ejecutadas ({len(search_queries)}):")
                for q in search_queries:
                    print(f"  🔍 {q}")

            # Chunks = páginas analizadas por Gemini
            chunks = getattr(gm, "grounding_chunks", None) or []
            print(f"\n[GEMINI] Páginas analizadas por Gemini: {len(chunks)}")
            for i, chunk in enumerate(chunks, 1):
                web = getattr(chunk, "web", None)
                if web:
                    title = getattr(web, "title", "") or "(sin título)"
                    uri = getattr(web, "uri", "") or ""
                    print(f"  [{i:02d}] {title}")
                    print(f"        {uri}")

            # Segmentos con respaldo de fuentes
            supports = getattr(gm, "grounding_supports", None) or []
            if supports:
                print(f"\n[GEMINI] Fragmentos respaldados por fuentes: {len(supports)}")
    except Exception as meta_err:
        print(f"[GEMINI] Error leyendo grounding metadata: {meta_err}")

    print(f"\n[GEMINI] Respuesta generada: {len(raw_text)} caracteres")
    print(f"{'='*60}\n")

    yield log.add(
        "success",
        f"Gemini respondió ({len(raw_text)} caracteres)."
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
    client = _get_client()

    yield log.add(
        "write",
        "Generando email personalizado con Gemini..."
    ), None

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prospect_json,
        config=types.GenerateContentConfig(
            system_instruction=OUTREACH_PROMPT,
        ),
    )

    if not response or not response.text:
        raise ValueError(
            "Gemini no devolvió contenido para el outreach."
        )

    raw_text = response.text

    yield log.add(
        "success",
        f"Email generado ({len(raw_text)} caracteres)."
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
    client = _get_client()

    yield log.add(
        "search",
        "Analizando pipeline con Gemini..."
    ), None

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=pipeline_json,
        config=types.GenerateContentConfig(
            system_instruction=EXECUTIVE_SUMMARY_PROMPT,
        ),
    )

    if not response or not response.text:
        raise ValueError(
            "Gemini no devolvió contenido para el resumen ejecutivo."
        )

    raw_text = response.text

    yield log.add(
        "success",
        f"Resumen ejecutivo generado ({len(raw_text)} caracteres)."
    ), raw_text
