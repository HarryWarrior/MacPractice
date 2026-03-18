# ui/views/workflow_view.py
# Vista Workflow — Pipeline de 6 etapas (Input → Research → Profile → Draft → Review → Send)
# Fase 1: estructura visual completa + mock research generator con yield

import time
import gradio as gr
from ui.theme import (
    C, stepper_html, badge_html, score_ring_svg,
    PRIORITY_COLORS, COMPETITOR_COLORS,
)
from ui.components.score_ring import score_ring_with_label

# ──────────────────────────────────────────────
#  Constantes de Input Stage
# ──────────────────────────────────────────────
INPUT_MODES = [
    {"id": "name",     "label": "🏥 Clinic Name",  "placeholder": "Bright Smile Dental, Austin TX",    "hint": "Name + city for best results"},
    {"id": "linkedin", "label": "🔗 LinkedIn",      "placeholder": "linkedin.com/company/...",           "hint": "Company or person profile URL"},
    {"id": "website",  "label": "🌐 Website",       "placeholder": "brightsmiledental.com",              "hint": "The clinic's official website"},
    {"id": "google",   "label": "📍 Google Maps",   "placeholder": "google.com/maps/place/...",          "hint": "Google Maps or Business URL"},
    {"id": "phone",    "label": "📞 Phone / NPI",   "placeholder": "(512) 555-0123 or NPI 1234567890", "hint": "US phone or NPI lookup"},
]

SOURCES = [
    "Google Business", "Clinic Website", "LinkedIn", "Job Postings",
    "Healthgrades", "Zocdoc", "Facebook", "Local News", "ADA Directory", "NPI Registry",
]

EXAMPLES = [
    {"icon": "🏥", "name": "Bright Smile Dental",  "sub": "Austin, TX — name mode",   "value": "Bright Smile Dental, Austin TX"},
    {"icon": "🔗", "name": "Aspen Dental LinkedIn","sub": "LinkedIn — company page",   "value": "linkedin.com/company/aspen-dental"},
    {"icon": "🌐", "name": "LoveTooth.com",        "sub": "Website — direct URL",      "value": "loveteeth.com"},
    {"icon": "📍", "name": "Mountain View Dental", "sub": "Google Maps listing",       "value": "google.com/maps/place/mountain-view-dental"},
]

RESEARCH_STEPS_LABELS = [
    "Searching clinic website & Google Business...",
    "Scanning LinkedIn for company & decision makers...",
    "Checking job postings for software & hiring signals...",
    "Analyzing reviews on Healthgrades, Zocdoc, Google...",
    "Detecting competitor software (Dentrix, Eaglesoft...)...",
    "Scoring fit & compiling intelligence report...",
]


# ──────────────────────────────────────────────
#  Auto-detect del modo de input
# ──────────────────────────────────────────────
def detect_input_mode(text: str) -> str:
    """Analiza el texto e infiere el modo de input."""
    t = text.strip().lower()
    if not t:
        return "name"
    if "linkedin.com" in t:
        return "linkedin"
    if "google.com/maps" in t or "goo.gl" in t or "maps.app" in t:
        return "google"
    if any(t.startswith(p) for p in ("http://", "https://")) or \
       any(ext in t for ext in (".com", ".dental", ".health", ".care", ".org", ".net")):
        return "website"
    import re
    if re.search(r"\(?\d{3}\)?[\s\-]\d{3}[\s\-]\d{4}", t):
        return "phone"
    if re.match(r"^\d{10}$", re.sub(r"\s", "", t)):
        return "phone"
    return "name"


# ──────────────────────────────────────────────
#  HTML builders para el Workflow
# ──────────────────────────────────────────────

def _input_stage_html(active_mode: str = "name") -> str:
    """HTML estático del InputStage (pills de modo + panel de fuentes + ejemplos)."""
    # Mode pills
    pills = ""
    for m in INPUT_MODES:
        active_cls = " active" if m["id"] == active_mode else ""
        pills += f'<span class="mode-pill{active_cls}" data-mode="{m["id"]}">{m["label"]}</span>'

    # Source badges
    sources = "".join(f'<span class="source-badge">{s}</span>' for s in SOURCES)

    # Example cards
    examples = ""
    for ex in EXAMPLES:
        examples += f"""
<div class="example-card">
    <div class="example-card-icon">{ex['icon']}</div>
    <div class="example-card-name">{ex['name']}</div>
    <div class="example-card-sub">{ex['sub']}</div>
</div>"""

    return f"""
<div style="margin-bottom:14px;">
    <div class="mode-pills">{pills}</div>
    <div style="font-size:11px; color:{C['text_dim']}; margin-bottom:10px;">
        <b style="color:{C['text_muted']};">Sources searched automatically:</b>
    </div>
    <div class="source-panel">{sources}</div>
</div>
<div style="margin-top:16px;">
    <div style="font-size:11px; font-weight:700; letter-spacing:1px; color:{C['text_dim']};
                text-transform:uppercase; margin-bottom:8px;">Quick Examples</div>
    <div class="example-cards">{examples}</div>
</div>
"""


