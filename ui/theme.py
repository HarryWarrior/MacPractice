# ui/theme.py
# Design System — Mac Practice Dental Prospector
# Paleta inspirada en macpractice.com: navy profundo + naranja de marca

# ──────────────────────────────────────────────
#  Paleta de colores
# ──────────────────────────────────────────────
C = {
    # Backgrounds — navy profundo de MacPractice
    "bg":           "#00253B",
    "surface":      "#04304B",
    "card":         "#0A3D5C",
    "card2":        "#0D4468",

    # Borders
    "border":       "#1A5272",
    "border_light": "#2A6888",

    # Texto
    "text":         "#F0F7FF",
    "text_muted":   "#8BBAD4",
    "text_dim":     "#4A8099",

    # Acento principal — naranja MacPractice
    "accent":       "#F67D11",
    "accent_light": "#FF9B44",
    "accent_glow":  "rgba(246,125,17,0.18)",
    "accent_deep":  "#D4660A",

    # Colores semánticos
    "amber":        "#F59E0B",
    "red":          "#EF4444",
    "blue":         "#3B82F6",
    "purple":       "#8B5CF6",
    "cyan":         "#06B6D4",
    "green":        "#10B981",
    "gray":         "#4A6070",

    # Gradients helpers (usados en f-strings del CSS)
    "grad_bg":      "linear-gradient(135deg, #00253B 0%, #03314D 100%)",
    "grad_card":    "linear-gradient(145deg, #0A3D5C 0%, #0D4870 100%)",
    "grad_accent":  "linear-gradient(135deg, #F67D11 0%, #FF9B44 100%)",
    "grad_surface": "linear-gradient(180deg, #04304B 0%, #052C45 100%)",
}

PRIORITY_COLORS = {
    "hot":  "#EF4444",
    "warm": "#F67D11",
    "cold": "#3B82F6",
}

COMPETITOR_COLORS = {
    "dentrix":      "#3B82F6",
    "eaglesoft":    "#8B5CF6",
    "open dental":  "#06B6D4",
    "curve dental": "#F59E0B",
    "unknown":      "#4A6070",
    "paper-based":  "#4A6070",
}

# ──────────────────────────────────────────────
#  CSS Global
# ──────────────────────────────────────────────
CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* ===== RESET ===== */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

/* ===== BASE ===== */
body, .gradio-container, #root {{
    background: {C['bg']} !important;
    background-image: radial-gradient(ellipse at 20% 0%, rgba(246,125,17,0.06) 0%, transparent 50%),
                      radial-gradient(ellipse at 80% 100%, rgba(4,48,75,0.8) 0%, transparent 50%) !important;
    color: {C['text']} !important;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    min-height: 100vh;
}}
.gradio-container {{ max-width: 100% !important; padding: 0 !important; }}
.contain {{ max-width: 100% !important; }}
footer, .footer {{ display: none !important; }}
.gr-box, .gr-form, .gr-panel {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}
.gap, .gap-4 {{ gap: 0 !important; }}
.form {{ border: none !important; background: transparent !important; }}
.block {{ padding: 0 !important; }}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {C['bg']}; }}
::-webkit-scrollbar-thumb {{ background: {C['border']}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {C['accent']}; }}

/* ===== TABS ===== */
.tab-nav, div[class*="tab-nav"] {{
    background: {C['surface']} !important;
    border-bottom: 1px solid {C['border']} !important;
    padding: 0 24px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3) !important;
}}
.tab-nav button {{
    color: {C['text_muted']} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 15px 22px !important;
    border: none !important;
    background: transparent !important;
    border-bottom: 3px solid transparent !important;
    transition: all 0.25s ease !important;
    letter-spacing: 0.3px !important;
}}
.tab-nav button:hover {{
    color: {C['text']} !important;
    background: rgba(246,125,17,0.06) !important;
}}
.tab-nav button.selected {{
    color: {C['accent']} !important;
    border-bottom-color: {C['accent']} !important;
    background: rgba(246,125,17,0.08) !important;
}}

