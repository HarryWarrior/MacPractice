# ui/views/dashboard_view.py
# Vista Dashboard — Pipeline Kanban + Métricas + Batch Import
# Fase 4: Batch CSV, barra de progreso, kanban funcional (move stages)

import gradio as gr
from ui.theme import C, navbar_html, metric_card_html, badge_html
from ui.components.prospect_card import prospect_card_html, empty_col_html
from ui.components.batch_modal import build_batch_section

from app.services.research_service import do_batch_research
from app.models.pipeline import PIPELINE_STAGES

# ──────────────────────────────────────────────
#  Constantes de columnas Kanban
# ──────────────────────────────────────────────
KANBAN_COLS = [
    {"id": "new",           "label": "New",           "color": C["blue"]},
    {"id": "researched",    "label": "Researched",     "color": C["purple"]},
    {"id": "outreach_sent", "label": "Outreach Sent",  "color": C["amber"]},
    {"id": "responded",     "label": "Responded",      "color": C["accent"]},
    {"id": "meeting",       "label": "Meeting Booked", "color": C["accent_light"]},
]

STAGE_CHOICES = [col["label"] for col in KANBAN_COLS]
STAGE_ID_FROM_LABEL = {col["label"]: col["id"] for col in KANBAN_COLS}
STAGE_LABEL_FROM_ID = {col["id"]: col["label"] for col in KANBAN_COLS}


# ──────────────────────────────────────────────
#  Builders de HTML puro
# ──────────────────────────────────────────────

def _build_metrics_html(prospects: list) -> str:
    """Genera el bloque de 5 MetricCards con los datos actuales del pipeline."""
    total = len(prospects)

    scored = [p["fit_score"] for p in prospects if p.get("fit_score") is not None]
    avg_score = round(sum(scored) / len(scored), 1) if scored else None
    if avg_score is None:
        score_val, score_color = "—", C["text_dim"]
    elif avg_score >= 7:
        score_val, score_color = str(avg_score), C["accent"]
    elif avg_score >= 5:
        score_val, score_color = str(avg_score), C["amber"]
    else:
        score_val, score_color = str(avg_score), C["red"]

    skip_sw = {"unknown", "paper-based", "paper", ""}
    competitors = sum(
        1 for p in prospects
        if (p.get("current_software") or "").lower().strip() not in skip_sw
    )

    sent_stages = {"outreach_sent", "responded", "meeting"}
    sent_count = sum(1 for p in prospects if p.get("pipeline_stage") in sent_stages)

    responded_count = sum(
        1 for p in prospects if p.get("pipeline_stage") in {"responded", "meeting"}
    )
    if sent_count > 0:
        rate = round(responded_count / sent_count * 100)
        rate_val = f"{rate}%"
        rate_color = C["accent"] if rate >= 20 else C["amber"]
    else:
        rate_val = "—"
        rate_color = C["text_dim"]

    cards_html = "".join([
        metric_card_html("Total Prospects", str(total) if total else "0",
                         color=C["text"]),
        metric_card_html("Avg Fit Score", score_val,
                         sub="out of 10", color=score_color),
        metric_card_html("Competitors Found", str(competitors),
                         sub="known software", color=C["purple"]),
        metric_card_html("Outreach Sent", str(sent_count),
                         sub="emails out", color=C["amber"]),
        metric_card_html("Response Rate", rate_val,
                         sub="of sent", color=rate_color),
    ])

    return f'<div class="metrics-grid">{cards_html}</div>'


def _build_kanban_html(prospects: list) -> str:
    """
    Genera el Kanban board con soporte drag & drop.
    Cada columna es un drop target. El payload del drop es prospect_id|stage_id,
    enviado a un gr.Textbox hidden con elem_id='kanban-drop-target'.
    """
    # Drop handlers inline (Gradio preserva atributos de evento en HTML)
    _drop_js = (
        "(function(e){{"
        "e.preventDefault();"
        "e.currentTarget.classList.remove('drag-over');"
        "var pid=e.dataTransfer.getData('text/plain');"
        "var stage=e.currentTarget.getAttribute('data-stage');"
        "var el=document.querySelector('#kanban-drop-target textarea');"
        "if(el&&pid&&stage){{"
        "el.value=pid+'|'+stage;"
        "el.dispatchEvent(new Event('input',{{bubbles:true}}));"
        "}}"
        "}})(event)"
    )
    _over_js = (
        "event.preventDefault();"
        "event.currentTarget.classList.add('drag-over')"
    )
    _leave_js = (
        "if(!event.currentTarget.contains(event.relatedTarget))"
        "{{event.currentTarget.classList.remove('drag-over')}}"
    )

    cols_html = ""
    for col in KANBAN_COLS:
        col_prospects = [
            p for p in prospects if p.get("pipeline_stage") == col["id"]
        ]
        count = len(col_prospects)
        cards_html = (
            "".join(prospect_card_html(p) for p in col_prospects)
            if col_prospects
            else empty_col_html()
        )
        cols_html += f"""
<div class="kanban-col"
     data-stage="{col['id']}"
     ondragover="{_over_js}"
     ondragleave="{_leave_js}"
     ondrop="{_drop_js}">
    <div class="kanban-col-header">
        <span class="kanban-dot" style="background:{col['color']};"></span>
        <span class="kanban-col-name">{col['label']}</span>
        <span class="kanban-count">{count}</span>
    </div>
    {cards_html}
</div>
"""
    return f'<div class="kanban-board">{cols_html}</div>'


