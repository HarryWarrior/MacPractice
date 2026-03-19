# ui/views/workflow_view.py
# Vista Workflow — Pipeline de 6 etapas
# FASE 2: conectado a do_research() y do_outreach() reales (Agente A)

import gradio as gr
from ui.theme import (
    C, stepper_html, badge_html, score_ring_svg,
    PRIORITY_COLORS,
)
from ui.components.score_ring import score_ring_with_label
from ui.components.competitor_card import competitor_card_html

# ── Importaciones del backend del Agente A ────────────────────────────────
from app.services.research_service import do_research
from app.models.prospect import Prospect
from app.services.outreach_service import do_outreach
from app.services.email_service import send_real_email, format_email_for_clipboard
from app.services.storage_service import storage

# ──────────────────────────────────────────────
#  Constantes de Input Stage
# ──────────────────────────────────────────────
INPUT_MODES = [
    {"id": "name",     "label": "🏥 Clinic Name",  "placeholder": "Bright Smile Dental, Austin TX",   "hint": "Name + city for best results"},
    {"id": "linkedin", "label": "🔗 LinkedIn",      "placeholder": "linkedin.com/company/...",          "hint": "Company or person profile URL"},
    {"id": "website",  "label": "🌐 Website",       "placeholder": "brightsmiledental.com",             "hint": "The clinic's official website"},
    {"id": "google",   "label": "📍 Google Maps",   "placeholder": "google.com/maps/place/...",         "hint": "Google Maps or Business URL"},
    {"id": "phone",    "label": "📞 Phone / NPI",   "placeholder": "(512) 555-0123 or NPI 1234567890","hint": "US phone or NPI lookup"},
]

SOURCES = [
    "Google Business", "Clinic Website", "LinkedIn", "Job Postings",
    "Healthgrades", "Zocdoc", "Facebook", "Local News", "ADA Directory", "NPI Registry",
]

EXAMPLES = [
    {"icon": "🏥", "name": "Bright Smile Dental",   "sub": "Austin, TX — name mode",  "value": "Bright Smile Dental, Austin TX"},
    {"icon": "🔗", "name": "Aspen Dental LinkedIn",  "sub": "LinkedIn — company page", "value": "linkedin.com/company/aspen-dental"},
    {"icon": "🌐", "name": "LoveTooth.com",          "sub": "Website — direct URL",    "value": "loveteeth.com"},
    {"icon": "📍", "name": "Mountain View Dental",   "sub": "Google Maps listing",     "value": "google.com/maps/place/mountain-view-dental"},
]

RESEARCH_STEPS_LABELS = [
    "Searching clinic website & Google Business...",
    "Scanning LinkedIn for company & decision makers...",
    "Checking job postings for software & hiring signals...",
    "Analyzing reviews on Healthgrades, Zocdoc, Google...",
    "Detecting competitor software (Dentrix, Eaglesoft...)...",
    "Scoring fit & compiling intelligence report...",
]

# Palabras clave para mapear líneas de log → paso visual activo
_STEP_KEYWORDS = [
    ["Searching clinic website", "Google Business", "clinic website"],
    ["Scanning LinkedIn", "decision maker", "LinkedIn"],
    ["Checking job postings", "job posting", "hiring", "Indeed", "Glassdoor"],
    ["Analyzing reviews", "Healthgrades", "Zocdoc", "reviews"],
    ["Detecting competitor", "Competidor detectado", "competitor software"],
    ["Scoring fit", "compiling intelligence", "JSON parseado", "Investigación completa", "completo"],
]


# ──────────────────────────────────────────────
#  Auto-detect del modo de input
# ──────────────────────────────────────────────
def detect_input_mode(text: str) -> str:
    """Analiza el texto e infiere el modo de input."""
    import re
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
    if re.search(r"\(?\d{3}\)?[\s\-]\d{3}[\s\-]\d{4}", t):
        return "phone"
    if re.match(r"^\d{10}$", re.sub(r"\s", "", t)):
        return "phone"
    return "name"


# ──────────────────────────────────────────────
#  Step animation helpers
# ──────────────────────────────────────────────
def _build_initial_steps() -> list:
    return [{"label": lbl, "status": "pending"} for lbl in RESEARCH_STEPS_LABELS]


