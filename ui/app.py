# ui/app.py
# Punto de entrada principal del frontend Gradio
# Mac Practice Dental Prospector — Layout Single-Page

import os
import gradio as gr
from dotenv import load_dotenv
from ui.theme import CSS, C
from ui.views.dashboard_view import build_dashboard_tab, _render_top_html, _build_static_summary_html, _render_kanban_html
from ui.views.workflow_view import build_workflow_tab
from ui.views.batch_review_view import build_batch_review

load_dotenv()

GRADIO_PORT = int(os.getenv("GRADIO_SERVER_PORT", 7860))
GRADIO_HOST = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")


def build_app() -> gr.Blocks:
    """
    Construye y retorna la aplicación Gradio completa.
    Layout: Single-page — Workflow arriba, Kanban + Pipeline abajo.
    Estado global compartido via gr.State.
    """
    with gr.Blocks(
        title="Mac Practice · Dental Prospector",
        css=CSS,
        theme=gr.themes.Base(
            primary_hue=gr.themes.colors.emerald,
            neutral_hue=gr.themes.colors.slate,
            font=[gr.themes.GoogleFont("Plus Jakarta Sans"), "sans-serif"],
        ),
    ) as demo:

        # ── Estado Global ────────────────────────────────────────────────
        prospects_state       = gr.State(None)
        active_prospect_state = gr.State(None)
        batch_progress_state  = gr.State(None)

        # ════════════════════════════════════════════════════════════════
        #  SECCIÓN SUPERIOR: Workflow (Research & Outreach)
        #  Visible/colapsable via botón "＋ New Prospect"
        # ════════════════════════════════════════════════════════════════
        with gr.Group(visible=False) as workflow_section:
            workflow_handles = build_workflow_tab(
                prospects_state, active_prospect_state
            )

        # ════════════════════════════════════════════════════════════════
        #  SECCIÓN BATCH REVIEW: Outreach review queue (post bulk research)
        # ════════════════════════════════════════════════════════════════
        batch_review_group, batch_queue_state, btn_finish_review = build_batch_review(prospects_state)

        # ════════════════════════════════════════════════════════════════
        #  SECCIÓN PRINCIPAL: Dashboard / Pipeline / Kanban
        # ════════════════════════════════════════════════════════════════
        (
            dashboard_top_html, executive_summary_display, dashboard_kanban_html,
            btn_new, btn_csv, batch_group, btn_batch_close,
        ) = build_dashboard_tab(prospects_state, batch_progress_state, batch_queue_state)

        # ── Navegación — mutual exclusivity ──────────────────────────
        workflow_visible = gr.State(False)
        batch_visible    = gr.State(False)

        # "Research Prospect" → toggle workflow, always close batch
        def _toggle_workflow_exclusive(wf_vis):
            new_wf = not wf_vis
            return new_wf, gr.update(visible=new_wf), False, gr.update(visible=False)

        btn_new.click(
            fn=_toggle_workflow_exclusive,
            inputs=[workflow_visible],
            outputs=[workflow_visible, workflow_section, batch_visible, batch_group],
        )

        # "Bulk Research" → toggle batch, always close workflow
        def _toggle_batch_exclusive(b_vis):
            new_b = not b_vis
            return new_b, gr.update(visible=new_b), False, gr.update(visible=False)

        btn_csv.click(
            fn=_toggle_batch_exclusive,
            inputs=[batch_visible],
            outputs=[batch_visible, batch_group, workflow_visible, workflow_section],
        )

        # Cancel batch → always close
        btn_batch_close.click(
            fn=lambda: (False, gr.update(visible=False)),
            outputs=[batch_visible, batch_group],
        )

        # "Back to Pipeline" → always hide workflow (from send stage)
        workflow_handles["btn_back_to_pipeline"].click(
            fn=lambda: (False, gr.update(visible=False)),
            outputs=[workflow_visible, workflow_section],
        )
        # "← Pipeline" on profile stage → also hide workflow
        workflow_handles["btn_back_to_input"].click(
            fn=lambda: (False, gr.update(visible=False)),
            outputs=[workflow_visible, workflow_section],
        )


        # ── Seed de demo ──────────────────────────────────────────────
        demo.load(
            fn=_load_demo_data,
            outputs=[
                prospects_state,
                dashboard_top_html,
                executive_summary_display,
                dashboard_kanban_html,
            ],
        )

    return demo


