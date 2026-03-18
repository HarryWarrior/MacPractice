# ui/theme.py
# Design System — Mac Practice Dental Prospector
# Colores, CSS global, y builders de componentes HTML reutilizables

# ──────────────────────────────────────────────
#  Paleta de colores (Section 2.1 del SPEC)
# ──────────────────────────────────────────────
C = {
    "bg":           "#070A0F",
    "surface":      "#0E1219",
    "card":         "#141A23",
    "border":       "#1E2636",
    "border_light": "#2A3348",
    "text":         "#EDF2F7",
    "text_muted":   "#8899AD",
    "text_dim":     "#566577",
    "accent":       "#10B981",
    "accent_light": "#34D399",
    "accent_glow":  "rgba(16,185,129,0.12)",
    "amber":        "#F59E0B",
    "red":          "#EF4444",
    "blue":         "#3B82F6",
    "purple":       "#8B5CF6",
    "cyan":         "#06B6D4",
    "gray":         "#6B7280",
}

PRIORITY_COLORS = {
    "hot":  C["red"],
    "warm": C["amber"],
    "cold": C["blue"],
}

COMPETITOR_COLORS = {
    "dentrix":     C["blue"],
    "eaglesoft":   C["purple"],
    "open dental": C["cyan"],
    "curve dental":C["amber"],
    "unknown":     C["gray"],
    "paper-based": C["gray"],
}

# ──────────────────────────────────────────────
#  Google Fonts (Section 2.2 del SPEC)
# ──────────────────────────────────────────────
GOOGLE_FONTS_HTML = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
"""

# ──────────────────────────────────────────────
#  CSS Global
# ──────────────────────────────────────────────
# NOTA: las llaves CSS están escapadas ({{ }}) por ser f-string de Python.
CSS = f"""
/* ===== RESET & BASE ===== */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body, .gradio-container {{
    background: {C['bg']} !important;
    color: {C['text']} !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    min-height: 100vh;
}}

.gradio-container {{ max-width: 100% !important; padding: 0 !important; }}
.contain {{ max-width: 100% !important; }}
footer {{ display: none !important; }}
.gr-box, .gr-form, .gr-panel {{ background: transparent !important; border: none !important; box-shadow: none !important; }}
.gap {{ gap: 0 !important; }}

/* ===== TABS ===== */
.tab-nav {{
    background: {C['surface']} !important;
    border-bottom: 1px solid {C['border']} !important;
    padding: 0 8px !important;
}}
.tab-nav button {{
    color: {C['text_muted']} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 14px 20px !important;
    border: none !important;
    background: transparent !important;
    transition: color 0.2s !important;
}}
.tab-nav button.selected {{
    color: {C['accent']} !important;
    border-bottom: 2px solid {C['accent']} !important;
}}

/* ===== TEXTBOX — terminal de logs ===== */
.terminal-log label {{ display: none !important; }}
.terminal-log textarea {{
    background: {C['surface']} !important;
    color: {C['accent']} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    border: 1px solid {C['border']} !important;
    border-radius: 10px !important;
    padding: 14px !important;
    line-height: 1.7 !important;
    resize: none !important;
}}

/* ===== TEXTBOX — inputs normales ===== */
.mp-input input, .mp-input textarea {{
    background: {C['card']} !important;
    color: {C['text']} !important;
    border: 1px solid {C['border']} !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}}
.mp-input input:focus, .mp-input textarea:focus {{
    border-color: {C['accent']} !important;
    outline: none !important;
    box-shadow: 0 0 0 3px {C['accent_glow']} !important;
}}
.mp-input label {{
    color: {C['text_muted']} !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    margin-bottom: 6px !important;
}}

/* ===== BUTTONS ===== */
.gr-button, button.gr-button {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    border: 1px solid transparent !important;
}}
.gr-button.primary, button.primary {{
    background: {C['accent']} !important;
    color: #000 !important;
    border-color: {C['accent']} !important;
}}
.gr-button.primary:hover {{
    background: {C['accent_light']} !important;
    box-shadow: 0 4px 20px {C['accent_glow']} !important;
}}
.gr-button.secondary {{
    background: transparent !important;
    color: {C['text_muted']} !important;
    border-color: {C['border']} !important;
}}
.gr-button.secondary:hover {{
    border-color: {C['accent']} !important;
    color: {C['accent']} !important;
}}
.btn-danger {{
    background: transparent !important;
    color: {C['red']} !important;
    border-color: {C['red']} !important;
}}
.btn-danger:hover {{
    background: rgba(239,68,68,0.1) !important;
}}

/* ===== ANIMACIONES (Section 2.3 del SPEC) ===== */
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes spin {{
    to {{ transform: rotate(360deg); }}
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50%       {{ opacity: 0.3; }}
}}