def _steps_from_log(log_text: str) -> list:
    """
    Analiza el log acumulado y decide qué paso visual marcar como active/done.
    Mapea las líneas del log de do_research() → los 6 pasos del stepper visual.
    """
    steps = _build_initial_steps()
    last_active = -1

    for line in log_text.strip().split("\n"):
        line_lower = line.lower()
        for i, keywords in enumerate(_STEP_KEYWORDS):
            if any(kw.lower() in line_lower for kw in keywords):
                last_active = max(last_active, i)

    # Si hay algún match, marcar los anteriores como done y el actual como active
    if last_active >= 0:
        for i in range(len(steps)):
            if i < last_active:
                steps[i]["status"] = "done"
            elif i == last_active:
                steps[i]["status"] = "active"

    return steps


def _research_steps_html(steps: list) -> str:
    html = '<div class="research-steps-list">'
    for step in steps:
        status = step.get("status", "pending")
        label  = step.get("label", "")
        if status == "active":
            indicator = '<div class="step-indicator active"></div>'
            cls = "active"
        elif status == "done":
            indicator = '<div class="step-indicator done">✓</div>'
            cls = "done"
        else:
            indicator = '<div class="step-indicator"></div>'
            cls = ""
        html += f'<div class="research-step {cls}">{indicator}{label}</div>'
    html += '</div>'
    return html


# ──────────────────────────────────────────────
#  HTML builders — Input Stage
# ──────────────────────────────────────────────
def _input_stage_html(active_mode: str = "name") -> str:
    pills = "".join(
        f'<span class="mode-pill{"  active" if m["id"] == active_mode else ""}"'
        f' data-mode="{m["id"]}">{m["label"]}</span>'
        for m in INPUT_MODES
    )
    sources = "".join(f'<span class="source-badge">{s}</span>' for s in SOURCES)
    examples = "".join(f"""
<div class="example-card">
    <div class="example-card-icon">{ex['icon']}</div>
    <div class="example-card-name">{ex['name']}</div>
    <div class="example-card-sub">{ex['sub']}</div>
</div>""" for ex in EXAMPLES)

    return f"""
<div style="margin-bottom:14px;">
    <div class="mode-pills">{pills}</div>
    <div style="font-size:11px; color:{C['text_dim']}; margin-bottom:8px;">
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


# ──────────────────────────────────────────────
#  HTML builders — Profile Stage (tarea 2.7)
# ──────────────────────────────────────────────
def _profile_html(data: dict) -> str:
    """
    Renderiza el perfil completo del prospecto.
    data: dict compatible con Prospect.to_dict()
    """
    if not data:
        return f"<div style='padding:24px; color:{C['text_dim']};'>No data.</div>"

    name              = data.get("clinic_name") or data.get("input", "Unknown Clinic")
    location          = data.get("location", "")
    practitioners     = data.get("practitioners")
    staff             = data.get("staff_estimate")
    years             = data.get("years_in_practice")
    fit_score         = data.get("fit_score")
    fit_reasoning     = data.get("fit_reasoning", "")
    priority          = (data.get("priority") or "warm").lower()
    clinic_type       = data.get("type", "dental")
    best_angle        = data.get("best_angle", "")
    dm                = data.get("decision_maker") or {}
    current_software  = data.get("current_software", "Unknown")
    sw_confidence     = data.get("software_confidence", "")
    sw_signals        = data.get("software_signals", "")
    pain_points       = data.get("pain_points") or []
    growth_signals    = data.get("growth_signals") or []
    reviews_summary   = data.get("recent_reviews_summary", "")
    hiring_signals    = data.get("hiring_signals") or []
    sources_used      = data.get("sources_used") or []
    online            = data.get("online_presence") or {}
    google_rating     = online.get("google_rating")
    review_count      = online.get("review_count")
    talking_points    = data.get("talking_points") or []
    red_flags         = data.get("red_flags") or []

    # ── Header card ───────────────────────────────────────────
    priority_color = PRIORITY_COLORS.get(priority, C["amber"])
    badges = badge_html(priority.upper(), priority_color) + " " + \
             badge_html(clinic_type.upper(), C["blue"])

    meta_parts = []
    if location:      meta_parts.append(f"📍 {location}")
    if practitioners: meta_parts.append(f"👤 {practitioners} practitioners")
    if staff:         meta_parts.append(f"👥 ~{staff} staff")
    if years:         meta_parts.append(f"🏛 {years} yrs")
    if google_rating: meta_parts.append(f"⭐ {google_rating} ({review_count or '?'} reviews)")
    meta_html = "  ·  ".join(meta_parts)

    header = f"""