def _research_steps_html(steps: list) -> str:
    """
    Renderiza los 6 pasos de progreso del research.
    steps: lista de dicts {label, status} donde status = 'pending'|'active'|'done'
    """
    html = '<div class="research-steps-list">'
    for step in steps:
        status = step.get("status", "pending")
        label = step.get("label", "")
        if status == "active":
            indicator = '<div class="step-indicator active"></div>'
            step_cls = "active"
        elif status == "done":
            indicator = '<div class="step-indicator done">✓</div>'
            step_cls = "done"
        else:
            indicator = '<div class="step-indicator"></div>'
            step_cls = ""
        html += f'<div class="research-step {step_cls}">{indicator}{label}</div>'
    html += '</div>'
    return html


def _build_initial_steps() -> list:
    return [{"label": lbl, "status": "pending"} for lbl in RESEARCH_STEPS_LABELS]


def _profile_html(data: dict) -> str:
    """Renderiza la vista de Profile completa a partir del JSON de research."""
    if not data:
        return "<div style='padding:24px; color:#566577;'>No research data available.</div>"

    name = data.get("clinic_name", "Unknown Clinic")
    location = data.get("location", "")
    practitioners = data.get("practitioners", "")
    staff = data.get("staff_estimate", "")
    years = data.get("years_in_practice", "")
    fit_score = data.get("fit_score")
    fit_reasoning = data.get("fit_reasoning", "")
    priority = (data.get("priority") or "warm").lower()
    clinic_type = data.get("type", "dental")
    best_angle = data.get("best_angle", "")
    dm = data.get("decision_maker") or {}
    current_software = data.get("current_software", "Unknown")
    sw_confidence = data.get("software_confidence", "")
    sw_signals = data.get("software_signals", "")
    pain_points = data.get("pain_points") or []
    growth_signals = data.get("growth_signals") or []
    reviews_summary = data.get("recent_reviews_summary", "")
    hiring_signals = data.get("hiring_signals") or []
    sources_used = data.get("sources_used") or []
    online = data.get("online_presence") or {}
    google_rating = online.get("google_rating")
    review_count = online.get("review_count")

    # Badges
    priority_color = PRIORITY_COLORS.get(priority, C["amber"])
    badges = badge_html(priority.upper(), priority_color) + " " + \
             badge_html(clinic_type.upper(), C["blue"])

    # Score ring
    ring = score_ring_with_label(fit_score, size=88)

    # Meta row
    meta_parts = []
    if location:       meta_parts.append(f"📍 {location}")
    if practitioners:  meta_parts.append(f"👤 {practitioners} practitioners")
    if staff:          meta_parts.append(f"👥 ~{staff} staff")
    if years:          meta_parts.append(f"🏛 {years} yrs")
    if google_rating:  meta_parts.append(f"⭐ {google_rating} ({review_count or '?'} reviews)")
    meta_html = "  ·  ".join(meta_parts)

    # Header card
    header = f"""
<div class="profile-header-card">
    <div class="profile-info">
        <div class="profile-badges">{badges}</div>
        <div class="profile-name">{name}</div>
        <div class="profile-meta-row">{meta_html}</div>
        {f'<div style="font-size:12px; color:{C["text_muted"]}; margin-top:10px; line-height:1.6;">{fit_reasoning}</div>' if fit_reasoning else ''}
    </div>
    {ring}
</div>
"""

    # Metrics grid (best angle / decision maker / software)
    sw_color = C["gray"]
    sw_lower = current_software.lower()
    for sw_key, col in COMPETITOR_COLORS.items():
        if sw_key in sw_lower:
            sw_color = col
            break

    dm_name = dm.get("name", "Unknown")
    dm_role = dm.get("role", "")
    dm_linkedin = dm.get("linkedin", "")
    dm_display = f"{dm_name}" + (f" · {dm_role}" if dm_role else "")

    metrics_row = f"""
<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-top:14px;">
    <div class="insight-card">
        <div class="insight-card-title" style="color:{C['accent']};">💡 Best Angle</div>
        <div style="font-size:13px; color:{C['text']}; line-height:1.5;">{best_angle or '—'}</div>
    </div>
    <div class="insight-card">
        <div class="insight-card-title" style="color:{C['amber']};">🧑‍💼 Decision Maker</div>
        <div style="font-size:13px; color:{C['text']};">{dm_display}</div>
        {f'<a href="{dm_linkedin}" style="font-size:11px; color:{C["blue"]};">LinkedIn ↗</a>' if dm_linkedin else ''}
    </div>
    <div class="insight-card">
        <div class="insight-card-title" style="color:{sw_color};">💿 Current Software</div>
        <div style="font-size:13px;">{badge_html(current_software, sw_color)}</div>
        {f'<div style="font-size:11px; color:{C["text_dim"]}; margin-top:6px;">{sw_confidence} confidence</div>' if sw_confidence else ''}
    </div>
</div>
"""

    # Competitor switching card
    competitor_section = _competitor_card_html(current_software, sw_signals)

    # Insights grid
    pain_items = "".join(
        f'<div class="insight-item">⚡ {p}</div>' for p in pain_points[:4]
    ) or f'<div class="insight-item" style="color:{C["text_dim"]};">No pain points detected</div>'

    growth_items = "".join(
        f'<div class="insight-item">📈 {g}</div>' for g in growth_signals[:4]
    ) or f'<div class="insight-item" style="color:{C["text_dim"]};">No growth signals detected</div>'

    insights_grid = f"""
<div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:14px;">
    <div class="insight-card">
        <div class="insight-card-title" style="color:{C['accent']};">📈 Growth Signals</div>
        {growth_items}
    </div>
    <div class="insight-card">
        <div class="insight-card-title" style="color:{C['amber']};">⚡ Pain Points</div>
        {pain_items}
    </div>
</div>
"""

    # Reviews
    reviews_section = ""
    if reviews_summary:
        reviews_section = f"""
<div class="insight-card" style="margin-top:12px; border-color:{C['cyan']};">
    <div class="insight-card-title" style="color:{C['cyan']};">💬 Patient Reviews Insight</div>
    <div style="font-size:13px; color:{C['text_muted']}; line-height:1.6;">{reviews_summary}</div>
</div>
"""

    # Hiring
    hiring_section = ""
    if hiring_signals:
        hiring_items = "".join(
            f'<div class="insight-item">💼 {h}</div>' for h in hiring_signals
        )
        hiring_section = f"""
<div class="insight-card" style="margin-top:12px; border-color:{C['amber']};">
    <div class="insight-card-title" style="color:{C['amber']};">💼 Hiring / Job Postings</div>
    {hiring_items}
</div>
"""

    # Sources
    sources_badges = "".join(
        f'<span class="source-badge" style="font-size:10px;">✓ {s}</span>'
        for s in sources_used
    )
    sources_section = f"""
<div style="margin-top:14px; padding:12px; background:{C['surface']};
            border:1px solid {C['border']}; border-radius:10px;">
    <div style="font-size:10px; font-weight:700; letter-spacing:1px; color:{C['text_dim']};
                text-transform:uppercase; margin-bottom:8px;">
        🔍 Research Sources ({len(sources_used)})
    </div>
    <div class="source-panel">{sources_badges}</div>
</div>
""" if sources_used else ""

    return header + metrics_row + competitor_section + insights_grid + \
           reviews_section + hiring_section + sources_section


