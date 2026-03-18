"""
Servicio de persistencia de prospectos.
Ref: SPEC.md § 5 — Persistencia de Datos.

Almacena prospectos en memoria (diccionario) durante la sesión
y permite exportar/importar desde archivo JSON.
"""

import json
import os
from typing import Optional
from datetime import datetime, timezone

from app.models.prospect import Prospect


class StorageService:
    """
    Gestiona los prospectos en memoria con capacidad de
    serialización a JSON para persistencia entre sesiones.
    """

    def __init__(self, storage_path: str = "data/pipeline.json"):
        self._prospects: dict[str, Prospect] = {}
        self._storage_path = storage_path

    # ── CRUD ──────────────────────────────────────────────

    def add_prospect(self, prospect: Prospect) -> Prospect:
        """Agrega un prospecto al storage."""
        self._prospects[prospect.id] = prospect
        self._auto_save()
        return prospect

    def get_prospect(self, prospect_id: str) -> Optional[Prospect]:
        """Obtiene un prospecto por ID."""
        return self._prospects.get(prospect_id)

    def get_all_prospects(self) -> list[Prospect]:
        """Retorna todos los prospectos como lista."""
        return list(self._prospects.values())

    def update_prospect(
        self,
        prospect_id: str,
        updates: dict,
    ) -> Optional[Prospect]:
        """
        Actualiza campos de un prospecto existente.
        Solo actualiza campos que existen en el dataclass.
        """
        prospect = self._prospects.get(prospect_id)
        if not prospect:
            return None

        for key, value in updates.items():
            if hasattr(prospect, key):
                setattr(prospect, key, value)

        self._auto_save()
        return prospect

    def delete_prospect(self, prospect_id: str) -> bool:
        """Elimina un prospecto del storage."""
        if prospect_id in self._prospects:
            del self._prospects[prospect_id]
            self._auto_save()
            return True
        return False

    def move_prospect_stage(
        self,
        prospect_id: str,
        new_stage: str,
    ) -> Optional[Prospect]:
        """Mueve un prospecto a una nueva etapa del pipeline."""
        from app.models.pipeline import is_valid_stage
        if not is_valid_stage(new_stage):
            return None
        return self.update_prospect(
            prospect_id, {"pipeline_stage": new_stage}
        )

    # ── Métricas del Pipeline ─────────────────────────────

    def get_pipeline_metrics(self) -> dict:
        """
        Calcula las 5 métricas del dashboard.
        Ref: SPEC.md § 7.4.
        """
        prospects = self.get_all_prospects()
        total = len(prospects)

        # Avg fit score
        scored = [p for p in prospects if p.fit_score is not None]
        avg_score = (
            sum(p.fit_score for p in scored) / len(scored)
            if scored else 0.0
        )

        # Competitors found
        competitors = sum(
            1 for p in prospects
            if p.current_software.lower() not in ("unknown", "paper-based", "")
        )

        # Outreach sent
        sent_stages = {"outreach_sent", "responded", "meeting"}
        sent_count = sum(
            1 for p in prospects
            if p.pipeline_stage in sent_stages
        )

        # Response rate
        responded_count = sum(
            1 for p in prospects
            if p.pipeline_stage in ("responded", "meeting")
        )
        response_rate = (
            (responded_count / sent_count * 100)
            if sent_count > 0 else 0.0
        )

        return {
            "total_prospects": total,
            "avg_fit_score": round(avg_score, 1),
            "competitors_found": competitors,
            "outreach_sent": sent_count,
            "response_rate": round(response_rate, 1),
        }

    def get_prospects_by_stage(self) -> dict[str, list[Prospect]]:
        """Agrupa prospectos por etapa del pipeline (para Kanban)."""
        from app.models.pipeline import PIPELINE_STAGES
        grouped = {stage.id: [] for stage in PIPELINE_STAGES}
        for prospect in self._prospects.values():
            stage = prospect.pipeline_stage
            if stage in grouped:
                grouped[stage].append(prospect)
            else:
                grouped["new"].append(prospect)
        return grouped

    # ── Persistencia a archivo ────────────────────────────

    def save_to_file(self, path: str = "") -> bool:
        """Guarda todos los prospectos como JSON en disco."""
        file_path = path or self._storage_path
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            data = [p.to_dict() for p in self._prospects.values()]
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[StorageService] Error al guardar: {e}")
            return False

    def load_from_file(self, path: str = "") -> bool:
        """Carga prospectos desde un archivo JSON previamente guardado."""
        file_path = path or self._storage_path
        try:
            if not os.path.exists(file_path):
                return False
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._prospects = {
                item["id"]: Prospect.from_dict(item)
                for item in data
                if "id" in item
            }
            return True
        except Exception as e:
            print(f"[StorageService] Error al cargar: {e}")
            self._prospects = {}
            return False

    def _auto_save(self):
        """Auto-guarda después de cada cambio si existe un path configurado."""
        if self._storage_path:
            self.save_to_file()


# Instancia global (singleton simple) para uso en toda la app
storage = StorageService()
