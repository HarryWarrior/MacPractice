# ui/views/dashboard_view.py
# Vista Dashboard — Pipeline Kanban + Métricas
# Fase 1: estructura visual completa con datos de estado (gr.State)

import gradio as gr
from ui.theme import C, navbar_html, metric_card_html, badge_html
from ui.components.prospect_card import prospect_card_html, empty_col_html

# ──────────────────────────────────────────────
#  Constantes de columnas Kanban
# ──────────────────────────────────────────────
KANBAN_COLS = [
    {"id": "new",           "label": "New",           "color": C["blue"]},
    {"id": "researched",    "label": "Researched",     "color": C["purple"]},
    {"id": "outreach_sent", "label": "Outreach Sent",  "color": C["amber"]},
    {"id": "responded",     "label": "Responded",      "color": C["accent_light"]},
    {"id": "meeting",       "label": "Meeting Booked", "color": C["accent"]},
]


# ──────────────────────────────────────────────
#  Builders de HTML puro
# ──────────────────────────────────────────────

def _build_metrics_html(prospects: list) -> str:
    """Genera el bloque de 5 MetricCards con los datos actuales del pipeline."""
    total = len(prospects)

    # Avg fit score
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

    # Competitors found
    skip_sw = {"unknown", "paper-based", "paper", ""}
    competitors = sum(
        1 for p in prospects
        if (p.get("current_software") or "").lower().strip() not in skip_sw
    )

    # Outreach sent
    sent_stages = {"outreach_sent", "responded", "meeting"}
    sent_count = sum(1 for p in prospects if p.get("pipeline_stage") in sent_stages)

    # Response rate
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
    """Genera el Kanban board completo desde la lista de prospects."""
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
<div class="kanban-col">
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
    """Estado vacío del pipeline (sin prospects)."""
    return f"""
<div style="padding: 24px;">
  <div class="empty-state" style="border:1px dashed {C['border']}; border-radius:14px; padding:64px 32px;">
    <span class="empty-state-icon">🎯</span>
    <div class="empty-state-title">Your pipeline is empty</div>
    <div class="empty-state-sub">Import a CSV or research your first prospect to get started.</div>
  </div>
</div>
"""


def _build_batch_progress_html(batch_progress: dict | None) -> str:
    """Barra de progreso de batch (visible solo cuando batch_progress != None)."""
    if not batch_progress:
        return ""
    current = batch_progress.get("current", 0)
    total = batch_progress.get("total", 1)
    name = batch_progress.get("currentName", "")
    pct = round(current / total * 100) if total else 0
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
    """
    Compone el HTML completo del dashboard:
    navbar + batch bar + métricas + kanban (o empty state).
    """
    batch_bar = _build_batch_progress_html(batch_progress)
    metrics = _build_metrics_html(prospects)
    kanban = _build_kanban_html(prospects) if prospects else _build_empty_state_html()

    section_title = f"""
<div style="padding: 12px 24px 0; display:flex; align-items:center; justify-content:space-between;">
    <span style="font-size:13px; font-weight:700; color:{C['text_muted']};
                 text-transform:uppercase; letter-spacing:1px;">Pipeline Board</span>
    <span style="font-size:11px; color:{C['text_dim']};">
        {len(prospects)} prospect{'s' if len(prospects) != 1 else ''} total
    </span>
</div>
"""
    return navbar_html() + batch_bar + metrics + section_title + kanban


# ──────────────────────────────────────────────
#  build_dashboard_tab — crea los componentes Gradio
# ──────────────────────────────────────────────

def build_dashboard_tab(prospects_state: gr.State, batch_progress_state: gr.State):
    """
    Construye la pestaña Dashboard dentro de un gr.Blocks() activo.
    Retorna los componentes que el caller (app.py) necesita para conectar eventos.

    Returns:
        dashboard_html  : gr.HTML  — todo el panel visual
        btn_new         : gr.Button — "New Prospect"
        btn_csv         : gr.Button — "CSV Import"
    """
    # Navbar + botones de acción en una fila
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

    # Panel principal del kanban + métricas (se actualiza reactivamente)
    dashboard_html = gr.HTML(
        value=render_dashboard_html([]),
        label="",
    )

    # ── Lógica reactiva: re-renderiza cuando cambia el estado ──────────────
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

    return dashboard_html, btn_new, btn_csv