/* ===== TERMINAL DE LOGS ===== */
.terminal-log label {{ display: none !important; }}
.terminal-log textarea {{
    background: #001828 !important;
    color: #4ADE80 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11.5px !important;
    border: 1px solid {C['border']} !important;
    border-radius: 10px !important;
    padding: 14px 16px !important;
    line-height: 1.85 !important;
    resize: none !important;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.5), 0 0 0 1px rgba(26,82,114,0.3) !important;
}}

/* ===== INPUTS ===== */
.mp-input label {{
    color: {C['text_muted']} !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    margin-bottom: 6px !important;
}}
.mp-input input, .mp-input textarea {{
    background: {C['card']} !important;
    color: {C['text']} !important;
    border: 1.5px solid {C['border']} !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
    transition: all 0.2s ease !important;
    box-shadow: inset 0 1px 4px rgba(0,0,0,0.25) !important;
}}
.mp-input input:focus, .mp-input textarea:focus {{
    border-color: {C['accent']} !important;
    outline: none !important;
    box-shadow: 0 0 0 3px {C['accent_glow']}, inset 0 1px 4px rgba(0,0,0,0.25) !important;
    background: {C['card2']} !important;
}}

/* ===== BUTTONS ===== */
.gr-button, button.gr-button {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    border-radius: 10px !important;
    padding: 11px 22px !important;
    cursor: pointer !important;
    transition: all 0.2s cubic-bezier(0.16,1,0.3,1) !important;
    letter-spacing: 0.3px !important;
}}
.gr-button.primary, button.primary {{
    background: linear-gradient(135deg, {C['accent']} 0%, {C['accent_light']} 100%) !important;
    color: #fff !important;
    border: none !important;
    box-shadow: 0 4px 16px rgba(246,125,17,0.4) !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
}}
.gr-button.primary:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(246,125,17,0.55) !important;
    filter: brightness(1.07) !important;
}}
.gr-button.primary:active {{ transform: translateY(0) !important; }}
.gr-button.secondary {{
    background: transparent !important;
    color: {C['text_muted']} !important;
    border: 1.5px solid {C['border']} !important;
}}
.gr-button.secondary:hover {{
    border-color: {C['accent']} !important;
    color: {C['accent']} !important;
    background: {C['accent_glow']} !important;
    box-shadow: 0 0 12px {C['accent_glow']} !important;
}}
.btn-danger {{
    background: transparent !important;
    color: {C['red']} !important;
    border: 1.5px solid {C['red']} !important;
}}
.btn-danger:hover {{
    background: rgba(239,68,68,0.12) !important;
    box-shadow: 0 0 14px rgba(239,68,68,0.25) !important;
}}

