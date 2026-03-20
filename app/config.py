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
GRADIO_HOST = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")
GRADIO_PORT = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

# ── Entorno ───────────────────────────────────────────────
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

def verify_api_keys():
    """Verifica que las variables importantes existan y lanza alertas en log."""
    import logging
    logger = logging.getLogger("MacPracticeConfig")
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    missing = []
    
    if GEMINI_API_KEY:
        logger.info(f"✅ GEMINI_API_KEY detectada (termina en ...{GEMINI_API_KEY[-4:] if len(GEMINI_API_KEY) > 4 else '***'})")
    else:
        logger.warning("❌ GEMINI_API_KEY FALTA EN EL ENTORNO o está vacía. El Agente A (Investigación) y Agente B (Pipeline) fallarán.")
        missing.append("GEMINI_API_KEY")

    if OPENAI_API_KEY:
        logger.info(f"✅ OPENAI_API_KEY detectada (termina en ...{OPENAI_API_KEY[-4:] if len(OPENAI_API_KEY) > 4 else '***'})")
    else:
        logger.info("ℹ️ OPENAI_API_KEY no detectada. El Agente C (Corrección de tono) y fallbacks no funcionarán si no se provee.")

    if GMAIL_SENDER_EMAIL and GMAIL_APP_PASSWORD:
        logger.info(f"✅ Credenciales de Gmail detectadas (correo: {GMAIL_SENDER_EMAIL})")
    else:
        logger.warning("❌ Falta GMAIL_SENDER_EMAIL o GMAIL_APP_PASSWORD. El envío automático de correos fallará.")
        if not GMAIL_SENDER_EMAIL: missing.append("GMAIL_SENDER_EMAIL")
        if not GMAIL_APP_PASSWORD: missing.append("GMAIL_APP_PASSWORD")

    if not missing:
        logger.info("✅ Variables de entorno esenciales cargadas correctamente.")
    else:
        logger.warning(f"⚠️ Faltan las siguientes variables críticas: {', '.join(missing)}")

