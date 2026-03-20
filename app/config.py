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
GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").replace(" ", "")

# ── Modelos de IA ─────────────────────────────────────────
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ── Rate Limiting ─────────────────────────────────────────
# Google AI Studio free tier: 15 RPM
BATCH_DELAY_SECONDS = int(os.getenv("BATCH_DELAY_SECONDS", "5"))

# ── Gradio ────────────────────────────────────────────────
GRADIO_HOST = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")
GRADIO_PORT = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

# ── Entorno ───────────────────────────────────────────────
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

def verify_api_keys():
    """Verifies that important environment variables exist and logs warnings if missing."""
    import logging
    logger = logging.getLogger("MacPracticeConfig")
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    missing = []
    
    if GEMINI_API_KEY:
        logger.info(f"✅ GEMINI_API_KEY detected (ends with ...{GEMINI_API_KEY[-4:] if len(GEMINI_API_KEY) > 4 else '***'})")
    else:
        logger.warning("❌ GEMINI_API_KEY IS MISSING or empty. Agent A (Research) and Agent B (Pipeline) will fail.")
        missing.append("GEMINI_API_KEY")

    if OPENAI_API_KEY:
        logger.info(f"✅ OPENAI_API_KEY detected (ends with ...{OPENAI_API_KEY[-4:] if len(OPENAI_API_KEY) > 4 else '***'})")
    else:
        logger.info("ℹ️ OPENAI_API_KEY not detected. Agent C (Tone Correction) and fallbacks will not work unless provided.")

    if GMAIL_SENDER_EMAIL and GMAIL_APP_PASSWORD:
        logger.info(f"✅ Gmail credentials detected (email: {GMAIL_SENDER_EMAIL})")
    else:
        logger.warning("❌ Missing GMAIL_SENDER_EMAIL or GMAIL_APP_PASSWORD. Automated email sending will fail.")
        if not GMAIL_SENDER_EMAIL: missing.append("GMAIL_SENDER_EMAIL")
        if not GMAIL_APP_PASSWORD: missing.append("GMAIL_APP_PASSWORD")

    if not missing:
        logger.info("✅ Essential environment variables loaded successfully.")
    else:
        logger.warning(f"⚠️ Missing the following critical variables: {', '.join(missing)}")