/* ===== ANIMACIONES ===== */
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(18px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes fadeIn {{
    from {{ opacity: 0; }}
    to   {{ opacity: 1; }}
}}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50%       {{ opacity: 0.4; }}
}}
@keyframes glowPulse {{
    0%, 100% {{ box-shadow: 0 0 20px {C['accent_glow']}; }}
    50%       {{ box-shadow: 0 0 40px rgba(246,125,17,0.35); }}
}}
@keyframes slideInLeft {{
    from {{ opacity: 0; transform: translateX(-20px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
}}

.fade-up       {{ animation: fadeUp 0.45s cubic-bezier(0.16,1,0.3,1) forwards; }}
.fade-in       {{ animation: fadeIn 0.3s ease forwards; }}
.spin          {{ animation: spin 0.9s linear infinite; display: inline-block; }}
.pulse         {{ animation: pulse 1.2s ease infinite; }}
.glow-pulse    {{ animation: glowPulse 2s ease infinite; }}
.slide-in-left {{ animation: slideInLeft 0.35s cubic-bezier(0.16,1,0.3,1) forwards; }}

/* ===== NAVBAR ===== */
.mp-navbar {{
    background: linear-gradient(90deg, {C['surface']} 0%, #063A58 50%, {C['surface']} 100%);
    border-bottom: 1px solid {C['border']};
    padding: 0 28px;
    height: 62px;
    display: flex;
    align-items: center;
    gap: 16px;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 20px rgba(0,0,0,0.5);
}}
.mp-navbar-logo {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 20px;
    background: linear-gradient(135deg, {C['accent']} 0%, {C['accent_light']} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
    filter: drop-shadow(0 0 12px rgba(246,125,17,0.5));
}}
.mp-navbar-title {{
    font-weight: 600;
    font-size: 14px;
    color: {C['text_muted']};
    letter-spacing: 0.2px;
}}
.mp-navbar-badge {{
    background: linear-gradient(135deg, rgba(246,125,17,0.18), rgba(246,125,17,0.06));
    color: {C['accent']};
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2px;
    padding: 4px 11px;
    border-radius: 6px;
    border: 1px solid rgba(246,125,17,0.35);
    text-transform: uppercase;
    box-shadow: 0 0 10px rgba(246,125,17,0.15);
}}
.mp-navbar-spacer {{ flex: 1; }}
.mp-navbar-divider {{
    width: 1px;
    height: 26px;
    background: linear-gradient(to bottom, transparent, {C['border']}, transparent);
}}

/* ===== BADGE ===== */
.mp-badge {{
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    border: 1px solid currentColor;
    background: rgba(0,0,0,0.35);
    backdrop-filter: blur(6px);
}}
.mp-badge.sm {{ padding: 2px 8px; font-size: 10px; letter-spacing: 0.3px; }}

/* ===== METRIC CARDS ===== */
.metrics-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 14px;
    padding: 22px 24px 0;
}}
.mp-metric-card {{
    background: linear-gradient(145deg, {C['card']} 0%, {C['card2']} 100%);
    border: 1px solid {C['border']};
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    animation: fadeUp 0.5s cubic-bezier(0.16,1,0.3,1) forwards;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    position: relative;
    overflow: hidden;
    cursor: default;
}}
.mp-metric-card::after {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, {C['accent']}, transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
}}
.mp-metric-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.4), 0 0 0 1px rgba(246,125,17,0.15);
    border-color: {C['border_light']};
}}
.mp-metric-card:hover::after {{ opacity: 1; }}
.mp-metric-label {{
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.5px;
    color: {C['text_dim']};
    text-transform: uppercase;
    margin-bottom: 10px;
}}
.mp-metric-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 32px;
    font-weight: 700;
    line-height: 1;
    filter: drop-shadow(0 0 8px currentColor);
}}
.mp-metric-sub {{
    font-size: 11px;
    color: {C['text_dim']};
    margin-top: 7px;
    font-weight: 500;
}}

/* ===== KANBAN BOARD ===== */
.kanban-board {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 14px;
    padding: 18px 24px 28px;
    overflow-x: auto;
}}
.kanban-col {{
    background: linear-gradient(180deg, {C['surface']} 0%, rgba(4,48,75,0.7) 100%);
    border: 1px solid {C['border']};
    border-radius: 16px;
    padding: 14px;
    min-height: 340px;
    backdrop-filter: blur(8px);
    transition: border-color 0.2s ease;
}}
.kanban-col:hover {{ border-color: {C['border_light']}; }}
.kanban-col-header {{
    display: flex;
    align-items: center;
    gap: 9px;
    margin-bottom: 14px;
    padding-bottom: 12px;
    border-bottom: 1px solid {C['border']};
}}
.kanban-dot {{
    width: 9px;
    height: 9px;
    border-radius: 50%;
    flex-shrink: 0;
    filter: drop-shadow(0 0 5px currentColor);
}}
.kanban-col-name {{
    font-size: 12px;
    font-weight: 700;
    color: {C['text']};
    flex: 1;
    letter-spacing: 0.4px;
}}
.kanban-count {{
    background: rgba(255,255,255,0.07);
    color: {C['text_muted']};
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 10px;
    font-family: 'JetBrains Mono', monospace;
    border: 1px solid {C['border']};
}}