<div class="profile-header-card fade-up">
    <div class="profile-info">
        <div class="profile-badges">{badges}</div>
        <div class="profile-name">{name}</div>
        <div class="profile-meta-row">{meta_html}</div>
        {f'<div style="font-size:12px; color:{C["text_muted"]}; margin-top:10px; line-height:1.6;">{fit_reasoning}</div>' if fit_reasoning else ""}
    </div>
    {score_ring_with_label(fit_score, size=88)}
</div>
"""

    # ── Métricas: best angle / decision maker / software ─────
    dm_name    = dm.get("name", "Unknown")
    dm_role    = dm.get("role", "")
    dm_linkedin = dm.get("linkedin", "")
    dm_display  = dm_name + (f" · {dm_role}" if dm_role else "")

    from app.models.competitor import detect_competitor
    matched = detect_competitor(current_software)
    sw_color = matched[1]["color"] if matched else C["gray"]
    sw_badge = badge_html(current_software, sw_color)

    metrics_row = f"""
<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-top:14px;">
    <div class="insight-card">
        <div class="insight-card-title" style="color:{C['accent']};">💡 Best Angle</div>
        <div style="font-size:13px; color:{C['text']}; line-height:1.5;">{best_angle or "—"}</div>
    </div>
    <div class="insight-card">
        <div class="insight-card-title" style="color:{C['amber']};">🧑‍💼 Decision Maker</div>
        <div style="font-size:13px; color:{C['text']};">{dm_display}</div>
        {f'<a href="{dm_linkedin}" style="font-size:11px; color:{C["blue"]}; text-decoration:none;">LinkedIn ↗</a>' if dm_linkedin else ""}
    </div>
    <div class="insight-card">
        <div class="insight-card-title" style="color:{sw_color};">💿 Current Software</div>
        <div style="font-size:13px; margin-bottom:4px;">{sw_badge}</div>
        {f'<div style="font-size:11px; color:{C["text_dim"]};">{sw_confidence} confidence · {sw_signals[:80]}</div>' if sw_confidence else ""}
    </div>
</div>
"""

    # ── Competitor switching card (usa componente real del Agente A) ──
    competitor_section = competitor_card_html(current_software, sw_signals)

    # ── Insights grid ─────────────────────────────────────────
    pain_items = "".join(
        f'<div class="insight-item">⚡ {p}</div>' for p in pain_points[:5]
    ) or f'<div class="insight-item" style="color:{C["text_dim"]};">No pain points detected</div>'

    growth_items = "".join(
        f'<div class="insight-item">📈 {g}</div>' for g in growth_signals[:5]
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

    # ── Talking points ────────────────────────────────────────
    talking_section = ""
    if talking_points:
        tp_items = "".join(
            f'<div class="insight-item">💬 {t}</div>' for t in talking_points
        )
        talking_section = f"""
<div class="insight-card" style="margin-top:12px; border-color:{C['purple']};">
    <div class="insight-card-title" style="color:{C['purple']};">💬 Talking Points</div>
    {tp_items}
</div>
"""

    # ── Patient reviews ───────────────────────────────────────
    reviews_section = ""
    if reviews_summary:
        reviews_section = f"""
<div class="insight-card" style="margin-top:12px; border-color:{C['cyan']};">
    <div class="insight-card-title" style="color:{C['cyan']};">💬 Patient Reviews Insight</div>
    <div style="font-size:13px; color:{C['text_muted']}; line-height:1.6;">{reviews_summary}</div>
</div>
"""

    # ── Hiring signals ────────────────────────────────────────
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

    # ── Red flags ─────────────────────────────────────────────
    red_section = ""
    if red_flags:
        rf_items = "".join(
            f'<div class="insight-item" style="color:{C["red"]};">⚠ {r}</div>'
            for r in red_flags
        )
        red_section = f"""
<div class="insight-card" style="margin-top:12px; border-color:{C['red']};">
    <div class="insight-card-title" style="color:{C['red']};">⚠ Red Flags</div>
    {rf_items}
</div>
"""

    # ── Research sources ──────────────────────────────────────
    sources_section = ""
    if sources_used:
        src_badges = "".join(
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
    <div class="source-panel">{src_badges}</div>
</div>
"""

    return (header + metrics_row + competitor_section + insights_grid +
            talking_section + reviews_section + hiring_section +
            red_section + sources_section)


