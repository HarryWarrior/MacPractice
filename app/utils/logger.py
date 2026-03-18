"""
Generador de logs con timestamps para la interfaz de Gradio.
Ref: SPEC.md § 4.4 — Sistema de Logs en Tiempo Real.

Todas las funciones de log usan `yield` para alimentar
el componente gr.Textbox que simula una terminal en la UI.
"""

import time
from typing import Generator

# Emojis estándar del sistema de logs
_ICONS = {
    "start":    "🟢",
    "search":   "🔎",
    "warning":  "⚠️",
    "success":  "✅",
    "write":    "✍️",
    "error":    "🚨",
    "info":     "ℹ️",
    "email":    "📧",
    "batch":    "📦",
    "done":     "🏁",
}


class LogAccumulator:
    """
    Acumula líneas de log y las devuelve como texto completo.
    Diseñado para alimentar un gr.Textbox en modo streaming con `yield`.

    Uso típico:
        log = LogAccumulator()
        log.add("start", "Iniciando investigación...")
        yield log.text   # Gradio actualiza la UI
    """

    def __init__(self):
        self._lines: list[str] = []
        self._start_time: float = time.time()

    def _elapsed(self) -> str:
        """Retorna el tiempo transcurrido desde el inicio en formato [MM:SS]."""
        seconds = int(time.time() - self._start_time)
        minutes = seconds // 60
        secs = seconds % 60
        return f"[{minutes:02d}:{secs:02d}]"

    def add(self, icon_key: str, message: str) -> str:
        """
        Agrega una línea de log con timestamp e ícono.

        Args:
            icon_key: Clave del ícono (_ICONS).
            message: Texto del mensaje.

        Returns:
            El texto completo acumulado (para yield).
        """
        icon = _ICONS.get(icon_key, "•")
        line = f"{self._elapsed()} {icon} {message}"
        self._lines.append(line)
        return self.text

    @property
    def text(self) -> str:
        """Texto completo de todas las líneas acumuladas."""
        return "\n".join(self._lines)

    def clear(self):
        """Limpia el log y reinicia el timer."""
        self._lines.clear()
        self._start_time = time.time()


def create_research_log_steps() -> list[dict]:
    """
    Retorna los 6 pasos de progreso del research.
    Ref: SPEC.md § 9.3 — Etapa 2: Research.
    """
    return [
        {
            "icon": "search",
            "message": "Searching clinic website & Google Business...",
        },
        {
            "icon": "search",
            "message": "Scanning LinkedIn for company & decision makers...",
        },
        {
            "icon": "search",
            "message": "Checking job postings for software & hiring signals...",
        },
        {
            "icon": "search",
            "message": "Analyzing reviews on Healthgrades, Zocdoc, Google...",
        },
        {
            "icon": "info",
            "message": "Detecting competitor software (Dentrix, Eaglesoft...)...",
        },
        {
            "icon": "info",
            "message": "Scoring fit & compiling intelligence report...",
        },
    ]