def _competitor_card_html(current_software: str, signals: str = "") -> str:
    """Card de competidor con pains vs angles. Solo se muestra si hay competidor reconocido."""
    # Datos locales de competidores (Fase 1 — Agente B no depende del módulo del Agente A aún)
    COMPETITORS = {
        "dentrix": {
            "name": "Dentrix", "color": C["blue"],
            "pains": ["Expensive licensing", "Windows-only lock-in",
                      "Complex upgrade path", "Poor customer support"],
            "angles": ["Mac-native advantage", "Simpler pricing",
                       "20 years expertise", "Migration support included"],
        },
        "eaglesoft": {
            "name": "Eaglesoft", "color": C["purple"],
            "pains": ["Outdated UI", "Patterson-bundled limitations",
                      "Limited customization", "Slow feature releases"],
            "angles": ["Modern interface", "Independent platform",
                       "Faster iteration", "Open integration options"],
        },
        "open dental": {
            "name": "Open Dental", "color": C["cyan"],
            "pains": ["Requires technical setup", "Community-dependent support",
                      "Security on clinic", "No dedicated AM"],
            "angles": ["Turnkey solution", "Professional support SLA",
                       "Enterprise security", "Dedicated customer success"],
        },
        "curve dental": {
            "name": "Curve Dental", "color": C["amber"],
            "pains": ["Limited offline", "Newer less proven",
                      "Fewer integrations", "Cloud-only concerns"],
            "angles": ["Hybrid option (cloud Q3)", "20-year track record",
                       "Deep integrations", "Flexible deployment"],
        },
    }

    sw_lower = (current_software or "").lower().strip()
    matched = None
    for key, data in COMPETITORS.items():
        if key in sw_lower:
            matched = data
            break

    if not matched:
        return ""

    color = matched["color"]
    initial = matched["name"][0]

    pain_items = "".join(
        f'<div class="pa-item" style="color:{C["red"]};">− {p}</div>'
        for p in matched["pains"]
    )
    angle_items = "".join(
        f'<div class="pa-item" style="color:{C["accent"]};">+ {a}</div>'
        for a in matched["angles"]
    )
    signals_html = (
        f'<div style="font-size:11px; color:{C["text_dim"]}; margin-top:4px;">{signals}</div>'
        if signals else ""
    )

    return f"""
<div class="competitor-card" style="border-color:{color}; margin-top:14px;">
    <div class="competitor-header">
        <div class="competitor-icon-badge"
             style="background:rgba(0,0,0,0.3); color:{color}; border:1px solid {color};">
            {initial}
        </div>
        <div>
            <div style="font-weight:700; font-size:14px; color:{color};">{matched['name']}</div>
            {signals_html}
        </div>
        <div style="margin-left:auto;">
            {badge_html("SWITCHING OPP.", color)}
        </div>
    </div>
    <div class="competitor-pains-angles">
        <div>
            <div class="pa-col-title" style="color:{C['red']};">Their Pains</div>
            {pain_items}
        </div>
        <div>
            <div class="pa-col-title" style="color:{C['accent']};">Our Angles</div>
            {angle_items}
        </div>
    </div>
</div>
"""


