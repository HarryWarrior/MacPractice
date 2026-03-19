"""
Servicio de Investigación de Prospectos — Orquestador Real.
Ref: SPEC.md § 4.1, § 4.3, § 9.3, § 10.1.

Flujo: try Gemini (con Search Grounding) → except → fallback OpenAI+DDG.
Todas las funciones usan generadores (yield) para logs en tiempo real.

Nota: La generación de outreach ahora vive en outreach_service.py.
"""

import time
import random
from datetime import datetime, timezone
from typing import Generator

from app.models.prospect import Prospect
from app.models.competitor import detect_competitor
from app.agents.prompts import build_research_query, build_ddg_query
from app.agents.gemini_agent import call_gemini_research
from app.agents.openai_agent import call_openai_research
from app.utils.logger import LogAccumulator, create_research_log_steps
from app.utils.json_parser import (
    parse_llm_json,
    create_research_fallback,
)


# ──────────────────────────────────────────────────────────
# Investigación Principal (Gemini → Fallback → Parse → Prospect)
# ──────────────────────────────────────────────────────────

def do_research(
    user_input: str,
    mode: str = "name",
) -> Generator[tuple[str, Prospect | None], None, None]:
    """
    Orquestador principal de investigación de un prospecto.

    Flujo:
    1. Construye el query según el modo de input.
    2. Intenta con Gemini (Search Grounding).
    3. Si falla, activa el fallback de OpenAI + DuckDuckGo.
    4. Parsea el JSON de la respuesta.
    5. Detecta competidor y crea el Prospect.

    Yields:
        (log_text, prospect | None)
        El Prospect se produce solo al final cuando está completo.
    """
    log = LogAccumulator()

    # ── Inicio ────────────────────────────────────────
    yield log.add(
        "start",
        f"Iniciando investigación para: {user_input}..."
    ), None

    query     = build_research_query(user_input, mode)
    ddg_query = build_ddg_query(user_input, mode)
    yield log.add("info", f"Modo de búsqueda: {mode}"), None
    time.sleep(0.3)

    # ── Simular pasos de progreso visual ──────────────
    steps = create_research_log_steps()
    for step in steps[:3]:
        yield log.add(step["icon"], step["message"]), None
        time.sleep(random.uniform(0.3, 0.6))

    # ── Intento 1: Gemini ─────────────────────────────
    raw_response = None
    engine_used = "none"

    try:
        yield log.add(
            "search",
            "Conectando con Google Gemini + Search Grounding..."
        ), None

        for log_text, response in call_gemini_research(query, log):
            if response is not None:
                raw_response = response
            yield log_text, None

        if raw_response:
            engine_used = "gemini"

    except Exception as e:
        yield log.add(
            "warning",
            f"Gemini falló: {str(e)[:100]}. Activando fallback..."
        ), None
        time.sleep(0.3)

        # ── Intento 2: OpenAI + DuckDuckGo ────────────
        try:
            for log_text, response in call_openai_research(query, log, ddg_query=ddg_query):
                if response is not None:
                    raw_response = response
                yield log_text, None

            if raw_response:
                engine_used = "openai"

        except Exception as e2:
            yield log.add(
                "error",
                f"Fallback también falló: {str(e2)[:100]}"
            ), None

    # ── Pasos finales de progreso visual ──────────────
    for step in steps[3:]:
        yield log.add(step["icon"], step["message"]), None
        time.sleep(random.uniform(0.2, 0.4))

    # ── Parsear respuesta ─────────────────────────────
    if raw_response:
        try:
            research_data = parse_llm_json(raw_response)
            yield log.add(
                "success",
                f"JSON parseado correctamente ({engine_used})."
            ), None
        except ValueError as parse_err:
            yield log.add(
                "warning",
                f"Error parseando JSON: {str(parse_err)[:80]}. "
                "Usando datos parciales..."
            ), None
            research_data = create_research_fallback(
                user_input, raw_response
            )
    else:
        yield log.add(
            "error",
            "No se obtuvo respuesta de ningún motor de IA."
        ), None
        research_data = create_research_fallback(user_input)

    # ── Detectar competidor ───────────────────────────
    current_sw = research_data.get("current_software", "Unknown")
    competitor = detect_competitor(current_sw)

    if competitor:
        key, profile = competitor
        yield log.add(
            "success",
            f"Competidor detectado: {profile['name']}."
        ), None
    else:
        yield log.add("info", "No se detectó competidor conocido."), None

    # ── Crear el Prospect completo ────────────────────
    now_iso = datetime.now(timezone.utc).isoformat()

    prospect = Prospect(
        input=user_input,
        input_mode=mode,
        clinic_name=research_data.get("clinic_name", user_input.split(",")[0].strip()),
        location=research_data.get("location", "Unknown"),
        type=research_data.get("type", "dental"),
        practitioners=int(research_data.get("practitioners", 0)),
        staff_estimate=int(research_data.get("staff_estimate", 0)),
        specialty=research_data.get("specialty", ""),
        services=research_data.get("services", []),
        years_in_practice=int(research_data.get("years_in_practice", 0)),
        insurance_accepted=research_data.get("insurance_accepted", []),
        current_software=research_data.get("current_software", "Unknown"),
        software_confidence=research_data.get("software_confidence", "low"),
        software_signals=research_data.get("software_signals", ""),
        pain_points=research_data.get("pain_points", []),
        growth_signals=research_data.get("growth_signals", []),
        decision_maker=research_data.get("decision_maker", {}),
        online_presence=research_data.get("online_presence", {}),
        recent_reviews_summary=research_data.get("recent_reviews_summary", ""),
        hiring_signals=research_data.get("hiring_signals", []),
        fit_score=int(research_data.get("fit_score", 5)),
        fit_reasoning=research_data.get("fit_reasoning", ""),
        priority=research_data.get("priority", "warm"),
        best_angle=research_data.get("best_angle", ""),
        talking_points=research_data.get("talking_points", []),
        red_flags=research_data.get("red_flags", []),
        sources_used=research_data.get("sources_used", []),
        links_found=research_data.get("links_found", []),
        pipeline_stage="researched",
        researched_at=now_iso,
    )

    # ── Log final ─────────────────────────────────────
    score = prospect.fit_score or 0
    priority = (prospect.priority or "warm").upper()

    yield log.add(
        "done",
        f"Investigación completa. Fit Score: {score}/10 "
        f"— Prioridad: {priority} "
        f"— Motor: {engine_used}"
    ), prospect