def _load_demo_data():
    """Loads demo prospects so the kanban and funnel are populated on startup."""
    sample_prospects = [
        # ── New (8) ────────────────────────────────────────────
        {
            "id": "p_demo_001", "clinic_name": "Mountain View Dental",
            "location": "Denver, CO", "type": "dental", "practitioners": 2,
            "staff_estimate": 5, "fit_score": 6, "priority": "warm",
            "current_software": "Open Dental", "pipeline_stage": "new",
        },
        {
            "id": "p_demo_002", "clinic_name": "Lakeside Family Dentistry",
            "location": "Minneapolis, MN", "type": "dental", "practitioners": 3,
            "staff_estimate": 7, "fit_score": 7, "priority": "warm",
            "current_software": "Dentrix", "pipeline_stage": "new",
        },
        {
            "id": "p_demo_003", "clinic_name": "Coastal Smiles",
            "location": "San Diego, CA", "type": "dental", "practitioners": 2,
            "staff_estimate": 4, "fit_score": 5, "priority": "cool",
            "current_software": "Unknown", "pipeline_stage": "new",
        },
        {
            "id": "p_demo_004", "clinic_name": "Green Valley Dental",
            "location": "Las Vegas, NV", "type": "dental", "practitioners": 4,
            "staff_estimate": 9, "fit_score": 7, "priority": "warm",
            "current_software": "Eaglesoft", "pipeline_stage": "new",
        },
        {
            "id": "p_demo_005", "clinic_name": "Northgate Orthodontics",
            "location": "Chicago, IL", "type": "ortho", "practitioners": 2,
            "staff_estimate": 6, "fit_score": 6, "priority": "warm",
            "current_software": "Dolphin", "pipeline_stage": "new",
        },
        {
            "id": "p_demo_006", "clinic_name": "Riverbend Dental Group",
            "location": "Nashville, TN", "type": "dental", "practitioners": 5,
            "staff_estimate": 11, "fit_score": 8, "priority": "hot",
            "current_software": "Dentrix", "pipeline_stage": "new",
        },
        {
            "id": "p_demo_007", "clinic_name": "Westside Smiles",
            "location": "Portland, OR", "type": "dental", "practitioners": 3,
            "staff_estimate": 6, "fit_score": 6, "priority": "warm",
            "current_software": "Carestream", "pipeline_stage": "new",
        },
        {
            "id": "p_demo_008", "clinic_name": "Harbor View Dental",
            "location": "Baltimore, MD", "type": "dental", "practitioners": 2,
            "staff_estimate": 4, "fit_score": 5, "priority": "cool",
            "current_software": "Unknown", "pipeline_stage": "new",
        },
        # ── Researched (5) ─────────────────────────────────────
        {
            "id": "p_demo_009", "clinic_name": "Bright Smile Dental",
            "location": "Austin, TX", "type": "dental", "practitioners": 4,
            "staff_estimate": 8, "fit_score": 8, "priority": "hot",
            "current_software": "Dentrix", "pipeline_stage": "researched",
        },
        {
            "id": "p_demo_010", "clinic_name": "Summit Dental Group",
            "location": "Salt Lake City, UT", "type": "dental", "practitioners": 6,
            "staff_estimate": 13, "fit_score": 9, "priority": "hot",
            "current_software": "Eaglesoft", "pipeline_stage": "researched",
        },
        {
            "id": "p_demo_011", "clinic_name": "Pinecrest Family Dental",
            "location": "Atlanta, GA", "type": "dental", "practitioners": 3,
            "staff_estimate": 7, "fit_score": 7, "priority": "warm",
            "current_software": "Dentrix", "pipeline_stage": "researched",
        },
        {
            "id": "p_demo_012", "clinic_name": "Pacific Dental Studio",
            "location": "Seattle, WA", "type": "dental", "practitioners": 4,
            "staff_estimate": 9, "fit_score": 8, "priority": "hot",
            "current_software": "Open Dental", "pipeline_stage": "researched",
        },
        {
            "id": "p_demo_013", "clinic_name": "Desert Bloom Dentistry",
            "location": "Scottsdale, AZ", "type": "dental", "practitioners": 3,
            "staff_estimate": 6, "fit_score": 7, "priority": "warm",
            "current_software": "Eaglesoft", "pipeline_stage": "researched",
        },
        # ── Outreach Sent (3) ──────────────────────────────────
        {
            "id": "p_demo_014", "clinic_name": "Sunrise Family Dentistry",
            "location": "Phoenix, AZ", "type": "dental", "practitioners": 7,
            "staff_estimate": 15, "fit_score": 9, "priority": "hot",
            "current_software": "Eaglesoft", "pipeline_stage": "outreach_sent",
        },
        {
            "id": "p_demo_015", "clinic_name": "Blue Ridge Dental",
            "location": "Charlotte, NC", "type": "dental", "practitioners": 5,
            "staff_estimate": 10, "fit_score": 8, "priority": "hot",
            "current_software": "Dentrix", "pipeline_stage": "outreach_sent",
        },
        {
            "id": "p_demo_016", "clinic_name": "Maple Street Smiles",
            "location": "Columbus, OH", "type": "dental", "practitioners": 3,
            "staff_estimate": 6, "fit_score": 7, "priority": "warm",
            "current_software": "Carestream", "pipeline_stage": "outreach_sent",
        },
        # ── Responded (2) ──────────────────────────────────────
        {
            "id": "p_demo_017", "clinic_name": "Capitol Smiles",
            "location": "Sacramento, CA", "type": "dental", "practitioners": 3,
            "staff_estimate": 6, "fit_score": 8, "priority": "hot",
            "current_software": "Dentrix", "pipeline_stage": "responded",
        },
        {
            "id": "p_demo_018", "clinic_name": "Elmwood Dental Care",
            "location": "Houston, TX", "type": "dental", "practitioners": 4,
            "staff_estimate": 8, "fit_score": 9, "priority": "hot",
            "current_software": "Eaglesoft", "pipeline_stage": "responded",
        },
        # ── Meeting Booked (1) ─────────────────────────────────
        {
            "id": "p_demo_019", "clinic_name": "Prestige Dental Partners",
            "location": "Miami, FL", "type": "dental", "practitioners": 8,
            "staff_estimate": 18, "fit_score": 10, "priority": "hot",
            "current_software": "Dentrix", "pipeline_stage": "meeting",
        },
    ]
    return (
        sample_prospects,
        _render_top_html(sample_prospects),
        _build_static_summary_html(sample_prospects),
        _render_kanban_html(sample_prospects),
    )


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
        share=True
    )