/* ===== PROSPECT CARD (Kanban) ===== */
.prospect-card {{
    background: linear-gradient(145deg, {C['card']} 0%, {C['card2']} 100%);
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 13px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.22s cubic-bezier(0.16,1,0.3,1);
    position: relative;
    overflow: hidden;
}}
.prospect-card::before {{
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(135deg, {C['accent']} 0%, {C['accent_light']} 100%);
    opacity: 0;
    transition: opacity 0.2s ease;
    border-radius: 3px 0 0 3px;
}}
.prospect-card:hover {{
    border-color: rgba(246,125,17,0.5);
    transform: translateY(-2px) translateX(3px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}}
.prospect-card:hover::before {{ opacity: 1; }}
.prospect-name {{
    font-size: 13px;
    font-weight: 700;
    color: {C['text']};
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 155px;
}}
.prospect-meta {{
    font-size: 11px;
    color: {C['text_muted']};
    margin-bottom: 8px;
    font-weight: 500;
}}

/* ===== EMPTY STATE ===== */
.empty-state {{
    text-align: center;
    padding: 48px 16px;
    color: {C['text_dim']};
}}
.empty-state-icon {{
    font-size: 36px;
    display: block;
    margin-bottom: 12px;
    opacity: 0.4;
    filter: grayscale(0.5);
}}
.empty-state-title {{
    font-size: 13px;
    font-weight: 600;
    color: {C['text_dim']};
    margin-bottom: 4px;
}}

/* ===== BATCH PROGRESS ===== */
.batch-bar {{
    background: linear-gradient(90deg, rgba(246,125,17,0.1), rgba(246,125,17,0.04));
    border: 1px solid rgba(246,125,17,0.3);
    border-radius: 12px;
    padding: 12px 20px;
    margin: 10px 24px;
    display: flex;
    align-items: center;
    gap: 14px;
    font-size: 12px;
    color: {C['text_muted']};
    animation: fadeIn 0.3s ease;
    box-shadow: 0 0 20px rgba(246,125,17,0.08);
}}
.batch-spinner {{
    width: 16px;
    height: 16px;
    border: 2px solid {C['border']};
    border-top-color: {C['accent']};
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    flex-shrink: 0;
    filter: drop-shadow(0 0 4px rgba(246,125,17,0.5));
}}
.batch-track {{
    flex: 1;
    height: 5px;
    background: {C['border']};
    border-radius: 3px;
    overflow: hidden;
}}
.batch-fill {{
    height: 100%;
    background: linear-gradient(90deg, {C['accent']}, {C['accent_light']});
    border-radius: 3px;
    transition: width 0.5s cubic-bezier(0.16,1,0.3,1);
    box-shadow: 0 0 8px rgba(246,125,17,0.6);
}}

/* ===== STEPPER ===== */
.mp-stepper {{
    background: linear-gradient(90deg, {C['surface']} 0%, {C['card']} 50%, {C['surface']} 100%);
    border-bottom: 1px solid {C['border']};
    padding: 14px 28px;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 14px rgba(0,0,0,0.35);
}}
.stepper-back-btn {{
    font-size: 12px;
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
.stepper-back-btn:hover {{ color: {C['accent']}; }}
.stepper-steps {{ display: flex; align-items: center; }}
.step-dot {{
    width: 30px;
    height: 30px;
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
    transition: all 0.3s cubic-bezier(0.16,1,0.3,1);
}}
.step-dot.done {{
    background: linear-gradient(135deg, {C['accent']}, {C['accent_light']});
    border: none;
    color: #fff;
    box-shadow: 0 0 14px rgba(246,125,17,0.5);
    font-size: 12px;
}}
.step-dot.active {{
    border-color: {C['accent']};
    color: {C['accent']};
    box-shadow: 0 0 0 4px {C['accent_glow']}, 0 0 16px rgba(246,125,17,0.3);
    background: rgba(246,125,17,0.1);
}}
.step-connector {{
    width: 36px;
    height: 2px;
    background: {C['border']};
    flex-shrink: 0;
    transition: all 0.4s ease;
}}
.step-connector.done {{
    background: linear-gradient(90deg, {C['accent']}, {C['accent_light']});
    box-shadow: 0 0 6px rgba(246,125,17,0.4);
}}

/* ===== INPUT STAGE ===== */
.source-panel {{
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin-top: 12px;
}}
.source-badge {{
    background: rgba(246,125,17,0.08);
    color: {C['accent']};
    border: 1px solid rgba(246,125,17,0.22);
    border-radius: 7px;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 11px;
    transition: all 0.15s ease;
}}
.source-badge:hover {{
    background: rgba(246,125,17,0.16);
    border-color: rgba(246,125,17,0.45);
    transform: translateY(-1px);
}}
.mode-pills {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 14px;
}}
.mode-pill {{
    background: {C['surface']};
    border: 1.5px solid {C['border']};
    border-radius: 9px;
    color: {C['text_muted']};
    font-size: 12px;
    font-weight: 600;
    padding: 8px 15px;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
}}
.mode-pill:hover, .mode-pill.active {{
    border-color: {C['accent']};
    color: {C['accent']};
    background: {C['accent_glow']};
    box-shadow: 0 0 14px {C['accent_glow']};
}}
.example-cards {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-top: 14px;
}}
.example-card {{
    background: linear-gradient(145deg, {C['card']} 0%, {C['card2']} 100%);
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 13px 15px;
    cursor: pointer;
    transition: all 0.22s cubic-bezier(0.16,1,0.3,1);
    font-size: 12px;
}}
.example-card:hover {{
    border-color: rgba(246,125,17,0.5);
    background: linear-gradient(145deg, {C['card2']} 0%, #144060 100%);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.35);
}}
.example-card-icon {{ margin-bottom: 5px; font-size: 17px; }}
.example-card-name {{ font-weight: 700; color: {C['text']}; margin-bottom: 2px; }}
.example-card-sub {{ color: {C['text_dim']}; font-size: 11px; font-weight: 500; }}

/* ===== RESEARCH STAGE ===== */
.research-steps-list {{
    display: flex;
    flex-direction: column;
    gap: 9px;
    padding: 6px 0;
}}
.research-step {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 15px;
    border-radius: 11px;
    border: 1px solid {C['border']};
    background: {C['surface']};
    font-size: 13px;
    color: {C['text_dim']};
    transition: all 0.35s cubic-bezier(0.16,1,0.3,1);
    font-weight: 500;
}}
.research-step.active {{
    border-color: {C['accent']};
    background: linear-gradient(90deg, rgba(246,125,17,0.14) 0%, rgba(246,125,17,0.04) 100%);
    color: {C['accent_light']};
    box-shadow: 0 2px 16px rgba(246,125,17,0.18), inset 0 0 0 1px rgba(246,125,17,0.12);
}}
.research-step.done {{
    border-color: rgba(246,125,17,0.22);
    color: {C['text_muted']};
    background: rgba(246,125,17,0.04);
}}
.step-indicator {{
    width: 20px;
    height: 20px;
    border-radius: 50%;
    border: 2px solid {C['border']};
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 9px;
    font-weight: 800;
    transition: all 0.3s ease;
}}
.step-indicator.active {{
    border-color: {C['accent']};
    border-right-color: transparent;
    animation: spin 0.9s linear infinite;
    box-shadow: 0 0 10px {C['accent_glow']};
}}
.step-indicator.done {{
    background: linear-gradient(135deg, {C['accent']}, {C['accent_light']});
    border: none;
    color: #fff;
    box-shadow: 0 0 10px rgba(246,125,17,0.45);
    font-size: 10px;
}}

/* ===== PROFILE HEADER ===== */
.profile-header-card {{
    background: linear-gradient(145deg, {C['card']} 0%, {C['card2']} 60%, rgba(246,125,17,0.05) 100%);
    border: 1px solid {C['accent']};
    border-radius: 18px;
    padding: 26px;
    box-shadow: 0 0 50px rgba(246,125,17,0.15), 0 10px 40px rgba(0,0,0,0.5);
    display: flex;
    gap: 24px;
    align-items: flex-start;
    animation: fadeUp 0.45s cubic-bezier(0.16,1,0.3,1);
    position: relative;
    overflow: hidden;
}}
.profile-header-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, {C['accent']}, {C['accent_light']}, {C['accent']});
    background-size: 200% 100%;
    animation: gradientShift 3s linear infinite;
}}
@keyframes gradientShift {{
    0%   {{ background-position: 0% 50%; }}
    100% {{ background-position: 200% 50%; }}
}}
.profile-info {{ flex: 1; min-width: 0; }}
.profile-badges {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }}
.profile-name {{
    font-size: 24px;
    font-weight: 800;
    color: {C['text']};
    margin-bottom: 10px;
    line-height: 1.2;
    letter-spacing: -0.4px;
}}
.profile-meta-row {{
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    font-size: 12px;
    color: {C['text_muted']};
    font-weight: 500;
}}
.profile-score-col {{ flex-shrink: 0; text-align: center; }}
.profile-score-label {{
    font-size: 10px;
    font-weight: 700;
    color: {C['text_dim']};
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 8px;
}}