.fade-up {{ animation: fadeUp 0.4s ease forwards; }}
.spin     {{ animation: spin 0.8s linear infinite; display: inline-block; }}
.pulse    {{ animation: pulse 1s ease infinite; }}

/* ===== NAVBAR ===== */
.mp-navbar {{
    background: {C['surface']};
    border-bottom: 1px solid {C['border']};
    padding: 0 24px;
    height: 56px;
    display: flex;
    align-items: center;
    gap: 12px;
}}
.mp-navbar-logo {{
    font-family: 'JetBrains Mono', monospace;
    font-weight: 800;
    font-size: 20px;
    color: {C['accent']};
    letter-spacing: -0.5px;
}}
.mp-navbar-title {{
    font-weight: 700;
    font-size: 15px;
    color: {C['text']};
}}
.mp-navbar-badge {{
    background: rgba(16,185,129,0.12);
    color: {C['accent']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    padding: 3px 9px;
    border-radius: 5px;
    border: 1px solid rgba(16,185,129,0.25);
    text-transform: uppercase;
}}
.mp-navbar-spacer {{ flex: 1; }}

/* ===== BADGE ===== */
.mp-badge {{
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    border: 1px solid currentColor;
    background: rgba(0,0,0,0.25);
}}
.mp-badge.sm {{ padding: 2px 7px; font-size: 10px; }}

/* ===== METRIC CARDS (Dashboard) ===== */
.metrics-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    padding: 20px 24px 0;
}}
.mp-metric-card {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
    animation: fadeUp 0.4s ease forwards;
}}
.mp-metric-label {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    color: {C['text_dim']};
    text-transform: uppercase;
    margin-bottom: 8px;
}}
.mp-metric-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    line-height: 1;
}}
.mp-metric-sub {{
    font-size: 11px;
    color: {C['text_muted']};
    margin-top: 5px;
}}

/* ===== KANBAN BOARD ===== */
.kanban-board {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    padding: 16px 24px 24px;
    overflow-x: auto;
}}
.kanban-col {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 12px;
    min-height: 320px;
}}
.kanban-col-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid {C['border']};
}}
.kanban-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}}
.kanban-col-name {{
    font-size: 12px;
    font-weight: 700;
    color: {C['text']};
    flex: 1;
}}
.kanban-count {{
    background: {C['border']};
    color: {C['text_muted']};
    font-size: 11px;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 10px;
    font-family: 'JetBrains Mono', monospace;
}}

/* ===== PROSPECT CARD (Kanban) ===== */
.prospect-card {{
    background: {C['card']};
    border: 1px solid {C['border_light']};
    border-radius: 10px;
    padding: 11px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: border-color 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
    animation: fadeUp 0.35s ease forwards;
}}
.prospect-card:hover {{
    border-color: {C['accent']};
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}}
.prospect-name {{
    font-size: 13px;
    font-weight: 700;
    color: {C['text']};
    margin-bottom: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 140px;
}}
.prospect-meta {{
    font-size: 11px;
    color: {C['text_muted']};
    margin-bottom: 7px;
}}

/* ===== EMPTY STATE ===== */
.empty-state {{
    text-align: center;
    padding: 48px 16px;
    color: {C['text_dim']};
}}
.empty-state-icon {{ font-size: 40px; display: block; margin-bottom: 12px; }}
.empty-state-title {{
    font-size: 14px;
    font-weight: 700;
    color: {C['text_muted']};
    margin-bottom: 6px;
}}
.empty-state-sub {{
    font-size: 12px;
    color: {C['text_dim']};
}}

/* ===== BATCH PROGRESS BAR ===== */
.batch-bar {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 10px;
    padding: 10px 20px;
    margin: 8px 24px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 12px;
    color: {C['text_muted']};
}}
.batch-spinner {{
    width: 14px;
    height: 14px;
    border: 2px solid {C['border']};
    border-top-color: {C['accent']};
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    flex-shrink: 0;
}}
.batch-track {{
    flex: 1;
    height: 4px;
    background: {C['border']};
    border-radius: 2px;
    overflow: hidden;
}}
.batch-fill {{
    height: 100%;
    background: {C['accent']};
    border-radius: 2px;
    transition: width 0.4s ease;
}}

