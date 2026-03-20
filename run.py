"""
Mac Practice Dental Prospector — Punto de entrada principal.

Uso:
    python run.py

Este archivo resuelve el problema de imports entre paquetes (app/ y ui/)
asegurando que la raíz del proyecto esté en sys.path.
"""

import sys
import os

# Asegurar que la raíz del proyecto esté en el path de Python
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Ahora sí importamos la app de Gradio
import gradio as gr
from ui.app import build_app
from ui.theme import CSS
from app.config import GRADIO_HOST, GRADIO_PORT, DEBUG


def main():
    """Arranca la aplicación Gradio."""
    print("=" * 50)
    print("  🦷 Mac Practice · Dental Prospector")
    print("=" * 50)
    print(f"  Host:  {GRADIO_HOST}")
    print(f"  Port:  {GRADIO_PORT}")
    print(f"  Debug: {DEBUG}")
    print("=" * 50)

    app = build_app()
    app.launch(
        server_name=GRADIO_HOST,
        server_port=GRADIO_PORT,
        show_error=True,
        quiet=False,
    )


if __name__ == "__main__":
    main()
