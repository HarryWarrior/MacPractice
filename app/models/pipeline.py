"""
Estados y constantes del Pipeline de prospectos.
Ref: SPEC.md § 7.5 — Kanban Board.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineColumn:
    """Representa una columna del Kanban board."""
    id: str
    label: str
    color: str
    description: str


# Las 5 columnas del pipeline en orden de avance
PIPELINE_STAGES: list[PipelineColumn] = [
    PipelineColumn(
        id="new",
        label="New",
        color="#3B82F6",      # blue
        description="Importado pero no investigado",
    ),
    PipelineColumn(
        id="researched",
        label="Researched",
        color="#8B5CF6",      # purple
        description="IA completó investigación",
    ),
    PipelineColumn(
        id="outreach_sent",
        label="Outreach Sent",
        color="#F59E0B",      # amber
        description="Email aprobado y enviado/copiado",
    ),
    PipelineColumn(
        id="responded",
        label="Responded",
        color="#34D399",      # accentLight
        description="Prospecto respondió",
    ),
    PipelineColumn(
        id="meeting",
        label="Meeting Booked",
        color="#10B981",      # accent (verde esmeralda)
        description="Reunión agendada",
    ),
]

# Mapa rápido por id para lookups
STAGE_MAP: dict[str, PipelineColumn] = {
    stage.id: stage for stage in PIPELINE_STAGES
}

# IDs válidos como set para validación
VALID_STAGES: set[str] = {stage.id for stage in PIPELINE_STAGES}


def is_valid_stage(stage_id: str) -> bool:
    """Valida que un stage_id sea uno de los 5 permitidos."""
    return stage_id in VALID_STAGES


def get_stage_color(stage_id: str) -> str:
    """Devuelve el color hex asociado a un stage."""
    stage = STAGE_MAP.get(stage_id)
    return stage.color if stage else "#6B7280"