# ──────────────────────────────────────────────
#  HTML builders — Draft Stage
# ──────────────────────────────────────────────

def _draft_preview_html(draft: dict, subject: str = "", body: str = "", approved: bool = False) -> str:
    """Email preview card shown in the left column of the draft stage."""
    if not draft:
        return ""
    sender_name  = draft.get("sender_name", "Sales Team")
    sender_title = draft.get("sender_title", "Mac Practice")
    follow_up    = draft.get("follow_up_timing", "")
    initial      = sender_name[0].upper() if sender_name else "S"
    approved_badge = '<span class="approved-badge">✓ APPROVED</span>' if approved else ""
    follow_html = (
        f'<div style="font-size:11px; color:{C["amber"]}; margin-top:6px;">⏰ Follow-up: {follow_up}</div>'
    ) if follow_up else ""

    return f"""
<div class="mp-card" style="margin-bottom:14px; background:{C['card']};
     border:1px solid {C['border']}; border-radius:14px; padding:20px;">
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
    <div style="font-size:11px; color:{C['text_dim']}; margin-bottom:4px; text-transform:uppercase; letter-spacing:0.5px;">Subject</div>
    <div style="font-size:13px; font-weight:600; color:{C['text']}; margin-bottom:12px;">{subject or "(no subject selected)"}</div>
    <div style="font-size:11px; color:{C['text_dim']}; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.5px;">Body Preview</div>
    <div style="font-size:13px; color:{C['text_muted']}; line-height:1.7;
                white-space:pre-wrap; font-family:'Plus Jakarta Sans',sans-serif;">{body}</div>
    {follow_html}
</div>
"""


def _draft_hooks_html(draft: dict) -> str:
    """Personalization hooks + tone card."""
    if not draft:
        return ""
    hooks      = draft.get("personalization_hooks") or []
    tone_notes = draft.get("tone_notes", "")
    if not hooks and not tone_notes:
        return ""

    hooks_html = "".join(
        f'<div class="hook-item"><span>🎯</span><span>{h}</span></div>'
        for h in hooks
    )
    tone_html = (
        f'<div style="font-style:italic; font-size:12px; color:{C["text_dim"]}; '
        f'margin-top:8px; border-top:1px solid {C["border"]}; padding-top:8px;">'
        f'{tone_notes}</div>'
    ) if tone_notes else ""

    return f"""
<div style="background:{C['card']}; border:1px solid {C['purple']};
     border-radius:12px; padding:16px;">
    <div style="font-size:11px; font-weight:700; letter-spacing:1px; color:{C['purple']};
                text-transform:uppercase; margin-bottom:10px;">🎯 Personalization Hooks</div>
    {hooks_html}
    {tone_html}
</div>
"""


def _approved_email_html(draft: dict, subject: str, body: str) -> str:
    """Read-only approved email — displayed in approved_mode_group."""
    if not draft:
        return ""
    sender_name  = draft.get("sender_name", "Sales Team")
    sender_title = draft.get("sender_title", "Mac Practice")
    follow_up    = draft.get("follow_up_timing", "")
    initial      = sender_name[0].upper() if sender_name else "S"
    follow_html = (
        f'<div style="font-size:11px; color:{C["amber"]}; margin-top:8px;">⏰ Follow-up: {follow_up}</div>'
    ) if follow_up else ""

    return f"""
<div style="border:2px solid rgba(246,125,17,0.5); border-radius:14px; padding:20px;
            background:linear-gradient(145deg, rgba(246,125,17,0.08) 0%, {C['card']} 100%);
            box-shadow:0 0 30px rgba(246,125,17,0.12); margin-bottom:14px;">
    <div style="display:flex; align-items:center; justify-content:space-between;
                margin-bottom:14px; padding-bottom:12px;
                border-bottom:1px solid rgba(246,125,17,0.22);">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:34px; height:34px; border-radius:50%; background:{C['accent']};
                        display:flex; align-items:center; justify-content:center;
                        font-weight:800; font-size:14px; color:#000; flex-shrink:0;">{initial}</div>
            <div>
                <div style="font-weight:700; font-size:13px; color:{C['text']};">{sender_name}</div>
                <div style="font-size:11px; color:{C['text_muted']};">{sender_title}</div>
            </div>
        </div>
        <span class="approved-badge">✓ APPROVED</span>
    </div>
    <div style="font-size:11px; color:{C['text_dim']}; margin-bottom:4px;
                text-transform:uppercase; letter-spacing:0.5px;">Subject</div>
    <div style="font-size:14px; font-weight:700; color:{C['accent_light']};
                margin-bottom:14px;">{subject or "(no subject)"}</div>
    <div style="font-size:11px; color:{C['text_dim']}; margin-bottom:6px;
                text-transform:uppercase; letter-spacing:0.5px;">Body</div>
    <div style="font-size:13px; color:{C['text_muted']}; line-height:1.8;
                white-space:pre-wrap; font-family:'Plus Jakarta Sans',sans-serif;">{body}</div>
    {follow_html}
</div>
"""


