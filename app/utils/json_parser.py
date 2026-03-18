"""
Parser robusto de JSON desde respuestas de LLM.
Ref: SPEC.md § 4.4 — Parser de JSON.

Maneja respuestas con markdown (```json), texto extra,
y produce un fallback si la extracción falla.
"""

import re
import json
from typing import Any


def parse_llm_json(raw_text: str) -> dict[str, Any]:
    """
    Extrae y parsea un objeto JSON desde la respuesta cruda de un LLM.

    Estrategia:
    1. Limpia backticks de markdown (```json ... ```)
    2. Busca el primer objeto JSON con regex { ... }
    3. Lo parsea con json.loads
    4. Si falla, lanza ValueError para activar el fallback

    Args:
        raw_text: Texto crudo de la respuesta del LLM.

    Returns:
        Diccionario parseado del JSON.

    Raises:
        ValueError: Si no se encuentra JSON válido.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("La respuesta del LLM está vacía.")

    # Paso 1: Limpiar backticks de markdown
    cleaned = raw_text.strip()
    cleaned = re.sub(
        r"```(?:json)?\s*", "", cleaned
    )
    cleaned = cleaned.replace("```", "")

    # Paso 2: Encontrar el primer objeto JSON con regex
    json_match = re.search(r"\{[\s\S]*\}", cleaned)
    if not json_match:
        raise ValueError(
            f"No se encontró JSON en la respuesta: "
            f"{raw_text[:200]}..."
        )

    json_str = json_match.group(0)

    # Paso 3: Parsear
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"JSON inválido: {e}. "
            f"Fragmento: {json_str[:200]}..."
        ) from e


def create_research_fallback(
    user_input: str,
    raw_response: str = "",
) -> dict[str, Any]:
    """
    Crea un objeto de research con datos mínimos cuando el parsing falla.
    Ref: SPEC.md § 11.2.

    Args:
        user_input: Input original del usuario.
        raw_response: Respuesta cruda del LLM (para fit_reasoning).

    Returns:
        Diccionario con la estructura del research con valores por defecto.
    """
    clinic_name = user_input.split(",")[0].strip()
    return {
        "clinic_name": clinic_name,
        "location": "Unknown",
        "type": "dental",
        "practitioners": 0,
        "staff_estimate": 0,
        "specialty": "",
        "services": [],
        "years_in_practice": 0,
        "insurance_accepted": [],
        "current_software": "Unknown",
        "software_confidence": "low",
        "software_signals": "",
        "pain_points": [],
        "growth_signals": [],
        "decision_maker": {
            "name": "Unknown",
            "role": "Unknown",
            "linkedin": "",
            "email_pattern": "",
        },
        "online_presence": {
            "website": "",
            "google_rating": 0.0,
            "review_count": 0,
            "social_active": False,
            "facebook": "",
            "instagram": "",
        },
        "recent_reviews_summary": "",
        "hiring_signals": [],
        "fit_score": 5,
        "fit_reasoning": raw_response[:300] if raw_response else "Partial results",
        "priority": "warm",
        "best_angle": "General outreach",
        "talking_points": [],
        "red_flags": [],
        "sources_used": ["Web search (partial results)"],
    }


def create_outreach_fallback(
    clinic_name: str,
    location: str = "",
) -> dict[str, Any]:
    """
    Crea un email de outreach genérico cuando la generación falla.
    Ref: SPEC.md § 11.4.
    """
    return {
        "subject_options": [
            f"Quick question about {clinic_name}",
            f"Saw great things about {clinic_name}",
            f"Fellow dental tech professional reaching out",
        ],
        "body": (
            f"Hi,\n\n"
            f"I came across {clinic_name}"
            f"{' in ' + location if location else ''} "
            f"and was impressed by what you've built.\n\n"
            f"At Mac Practice, we've been helping dental practices "
            f"streamline their operations for 20 years. I'd love to "
            f"learn more about how things are going on your end — "
            f"no pitch, just a conversation.\n\n"
            f"Would you be open to a quick chat?\n\n"
            f"Best regards"
        ),
        "sender_name": "Sales Team",
        "sender_title": "Account Executive, Mac Practice",
        "follow_up_timing": "3-5 business days",
        "personalization_hooks": [
            f"Referenced clinic name: {clinic_name}",
        ],
        "tone_notes": "Generic fallback — personalization failed",
    }