/* ===== COMPETITOR CARD ===== */
.competitor-card {{
    background: linear-gradient(145deg, {C['card']} 0%, {C['card2']} 100%);
    border: 1px solid {C['border']};
    border-radius: 16px;
    padding: 20px;
    animation: fadeUp 0.45s cubic-bezier(0.16,1,0.3,1);
    position: relative;
    overflow: hidden;
}}
.competitor-header {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 16px;
}}
.competitor-icon-badge {{
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 16px;
    font-family: 'JetBrains Mono', monospace;
    flex-shrink: 0;
    box-shadow: 0 0 12px currentColor;
}}
.competitor-pains-angles {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid {C['border']};
}}
.pa-col-title {{
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 10px;
}}
.pa-item {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 12px;
    margin-bottom: 7px;
    line-height: 1.5;
    font-weight: 500;
}}

/* ===== DRAFT STAGE ===== */
.subject-option {{
    background: {C['surface']};
    border: 1.5px solid {C['border']};
    border-radius: 11px;
    padding: 12px 16px;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-bottom: 8px;
    color: {C['text']};
    font-weight: 500;
}}
.subject-option:hover {{
    border-color: {C['border_light']};
    background: {C['card']};
}}
.subject-option.selected {{
    border-color: {C['accent']};
    background: linear-gradient(90deg, rgba(246,125,17,0.14) 0%, rgba(246,125,17,0.04) 100%);
    color: {C['accent_light']};
    box-shadow: 0 0 18px {C['accent_glow']};
}}
.approved-badge {{
    background: linear-gradient(135deg, rgba(246,125,17,0.22), rgba(246,125,17,0.08));
    color: {C['accent']};
    border: 1px solid rgba(246,125,17,0.45);
    border-radius: 7px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.5px;
    padding: 5px 12px;
    display: inline-block;
    text-transform: uppercase;
    box-shadow: 0 0 14px rgba(246,125,17,0.25);
}}
.hook-item {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    font-size: 12px;
    color: {C['text_muted']};
    margin-bottom: 8px;
    line-height: 1.6;
    font-weight: 500;
    padding: 5px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}}
