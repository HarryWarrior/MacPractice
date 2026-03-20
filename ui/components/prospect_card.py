# ui/components/prospect_card.py
# Renderiza una ProspectCard para el Kanban board del Dashboard

from ui.theme import C, badge_html, score_ring_svg, PRIORITY_COLORS
from ui.components.competitor_card import competitor_badge_html


def prospect_card_html(prospect) -> str:
    """
    Genera el HTML de una tarjeta de prospecto para el kanban.
    Props: clinic_name, location, practitioners, fit_score, priority, current_software
    """
    name = prospect.get("clinic_name") or prospect.get("input", "Unknown Clinic")
    location = prospect.get("location", "")
    practitioners = prospect.get("practitioners")
    fit_score = prospect.get("fit_score")
    priority = (prospect.get("priority") or "warm").lower()
    current_software = (prospect.get("current_software") or "").strip()
    pid = prospect.get("id", "")

    # Priority badge
    priority_color = PRIORITY_COLORS.get(priority, C["amber"])
    priority_badge = badge_html(priority.upper(), priority_color, small=True)

    # Competitor badge — usa la DB real del Agente A
    competitor_badge = competitor_badge_html(current_software, small=True)

    # Mini score ring (28x28)
    ring_html = score_ring_svg(fit_score, size=28) if fit_score is not None else ""

    # Meta line
    meta_parts = []
    if location:
        meta_parts.append(location)
    if practitioners:
        meta_parts.append(f"{practitioners} prac.")
    meta = " · ".join(meta_parts)

    # Drag & drop — inline handlers (Gradio strips <script> but keeps event attrs)
    drag_handlers = (
        f'draggable="true" '
        f'ondragstart="event.dataTransfer.setData(\'text/plain\',\'{pid}\'); '
        f'event.currentTarget.classList.add(\'dragging\')" '
        f'ondragend="event.currentTarget.classList.remove(\'dragging\')"'
    ) if pid else ""

    return f"""
<div class="prospect-card" data-id="{pid}" {drag_handlers}>
    <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:6px; margin-bottom:3px;">
        <span class="prospect-name" title="{name}">{name}</span>
        {ring_html}
    </div>
    <div class="prospect-meta">{meta}</div>
    <div style="display:flex; gap:4px; flex-wrap:wrap;">
        {priority_badge}
        {competitor_badge}
    </div>
</div>
"""


def empty_col_html() -> str:
    """Placeholder cuando no hay prospectos en una columna."""
    return f"""
<div class="empty-state">
    <span style="font-size:20px; opacity:0.4">—</span>
    <div style="font-size:11px; color:{C['text_dim']}; margin-top:6px;">No prospects</div>
</div>
"""
