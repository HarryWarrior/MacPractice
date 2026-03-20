"""
Servicio de Outreach — Generación de emails personalizados.
Ref: SPEC.md § 4.2, § 9.5, § 9.6.

Extrae la lógica de outreach de research_service para que viva
en su propio módulo con responsabilidad única.
"""

import json
import os
from pathlib import Path
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

# Path where permanent feedback/memory is stored
_MEMORY_FILE = Path(__file__).parent.parent / "agents" / "outreach_memory.txt"


def load_outreach_memory() -> str:
    """Loads accumulated outreach feedback from the permanent memory file."""
    if _MEMORY_FILE.exists():
        content = _MEMORY_FILE.read_text(encoding="utf-8").strip()
        return content
    return ""


def save_outreach_feedback(feedback: str) -> None:
    """Appends new feedback to the permanent memory file."""
    _MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_MEMORY_FILE, "a", encoding="utf-8") as f:
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"\n[{ts}] {feedback.strip()}\n")


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
        f"Drafting outreach for: {prospect.clinic_name}..."
    ), None

    # ── Enrich context with competitor data ───────────
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
            f"Applying switching playbook for {profile['name']}."
        ), None
    else:
        yield log.add(
            "info",
            "No competitor detected — using general outreach template."
        ), None

    # ── Inject phone if available ──────────────────────
    phone = (prospect.online_presence or {}).get("phone", "")
    if phone:
        prospect_dict["_contact_phone"] = phone

    # ── Load accumulated feedback memory ──────────────
    memory = load_outreach_memory()
    if memory:
        prospect_dict["_style_feedback_memory"] = (
            "IMPORTANT — Apply these learned style corrections from "
            "previous feedback:\n" + memory
        )
        yield log.add(
            "info",
            "Applying style memory from previous feedback."
        ), None

    # Serialize as JSON string for the LLM
    context_json = json.dumps(prospect_dict, indent=2)

    raw_response = None
    engine_used = "none"

    # ── Attempt 1: Gemini ─────────────────────────────
    try:
        for log_text, response in call_gemini_outreach(
            context_json, log
        ):
            if response is not None:
                raw_response = response
            yield log_text, None

        if raw_response:
            engine_used = "gemini"

    except Exception:
        # ── Attempt 2: OpenAI fallback ─────────────────
        yield log.add("write", "Switching to backup AI engine..."), None
        try:
            for log_text, response in call_openai_outreach(
                context_json, log
            ):
                if response is not None:
                    raw_response = response
                yield log_text, None

            if raw_response:
                engine_used = "openai"

        except Exception:
            pass  # Will use fallback template below

    # ── Parse and enrich response ─────────────────────
    draft_data = _parse_and_enrich_draft(
        raw_response,
        prospect,
        log,
    )

    yield log.add(
        "done",
        f"Outreach ready — "
        f"{len(draft_data.get('subject_options', []))} subject lines generated."
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
            log.add("success", "Email draft parsed successfully.")
        except ValueError:
            draft = create_outreach_fallback(
                prospect.clinic_name, prospect.location
            )
    else:
        draft = create_outreach_fallback(
            prospect.clinic_name, prospect.location
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

    if not draft.get("whatsapp_message"):
        draft["whatsapp_message"] = (
            f"Hi! I came across {prospect.clinic_name} and was really impressed. "
            "I work with Mac Practice and thought it might be a good fit for your team. "
            "Would love to share a quick idea — is now a bad time?"
        )

    if not draft.get("linkedin_message"):
        draft["linkedin_message"] = (
            f"Hi! I noticed {prospect.clinic_name} and thought there might be a fit "
            "with what we do at Mac Practice. Open to connect?"
        )

    # Inject phone for WhatsApp link generation (UI uses this)
    if not draft.get("_phone"):
        draft["_phone"] = (
            getattr(prospect, "online_presence", {}) or {}
        ).get("phone", "")

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