def _send_stage_html(sent: bool = False, error: str = "") -> str:
    if sent:
        return f"""
<div class="send-result" style="background:{C['card']}; border:1px solid rgba(16,185,129,0.3);">
    <span class="send-result-icon">✅</span>
    <div class="send-result-title" style="color:{C['accent']};">Draft Created!</div>
    <div class="send-result-sub">Open Gmail to review and send your personalized outreach.</div>
</div>"""
    if error:
        return f"""
<div class="send-result" style="background:{C['card']}; border:1px solid rgba(245,158,11,0.3);">
    <span class="send-result-icon">📋</span>
    <div class="send-result-title" style="color:{C['amber']};">Draft Saved Locally</div>
    <div class="send-result-sub">Gmail connection unavailable. Copy the email and send manually.</div>
</div>"""
    return f"""
<div class="send-result" style="background:{C['surface']}; border:1px solid {C['border']};">
    <span class="send-result-icon" style="display:inline-block; animation:spin 1s linear infinite;">⚙️</span>
    <div class="send-result-title" style="color:{C['text_muted']};">Creating Gmail Draft...</div>
</div>"""


# ──────────────────────────────────────────────
#  Generators reales (Fase 2)
# ──────────────────────────────────────────────

def _real_research_gen(clinic_text: str, current_prospects: list):
    """
    Wraps do_research() del Agente A y mapea sus yields al formato de Gradio.
    Yields 12 valores en cada iteración (consistente para Gradio).
    """
    if not clinic_text.strip():
        return

    mode = detect_input_mode(clinic_text)

    # Constantes de posición para los gr.update visibility (6 grupos)
    # Orden: input, research, profile, draft_loading, draft, send
    _RESEARCH_VIS  = (False, True,  False, False, False, False)
    _PROFILE_VIS   = (False, False, True,  False, False, False)

    for log_text, prospect in do_research(clinic_text, mode):
        steps = _steps_from_log(log_text)

        if prospect is not None:
            # ── Research completado ──────────────────────────────────
            prospect_dict = prospect.to_dict()
            updated_prospects = list(current_prospects or []) + [prospect_dict]

            yield (
                log_text,
                _research_steps_html(steps),
                *[gr.update(visible=v) for v in _PROFILE_VIS],
                stepper_html("profile"),
                _profile_html(prospect_dict),
                prospect_dict,
                updated_prospects,
            )
        else:
            # ── Yield intermedio — streaming de logs ─────────────────
            yield (
                log_text,
                _research_steps_html(steps),
                *[gr.update(visible=v) for v in _RESEARCH_VIS],
                stepper_html("research"),
                gr.update(),   # profile_display sin cambio
                gr.update(),   # active_prospect_state sin cambio
                gr.update(),   # prospects_state sin cambio
            )