.hook-item:last-child {{ border-bottom: none; }}

/* ===== SUBJECT RADIO — styled as clickable cards ===== */
.subject-radio {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    gap: 0 !important;
}}
.subject-radio > .wrap,
.subject-radio fieldset,
.subject-radio .wrap {{
    display: flex !important;
    flex-direction: column !important;
    gap: 0 !important;
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}}
.subject-radio legend,
.subject-radio > label:first-of-type {{
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    color: {C['text_dim']} !important;
    text-transform: uppercase !important;
    margin-bottom: 8px !important;
    display: block !important;
}}
.subject-radio label {{
    display: block !important;
    background: {C['surface']} !important;
    border: 1.5px solid {C['border']} !important;
    border-radius: 11px !important;
    padding: 12px 16px !important;
    font-size: 13px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    margin-bottom: 8px !important;
    color: {C['text']} !important;
    font-weight: 500 !important;
    line-height: 1.4 !important;
}}
.subject-radio label:hover {{
    border-color: {C['border_light']} !important;
    background: {C['card']} !important;
}}
.subject-radio label:has(input:checked),
.subject-radio input[type="radio"]:checked + span {{
    color: {C['accent_light']} !important;
}}
.subject-radio label:has(input:checked) {{
    border-color: {C['accent']} !important;
    background: linear-gradient(90deg, rgba(246,125,17,0.14) 0%, rgba(246,125,17,0.04) 100%) !important;
    color: {C['accent_light']} !important;
    box-shadow: 0 0 18px {C['accent_glow']} !important;
}}
.subject-radio input[type="radio"] {{
    display: none !important;
}}
.subject-radio span {{
    color: inherit !important;
}}