def _draft_html(draft: dict, selected_subject_idx: int = 0, approved: bool = False) -> str:
    """Renderiza la etapa de Draft (subject selector + email preview + hooks)."""
    if not draft:
        return ""

    subjects = draft.get("subject_options", ["(no subjects)"])
    body = draft.get("body", "")
    sender_name = draft.get("sender_name", "Sales Team")
    sender_title = draft.get("sender_title", "Mac Practice")
    hooks = draft.get("personalization_hooks") or []
    tone_notes = draft.get("tone_notes", "")
    follow_up = draft.get("follow_up_timing", "")

    # Subject options
    subj_html = ""
    for i, s in enumerate(subjects):
        sel_cls = " selected" if i == selected_subject_idx else ""
        subj_html += f'<div class="subject-option{sel_cls}">✉ {s}</div>'

    approved_badge = '<span class="approved-badge">✓ APPROVED</span>' if approved else ""
    selected_subject = subjects[selected_subject_idx] if subjects else ""

    # Hooks
    hooks_html = "".join(
        f'<div class="hook-item"><span>🎯</span><span>{h}</span></div>'
        for h in hooks
    )
    tone_html = (
        f'<div style="font-style:italic; font-size:12px; color:{C["text_dim"]}; '
        f'margin-top:8px; border-top:1px solid {C["border"]}; padding-top:8px;">'
        f'{tone_notes}</div>'
    ) if tone_notes else ""

    follow_html = (
        f'<div style="font-size:11px; color:{C["amber"]}; margin-top:6px;">⏰ Follow-up: {follow_up}</div>'
    ) if follow_up else ""

    # Avatar initial
    initial = sender_name[0].upper() if sender_name else "S"

    return f"""
<div style="margin-bottom:14px;">
    <div style="font-size:11px; font-weight:700; letter-spacing:1px; color:{C['text_dim']};
                text-transform:uppercase; margin-bottom:8px;">Select Subject Line</div>
    {subj_html}
</div>

<div class="mp-card" style="margin-bottom:14px;">
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;
                padding-bottom:12px; border-bottom:1px solid {C['border']};">
        <div style="width:34px; height:34px; border-radius:50%; background:{C['accent']};
                    display:flex; align-items:center; justify-content:center;
                    font-weight:800; font-size:14px; color:#000; flex-shrink:0;">{initial}</div>
        <div>
            <div style="font-weight:700; font-size:13px; color:{C['text']};">{sender_name}</div>
            <div style="font-size:11px; color:{C['text_muted']};">{sender_title}</div>
        </div>
        <div style="margin-left:auto;">{approved_badge}</div>
    </div>
    <div style="font-size:12px; color:{C['text_dim']}; margin-bottom:4px; text-transform:uppercase; letter-spacing:0.5px;">Subject</div>
    <div style="font-size:13px; font-weight:600; color:{C['text']}; margin-bottom:12px;">{selected_subject}</div>
    <div style="font-size:12px; color:{C['text_dim']}; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.5px;">Body</div>
    <div style="font-size:13px; color:{C['text_muted']}; line-height:1.7;
                white-space:pre-wrap; font-family:'Plus Jakarta Sans',sans-serif;">{body}</div>
    {follow_html}
</div>

<div class="mp-card" style="border-color:{C['purple']};">
    <div style="font-size:11px; font-weight:700; letter-spacing:1px; color:{C['purple']};
                text-transform:uppercase; margin-bottom:10px;">🎯 Personalization Hooks</div>
    {hooks_html}
    {tone_html}
</div>
"""


def _send_stage_html(sent: bool = False, error: str = "") -> str:
    """Renderiza el estado final de envío."""
    if sent:
        return f"""
<div class="send-result" style="background:{C['card']}; border:1px solid rgba(16,185,129,0.3);">
    <span class="send-result-icon">✅</span>
    <div class="send-result-title" style="color:{C['accent']};">Draft Created!</div>
    <div class="send-result-sub">Open Gmail to review and send your personalized outreach.</div>
</div>
"""
    if error:
        return f"""
<div class="send-result" style="background:{C['card']}; border:1px solid rgba(245,158,11,0.3);">
    <span class="send-result-icon">📋</span>
    <div class="send-result-title" style="color:{C['amber']};">Draft Saved Locally</div>
    <div class="send-result-sub">Gmail connection unavailable. Copy the email below and send manually.</div>
</div>
"""
    # Loading state
    return f"""
<div class="send-result" style="background:{C['surface']}; border:1px solid {C['border']};">
    <span class="send-result-icon spin" style="display:inline-block;">⚙️</span>
    <div class="send-result-title" style="color:{C['text_muted']};">Creating Gmail Draft...</div>
</div>
"""


