"""
Servicios de negocio del sistema Mac Practice Dental Prospector.
"""

from app.services.research_service import do_research, do_batch_research
from app.services.outreach_service import do_outreach, regenerate_outreach
from app.services.email_service import send_real_email, format_email_for_clipboard, EmailResult
from app.services.csv_service import parse_csv, format_csv_preview
from app.services.storage_service import StorageService, storage

__all__ = [
    # Research
    "do_research",
    "do_batch_research",
    # Outreach
    "do_outreach",
    "regenerate_outreach",
    # Email
    "send_real_email",
    "format_email_for_clipboard",
    "EmailResult",
    # CSV
    "parse_csv",
    "format_csv_preview",
    # Storage
    "StorageService",
    "storage",
]