/* ===== KANBAN DRAG & DROP ===== */
.prospect-card[draggable="true"] {{
    cursor: grab;
    transition: opacity 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
    user-select: none;
}}
.prospect-card[draggable="true"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.35), 0 0 0 1px {C['border_light']};
}}
.prospect-card.dragging {{
    opacity: 0.42;
    transform: scale(0.96);
    cursor: grabbing;
}}
.kanban-col {{
    transition: background 0.18s ease;
}}
.kanban-col.drag-over {{
    background: rgba(246,125,17,0.07) !important;
    outline: 2px dashed rgba(246,125,17,0.5);
    outline-offset: -4px;
    border-radius: 16px;
}}

/* ===== BATCH MODAL ===== */
.batch-modal {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 18px;
    padding: 28px;
    margin: 16px 0;
    animation: fadeUp 0.3s ease;
}}
.batch-modal-title {{
    font-size: 16px;
    font-weight: 800;
    color: {C['text']};
    margin-bottom: 6px;
}}
.batch-modal-sub {{
    font-size: 13px;
    color: {C['text_muted']};
    margin-bottom: 20px;
    font-weight: 500;
}}
.csv-preview-card {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 14px;
    max-height: 260px;
    overflow-y: auto;
}}
.csv-preview-title {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: {C['accent']};
    margin-bottom: 10px;
    display: flex;
    gap: 8px;
    align-items: center;
}}
.csv-preview-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 13px;
    color: {C['text_muted']};
}}
.csv-preview-row:last-child {{ border-bottom: none; }}
.csv-preview-num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: {C['text_dim']};
    min-width: 22px;
    font-weight: 700;
}}
.csv-preview-more {{
    font-size: 12px;
    color: {C['text_dim']};
    padding: 8px 0;
    font-style: italic;
}}

/* ===== PROSPECT MANAGER (kanban move) ===== */
.prospect-manager {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 14px;
    padding: 18px 20px;
    margin-top: 16px;
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
}}
.prospect-manager-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: {C['text_dim']};
    white-space: nowrap;
}}

/* ===== APPROVED MODE ===== */
.approved-mode-notice {{
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(90deg, rgba(246,125,17,0.12) 0%, rgba(246,125,17,0.04) 100%);
    border: 1px solid rgba(246,125,17,0.35);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 14px;
    font-size: 13px;
    font-weight: 600;
    color: {C['accent_light']};
}}

/* ===== SEND STAGE ===== */
.send-result {{
    text-align: center;
    padding: 48px 40px;
    border-radius: 18px;
    animation: fadeUp 0.45s cubic-bezier(0.16,1,0.3,1);
}}
.send-result-icon {{ font-size: 56px; display: block; margin-bottom: 18px; }}
.send-result-title {{
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 10px;
    letter-spacing: -0.3px;
}}
.send-result-sub {{
    font-size: 14px;
    color: {C['text_muted']};
    font-weight: 500;
    line-height: 1.6;
}}

/* ===== INSIGHT CARDS ===== */
.insight-card {{
    background: linear-gradient(145deg, {C['card']} 0%, {C['card2']} 100%);
    border: 1px solid {C['border']};
    border-radius: 14px;
    padding: 16px;
    transition: all 0.2s ease;
}}
.insight-card:hover {{
    border-color: {C['border_light']};
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.3);
}}
.insight-card-title {{
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 7px;
}}
.insight-item {{
    font-size: 12px;
    color: {C['text_muted']};
    padding: 7px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    line-height: 1.6;
    font-weight: 500;
}}
.insight-item:last-child {{ border-bottom: none; }}

/* ===== MP-CARD genérico ===== */
.mp-card {{
    background: linear-gradient(145deg, {C['card']} 0%, {C['card2']} 100%);
    border: 1px solid {C['border']};
    border-radius: 16px;
    padding: 22px;
    animation: fadeUp 0.4s cubic-bezier(0.16,1,0.3,1);
}}
.mp-card.glow {{
    border-color: {C['accent']};
    box-shadow: 0 0 36px {C['accent_glow']};
}}