def _real_outreach_gen(prospect_dict: dict | None):
    """
    Wraps do_outreach() del Agente A y mapea sus yields al formato de Gradio.
    Yields 16 valores en cada iteración (consistente para Gradio).
    Outputs: outreach_log, *all_stage_groups(6), stepper_display,
             draft_preview_display, draft_hooks_display, draft_state,
             draft_subject_input, draft_body_input, subject_radio,
             edit_mode_group, approved_mode_group
    """
    if not prospect_dict:
        return

    # Convertir dict → Prospect para la API del Agente A
    try:
        prospect_obj = Prospect.from_dict(prospect_dict)
    except Exception:
        prospect_obj = Prospect.create_from_input(
            prospect_dict.get("input", "Unknown")
        )

    _LOADING_VIS = (False, False, False, True,  False, False)
    _DRAFT_VIS   = (False, False, False, False, True,  False)

    for log_text, draft_data in do_outreach(prospect_obj):
        if draft_data is not None:
            # ── Draft generado ────────────────────────────────────────
            subjects = draft_data.get("subject_options") or []
            body     = draft_data.get("body", "")
            first_subject = subjects[0] if subjects else ""

            yield (
                log_text,
                *[gr.update(visible=v) for v in _DRAFT_VIS],
                stepper_html("draft"),
                _draft_preview_html(draft_data, first_subject, body),
                _draft_hooks_html(draft_data),
                draft_data,
                first_subject,
                body,
                gr.update(choices=subjects, value=first_subject),
                gr.update(visible=True),   # edit_mode_group
                gr.update(visible=False),  # approved_mode_group
            )
        else:
            # ── Yield intermedio ──────────────────────────────────────
            yield (
                log_text,
                *[gr.update(visible=v) for v in _LOADING_VIS],
                stepper_html("draft_loading"),
                gr.update(),  # draft_preview_display
                gr.update(),  # draft_hooks_display
                gr.update(),  # draft_state
                gr.update(),  # draft_subject_input
                gr.update(),  # draft_body_input
                gr.update(),  # subject_radio
                gr.update(),  # edit_mode_group
                gr.update(),  # approved_mode_group
            )


# ──────────────────────────────────────────────
#  build_workflow_tab
# ──────────────────────────────────────────────

def build_workflow_tab(prospects_state: gr.State, active_prospect_state: gr.State):
    """
    Construye la pestaña Workflow dentro de un gr.Blocks() activo.
    """
    # ── Estado local ─────────────────────────────────────────
    draft_state       = gr.State(None)
    approved_state    = gr.State(False)

    # ── Stepper ──────────────────────────────────────────────
    stepper_display = gr.HTML(value=stepper_html("input"))

    # ════ ETAPA 1: INPUT ════════════════════════════════════
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
    <div style="font-size:11px; font-weight:700; letter-spacing:1px;
                color:{C['text_dim']}; text-transform:uppercase; margin-bottom:10px;">
        Research Log
    </div>
    <div style="font-size:12px; color:{C['text_dim']}; padding:20px;
                background:{C['surface']}; border:1px solid {C['border']};
                border-radius:10px; font-family:'JetBrains Mono',monospace;">
        Waiting for input...
    </div>
