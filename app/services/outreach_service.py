"""
Servicio de Outreach — Generación de emails personalizados.
Ref: SPEC.md § 4.2, § 9.5, § 9.6.

Extrae la lógica de outreach de research_service para que viva
en su propio módulo con responsabilidad única.
"""

import json
from typing import Generator

from app.models.prospect import Prospect
from app.models.competitor import detect_competitor
from app.agents.gemini_agent import call_gemini_outreach
from app.agents.openai_agent import call_openai_outreach
from app.utils.logger import LogAccumulator
from app.utils.json_parser import (
    parse_llm_json,
    create_outreach_fallback,
)


def do_outreach(
    prospect: Prospect,
) -> Generator[tuple[str, dict | None], None, None]:
    """
    Genera un email de outreach personalizado basado
    en los datos de research del prospecto.

    Flujo:
    1. Enriquece el contexto con datos de competidor.
    2. Intenta con Gemini.
    3. Si falla, activa el fallback de OpenAI.
    4. Parsea el JSON de la respuesta.
    5. Inyecta sender_name/title por defecto si faltan.

    Yields:
        (log_text, draft_data | None)
        El draft_data solo se produce al final.
    """
    log = LogAccumulator()

    yield log.add(
        "write",
        f"Redactando outreach para: {prospect.clinic_name}..."
    ), None

    # ── Enriquecer contexto con competidor ────────────
    prospect_dict = prospect.to_dict()

    competitor = detect_competitor(prospect.current_software)
    if competitor:
        key, profile = competitor
        prospect_dict["competitor_profile"] = {
            "name": profile["name"],
            "pains": profile["pains"],
            "our_angles": profile["angles"],
        }
        yield log.add(
            "info",
            f"Usando playbook de switching para {profile['name']}."
        ), None
    else:
        yield log.add(
            "info",
            "Sin competidor detectado — outreach general."
        ), None

    # Serializar como JSON string para el LLM
    context_json = json.dumps(prospect_dict, indent=2)

    raw_response = None
    engine_used = "none"

    # ── Intento 1: Gemini ─────────────────────────────
    try:
        for log_text, response in call_gemini_outreach(
            context_json, log
        ):
            if response is not None:
                raw_response = response
            yield log_text, None

        if raw_response:
            engine_used = "gemini"

    except Exception as e:
        yield log.add(
            "warning",
            f"Gemini falló para outreach: {str(e)[:80]}. "
            "Usando OpenAI..."
        ), None

        # ── Intento 2: OpenAI ─────────────────────────
        try:
            for log_text, response in call_openai_outreach(
                context_json, log
            ):
                if response is not None:
                    raw_response = response
                yield log_text, None

            if raw_response:
                engine_used = "openai"

        except Exception as e2:
            yield log.add(
                "error",
                f"Fallback de outreach también falló: {str(e2)[:80]}"
            ), None

    # ── Parsear y enriquecer respuesta ────────────────
    draft_data = _parse_and_enrich_draft(
        raw_response,
        prospect,
        log,
    )

    yield log.add(
        "done",
        f"Outreach listo ({engine_used}). "
        f"{len(draft_data.get('subject_options', []))} "
        f"opciones de subject generadas."
    ), draft_data


def _parse_and_enrich_draft(
    raw_response: str | None,
    prospect: Prospect,
    log: LogAccumulator,
) -> dict:
    """
    Parsea la respuesta del LLM y rellena campos faltantes
    con valores por defecto razonables.
    """
    if raw_response:
        try:
            draft = parse_llm_json(raw_response)
            log.add("success", "Email parseado correctamente.")
        except ValueError as e:
            log.add(
                "warning",
                f"Error parseando email: {str(e)[:60]}. "
                "Usando template genérico..."
            )
            draft = create_outreach_fallback(
                prospect.clinic_name, prospect.location
            )
    else:
        log.add(
            "warning",
            "Sin respuesta de IA. Usando template genérico..."
        )
        draft = create_outreach_fallback(
            prospect.clinic_name, prospect.location
        )

    # ── Defaults de seguridad ─────────────────────────
    if not draft.get("sender_name"):
        draft["sender_name"] = "Sales Team"

    if not draft.get("sender_title"):
        draft["sender_title"] = "Account Executive, Mac Practice"

    if not draft.get("follow_up_timing"):
        draft["follow_up_timing"] = "3-5 business days"

    if not draft.get("subject_options"):
        draft["subject_options"] = [
            f"Quick question about {prospect.clinic_name}"
        ]

    if not draft.get("personalization_hooks"):
        draft["personalization_hooks"] = []

    if not draft.get("tone_notes"):
        draft["tone_notes"] = ""

    return draft


def regenerate_outreach(
    prospect: Prospect,
) -> Generator[tuple[str, dict | None], None, None]:
    """
    Regenera completamente el draft (cuando el usuario hace Reject).
    Ref: SPEC.md § 9.5 — Reject: regenera completamente.
    Es esencialmente lo mismo que do_outreach pero con un log distinto.
    """
    log = LogAccumulator()
    yield log.add(
        "write",
        "Regenerando email (rechazado por el usuario)..."
    ), None

    # Reutilizar toda la lógica de do_outreach
    for log_text, draft_data in do_outreach(prospect):
        yield log_text, draft_data
