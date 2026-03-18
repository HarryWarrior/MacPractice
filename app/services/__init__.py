"""
Servicios de negocio del sistema.
"""

from app.services.research_service import do_research, mock_research_generator
from app.services.storage_service import StorageService, storage

__all__ = [
    "do_research",
    "mock_research_generator",
    "StorageService",
    "storage",
]
