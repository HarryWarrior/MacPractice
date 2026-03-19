# ui/app.py
# Punto de entrada principal del frontend Gradio
# Mac Practice Dental Prospector — Fase 1

import os
import gradio as gr
from dotenv import load_dotenv
from ui.theme import CSS, C
from ui.views.dashboard_view import build_dashboard_tab, render_dashboard_html
from ui.views.workflow_view import build_workflow_tab

load_dotenv()

GRADIO_PORT = int(os.getenv("GRADIO_SERVER_PORT", 7860))
GRADIO_HOST = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")


def build_app() -> gr.Blocks:
    """
    Construye y retorna la aplicación Gradio completa.
    Layout: 2 tabs (Dashboard | Research & Outreach)
    Estado global compartido entre tabs via gr.State.
    """
    with gr.Blocks(title="Mac Practice · Dental Prospector") as demo:

        # ── Estado Global ────────────────────────────────────────────────
        prospects_state       = gr.State([])    # list[dict] — todos los prospects
        active_prospect_state = gr.State(None)  # dict | None — prospect activo en workflow
        batch_progress_state  = gr.State(None)  # dict | None — {current, total, currentName}

        # ── Tabs Principales ─────────────────────────────────────────────
        with gr.Tabs(elem_classes=["mp-tabs"]) as tabs:

            # ════════════════════════════════════════════════
            #  TAB 1 — PIPELINE / DASHBOARD
            # ════════════════════════════════════════════════
            with gr.Tab("📊 Pipeline", elem_id="tab-dashboard"):
                dashboard_html, btn_new, btn_csv = build_dashboard_tab(
                    prospects_state, batch_progress_state
                )

            # ════════════════════════════════════════════════
            #  TAB 2 — RESEARCH & OUTREACH WORKFLOW
            # ════════════════════════════════════════════════
            with gr.Tab("🔍 Research & Outreach", elem_id="tab-workflow"):
                workflow_handles = build_workflow_tab(
                    prospects_state, active_prospect_state
                )

        # ── Navegación entre tabs ─────────────────────────────────────────
        # "New Prospect" → cambia a la tab de workflow
        btn_new.click(
            fn=lambda: gr.update(selected="🔍 Research & Outreach"),
            outputs=[tabs],
        )

        # "Back to Pipeline" en el workflow → vuelve al dashboard
        workflow_handles["btn_back_to_pipeline"].click(
            fn=lambda: gr.update(selected="📊 Pipeline"),
            outputs=[tabs],
        )

        # ── Seed de demo (opcional) ────────────────────────────────────────
        # Añade un prospect de ejemplo al cargar para que el kanban no esté vacío
        demo.load(
            fn=_load_demo_data,
            outputs=[prospects_state, dashboard_html],
        )

    return demo


def _load_demo_data():
    """Carga un prospect de demo para que el pipeline no esté vacío al iniciar."""
    sample_prospects = [
        {
            "id": "p_demo_001",
            "input": "Bright Smile Dental, Austin TX",
            "clinic_name": "Bright Smile Dental",
            "location": "Austin, TX",
            "type": "dental",
            "practitioners": 4,
            "staff_estimate": 8,
            "fit_score": 8,
            "priority": "hot",
            "current_software": "Dentrix",
            "pipeline_stage": "researched",
            "researched_at": "2026-03-18T10:00:00",
        },
        {
            "id": "p_demo_002",
            "input": "Mountain View Dental, Denver CO",
            "clinic_name": "Mountain View Dental",
            "location": "Denver, CO",
            "type": "dental",
            "practitioners": 2,
            "staff_estimate": 5,
            "fit_score": 6,
            "priority": "warm",
            "current_software": "Open Dental",
            "pipeline_stage": "new",
        },
        {
            "id": "p_demo_003",
            "input": "Sunrise Family Dentistry, Phoenix AZ",
            "clinic_name": "Sunrise Family Dentistry",
            "location": "Phoenix, AZ",
            "type": "dental",
            "practitioners": 7,
            "staff_estimate": 15,
            "fit_score": 9,
            "priority": "hot",
            "current_software": "Eaglesoft",
            "pipeline_stage": "outreach_sent",
            "outreach_sent_at": "2026-03-17T14:30:00",
        },
        {
            "id": "p_demo_004",
            "input": "Capitol Smiles, Sacramento CA",
            "clinic_name": "Capitol Smiles",
            "location": "Sacramento, CA",
            "type": "dental",
            "practitioners": 3,
            "staff_estimate": 6,
            "fit_score": 5,
            "priority": "warm",
            "current_software": "Unknown",
            "pipeline_stage": "responded",
        },
    ]
    return sample_prospects, render_dashboard_html(sample_prospects)


if __name__ == "__main__":
    app = build_app()
    app.launch(
        server_name=GRADIO_HOST,
        server_port=GRADIO_PORT,
        show_error=True,
        quiet=False,
        css=CSS,
        theme=gr.themes.Base(
            primary_hue=gr.themes.colors.emerald,
            neutral_hue=gr.themes.colors.slate,
            font=[gr.themes.GoogleFont("Plus Jakarta Sans"), "sans-serif"],
        ),
    )
