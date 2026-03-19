"""
Servicio de Email — Envío real via Gmail con smtplib.
Ref: SPEC.md § 9.7, § 16.3.

Usa Gmail App Password para envío directo sin OAuth.
Fallback: si el envío falla, retorna el email listo para copiar al portapapeles.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Generator
from dataclasses import dataclass

from app.config import GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD
from app.utils.logger import LogAccumulator


@dataclass
class EmailResult:
    """Resultado del intento de envío de email."""
    sent: bool = False
    error: str = ""
    subject: str = ""
    body: str = ""
    recipient: str = ""
    sender: str = ""


# Palabras clave que indican que las credenciales son placeholder
_PLACEHOLDER_KEYWORDS = [
    "tu-", "your-", "xxxx", "aqui", "here",
    "example", "placeholder", "change-me",
    "tu_email", "your_email", "test@",
]


def _credentials_are_valid() -> bool:
    """
    Verifica que las credenciales de Gmail sean reales,
    no los placeholder del .env.development.
    """
    if not GMAIL_SENDER_EMAIL or not GMAIL_APP_PASSWORD:
        return False

    email_lower = GMAIL_SENDER_EMAIL.lower()
    pass_lower = GMAIL_APP_PASSWORD.lower()
    print(f"[EMAIL] Sender: {GMAIL_SENDER_EMAIL}")
    print(f"[EMAIL] Password: {GMAIL_APP_PASSWORD}")
    for keyword in _PLACEHOLDER_KEYWORDS:
        if keyword in email_lower or keyword in pass_lower:
            return False

    # Verificar que el email tenga formato básico válido
    if "@" not in GMAIL_SENDER_EMAIL or "." not in GMAIL_SENDER_EMAIL:
        return False

    return True


def send_real_email(
    recipient: str,
    subject: str,
    body: str,
    sender_name: str = "Mac Practice Sales",
) -> Generator[tuple[str, EmailResult | None], None, None]:
    """
    Envía un email real usando Gmail SMTP con App Password.
    Ref: SPEC.md § 16.3 — Integración de Gmail (Fricción Cero).

    Yields:
        (log_text, email_result | None)
        El EmailResult se produce al final.

    Graceful degradation:
        Si falla, el email queda disponible para copiar
        y el prospect se marca como outreach_sent igualmente.
    """
    log = LogAccumulator()

    yield log.add("email", f"Preparando envío a: {recipient}..."), None

    result = EmailResult(
        subject=subject,
        body=body,
        recipient=recipient,
        sender=GMAIL_SENDER_EMAIL or sender_name,
    )

    # ── Validar credenciales ──────────────────────────
    if not _credentials_are_valid():
        result.error = (
            "Credenciales de Gmail no configuradas. "
            "Agrega GMAIL_SENDER_EMAIL y GMAIL_APP_PASSWORD reales a tu .env"
        )
        yield log.add("warning", result.error), None
        yield log.add(
            "info",
            "📋 Email guardado localmente — puedes copiarlo al portapapeles."
        ), result
        return

    # ── Construir el mensaje ──────────────────────────
    yield log.add("info", "Construyendo mensaje MIME..."), None

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{sender_name} <{GMAIL_SENDER_EMAIL}>"
    msg["To"] = recipient
    msg["Subject"] = subject

    # Versión de texto plano
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # Versión HTML simple (preserva saltos de línea)
    html_body = body.replace("\n", "<br>")
    html = f"""
    <html>
    <body style="font-family: 'Plus Jakarta Sans', Arial, sans-serif;
                 font-size: 14px; color: #333; line-height: 1.6;">
        {html_body}
    </body>
    </html>
    """
    msg.attach(MIMEText(html, "html", "utf-8"))

    # ── Enviar via SMTP (timeout de 10s) ──────────────
    try:
        yield log.add("email", "Conectando a Gmail SMTP..."), None

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        result.sent = True
        yield log.add(
            "success",
            f"✅ Email enviado exitosamente a {recipient}"
        ), result

    except smtplib.SMTPAuthenticationError:
        result.error = (
            "Error de autenticación con Gmail. "
            "Verifica tu GMAIL_APP_PASSWORD (no es tu contraseña normal, "
            "es una App Password de Google)."
        )
        yield log.add("error", result.error), None
        yield log.add(
            "info",
            "📋 Email guardado — cópialo manualmente."
        ), result

    except smtplib.SMTPRecipientsRefused:
        result.error = f"Gmail rechazó al destinatario: {recipient}"
        yield log.add("error", result.error), None
        yield log.add(
            "info",
            "📋 Verifica la dirección de email del destinatario."
        ), result

    except Exception as e:
        result.error = f"Error de envío: {str(e)[:120]}"
        yield log.add("error", result.error), None
        yield log.add(
            "info",
            "📋 Email guardado localmente — puedes copiarlo."
        ), result


def format_email_for_clipboard(
    subject: str,
    body: str,
    sender_name: str = "",
    sender_title: str = "",
    recipient: str = "",
) -> str:
    """
    Formatea el email completo como texto listo para copiar al portapapeles.
    Ref: SPEC.md § 9.7 — Clipboard fallback.
    """
    parts = []
    if recipient:
        parts.append(f"To: {recipient}")
    parts.append(f"Subject: {subject}")
    parts.append("")
    parts.append(body)
    if sender_name:
        parts.append("")
        parts.append(sender_name)
    if sender_title:
        parts.append(sender_title)
    return "\n".join(parts)