# ──────────────────────────────────────────────
#  Mock Research Generator (Fase 1)
# ──────────────────────────────────────────────

def mock_research_generator(clinic_input: str):
    """
    Generador que simula el proceso de investigación con yield.
    Emite líneas de log al terminal y actualiza los steps.
    Retorna: (log_text, steps_html, stage_flag)
    stage_flag: 'research' mientras corre, 'profile' cuando termina.
    """
    import random

    steps = _build_initial_steps()
    log_lines = []

    def log(msg: str) -> str:
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        log_lines.append(line)
        return "\n".join(log_lines)

    # Inicio
    yield log(f"🟢 Starting research for: {clinic_input}"), \
          _research_steps_html(steps), "research"
    time.sleep(0.5)

    step_messages = [
        ("🔎 Querying clinic website & Google Business...",   "✅ Clinic website found. Services and team page analyzed."),
        ("🔎 Scanning LinkedIn for company & decision makers...", "✅ LinkedIn company page located. Decision maker identified."),
        ("🔎 Checking job postings (Indeed, Glassdoor)...",   "✅ 2 active job postings found — reveals software & hiring signals."),
        ("🔎 Analyzing reviews (Healthgrades, Zocdoc, Google)...", "✅ 47 reviews analyzed. Key patient pain points extracted."),
        ("🔍 Detecting competitor software...",               "✅ Competitor detected in database: Dentrix."),
        ("📊 Scoring fit & compiling intelligence report...", "✅ Intelligence report compiled. Fit score: 8/10."),
    ]

    for i, (start_msg, done_msg) in enumerate(step_messages):
        steps[i]["status"] = "active"
        yield log(start_msg), _research_steps_html(steps), "research"
        time.sleep(0.7 + random.uniform(0, 0.4))

        steps[i]["status"] = "done"
        yield log(done_msg), _research_steps_html(steps), "research"
        time.sleep(0.3)

    yield log("✨ Research complete. Loading prospect profile..."), \
          _research_steps_html(steps), "profile"


# ──────────────────────────────────────────────
#  Mock Outreach Generator (Fase 1)
# ──────────────────────────────────────────────

def mock_outreach_generator(prospect_data: dict):
    """
    Generador que simula la generación del email de outreach.
    Yields: (log_text, stage_flag)
    """
    log_lines = []

    def log(msg: str) -> str:
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        log_lines.append(line)
        return "\n".join(log_lines)

    name = prospect_data.get("clinic_name", "the clinic") if prospect_data else "the clinic"

    yield log("✍️  Crafting personalized outreach..."), "draft_loading"
    time.sleep(0.5)
    yield log(f"🎯 Analyzing competitor pain points for {name}..."), "draft_loading"
    time.sleep(0.6)
    yield log("📝 Generating 3 subject line options..."), "draft_loading"
    time.sleep(0.5)
    yield log("🧠 Applying personalization hooks from research..."), "draft_loading"
    time.sleep(0.4)
    yield log("✅ Outreach draft ready for review."), "draft"


# ──────────────────────────────────────────────
#  build_workflow_tab — crea los componentes Gradio
# ──────────────────────────────────────────────

