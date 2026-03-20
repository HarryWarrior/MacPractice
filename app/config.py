"""
Configuración central del proyecto Mac Practice Dental Prospector.
Carga las variables de entorno desde .env y expone constantes globales.
"""

import os
from dotenv import load_dotenv

# Cargar .env del directorio raíz del proyecto
load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(os.path.dirname(__file__)), ".env"
    )
)


# ── API Keys ──────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ── Gmail ─────────────────────────────────────────────────
GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

# ── Modelos de IA ─────────────────────────────────────────
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ── Rate Limiting ─────────────────────────────────────────
# Google AI Studio free tier: 15 RPM
BATCH_DELAY_SECONDS = int(os.getenv("BATCH_DELAY_SECONDS", "5"))

# ── Gradio ────────────────────────────────────────────────
GRADIO_HOST = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
GRADIO_PORT = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

# ── Entorno ───────────────────────────────────────────────
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