/* ===== PIPELINE BOARD HEADER ===== */
.pipeline-header {{
    padding: 14px 24px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
.pipeline-title {{
    font-size: 11px;
    font-weight: 800;
    color: {C['text_dim']};
    text-transform: uppercase;
    letter-spacing: 2px;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.pipeline-title::before {{
    content: '';
    width: 4px;
    height: 14px;
    background: linear-gradient(135deg, {C['accent']}, {C['accent_light']});
    border-radius: 2px;
}}
"""


# ──────────────────────────────────────────────
#  HTML Builder Functions
# ──────────────────────────────────────────────

def navbar_html(show_badge: bool = True) -> str:
    badge = '<span class="mp-navbar-badge">PIPELINE</span>' if show_badge else ''
    return f"""
<div class="mp-navbar">
    <span class="mp-navbar-logo">MacPractice</span>
    <div class="mp-navbar-divider"></div>
    <span class="mp-navbar-title">Dental Prospector</span>
    {badge}
    <span class="mp-navbar-spacer"></span>
</div>
"""


def badge_html(text: str, color: str, small: bool = False) -> str:
    cls = "mp-badge sm" if small else "mp-badge"
    return (
        f'<span class="{cls}" style="color:{color}; border-color:{color}; '
        f'box-shadow: 0 0 8px rgba(0,0,0,0.2);">{text}</span>'
    )


def metric_card_html(label: str, value: str, sub: str = "", color: str = None) -> str:
    val_color = color or C["text"]
    sub_html  = f'<div class="mp-metric-sub">{sub}</div>' if sub else ''
    return f"""
<div class="mp-metric-card">
    <div class="mp-metric-label">{label}</div>
    <div class="mp-metric-value" style="color:{val_color}">{value}</div>
    {sub_html}
</div>
"""


def score_ring_svg(score, size: int = 88) -> str:
    score_val = score if score is not None else 0
    radius    = (size - 10) / 2
    circ      = 2 * 3.14159265 * radius
    progress  = (score_val / 10) * circ if score_val else 0

    if score_val >= 8:
        color = C["accent"]
        glow  = "rgba(246,125,17,0.5)"
    elif score_val >= 5:
        color = C["amber"]
        glow  = "rgba(245,158,11,0.5)"
    else:
        color = C["red"]
        glow  = "rgba(239,68,68,0.5)"

    cx = cy   = size / 2
    font_size = max(size // 4, 10)
    display   = str(score_val) if score else "—"

    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
        f'style="display:block;filter:drop-shadow(0 0 8px {glow});">'
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{C["border"]}" stroke-width="6"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{color}" stroke-width="6" '
        f'stroke-dasharray="{progress:.1f} {circ:.1f}" stroke-linecap="round" '
        f'transform="rotate(-90 {cx} {cy})"/>'
        f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
        f'fill="{color}" font-family="JetBrains Mono,monospace" '
        f'font-size="{font_size}" font-weight="700">{display}</text>'
        f'</svg>'
    )


def stepper_html(current_stage: str) -> str:
    stage_index = {
        "input": 0, "research": 1, "profile": 2,
        "draft_loading": 3, "draft": 3, "send": 5,
    }
    active_idx = stage_index.get(current_stage, 0)
    labels = ["1", "2", "3", "4", "5", "6"]
    step_names = ["Input", "Research", "Profile", "Draft", "Review", "Send"]

    dots = ""
    for i, (label, name) in enumerate(zip(labels, step_names)):
        if i < active_idx:
            cls, content = "done", "✓"
        elif i == active_idx:
            cls, content = "active", label
        else:
            cls, content = "", label

        dots += f'<div class="step-dot {cls}" title="{name}">{content}</div>'
        if i < len(labels) - 1:
            conn_cls = "done" if i < active_idx else ""
            dots += f'<div class="step-connector {conn_cls}"></div>'

    return f"""
<div class="mp-stepper">
    <button class="stepper-back-btn">← Pipeline</button>
    <div class="stepper-steps">{dots}</div>
</div>
"""
