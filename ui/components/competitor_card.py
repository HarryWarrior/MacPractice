# ui/components/competitor_card.py
# Card de competidor: "Their Pains" vs "Our Angles"
# Usa los perfiles reales de app.models.competitor (Agente A, Fase 2)

from ui.theme import C, badge_html

# Importamos la base de datos real del Agente A
from app.models.competitor import COMPETITORS, detect_competitor


def competitor_card_html(current_software: str, signals: str = "") -> str:
    """
    Renderiza la card de switching opportunity para un competidor detectado.
    Retorna string vacío si no se detecta ningún competidor conocido.

    Args:
        current_software: Valor del campo current_software del research.
        signals:          Texto de software_signals (evidencia de la detección).
    """
    result = detect_competitor(current_software)
    if result is None:
        return ""

    _key, profile = result
    name  = profile["name"]
    color = profile["color"]
    pains = profile["pains"]
    angles = profile["angles"]
    initial = name[0].upper()

    pain_items = "".join(
        f'<div class="pa-item" style="color:{C["red"]};">− {p}</div>'
        for p in pains
    )
    angle_items = "".join(
        f'<div class="pa-item" style="color:{C["accent"]};">+ {a}</div>'
        for a in angles
    )
    signals_html = (
        f'<div style="font-size:11px; color:{C["text_dim"]}; margin-top:2px;">'
        f'{signals}</div>'
    ) if signals else ""

    return f"""
<div class="competitor-card" style="border-color:{color}; margin-top:14px;">
    <div class="competitor-header">
        <div class="competitor-icon-badge"
             style="background:rgba(0,0,0,0.35); color:{color}; border:1px solid {color};">
            {initial}
        </div>
        <div style="flex:1; min-width:0;">
            <div style="font-weight:700; font-size:14px; color:{color};">{name}</div>
            {signals_html}
        </div>
        <div style="flex-shrink:0;">
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


# Competidores que NO muestran badge en el Kanban (no es un "switching opp" identificado)
_NO_BADGE_KEYS = {"unknown", "paper-based", "paper"}


def competitor_badge_html(current_software: str, small: bool = True) -> str:
    """
    Retorna solo el badge del competidor (para usar en ProspectCard Kanban).
    Excluye Unknown/Paper-based — no cuenta como competidor identificado.
    """
    result = detect_competitor(current_software)
    if result is None:
        return ""
    key, profile = result
    if key in _NO_BADGE_KEYS:
        return ""
    return badge_html(profile["name"], profile["color"], small=small)
