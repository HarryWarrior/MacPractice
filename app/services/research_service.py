"""
Servicio de Investigación de Prospectos.
Ref: SPEC.md § 4.1, § 4.3, § 9.3, § 10.1.

En la FASE 1 contiene el mock_research_generator.
En la FASE 2 se conectará a Gemini + Fallback reales.
"""

import time
import random
from datetime import datetime, timezone
from typing import Generator

from app.models.prospect import Prospect
from app.models.competitor import detect_competitor
from app.agents.prompts import build_research_query
from app.utils.logger import LogAccumulator, create_research_log_steps
from app.utils.json_parser import (
    parse_llm_json,
    create_research_fallback,
)


# ──────────────────────────────────────────────────────────
# MOCK: Datos simulados para la Fase 1
# ──────────────────────────────────────────────────────────
_MOCK_RESEARCH_DATA = {
    "clinic_name": "Bright Smile Dental",
    "location": "Austin, TX",
    "type": "dental",
    "practitioners": 6,
    "staff_estimate": 18,
    "specialty": "General Dentistry, Cosmetic, Orthodontics",
    "services": [
        "General Dentistry",
        "Teeth Whitening",
        "Invisalign",
        "Dental Implants",
        "Emergency Care",
    ],
    "years_in_practice": 12,
    "insurance_accepted": [
        "Delta Dental", "Cigna", "Aetna", "MetLife",
    ],
    "current_software": "Dentrix",
    "software_confidence": "high",
    "software_signals": (
        "Job posting on Indeed mentions 'Dentrix experience preferred'. "
        "LinkedIn employee endorsement also lists Dentrix."
    ),
    "pain_points": [
        "Multiple Google reviews mention long wait times for billing",
        "Glassdoor review from staff mentions outdated software",
        "Patient review cites difficulty with online scheduling",
    ],
    "growth_signals": [
        "Hiring hygienist and front desk (Indeed, posted last week)",
        "New office renovation photos on Instagram (Feb 2026)",
        "Added pediatric dentistry service this year",
    ],
    "decision_maker": {
        "name": "Dr. Sarah Mitchell",
        "role": "Owner / Lead Dentist",
        "linkedin": "https://linkedin.com/in/sarahmitchelldds",
        "email_pattern": "smitchell@brightsmiledental.com",
    },
    "online_presence": {
        "website": "https://brightsmiledental.com",
        "google_rating": 4.6,
        "review_count": 287,
        "social_active": True,
        "facebook": "https://facebook.com/brightsmiledental",
        "instagram": "@brightsmiledental",
    },
    "recent_reviews_summary": (
        "Patients praise the friendly staff and modern office. "
        "However, several recent reviews mention frustration with "
        "billing and the online appointment system being down."
    ),
    "hiring_signals": [
        "Dental Hygienist — Indeed, posted 5 days ago",
        "Front Desk Coordinator — Indeed, posted 12 days ago",
    ],
    "fit_score": 8,
    "fit_reasoning": (
        "6-practitioner clinic in growth mode (hiring 2 roles). "
        "Currently on Dentrix with documented billing pain points. "
        "Active social media presence suggests tech-forward mindset."
    ),
    "priority": "hot",
    "best_angle": (
        "Lead with billing pain from reviews + Dentrix switching"
    ),
    "talking_points": [
        "Their patients are complaining about billing — Mac Practice automates this",
        "They're hiring 2 new staff — perfect time to switch before onboarding",
        "Dr. Mitchell is active on LinkedIn — warm intro opportunity",
    ],
    "red_flags": [
        "May have recently renewed Dentrix contract (check timing)",
    ],
    "sources_used": [
        "Google Business (4.6★, 287 reviews)",
        "Clinic website (brightsmiledental.com)",
        "LinkedIn (company page + Dr. Mitchell profile)",
        "Indeed (2 active job postings)",
        "Instagram (@brightsmiledental, active)",
        "Facebook (page with 1.2k followers)",
    ],
}


def mock_research_generator(
    user_input: str,
    mode: str = "name",
) -> Generator[tuple[str, dict | None], None, None]:
    """
    Generador MOCK que simula los pasos de investigación.
    Produce (log_text, research_data | None) en cada yield.

    En cada paso produce el log actualizado.
    Al final produce los datos de research completos.

    Uso en Gradio:
        for log_text, data in mock_research_generator("Bright Smile Dental"):
            log_output.value = log_text
            if data is not None:
                # Research completo, procesar datos
    """
    log = LogAccumulator()
    steps = create_research_log_steps()

    # Log de inicio
    yield log.add("start", f"Iniciando investigación para: {user_input}..."), None
    time.sleep(0.5)

    query = build_research_query(user_input, mode)
    yield log.add("info", f"Modo de búsqueda: {mode}"), None
    time.sleep(0.3)

    # Simular los 6 pasos de progreso
    for step in steps:
        yield log.add(step["icon"], step["message"]), None
        # Delay aleatorio entre 500-900ms para sensación de progreso real
        time.sleep(random.uniform(0.5, 0.9))

    # Simular detección de competidor
    mock_data = _MOCK_RESEARCH_DATA.copy()
    # Personalizar el nombre de la clínica al input del usuario
    mock_data["clinic_name"] = user_input.split(",")[0].strip()

    competitor = detect_competitor(mock_data["current_software"])
    if competitor:
        key, profile = competitor
        yield log.add(
            "success",
            f"Competidor detectado en base de datos: {profile['name']}."
        ), None
    else:
        yield log.add("info", "No se detectó competidor conocido."), None

    time.sleep(0.3)

    # Resultado final
    yield log.add(
        "done",
        f"Investigación completa. Fit Score: {mock_data['fit_score']}/10 "
        f"— Prioridad: {mock_data['priority'].upper()}"
    ), mock_data


def do_research(
    user_input: str,
    mode: str = "name",
) -> Generator[tuple[str, dict | None], None, None]:
    """
    Orquestador principal de investigación.
    FASE 1: Delega al mock.
    FASE 2: try Gemini → except → fallback OpenAI.

    Yields:
        (log_text, research_data | None)
    """
    # FASE 1: Usar mock
    yield from mock_research_generator(user_input, mode)

    # FASE 2 (futuro): Reemplazar por:
    # try:
    #     yield from gemini_research_generator(user_input, mode)
    # except Exception as e:
    #     yield log.add("warning", f"Gemini falló: {e}. Usando fallback...")
    #     yield from openai_fallback_generator(user_input, mode)
