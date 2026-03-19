"""
Modelo del Prospecto — estructura de datos central del sistema.
Contiene los 21 campos de research + metadata de pipeline.
Ref: SPEC.md § 4.1 (Output JSON) y § 5.3 (Estructura persistida).
"""

import time
import random
import string
from dataclasses import dataclass, field, asdict
from typing import Optional


def _generate_id() -> str:
    """Genera un ID único: p_{timestamp}_{sufijo_aleatorio}."""
    ts = int(time.time() * 1000)
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"p_{ts}_{suffix}"


@dataclass
class DecisionMaker:
    """Información del tomador de decisiones de la clínica."""
    name: str = "Unknown"
    role: str = "Unknown"
    linkedin: str = ""
    email_pattern: str = ""


@dataclass
class OnlinePresence:
    """Presencia digital de la clínica."""
    website: str = ""
    google_rating: float = 0.0
    review_count: int = 0
    social_active: bool = False
    facebook: str = ""
    instagram: str = ""


@dataclass
class Prospect:
    """
    Modelo completo de un prospecto en el pipeline.
    Incluye los 21 campos del research + metadata del pipeline.
    """

    # ── Identificación ────────────────────────────────────
    id: str = field(default_factory=_generate_id)
    input: str = ""              # Input original del usuario
    input_mode: str = "name"     # name|linkedin|website|google|phone

    # ── Research: datos de la clínica (21 campos) ─────────
    clinic_name: str = ""
    location: str = ""
    type: str = "dental"         # dental|medical|multi-specialty
    practitioners: int = 0
    staff_estimate: int = 0
    specialty: str = ""
    services: list[str] = field(default_factory=list)
    years_in_practice: int = 0
    insurance_accepted: list[str] = field(default_factory=list)

    # ── Software / Competidor ─────────────────────────────
    current_software: str = "Unknown"
    software_confidence: str = "low"   # high|medium|low
    software_signals: str = ""

    # ── Inteligencia de ventas ────────────────────────────
    pain_points: list[str] = field(default_factory=list)
    growth_signals: list[str] = field(default_factory=list)
    decision_maker: dict = field(default_factory=lambda: asdict(DecisionMaker()))
    online_presence: dict = field(default_factory=lambda: asdict(OnlinePresence()))
    recent_reviews_summary: str = ""
    hiring_signals: list[str] = field(default_factory=list)

    # ── Scoring ───────────────────────────────────────────
    fit_score: Optional[int] = None   # 1-10
    fit_reasoning: str = ""
    priority: str = "cold"            # hot|warm|cold
    best_angle: str = ""
    talking_points: list[str] = field(default_factory=list)
    red_flags: list[str] = field(default_factory=list)
    sources_used: list[str] = field(default_factory=list)
    links_found: list[str] = field(default_factory=list)

    # ── Metadata de Pipeline ──────────────────────────────
    pipeline_stage: str = "new"       # new|researched|outreach_sent|responded|meeting
    researched_at: str = ""
    outreach_sent_at: str = ""
    outreach_subject: str = ""

    def to_dict(self) -> dict:
        """Serializa el prospecto a diccionario plano."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Prospect":
        """Crea un Prospect desde un diccionario (ej. cargado de JSON)."""
        return cls(**{
            k: v for k, v in data.items()
            if k in cls.__dataclass_fields__
        })

    @classmethod
    def create_from_input(cls, user_input: str, mode: str = "name") -> "Prospect":
        """Crea un prospecto nuevo a partir del input del usuario."""
        return cls(
            input=user_input,
            input_mode=mode,
            clinic_name=user_input.split(",")[0].strip(),
            pipeline_stage="new",
        )

    @classmethod
    def create_fallback(cls, user_input: str, error_msg: str = "") -> "Prospect":
        """
        Crea un prospecto con datos mínimos cuando la investigación falla.
        Ref: SPEC.md § 11.3.
        """
        return cls(
            input=user_input,
            clinic_name=user_input.split(",")[0].strip(),
            location="Research failed",
            fit_score=5,
            priority="warm",
            fit_reasoning=error_msg[:300] if error_msg else "Research failed",
            best_angle="General outreach",
            sources_used=["Web search (partial results)"],
            pipeline_stage="new",
        )
