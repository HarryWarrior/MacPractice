# ui/components/score_ring.py
# ScoreRing — SVG circular que muestra el fit score (1-10)
# Re-exporta la función canónica desde theme.py para que otros módulos
# puedan importarla directamente desde este componente.

from ui.theme import score_ring_svg, C


def score_ring_html(score, size: int = 88) -> str:
    """
    Wrapper del ScoreRing SVG.
    score : int 1-10  |  None → muestra "—"
    size  : int px (default 88 para Profile, 28 para ProspectCard mini)
    Colores: verde ≥8, amber ≥5, rojo <5
    """
    return score_ring_svg(score, size)


def score_ring_with_label(score, size: int = 88) -> str:
    """
    ScoreRing + label "FIT SCORE" debajo. Usado en Profile Stage.
    """
    label_color = C["text_dim"]
    return f"""
<div class="profile-score-col">
    {score_ring_svg(score, size)}
    <div class="profile-score-label" style="color:{label_color};">FIT SCORE</div>
</div>
"""
