"""
Modelos de datos del sistema Mac Practice Dental Prospector.
"""

from app.models.prospect import Prospect, DecisionMaker, OnlinePresence
from app.models.competitor import COMPETITORS, detect_competitor
from app.models.pipeline import (
    PIPELINE_STAGES,
    STAGE_MAP,
    VALID_STAGES,
    is_valid_stage,
    get_stage_color,
)

__all__ = [
    "Prospect",
    "DecisionMaker",
    "OnlinePresence",
    "COMPETITORS",
    "detect_competitor",
    "PIPELINE_STAGES",
    "STAGE_MAP",
    "VALID_STAGES",
    "is_valid_stage",
    "get_stage_color",
]
