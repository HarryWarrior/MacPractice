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
from app.agents.prompts import RESEARCH_PROMPT, OUTREACH_PROMPT
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