def _build_empty_state_html() -> str:
    return f"""
<div style="padding:32px;">
  <div style="border:1px dashed {C['border']}; border-radius:18px; padding:72px 40px; text-align:center;
              background:linear-gradient(145deg, {C['surface']} 0%, {C['card']} 100%);">
    <div style="font-size:52px; margin-bottom:18px; opacity:0.5; filter:grayscale(0.3);">🎯</div>
    <div style="font-size:20px; font-weight:800; color:{C['text']}; margin-bottom:8px;">
        Your pipeline is empty
    </div>
    <div style="font-size:14px; color:{C['text_muted']}; margin-bottom:28px; font-weight:500;">
        Import a CSV or research your first dental prospect to get started.
    </div>
  </div>
</div>
"""


def _build_batch_progress_html(batch_progress: dict | None) -> str:
    if not batch_progress:
        return ""
    current = batch_progress.get("current", 0)
    total   = batch_progress.get("total", 1)
    name    = batch_progress.get("currentName", "")
    pct     = round(current / total * 100) if total else 0
    return f"""
<div class="batch-bar">
    <div class="batch-spinner"></div>
    <div style="flex:1; min-width:0;">
        <div style="font-weight:600; color:{C['text']}; margin-bottom:4px;">
            Batch researching: {current}/{total}
            <span style="color:{C['text_muted']}; font-weight:400;"> — {name}</span>
        </div>
        <div class="batch-track">
            <div class="batch-fill" style="width:{pct}%;"></div>
        </div>
    </div>
    <div style="font-family:'JetBrains Mono',monospace; font-size:12px;
                color:{C['accent']}; font-weight:600; flex-shrink:0;">{pct}%</div>
</div>
"""


def render_dashboard_html(prospects: list, batch_progress: dict | None = None) -> str:
    batch_bar = _build_batch_progress_html(batch_progress)
    metrics   = _build_metrics_html(prospects)
    kanban    = _build_kanban_html(prospects) if prospects else _build_empty_state_html()

    count = len(prospects)
    section_title = f"""
<div class="pipeline-header" style="margin-top:16px;">
    <div class="pipeline-title">Pipeline Board</div>
    <div style="font-size:11px; color:{C['text_dim']}; font-weight:600;
                font-family:'JetBrains Mono',monospace;">
        {count} prospect{'s' if count != 1 else ''}
    </div>
</div>
"""
    return navbar_html() + batch_bar + metrics + section_title + kanban


# ──────────────────────────────────────────────
#  build_dashboard_tab
# ──────────────────────────────────────────────