def build_workflow_tab(prospects_state: gr.State, active_prospect_state: gr.State):
    """
    Construye la pestaña Workflow dentro de un gr.Blocks() activo.
    Retorna los handles de componentes que app.py necesita para conectar eventos.
    """
    # ── Estado local de la vista ─────────────────────────────────────────
    stage_state       = gr.State("input")         # input|research|profile|draft_loading|draft|send
    draft_state       = gr.State(None)            # dict del draft generado
    approved_state    = gr.State(False)           # bool: draft aprobado
    selected_subj_idx = gr.State(0)               # índice del subject seleccionado
    research_steps_st = gr.State(_build_initial_steps())

    # ── Stepper (siempre visible en esta tab) ────────────────────────────
    stepper_display = gr.HTML(value=stepper_html("input"), label="")

    # ════════════════════════════════════════════════════════
    #  ETAPA 1 — INPUT
    # ════════════════════════════════════════════════════════
    with gr.Group(visible=True) as stage_input:
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML(_input_stage_html("name"))
                clinic_input = gr.Textbox(
                    label="Clinic Name / URL / Phone / NPI",
                    placeholder="Bright Smile Dental, Austin TX",
                    lines=1,
                    elem_classes=["mp-input"],
                )
                btn_research = gr.Button(
                    "🔍 Research Clinic  →",
                    variant="primary",
                    elem_classes=["gr-button", "primary"],
                )
            with gr.Column(scale=1):
                gr.HTML(f"""
<div style="padding:16px 0 0;">
    <div style="font-size:11px; font-weight:700; letter-spacing:1px; color:{C['text_dim']};
                text-transform:uppercase; margin-bottom:12px;">Research Log</div>
    <div style="font-size:12px; color:{C['text_dim']}; padding:20px; background:{C['surface']};
                border:1px solid {C['border']}; border-radius:10px; font-family:'JetBrains Mono',monospace;">
        Waiting for input...
    </div>
</div>
""")

    # ════════════════════════════════════════════════════════
    #  ETAPA 2 — RESEARCH (log + animated steps)
    # ════════════════════════════════════════════════════════
    with gr.Group(visible=False) as stage_research:
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML(f'<div style="font-size:14px; font-weight:700; color:{C["text"]}; '
                        f'padding:8px 0 12px;">Researching clinic across 10 sources...</div>')
                research_steps_html_comp = gr.HTML(
                    value=_research_steps_html(_build_initial_steps()),
                )
            with gr.Column(scale=1):
                gr.HTML(f'<div style="font-size:11px; font-weight:700; color:{C["text_dim"]}; '
                        f'letter-spacing:1px; text-transform:uppercase; '
                        f'padding:8px 0 8px;">Live Research Log</div>')
                research_log = gr.Textbox(
                    value="",
                    label="",
                    lines=14,
                    max_lines=14,
                    interactive=False,
                    elem_classes=["terminal-log"],
                )

    # ════════════════════════════════════════════════════════
    #  ETAPA 3 — PROFILE
    # ════════════════════════════════════════════════════════
    with gr.Group(visible=False) as stage_profile:
        profile_display = gr.HTML(value="", label="")
        with gr.Row():
            btn_back_to_input = gr.Button(
                "← Pipeline",
                variant="secondary",
                elem_classes=["gr-button", "secondary"],
            )
            btn_generate_outreach = gr.Button(
                "Generate Outreach →",
                variant="primary",
                elem_classes=["gr-button", "primary"],
            )

    # ════════════════════════════════════════════════════════
    #  ETAPA 4 — DRAFT LOADING
    # ════════════════════════════════════════════════════════
    with gr.Group(visible=False) as stage_draft_loading:
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML(f"""
<div style="text-align:center; padding:40px 20px;">
    <div class="spin" style="font-size:32px; display:inline-block; margin-bottom:12px;">✍️</div>
    <div style="font-size:16px; font-weight:700; color:{C['text']}; margin-bottom:6px;">
        Crafting outreach...
    </div>
    <div style="font-size:13px; color:{C['text_muted']};">
        Personalizing based on research and competitor analysis
    </div>
</div>
""")
            with gr.Column(scale=1):
                outreach_log = gr.Textbox(
                    value="",
                    label="",
                    lines=10,
                    interactive=False,
                    elem_classes=["terminal-log"],
                )

    # ════════════════════════════════════════════════════════
    #  ETAPA 5 — DRAFT (review + approve/reject)
    # ════════════════════════════════════════════════════════
    with gr.Group(visible=False) as stage_draft:
        with gr.Row():
            with gr.Column(scale=1):
                draft_display = gr.HTML(value="", label="")

            with gr.Column(scale=1):
                gr.HTML(f'<div style="font-size:14px; font-weight:700; color:{C["text"]}; '
                        f'padding:0 0 12px;">Edit & Approve</div>')
                draft_subject_input = gr.Textbox(
                    label="Subject",
                    lines=1,
                    elem_classes=["mp-input"],
                )
                draft_body_input = gr.Textbox(
                    label="Email Body",
                    lines=10,
                    elem_classes=["mp-input"],
                )
                with gr.Row():
                    btn_draft_back = gr.Button(
                        "← Back",
                        variant="secondary",
                        elem_classes=["gr-button", "secondary"],
                        scale=1,
                    )
                    btn_reject = gr.Button(
                        "✗ Reject",
                        variant="secondary",
                        elem_classes=["gr-button", "btn-danger"],
                        scale=1,
                    )
                    btn_approve = gr.Button(
                        "✓ Approve",
                        variant="primary",
                        elem_classes=["gr-button", "primary"],
                        scale=1,
                    )
                btn_create_gmail = gr.Button(
                    "📧 Create Gmail Draft",
                    variant="primary",
                    elem_classes=["gr-button", "primary"],
                    visible=False,
                )

    # ════════════════════════════════════════════════════════
    #  ETAPA 6 — SEND
    # ════════════════════════════════════════════════════════
    with gr.Group(visible=False) as stage_send:
        send_display = gr.HTML(value=_send_stage_html(), label="")
        btn_back_to_pipeline = gr.Button(
            "← Back to Pipeline",
            variant="secondary",
            elem_classes=["gr-button", "secondary"],
        )

    # ════════════════════════════════════════════════════════
    #  EVENTOS
    # ════════════════════════════════════════════════════════

    all_stage_groups = [
        stage_input, stage_research, stage_profile,
        stage_draft_loading, stage_draft, stage_send
    ]

    def _show_only(active_group):
        """Retorna lista de visibility updates para mostrar solo un grupo."""
        return [gr.update(visible=(g == active_group)) for g in all_stage_groups]

    # ── Botón: Research ──────────────────────────────────────
    def _start_research(clinic_text, steps):
        """Inicia la investigación: muestra stage_research y corre el generator."""
        if not clinic_text.strip():
            return (
                *_show_only(stage_input),
                stepper_html("input"),
                _research_steps_html(steps),
                "",
            )
        return (
            *_show_only(stage_research),
            stepper_html("research"),
            _research_steps_html(_build_initial_steps()),
            "",
        )

    btn_research.click(
        fn=_start_research,
        inputs=[clinic_input, research_steps_st],
        outputs=[*all_stage_groups, stepper_display, research_steps_html_comp, research_log],
    )

    # Generator de research (stream de logs + steps)
    def _run_mock_research(clinic_text):
        for log_text, steps_html, flag in mock_research_generator(clinic_text):
            if flag == "profile":
                # Construir mock prospect data
                mock_prospect = {
                    "clinic_name":  clinic_text.split(",")[0].strip() or clinic_text,
                    "location":     clinic_text.split(",")[1].strip() if "," in clinic_text else "Unknown",
                    "practitioners": 4,
                    "staff_estimate": 8,
                    "years_in_practice": 6,
                    "fit_score":    8,
                    "priority":     "hot",
                    "type":         "dental",
                    "best_angle":   "Replace aging Dentrix setup with Mac-native solution",
                    "current_software": "Dentrix",
                    "software_confidence": "high",
                    "software_signals": "Job posting mentions 'Dentrix experience required'",
                    "decision_maker": {
                        "name": "Dr. Sarah Johnson",
                        "role": "Owner",
                        "linkedin": "linkedin.com/in/sarah-johnson-dds",
                        "email_pattern": "sarah@{domain}",
                    },
                    "online_presence": {
                        "google_rating": 4.6, "review_count": 94,
                        "social_active": True, "website": "#",
                    },
                    "fit_reasoning": "3-location practice on aging Dentrix — active hiring for front desk suggests scaling pain. 4.6★ Google rating with 94 reviews shows established patient base. Prime ICP match.",
                    "pain_points": [
                        "Dentrix billing module crashes reported on social media",
                        "Patient reviews mention long wait times at check-in (scheduling friction)",
                        "Job posting requests 'experience with insurance claim management'",
                    ],
                    "growth_signals": [
                        "Hiring Front Desk Coordinator — signals scaling",
                        "New Invisalign provider page added recently",
                        "2nd location opened 18 months ago",
                    ],
                    "recent_reviews_summary": "Patients consistently praise the clinical team but note friction at checkout and billing. Several mention insurance claim delays, suggesting pain with current billing software.",
                    "hiring_signals": [
                        "Front Desk Coordinator — reveals scheduling/insurance pain",
                        "Dental Assistant with Dentrix exp. — confirms current stack",
                    ],
                    "sources_used": [
                        "Clinic Website", "Google Business", "LinkedIn",
                        "Indeed Job Postings", "Healthgrades", "Google Reviews",
                    ],
                    "talking_points": [
                        "Dentrix billing issues mentioned in 3 recent reviews",
                        "Active hiring signals scaling intent",
                        "Mac-native solution saves ~40% on licensing",
                    ],
                    "red_flags": [],
                    "pipeline_stage": "researched",
                }
                yield (
                    log_text,
                    steps_html,
                    gr.update(visible=False),  # stage_input
                    gr.update(visible=False),  # stage_research
                    gr.update(visible=True),   # stage_profile
                    gr.update(visible=False),  # stage_draft_loading
                    gr.update(visible=False),  # stage_draft
                    gr.update(visible=False),  # stage_send
                    stepper_html("profile"),
                    _profile_html(mock_prospect),
                    mock_prospect,
                )
            else:
                yield (
                    log_text,
                    steps_html,
                    gr.update(visible=False),
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    stepper_html("research"),
                    gr.update(),
                    gr.update(),
                )

    btn_research.click(
        fn=_run_mock_research,
        inputs=[clinic_input],
        outputs=[
            research_log,
            research_steps_html_comp,
            *all_stage_groups,
            stepper_display,
            profile_display,
            active_prospect_state,
        ],
    )

    # ── Botón: Generate Outreach ─────────────────────────────
    def _start_outreach():
        return (
            *_show_only(stage_draft_loading),
            stepper_html("draft_loading"),
            "",
        )

    btn_generate_outreach.click(
        fn=_start_outreach,
        outputs=[*all_stage_groups, stepper_display, outreach_log],
    )

    def _run_mock_outreach(prospect):
        mock_draft = {
            "subject_options": [
                f"Quick question about your billing workflow",
                f"Helping practices like yours move beyond Dentrix",
                f"3 min call? Something we noticed about {(prospect or {}).get('clinic_name', 'your practice')}",
            ],
            "body": (
                "Hi Dr. Johnson,\n\n"
                "Noticed Bright Smile Dental is growing fast — congrats on the Invisalign expansion.\n\n"
                "I saw a couple of your recent reviews mention checkout friction, and your Indeed posting "
                "asking for Dentrix experience caught my eye. A lot of practices we work with hit that same "
                "wall around 3+ locations.\n\n"
                "Mac Practice has helped similar-sized dental groups cut billing time by ~40% without "
                "the licensing headache. Worth a quick chat to see if it could help your team?\n\n"
                "No deck, no pitch — just a 15-min conversation."
            ),
            "sender_name":  "Alex Rivera",
            "sender_title": "Account Executive · Mac Practice",
            "follow_up_timing": "4-5 business days if no response",
            "personalization_hooks": [
                "Recent Invisalign expansion mentioned on website",
                "Dentrix billing pain mentioned in 3 Google reviews",
                "Active hiring for Front Desk — scaling signal",
                "3-location practice = sweet spot ICP",
            ],
            "tone_notes": "Human and direct — leads with their pain, not our features. No buzzwords. CTA is conversational, not a forced demo booking.",
        }

        for log_text, flag in mock_outreach_generator(prospect):
            if flag == "draft":
                yield (
                    log_text,
                    gr.update(visible=False),  # stage_input
                    gr.update(visible=False),  # stage_research
                    gr.update(visible=False),  # stage_profile
                    gr.update(visible=False),  # stage_draft_loading
                    gr.update(visible=True),   # stage_draft
                    gr.update(visible=False),  # stage_send
                    stepper_html("draft"),
                    _draft_html(mock_draft, 0, False),
                    mock_draft,
                    mock_draft["subject_options"][0],
                    mock_draft["body"],
                )
            else:
                yield (
                    log_text,
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    stepper_html("draft_loading"),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                )

    btn_generate_outreach.click(
        fn=_run_mock_outreach,
        inputs=[active_prospect_state],
        outputs=[
            outreach_log,
            *all_stage_groups,
            stepper_display,
            draft_display,
            draft_state,
            draft_subject_input,
            draft_body_input,
        ],
    )

    # ── Botón: Approve ───────────────────────────────────────
    def _approve_draft(draft, subject, body):
        updated = (draft or {}).copy()
        updated["_approved_subject"] = subject
        updated["_approved_body"] = body
        draft_html = _draft_html(updated, 0, approved=True)
        return (
            draft_html,
            updated,
            True,
            gr.update(visible=True),   # btn_create_gmail
            gr.update(visible=False),  # btn_approve
            gr.update(visible=False),  # btn_reject
        )

    btn_approve.click(
        fn=_approve_draft,
        inputs=[draft_state, draft_subject_input, draft_body_input],
        outputs=[draft_display, draft_state, approved_state, btn_create_gmail, btn_approve, btn_reject],
    )

    # ── Botón: Reject (regenera) ─────────────────────────────
    def _reject_draft():
        return (
            *_show_only(stage_draft_loading),
            stepper_html("draft_loading"),
            "",
            False,
            gr.update(visible=False),
        )

    btn_reject.click(
        fn=_reject_draft,
        outputs=[*all_stage_groups, stepper_display, outreach_log, approved_state, btn_create_gmail],
    )

    # Después del reject, volver a correr el outreach generator
    btn_reject.click(
        fn=_run_mock_outreach,
        inputs=[active_prospect_state],
        outputs=[
            outreach_log,
            *all_stage_groups,
            stepper_display,
            draft_display,
            draft_state,
            draft_subject_input,
            draft_body_input,
        ],
    )

    # ── Botón: Create Gmail Draft ────────────────────────────
    def _send_email(draft, subject, body):
        # Fase 1: simula éxito (Fase 4 conectará smtplib real)
        return (
            *_show_only(stage_send),
            stepper_html("send"),
            _send_stage_html(sent=True),
        )

    btn_create_gmail.click(
        fn=_send_email,
        inputs=[draft_state, draft_subject_input, draft_body_input],
        outputs=[*all_stage_groups, stepper_display, send_display],
    )

    # ── Botón: Back to Pipeline ──────────────────────────────
    # (retorna visible stage_input + resetea stepper — app.py cambia la tab)
    def _back_to_input():
        return (
            *_show_only(stage_input),
            stepper_html("input"),
        )

    btn_back_to_pipeline.click(
        fn=_back_to_input,
        outputs=[*all_stage_groups, stepper_display],
    )
    btn_back_to_input.click(
        fn=_back_to_input,
        outputs=[*all_stage_groups, stepper_display],
    )
    btn_draft_back.click(
        fn=lambda: (
            *_show_only(stage_profile),
            stepper_html("profile"),
        ),
        outputs=[*all_stage_groups, stepper_display],
    )

    return {
        "stage_state":          stage_state,
        "clinic_input":         clinic_input,
        "btn_research":         btn_research,
        "research_log":         research_log,
        "profile_display":      profile_display,
        "draft_display":        draft_display,
        "draft_subject_input":  draft_subject_input,
        "draft_body_input":     draft_body_input,
        "btn_approve":          btn_approve,
        "btn_reject":           btn_reject,
        "btn_create_gmail":     btn_create_gmail,
        "btn_back_to_pipeline": btn_back_to_pipeline,
        "send_display":         send_display,
        "stepper_display":      stepper_display,
    }