</div>
""")

    # ════ ETAPA 2: RESEARCH ══════════════════════════════════
    with gr.Group(visible=False) as stage_research:
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML(
                    f'<div style="font-size:14px; font-weight:700; color:{C["text"]}; '
                    f'padding:8px 0 12px;">Researching clinic across 10 sources...</div>'
                )
                research_steps_display = gr.HTML(
                    value=_research_steps_html(_build_initial_steps())
                )
            with gr.Column(scale=1):
                gr.HTML(
                    f'<div style="font-size:11px; font-weight:700; color:{C["text_dim"]}; '
                    f'letter-spacing:1px; text-transform:uppercase; padding:8px 0 8px;">Live Research Log</div>'
                )
                research_log = gr.Textbox(
                    value="",
                    label="",
                    lines=14,
                    max_lines=14,
                    interactive=False,
                    elem_classes=["terminal-log"],
                )

    # ════ ETAPA 3: PROFILE ═══════════════════════════════════
    with gr.Group(visible=False) as stage_profile:
        profile_display = gr.HTML(value="")
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

    # ════ ETAPA 4: DRAFT LOADING ═════════════════════════════
    with gr.Group(visible=False) as stage_draft_loading:
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML(f"""
<div style="text-align:center; padding:40px 20px;">
    <div style="font-size:32px; display:inline-block; margin-bottom:12px;
                animation:spin 1s linear infinite;">✍️</div>
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

    # ════ ETAPA 5: DRAFT (review + approve/reject) ═══════════
    with gr.Group(visible=False) as stage_draft:
        with gr.Row():
            # ── Left: interactive subject selector + email preview + hooks ──
            with gr.Column(scale=1):
                subject_radio = gr.Radio(
                    choices=[],
                    value=None,
                    label="Select Subject Line",
                    elem_classes=["subject-radio"],
                )
                draft_preview_display = gr.HTML(value="")
                draft_hooks_display   = gr.HTML(value="")

            # ── Right: edit controls (edit mode) / approved view ──────────
            with gr.Column(scale=1):
                gr.HTML(
                    f'<div style="font-size:14px; font-weight:700; color:{C["text"]}; '
                    f'padding:0 0 12px;">Edit & Approve</div>'
                )

                # Edit mode group
                with gr.Group(visible=True) as edit_mode_group:
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

                # Approved mode group
                with gr.Group(visible=False) as approved_mode_group:
                    gr.HTML(f"""
<div class="approved-mode-notice">
    ✓ Email approved and ready to send
</div>
""")
                    approved_display = gr.HTML(value="")
                    with gr.Row():
                        btn_edit = gr.Button(
                            "✏️ Edit",
                            variant="secondary",
                            elem_classes=["gr-button", "secondary"],
                            scale=1,
                        )
                        btn_create_gmail = gr.Button(
                            "📧 Create Gmail Draft",
                            variant="primary",
                            elem_classes=["gr-button", "primary"],
                            scale=2,
                        )

    # ════ ETAPA 6: SEND ══════════════════════════════════════
    with gr.Group(visible=False) as stage_send:
        send_display = gr.HTML(value=_send_stage_html())
        clipboard_box = gr.Textbox(
            label="📋 Copy to clipboard (fallback)",
            lines=8,
            visible=False,
            interactive=True,
            elem_classes=["terminal-log"],
        )
        btn_back_to_pipeline = gr.Button(
            "← Back to Pipeline",
            variant="secondary",
            elem_classes=["gr-button", "secondary"],
        )

    # ────────────────────────────────────────────────────────
    #  Lista ordenada de todos los grupos para visibility
    # ────────────────────────────────────────────────────────
    all_stage_groups = [
        stage_input, stage_research, stage_profile,
        stage_draft_loading, stage_draft, stage_send,
    ]

    def _show_only(active):
        return [gr.update(visible=(g == active)) for g in all_stage_groups]

    # ════ EVENTOS ════════════════════════════════════════════

    # ── Research: single generator handler ───────────────────
    btn_research.click(
        fn=_real_research_gen,
        inputs=[clinic_input, prospects_state],
        outputs=[
            research_log,
            research_steps_display,
            *all_stage_groups,
            stepper_display,
            profile_display,
            active_prospect_state,
            prospects_state,
        ],
    )

    # ── Outreach: single generator handler ───────────────────
    _OUTREACH_GEN_OUTPUTS = [
        outreach_log,
        *all_stage_groups,
        stepper_display,
        draft_preview_display,
        draft_hooks_display,
        draft_state,
        draft_subject_input,
        draft_body_input,
        subject_radio,
        edit_mode_group,
        approved_mode_group,
    ]

    def _start_outreach_ui():
        """Limpia la UI antes de iniciar el generator de outreach."""
        return (
            *_show_only(stage_draft_loading),
            stepper_html("draft_loading"),
            "",
        )

    btn_generate_outreach.click(
        fn=_start_outreach_ui,
        outputs=[*all_stage_groups, stepper_display, outreach_log],
    )
    btn_generate_outreach.click(
        fn=_real_outreach_gen,
        inputs=[active_prospect_state],
        outputs=_OUTREACH_GEN_OUTPUTS,
    )

    # ── Radio → subject textbox sync ─────────────────────────
    subject_radio.change(
        fn=lambda subj: subj or "",
        inputs=[subject_radio],
        outputs=[draft_subject_input],
    )

    # ── Reject: también limpia y re-corre outreach ────────────
    btn_reject.click(
        fn=_start_outreach_ui,
        outputs=[*all_stage_groups, stepper_display, outreach_log],
    )
    btn_reject.click(
        fn=_real_outreach_gen,
        inputs=[active_prospect_state],
        outputs=_OUTREACH_GEN_OUTPUTS,
    )

    # ── Approve ───────────────────────────────────────────────
    def _approve_draft(draft, subject, body):
        updated = dict(draft or {})
        updated["_approved_subject"] = subject
        updated["_approved_body"]    = body
        return (
            _draft_preview_html(updated, subject, body, approved=True),
            updated,
            True,
            gr.update(visible=False),  # edit_mode_group
            gr.update(visible=True),   # approved_mode_group
            _approved_email_html(updated, subject, body),
        )

    btn_approve.click(
        fn=_approve_draft,
        inputs=[draft_state, draft_subject_input, draft_body_input],
        outputs=[
            draft_preview_display, draft_state, approved_state,
            edit_mode_group, approved_mode_group, approved_display,
        ],
    )

    # ── Edit (post-approval: return to edit mode) ─────────────
    def _edit_draft():
        return (
            gr.update(visible=True),   # edit_mode_group
            gr.update(visible=False),  # approved_mode_group
            False,                     # approved_state
        )

    btn_edit.click(
        fn=_edit_draft,
        outputs=[edit_mode_group, approved_mode_group, approved_state],
    )

    # ── Create Gmail Draft (Fase 4: envío real via Gmail SMTP) ────
    def _do_send(draft, subject, body, prospect_dict):
        """
        Intenta enviar el email via Gmail SMTP.
        Si falla, muestra el email formateado para copy/paste.
        También actualiza el pipeline stage del prospect.
        NUNCA se queda colgado — try/except global.
        """
        try:
            sender_name = (draft or {}).get("sender_name", "Sales Team")
            sender_title = (draft or {}).get("sender_title", "Mac Practice")

            # Intentar obtener el email del decision maker
            dm = (prospect_dict or {}).get("decision_maker") or {}
            recipient = dm.get("email", "")

            # Preparar email para clipboard (siempre disponible)
            clipboard_text = format_email_for_clipboard(
                subject=subject or "",
                body=body or "",
                sender_name=sender_name,
                sender_title=sender_title,
                recipient=recipient,
            )

            # Intentar envío real si hay recipient
            sent = False
            error_msg = ""

            if recipient:
                try:
                    for log_text, result in send_real_email(
                        recipient=recipient,
                        subject=subject,
                        body=body,
                        sender_name=sender_name,
                    ):
                        if result is not None:
                            sent = result.sent
                            error_msg = result.error
                except Exception as e:
                    error_msg = str(e)[:120]
            else:
                error_msg = "No decision maker email found. Copy the draft manually."

            # Hard fallback on message
            if not sent and not error_msg:
                error_msg = "Saved locally. (Gmail connection skipped)"

            # Actualizar pipeline stage del prospect
            if prospect_dict:
                prospect_id = prospect_dict.get("id", "")
                if prospect_id:
                    try:
                        storage.move_prospect_stage(
                            prospect_id, "outreach_sent"
                        )
                    except Exception:
                        pass  # Non-critical

            # UI result
            show_clipboard = not sent
            return (
                *_show_only(stage_send),
                stepper_html("send"),
                _send_stage_html(sent=sent, error=error_msg if not sent else ""),
                gr.update(visible=show_clipboard, value=clipboard_text),
            )

        except Exception as e:
            # Fallback absoluto — NUNCA dejar la UI colgada
            fallback_clipboard = f"Subject: {subject or ''}\n\n{body or ''}"
            return (
                *_show_only(stage_send),
                stepper_html("send"),
                _send_stage_html(sent=False, error=f"Error inesperado: {str(e)[:80]}"),
                gr.update(visible=True, value=fallback_clipboard),
            )

    btn_create_gmail.click(
        fn=_do_send,
        inputs=[draft_state, draft_subject_input, draft_body_input, active_prospect_state],
        outputs=[*all_stage_groups, stepper_display, send_display, clipboard_box],
    )

    # ── Navegación: back buttons ──────────────────────────────
    def _back_to_input_stage():
        return (
            *_show_only(stage_input),
            stepper_html("input"),
        )

    def _back_to_profile_stage():
        return (
            *_show_only(stage_profile),
            stepper_html("profile"),
        )

    btn_back_to_input.click(
        fn=_back_to_input_stage,
        outputs=[*all_stage_groups, stepper_display],
    )
    btn_draft_back.click(
        fn=_back_to_profile_stage,
        outputs=[*all_stage_groups, stepper_display],
    )
    btn_back_to_pipeline.click(
        fn=_back_to_input_stage,
        outputs=[*all_stage_groups, stepper_display],
    )

    return {
        "stage_input":           stage_input,
        "clinic_input":          clinic_input,
        "btn_research":          btn_research,
        "research_log":          research_log,
        "profile_display":       profile_display,
        "subject_radio":         subject_radio,
        "draft_preview_display": draft_preview_display,
        "draft_hooks_display":   draft_hooks_display,
        "draft_subject_input":   draft_subject_input,
        "draft_body_input":      draft_body_input,
        "btn_approve":           btn_approve,
        "btn_reject":            btn_reject,
        "btn_edit":              btn_edit,
        "btn_create_gmail":      btn_create_gmail,
        "approved_display":      approved_display,
        "btn_back_to_pipeline":  btn_back_to_pipeline,
        "send_display":          send_display,
        "stepper_display":       stepper_display,
    }