/* ===== STEPPER ===== */
.mp-stepper {{
    background: {C['surface']};
    border-bottom: 1px solid {C['border']};
    padding: 14px 24px;
    display: flex;
    align-items: center;
    gap: 0;
}}
.stepper-back-btn {{
    font-size: 13px;
    font-weight: 600;
    color: {C['text_muted']};
    display: flex;
    align-items: center;
    gap: 6px;
    margin-right: 20px;
    padding-right: 20px;
    border-right: 1px solid {C['border']};
    background: none;
    border-left: none;
    border-top: none;
    border-bottom: none;
    cursor: pointer;
    transition: color 0.2s;
    white-space: nowrap;
}}
.stepper-back-btn:hover {{ color: {C['text']}; }}
.stepper-steps {{
    display: flex;
    align-items: center;
    gap: 0;
}}
.step-dot {{
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 2px solid {C['border']};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    color: {C['text_dim']};
    background: {C['surface']};
    flex-shrink: 0;
    position: relative;
    z-index: 1;
}}
.step-dot.done {{
    background: {C['accent']};
    border-color: {C['accent']};
    color: #000;
    font-size: 12px;
}}
.step-dot.active {{
    border-color: {C['accent']};
    color: {C['accent']};
    box-shadow: 0 0 0 3px {C['accent_glow']};
}}
.step-connector {{
    width: 32px;
    height: 2px;
    background: {C['border']};
    flex-shrink: 0;
}}
.step-connector.done {{ background: {C['accent']}; }}

/* ===== INPUT STAGE ===== */
.source-panel {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 10px;
}}
.source-badge {{
    background: rgba(16,185,129,0.08);
    color: {C['accent']};
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 10px;
}}
.mode-pills {{
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 12px;
}}
.mode-pill {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 7px;
    color: {C['text_muted']};
    font-size: 12px;
    font-weight: 600;
    padding: 7px 13px;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}}
.mode-pill:hover, .mode-pill.active {{
    border-color: {C['accent']};
    color: {C['accent']};
    background: {C['accent_glow']};
}}
.example-cards {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-top: 12px;
}}
.example-card {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 10px 13px;
    cursor: pointer;
    transition: border-color 0.2s;
    font-size: 12px;
}}
.example-card:hover {{ border-color: {C['accent']}; }}
.example-card-icon {{ margin-bottom: 2px; font-size: 14px; }}
.example-card-name {{ font-weight: 700; color: {C['text']}; }}
.example-card-sub {{ color: {C['text_dim']}; margin-top: 2px; }}

/* ===== RESEARCH STAGE ===== */
.research-steps-list {{
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 8px 0;
}}
.research-step {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-radius: 9px;
    border: 1px solid {C['border']};
    background: {C['surface']};
    font-size: 13px;
    color: {C['text_dim']};
    transition: all 0.3s;
}}
.research-step.active {{
    border-color: {C['accent']};
    background: {C['accent_glow']};
    color: {C['accent']};
}}
.research-step.done {{
    border-color: rgba(16,185,129,0.25);
    color: {C['text_muted']};
}}
.step-indicator {{
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: 2px solid {C['border']};
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 9px;
    font-weight: 800;
}}
.step-indicator.active {{
    border-color: {C['accent']};
    border-right-color: transparent;
    animation: spin 0.9s linear infinite;
}}
.step-indicator.done {{
    background: {C['accent']};
    border-color: {C['accent']};
    color: #000;
}}

/* ===== PROFILE STAGE ===== */
.profile-header-card {{
    background: {C['card']};
    border: 1px solid {C['accent']};
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 0 32px {C['accent_glow']};
    display: flex;
    gap: 20px;
    align-items: flex-start;
    animation: fadeUp 0.4s ease;
}}
.profile-info {{ flex: 1; min-width: 0; }}
.profile-badges {{ display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }}
.profile-name {{
    font-size: 20px;
    font-weight: 800;
    color: {C['text']};
    margin-bottom: 6px;
    line-height: 1.2;
}}
.profile-meta-row {{
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    font-size: 12px;
    color: {C['text_muted']};
    margin-bottom: 4px;
}}
.profile-score-col {{ flex-shrink: 0; text-align: center; }}
.profile-score-label {{
    font-size: 10px;
    font-weight: 700;
    color: {C['text_dim']};
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 6px;
}}

/* ===== COMPETITOR CARD ===== */
.competitor-card {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 18px;
    animation: fadeUp 0.4s ease;
}}
.competitor-header {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
}}
.competitor-icon-badge {{
    width: 34px;
    height: 34px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 14px;
    font-family: 'JetBrains Mono', monospace;
}}
.competitor-pains-angles {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-top: 10px;
}}
.pa-col-title {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 8px;
}}
.pa-item {{
    display: flex;
    align-items: flex-start;
    gap: 6px;
    font-size: 12px;
    margin-bottom: 5px;
    line-height: 1.4;
}}

/* ===== DRAFT STAGE ===== */
.subject-option {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 6px;
    color: {C['text']};
}}
.subject-option:hover {{
    border-color: {C['border_light']};
}}
.subject-option.selected {{
    border-color: {C['accent']};
    background: {C['accent_glow']};
    color: {C['accent']};
}}
.approved-badge {{
    background: rgba(16,185,129,0.15);
    color: {C['accent']};
    border: 1px solid {C['accent']};
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 4px 10px;
    display: inline-block;
    text-transform: uppercase;
}}
.hook-item {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 12px;
    color: {C['text_muted']};
    margin-bottom: 5px;
    line-height: 1.5;
}}