# ──────────────────────────────────────────────────────────
# Batch Processing (para CSV imports)
# ──────────────────────────────────────────────────────────

def do_batch_research(
    items: list[dict],
    delay_seconds: int = 5,
) -> Generator[tuple[str, int, int, Prospect | None], None, None]:
    """
    Procesa múltiples prospectos en secuencia con delay entre cada uno.
    Ref: SPEC.md § 10.2.

    Args:
        items: Lista de dicts con {input, mode}.
        delay_seconds: Pausa entre cada research (rate limiting).

    Yields:
        (log_text, current_index, total, prospect | None)
    """
    from app.config import BATCH_DELAY_SECONDS
    delay = delay_seconds or BATCH_DELAY_SECONDS
    total = len(items)
    log = LogAccumulator()

    yield log.add(
        "batch",
        f"Iniciando batch research: {total} prospectos..."
    ), 0, total, None

    for i, item in enumerate(items):
        user_input = item.get("input", "")
        mode = item.get("mode", "name")
        current = i + 1

        yield log.add(
            "start",
            f"[{current}/{total}] Investigando: {user_input}..."
        ), current, total, None

        # Ejecutar research individual
        prospect = None
        try:
            for res_log, res_prospect in do_research(user_input, mode):
                if res_prospect is not None:
                    prospect = res_prospect
                yield res_log, current, total, None

        except Exception as e:
            yield log.add(
                "error",
                f"[{current}/{total}] Error: {str(e)[:80]}"
            ), current, total, None

            # Crear prospecto de fallback
            prospect = Prospect.create_fallback(user_input, str(e))

        yield log.add(
            "success",
            f"[{current}/{total}] Completado: {user_input}"
        ), current, total, prospect

        # Rate limiting: pausa entre requests
        if i < total - 1:
            yield log.add(
                "info",
                f"Esperando {delay}s (rate limiting)..."
            ), current, total, None
            time.sleep(delay)

    yield log.add(
        "done",
        f"Batch completo: {total} prospectos procesados."
    ), total, total, None