def build_dashboard_tab(prospects_state: gr.State, batch_progress_state: gr.State):
    """
    Construye la pestaña Dashboard dentro de un gr.Blocks() activo.
    Fase 4: incluye batch modal + progress + kanban funcional.
    """
    # ── Top bar ─────────────────────────────────────────────
    with gr.Row(elem_classes=["mp-topbar"]):
        with gr.Column(scale=1, min_width=0):
            gr.HTML(navbar_html())
        with gr.Column(scale=0, min_width=140):
            btn_csv = gr.Button(
                "📂 CSV Import",
                variant="secondary",
                elem_classes=["gr-button", "secondary"],
            )
        with gr.Column(scale=0, min_width=150):
            btn_new = gr.Button(
                "＋ New Prospect",
                variant="primary",
                elem_classes=["gr-button", "primary"],
            )

    # ── Batch modal section ──────────────────────────────────
    batch_group, btn_batch_close, btn_batch_confirm, parsed_state, batch_log_box = \
        build_batch_section()

    # ── Main kanban + metrics ────────────────────────────────
    dashboard_html = gr.HTML(
        value=render_dashboard_html([]),
        label="",
    )

    # ── Hidden drop target — recibe payload "prospect_id|stage_id" del drag&drop ──
    kanban_drop = gr.Textbox(
        value="",
        visible=False,
        interactive=True,
        elem_id="kanban-drop-target",
        label="",
    )

    # ── Fallback move panel (accesibilidad / sin mouse) ──────
    with gr.Group(visible=False) as prospect_manager_group:
        gr.HTML(f"""
<div style="border-top:1px solid {C['border']}; margin-top:8px; padding-top:14px;
            display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
    <span style="font-size:11px; font-weight:700; letter-spacing:1px; color:{C['text_dim']};
                 text-transform:uppercase;">🗂 Move Prospect</span>
</div>
""")
        with gr.Row():
            with gr.Column(scale=2):
                prospect_dropdown = gr.Dropdown(
                    choices=[],
                    label="Select Prospect",
                    interactive=True,
                )
            with gr.Column(scale=2):
                stage_radio = gr.Radio(
                    choices=STAGE_CHOICES,
                    label="Move to Stage",
                    interactive=True,
                )
            with gr.Column(scale=1, min_width=120):
                btn_move_stage = gr.Button(
                    "Move →",
                    variant="primary",
                    elem_classes=["gr-button", "primary"],
                )
        move_status = gr.HTML(value="")

    # ════ REACTIVE EVENTS ════════════════════════════════════

    def _refresh(prospects, batch_progress):
        return render_dashboard_html(prospects or [], batch_progress)

    prospects_state.change(
        fn=_refresh,
        inputs=[prospects_state, batch_progress_state],
        outputs=[dashboard_html],
    )
    batch_progress_state.change(
        fn=_refresh,
        inputs=[prospects_state, batch_progress_state],
        outputs=[dashboard_html],
    )

    # ── Update prospect dropdown when prospects change ────────
    def _update_dropdown(prospects):
        choices = [
            p.get("clinic_name") or p.get("input", f"Prospect {i+1}")
            for i, p in enumerate(prospects or [])
        ]
        show = len(choices) > 0
        return (
            gr.update(choices=choices, value=None),
            gr.update(visible=show),
        )

    prospects_state.change(
        fn=_update_dropdown,
        inputs=[prospects_state],
        outputs=[prospect_dropdown, prospect_manager_group],
    )

    # ── Move prospect stage ───────────────────────────────────
    def _move_stage(selected_name, target_stage_label, prospects):
        if not selected_name or not target_stage_label:
            return (
                prospects,
                f'<div style="color:{C["amber"]}; font-size:12px; padding:6px 0;">Select a prospect and target stage.</div>',
            )
        target_stage_id = STAGE_ID_FROM_LABEL.get(target_stage_label, "")
        updated = []
        moved = False
        for p in (prospects or []):
            name = p.get("clinic_name") or p.get("input", "")
            if name == selected_name and target_stage_id:
                p = dict(p)
                p["pipeline_stage"] = target_stage_id
                moved = True
            updated.append(p)

        if moved:
            status_html = (
                f'<div style="color:{C["accent"]}; font-size:12px; padding:6px 0;">'
                f'✓ Moved <b>{selected_name}</b> → {target_stage_label}</div>'
            )
        else:
            status_html = (
                f'<div style="color:{C["red"]}; font-size:12px; padding:6px 0;">'
                f'Prospect not found.</div>'
            )
        return updated, status_html

    btn_move_stage.click(
        fn=_move_stage,
        inputs=[prospect_dropdown, stage_radio, prospects_state],
        outputs=[prospects_state, move_status],
    )

    # ── Drag & drop handler ───────────────────────────────────
    def _on_drag_drop(drop_data, prospects):
        """
        Procesa el payload 'prospect_id|stage_id' del drop.
        Retorna la lista actualizada y limpia el textbox.
        """
        if not drop_data or "|" not in drop_data:
            return gr.update(), ""
        pid, new_stage = drop_data.split("|", 1)
        if new_stage not in {col["id"] for col in KANBAN_COLS}:
            return gr.update(), ""
        updated = []
        for p in (prospects or []):
            if p.get("id") == pid:
                p = dict(p)
                p["pipeline_stage"] = new_stage
            updated.append(p)
        return updated, ""   # clear the hidden textbox

    kanban_drop.change(
        fn=_on_drag_drop,
        inputs=[kanban_drop, prospects_state],
        outputs=[prospects_state, kanban_drop],
    )

    # ── Open batch modal ─────────────────────────────────────
    btn_csv.click(
        fn=lambda: gr.update(visible=True),
        outputs=[batch_group],
    )

    # ── Close batch modal ────────────────────────────────────
    btn_batch_close.click(
        fn=lambda: gr.update(visible=False),
        outputs=[batch_group],
    )

    # ── Batch research generator ─────────────────────────────
    def _run_batch(items, current_prospects):
        if not items:
            return
        prospects = list(current_prospects or [])

        for log_text, current, total, prospect in do_batch_research(items):
            current_name = ""
            if 0 < current <= len(items):
                current_name = items[current - 1].get("input", "")

            progress = {"current": current, "total": total, "currentName": current_name}

            if prospect is not None:
                prospects = list(prospects) + [prospect.to_dict()]
                yield (
                    gr.update(visible=True, value=log_text),
                    prospects,
                    progress if current < total else None,
                    gr.update(visible=False) if current >= total else gr.update(),
                )
            else:
                yield (
                    gr.update(visible=True, value=log_text),
                    gr.update(),
                    progress,
                    gr.update(),
                )

        # Batch done — hide log, clear progress
        yield (
            gr.update(visible=False, value=""),
            prospects,
            None,
            gr.update(visible=False),
        )

    btn_batch_confirm.click(
        fn=lambda: gr.update(visible=False),   # close modal first
        outputs=[batch_group],
    )
    btn_batch_confirm.click(
        fn=_run_batch,
        inputs=[parsed_state, prospects_state],
        outputs=[batch_log_box, prospects_state, batch_progress_state, batch_group],
    )

    return dashboard_html, btn_new, btn_csv