/* ===== SEND STAGE ===== */
.send-result {{
    text-align: center;
    padding: 36px;
    border-radius: 14px;
    animation: fadeUp 0.4s ease;
}}
.send-result-icon {{ font-size: 44px; display: block; margin-bottom: 12px; }}
.send-result-title {{
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 6px;
}}
.send-result-sub {{
    font-size: 13px;
    color: {C['text_muted']};
}}

/* ===== INSIGHT CARDS ===== */
.insight-card {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 10px;
    padding: 14px;
}}
.insight-card-title {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.insight-item {{
    font-size: 12px;
    color: {C['text_muted']};
    padding: 5px 0;
    border-bottom: 1px solid {C['border']};
    line-height: 1.5;
}}
.insight-item:last-child {{ border-bottom: none; }}
"""


# ──────────────────────────────────────────────
#  HTML Builder Functions
# ──────────────────────────────────────────────

def navbar_html(show_badge: bool = True) -> str:
    """Barra de navegación superior."""
    badge = '<span class="mp-navbar-badge">PIPELINE</span>' if show_badge else ''
    return f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<div class="mp-navbar">
    <span class="mp-navbar-logo">MP</span>
    <span class="mp-navbar-title">Dental Prospector</span>
    {badge}
    <span class="mp-navbar-spacer"></span>
</div>
"""


def badge_html(text: str, color: str, small: bool = False) -> str:
    """Pill badge con color."""
    cls = "mp-badge sm" if small else "mp-badge"
    return f'<span class="{cls}" style="color:{color}; border-color:{color};">{text}</span>'


def metric_card_html(label: str, value: str, sub: str = "", color: str = None) -> str:
    """Card de métrica para el dashboard."""
    val_color = color or C["text"]
    sub_html = f'<div class="mp-metric-sub">{sub}</div>' if sub else ''
    return f"""
<div class="mp-metric-card">
    <div class="mp-metric-label">{label}</div>
    <div class="mp-metric-value" style="color:{val_color}">{value}</div>
    {sub_html}
</div>
"""


def score_ring_svg(score, size: int = 88) -> str:
    """SVG circular que muestra el fit score (1-10)."""
    score_val = score if score is not None else 0
    radius = (size - 10) / 2
    circumference = 2 * 3.14159265 * radius
    progress = (score_val / 10) * circumference if score_val else 0

    if score_val >= 8:
        color = C["accent"]
    elif score_val >= 5:
        color = C["amber"]
    else:
        color = C["red"]

    cx = cy = size / 2
    font_size = max(size // 4, 10)
    display = str(score_val) if score else "—"

    return f"""<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" style="display:block;">
  <circle cx="{cx}" cy="{cy}" r="{radius}"
          fill="none" stroke="{C['border']}" stroke-width="6"/>
  <circle cx="{cx}" cy="{cy}" r="{radius}"
          fill="none" stroke="{color}" stroke-width="6"
          stroke-dasharray="{progress:.1f} {circumference:.1f}"
          stroke-linecap="round"
          transform="rotate(-90 {cx} {cy})"/>
  <text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central"
        fill="{color}" font-family="JetBrains Mono,monospace"
        font-size="{font_size}" font-weight="700">{display}</text>
</svg>"""


def stepper_html(current_stage: str) -> str:
    """
    Renderiza el stepper de 6 pasos.
    current_stage: 'input' | 'research' | 'profile' | 'draft_loading' | 'draft' | 'send'
    """
    stage_order = ["input", "research", "profile", "draft", "draft", "send"]
    stage_index = {
        "input": 0, "research": 1, "profile": 2,
        "draft_loading": 3, "draft": 3, "send": 5
    }
    active_idx = stage_index.get(current_stage, 0)

    labels = ["①", "②", "③", "④", "⑤", "⑥"]
    dots = ""
    for i, label in enumerate(labels):
        if i < active_idx:
            cls = "done"
            content = "✓"
        elif i == active_idx:
            cls = "active"
            content = str(i + 1)
        else:
            cls = ""
            content = str(i + 1)

        dots += f'<div class="step-dot {cls}">{content}</div>'
        if i < len(labels) - 1:
            connector_cls = "done" if i < active_idx else ""
            dots += f'<div class="step-connector {connector_cls}"></div>'

    return f"""
<div class="mp-stepper">
    <button class="stepper-back-btn" onclick="void(0)">← Pipeline</button>
    <div class="stepper-steps">{dots}</div>
</div>
"""
