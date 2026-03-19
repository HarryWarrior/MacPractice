# ui/views/dashboard_view.py
# Vista Dashboard — Pipeline Kanban + Métricas + Batch Import
# Fase 4: Batch CSV, barra de progreso, kanban funcional (move stages)

import json
import gradio as gr
from ui.theme import C, navbar_html, metric_card_html, badge_html
from ui.components.prospect_card import prospect_card_html, empty_col_html
from ui.components.batch_modal import build_batch_section

from app.services.research_service import do_batch_research
from app.services.storage_service import storage
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

def _build_funnel_html(prospects: list) -> str:
    """Renders a visual sales funnel with prospect counts per stage."""
    if not prospects:
        return ""

    stage_counts = {col["id"]: 0 for col in KANBAN_COLS}
    for p in prospects:
        sid = p.get("pipeline_stage", "new")
        if sid in stage_counts:
            stage_counts[sid] += 1

    max_count = max(stage_counts.values()) or 1
    total = len(prospects)

    rows = ""
    for col in KANBAN_COLS:
        count = stage_counts[col["id"]]
        pct = round(count / total * 100) if total else 0
        bar_pct = round(count / max_count * 100) if max_count else 0
        # Funnel tapers: min 18% width so label is always readable
        bar_width = max(18, bar_pct)

        rows += f"""
<div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
    <div style="width:110px; font-size:11px; font-weight:600; color:{C['text_dim']};
                text-align:right; flex-shrink:0; white-space:nowrap;">{col['label']}</div>
    <div style="flex:1; position:relative; height:26px;">
        <div style="position:absolute; left:50%; transform:translateX(-50%);
                    width:{bar_width}%; height:100%; border-radius:5px;
                    background:linear-gradient(90deg, {col['color']}33, {col['color']}88);
                    border:1px solid {col['color']}55;
                    display:flex; align-items:center; justify-content:center; gap:6px;
                    transition:width 0.3s ease;">
            <span style="font-size:12px; font-weight:800; color:{col['color']};">{count}</span>
            <span style="font-size:10px; color:{C['text_dim']}; font-weight:500;">{pct}%</span>
        </div>
    </div>
</div>"""

    return f"""
<div style="background:{C['card']}; border:1px solid {C['border']}; border-radius:14px;
            padding:18px 20px; margin-bottom:14px;">
    <div style="font-size:11px; font-weight:700; letter-spacing:1px; color:{C['text_dim']};
                text-transform:uppercase; margin-bottom:14px;">📊 Sales Funnel · {total} prospect{'s' if total != 1 else ''}</div>
    {rows}
</div>
"""


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
        "(function(e){"
        "e.preventDefault();"
        "e.currentTarget.classList.remove('drag-over');"
        "var pid=e.dataTransfer.getData('text/plain');"
        "var stage=e.currentTarget.getAttribute('data-stage');"
        "var el=document.querySelector('#kanban-drop-target textarea, #kanban-drop-target input');"
        "if(el&&pid&&stage){"
        "var setter=Object.getOwnPropertyDescriptor(Object.getPrototypeOf(el), 'value').set;"
        "setter.call(el, pid+'|'+stage);"
        "el.dispatchEvent(new Event('input',{bubbles:true}));"
        "}"
        "})(event)"
    )
    _over_js = (
        "event.preventDefault();"
        "event.currentTarget.classList.add('drag-over')"
    )
    _leave_js = (
        "if(!event.currentTarget.contains(event.relatedTarget))"
        "{event.currentTarget.classList.remove('drag-over')}"
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


def _render_top_html(prospects: list, batch_progress: dict | None = None) -> str:
    """Renders batch bar + metrics + funnel (top section)."""
    batch_bar = _build_batch_progress_html(batch_progress)
    metrics   = _build_metrics_html(prospects)
    funnel    = _build_funnel_html(prospects)
    return batch_bar + metrics + funnel


def _render_kanban_html(prospects: list) -> str:
    """Renders pipeline section title + kanban board."""
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
    kanban = _build_kanban_html(prospects) if prospects else _build_empty_state_html()
    return section_title + kanban


def _summary_card_html(
    headline: str,
    observations: str,
    next_steps: list,
    watch_out: str,
    is_ai: bool = False,
) -> str:
    """Renders the executive summary card (static or AI-generated)."""
    if not headline:
        return ""

    ai_badge = (
        f'<span style="display:inline-flex; align-items:center; gap:5px; '
        f'background:linear-gradient(135deg, rgba(99,102,241,0.15), rgba(16,185,129,0.1)); '
        f'border:1px solid rgba(99,102,241,0.3); border-radius:20px; '
        f'padding:3px 10px; font-size:10px; font-weight:700; color:{C["purple"]}; '
        f'letter-spacing:0.5px; white-space:nowrap;">'
        f'{"🤖 Generated with AI" if is_ai else "🤖 IA Summary"}</span>'
    )

    title_label = "🤖 AI Executive Summary" if is_ai else "📊 Pipeline Summary"
    border_color = C["purple"] if is_ai else C["border"]
    bg_extra = (
        f"background:linear-gradient(145deg, rgba(99,102,241,0.04) 0%, {C['card']} 100%);"
        if is_ai else f"background:{C['card']};"
    )

    obs_html = (
        f'<div style="font-size:13px; color:{C["text_muted"]}; line-height:1.65; '
        f'margin-top:8px;">{observations}</div>'
    ) if observations else ""

    steps_html = ""
    if next_steps:
        items = "".join(
            f'<div style="display:flex; gap:8px; align-items:flex-start; margin-bottom:6px;">'
            f'<span style="color:{C["accent"]}; font-weight:800; flex-shrink:0; font-size:13px;">→</span>'
            f'<span style="font-size:12.5px; color:{C["text_muted"]}; line-height:1.5;">{s}</span>'
            f'</div>'
            for s in next_steps
        )
        steps_html = f"""
<div style="margin-top:12px; padding:12px 14px; background:{C['surface']};
            border:1px solid {C['border']}; border-radius:10px;">
    <div style="font-size:10px; font-weight:700; letter-spacing:1px; color:{C['text_dim']};
                text-transform:uppercase; margin-bottom:8px;">⚡ Next Steps</div>
    {items}
</div>"""

    watch_html = ""
    if watch_out:
        watch_html = f"""
<div style="margin-top:10px; padding:10px 12px; background:rgba(245,158,11,0.06);
            border:1px solid rgba(245,158,11,0.25); border-radius:8px;
            display:flex; gap:8px; align-items:flex-start;">
    <span style="font-size:14px; flex-shrink:0;">⚠️</span>
    <span style="font-size:12px; color:{C['amber']}; line-height:1.5;">{watch_out}</span>
</div>"""

    return f"""
<div style="{bg_extra} border:1px solid {border_color}; border-radius:14px;
            padding:18px 20px; margin-bottom:14px;">
    <div style="display:flex; align-items:center; justify-content:space-between;
                margin-bottom:10px;">
        <div style="font-size:11px; font-weight:700; letter-spacing:1px; color:{C['text_dim']};
                    text-transform:uppercase;">{title_label}</div>
        {ai_badge}
    </div>
    <div style="font-size:14px; font-weight:700; color:{C['text']}; line-height:1.5;">{headline}</div>
    {obs_html}
    {steps_html}
    {watch_html}
</div>"""


def _summary_loading_html() -> str:
    return f"""
<div style="background:{C['card']}; border:1px solid {C['purple']}; border-radius:14px;
            padding:24px 20px; margin-bottom:14px; text-align:center;">
    <div style="font-size:11px; font-weight:700; letter-spacing:1px; color:{C['purple']};
                text-transform:uppercase; margin-bottom:14px;">🤖 AI Executive Summary</div>
    <div style="font-size:24px; display:inline-block;
                animation:spin 1s linear infinite; margin-bottom:8px;">✨</div>
    <div style="font-size:13px; color:{C['text_muted']};">Analyzing pipeline with AI...</div>
</div>"""


def _build_static_summary_html(prospects: list) -> str:
    """Generates a static (no-AI) executive summary from pipeline data."""
    total = len(prospects)

    if not total:
        return _summary_card_html(
            headline="Pipeline is empty — add your first prospect to begin.",
            observations="",
            next_steps=[
                "Use 🔍 Research Prospect to investigate a dental clinic by name, URL, or phone",
                "Use 🚀 Bulk Research to import and research an entire CSV list at once",
                "Target clinics using Dentrix, Eaglesoft, or Open Dental — they're your top switchers",
            ],
            watch_out="",
            is_ai=False,
        )

    stage_counts = {col["id"]: 0 for col in KANBAN_COLS}
    for p in prospects:
        sid = p.get("pipeline_stage", "new")
        if sid in stage_counts:
            stage_counts[sid] += 1

    scored = [p["fit_score"] for p in prospects if p.get("fit_score") is not None]
    avg_score = round(sum(scored) / len(scored), 1) if scored else None
    hot = sum(1 for p in prospects if p.get("priority") == "hot")

    skip_sw = {"unknown", "paper-based", "paper", ""}
    competitors: dict[str, int] = {}
    for p in prospects:
        sw = (p.get("current_software") or "").strip()
        if sw.lower() not in skip_sw:
            competitors[sw] = competitors.get(sw, 0) + 1

    in_play = stage_counts.get("outreach_sent", 0) + stage_counts.get("responded", 0) + stage_counts.get("meeting", 0)
    researched = stage_counts.get("researched", 0)

    score_text = f"Avg fit score {avg_score}/10." if avg_score else ""
    hot_text = f" {hot} hot lead{'s' if hot != 1 else ''} ready for contact." if hot else ""
    top_sw = sorted(competitors.items(), key=lambda x: x[1], reverse=True)
    sw_text = ""
    if top_sw:
        sw_text = " Top competitor: " + ", ".join(f"{k} ({v})" for k, v in top_sw[:2]) + "."

    headline = (
        f"{total} prospect{'s' if total != 1 else ''} tracked — "
        f"{researched} researched, {in_play} in active outreach."
    )
    observations = (score_text + hot_text + sw_text).strip()

    next_steps = []
    if researched > 0:
        next_steps.append(f"Send outreach to {researched} researched prospect{'s' if researched > 1 else ''} — they're ready")
    if hot > 0:
        next_steps.append(f"Follow up on {hot} hot lead{'s' if hot > 1 else ''} — highest close probability")
    if top_sw:
        next_steps.append(f"Lead with switching angle for {top_sw[0][0]} users ({top_sw[0][1]} clinic{'s' if top_sw[0][1] > 1 else ''})")
    while len(next_steps) < 2:
        next_steps.append("Research more prospects to build pipeline depth")

    watch_out = ""
    if stage_counts.get("new", 0) > total * 0.5:
        n = stage_counts["new"]
        watch_out = f"{n} prospects stuck in 'New' without research — run bulk research to move them forward."

    return _summary_card_html(headline, observations, next_steps, watch_out, is_ai=False)


def render_dashboard_html(prospects: list, batch_progress: dict | None = None) -> str:
    """Legacy function — kept for any external callers."""
    return _render_top_html(prospects, batch_progress) + _render_kanban_html(prospects)


# ──────────────────────────────────────────────
#  build_dashboard_tab
# ──────────────────────────────────────────────

def build_dashboard_tab(prospects_state: gr.State, batch_progress_state: gr.State):
    """
    Construye la sección Dashboard (single-page layout).
    Incluye batch modal + progress + kanban funcional.
    """
    # ── Top bar ─────────────────────────────────────────────
    with gr.Row(elem_classes=["mp-topbar"]):
        with gr.Column(scale=1, min_width=0):
            gr.HTML(navbar_html())
        with gr.Column(scale=0, min_width=140):
            btn_csv = gr.Button(
                "🚀 Bulk Research",
                variant="secondary",
                elem_classes=["gr-button", "secondary"],
            )
        with gr.Column(scale=0, min_width=160):
            btn_new = gr.Button(
                "🔍 Research Prospect",
                variant="primary",
                elem_classes=["gr-button", "primary"],
            )

    # ── Batch modal section ──────────────────────────────────
    batch_group, btn_batch_close, btn_batch_confirm, parsed_state, batch_log_box = \
        build_batch_section()

    # ── Top section: metrics + funnel ────────────────────────
    dashboard_top_html = gr.HTML(
        value=_render_top_html([]),
        label="",
    )

    # ── Executive Summary ────────────────────────────────────
    executive_summary_display = gr.HTML(
        value=_build_static_summary_html([]),
    )
    with gr.Row(elem_classes=["mp-summary-row"]):
        with gr.Column(scale=1, min_width=0):
            gr.HTML(
                f'<div style="font-size:11px; color:{C["text_dim"]}; padding:2px 0; '
                f'font-style:italic;">Updates automatically when prospects change. '
                f'Click to get AI-powered strategic analysis.</div>'
            )
        with gr.Column(scale=0, min_width=200):
            btn_ai_summary = gr.Button(
                "🤖 Regenerate with AI",
                variant="secondary",
                elem_classes=["gr-button", "secondary"],
            )

    # ── Kanban board ─────────────────────────────────────────
    dashboard_kanban_html = gr.HTML(
        value=_render_kanban_html([]),
        label="",
    )

    # ── Hidden drop target — recibe payload "prospect_id|stage_id" del drag&drop ──
    # Es vital que sea visible=True para que esté en el DOM y JS lo encuentre.
    # Se ocultará puramente por CSS.
    gr.HTML("<style>#kanban-drop-target { display: none !important; opacity: 0; pointer-events: none; height: 0; }</style>")
    kanban_drop = gr.Textbox(
        value="",
        visible=True,
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
        p = prospects or []
        return (
            _render_top_html(p, batch_progress),
            _build_static_summary_html(p),
            _render_kanban_html(p),
        )

    prospects_state.change(
        fn=_refresh,
        inputs=[prospects_state, batch_progress_state],
        outputs=[dashboard_top_html, executive_summary_display, dashboard_kanban_html],
    )
    batch_progress_state.change(
        fn=_refresh,
        inputs=[prospects_state, batch_progress_state],
        outputs=[dashboard_top_html, executive_summary_display, dashboard_kanban_html],
    )

    # ── AI Executive Summary generator ───────────────────────
    def _do_ai_summary(prospects):
        """Calls AI to generate an executive summary of the pipeline."""
        from app.agents.gemini_agent import call_gemini_summary
        from app.agents.openai_agent import call_openai_summary
        from app.utils.logger import LogAccumulator
        from app.utils.json_parser import parse_llm_json

        p = prospects or []

        if not p:
            yield _build_static_summary_html([])
            return

        log = LogAccumulator()

        # Show loading state immediately
        yield _summary_loading_html()

        # Build compact pipeline context for the LLM
        stage_counts = {col["id"]: 0 for col in KANBAN_COLS}
        for prospect in p:
            sid = prospect.get("pipeline_stage", "new")
            if sid in stage_counts:
                stage_counts[sid] += 1

        scored = [prospect["fit_score"] for prospect in p if prospect.get("fit_score") is not None]
        avg_score = round(sum(scored) / len(scored), 1) if scored else None

        prospect_summaries = [
            {
                "clinic_name": prospect.get("clinic_name", ""),
                "location": prospect.get("location", ""),
                "fit_score": prospect.get("fit_score"),
                "priority": prospect.get("priority"),
                "current_software": prospect.get("current_software"),
                "pipeline_stage": prospect.get("pipeline_stage"),
                "best_angle": prospect.get("best_angle", ""),
                "pain_points": (prospect.get("pain_points") or [])[:2],
            }
            for prospect in p
        ]

        context_json = json.dumps({
            "total_prospects": len(p),
            "stage_distribution": stage_counts,
            "avg_fit_score": avg_score,
            "prospects": prospect_summaries,
        }, indent=2)

        raw_response = None
        try:
            for _log_text, response in call_gemini_summary(context_json, log):
                if response is not None:
                    raw_response = response
        except Exception:
            try:
                for _log_text, response in call_openai_summary(context_json, log):
                    if response is not None:
                        raw_response = response
            except Exception:
                yield _build_static_summary_html(p)
                return

        if raw_response:
            try:
                data = parse_llm_json(raw_response)
                html = _summary_card_html(
                    headline=data.get("headline", ""),
                    observations=data.get("observations", ""),
                    next_steps=data.get("next_steps") or [],
                    watch_out=data.get("watch_out", ""),
                    is_ai=True,
                )
            except Exception:
                html = _build_static_summary_html(p)
        else:
            html = _build_static_summary_html(p)

        yield html

    btn_ai_summary.click(
        fn=_do_ai_summary,
        inputs=[prospects_state],
        outputs=[executive_summary_display],
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
                
                # Guardar en Storage Service
                pid = p.get("id")
                if pid:
                    storage.move_prospect_stage(pid, target_stage_id)
                    
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
            
        # Guardar en Storage Service
        storage.move_prospect_stage(pid, new_stage)

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

    # btn_csv toggle and btn_batch_close are wired in app.py
    # so both sections can close each other (mutual exclusivity).

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

    return (
        dashboard_top_html, executive_summary_display, dashboard_kanban_html,
        btn_new, btn_csv, batch_group, btn_batch_close,
    )
