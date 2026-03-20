# ui/components/batch_modal.py
# Bulk Research modal — multi-clinic CSV import for automated research.

import gradio as gr
from ui.theme import C
from app.services.csv_service import parse_csv


# Pre-loaded example CSV
_EXAMPLE_CSV = """clinic_name,location
"Smiles of Bellevue","Bellevue, WA"
"Downtown Dental","Seattle, WA"
"Evergreen Care","Redmond, WA"
"""


def _csv_preview_html(items) -> str:
    """Renders preview cards for detected clinics."""
    if not items:
        return ""

    count = len(items)
    rows_html = "".join(
        f"""<div style="display:flex; align-items:center; gap:10px;
                       padding:8px 12px; border-radius:8px; margin-bottom:4px;
                       background:rgba(16,185,129,0.06); border:1px solid rgba(16,185,129,0.15);">
            <span style="font-size:12px; font-weight:700; color:{C['accent']};
                         min-width:22px; text-align:right;">{i + 1}</span>
            <span style="font-size:13px; color:{C['text']}; font-weight:500;">{item['input']}</span>
        </div>"""
        for i, item in enumerate(items[:20])
    )

    remaining = count - 20
    more_html = (
        f'<div style="text-align:center; font-size:12px; color:{C["text_dim"]}; '
        f'padding:6px 0; font-style:italic;">... and {remaining} more</div>'
        if remaining > 0 else ""
    )

    return f"""
<div style="background:{C['card']}; border:1px solid {C['border']}; border-radius:12px;
            padding:16px; margin-top:8px;">
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
        <span style="font-size:16px;">✅</span>
        <span style="font-size:13px; font-weight:700; color:{C['accent']};">
            {count} clinic{'s' if count != 1 else ''} ready to research
        </span>
    </div>
    {rows_html}
    {more_html}
</div>
"""


def build_batch_section() -> tuple:
    """
    Creates the Bulk Research modal.
    Returns: (batch_group, btn_close, btn_confirm, parsed_state, batch_log_box)
    """
    try:
        initial_items = parse_csv(_EXAMPLE_CSV)
    except Exception:
        initial_items = []

    parsed_state = gr.State(None)

    with gr.Group(visible=False) as batch_group:

        gr.HTML(f"""
<div style="background:linear-gradient(135deg, {C['surface']} 0%, {C['card']} 100%);
            border:1px solid {C['border']}; border-radius:16px; padding:24px 28px 20px;">
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
        <span style="font-size:28px;">🚀</span>
        <div>
            <div style="font-size:18px; font-weight:800; color:{C['text']};">
                Bulk Research
            </div>
            <div style="font-size:13px; color:{C['text_muted']}; margin-top:2px;">
                Research dozens of clinics automatically with AI
            </div>
        </div>
    </div>
    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:10px;">
        <span style="background:rgba(16,185,129,0.12); color:{C['accent']}; font-size:11px;
                     font-weight:700; padding:3px 10px; border-radius:20px;">✓ CSV / TSV</span>
        <span style="background:rgba(99,102,241,0.12); color:{C['purple']}; font-size:11px;
                     font-weight:700; padding:3px 10px; border-radius:20px;">✓ No headers needed</span>
        <span style="background:rgba(245,158,11,0.12); color:{C['amber']}; font-size:11px;
                     font-weight:700; padding:3px 10px; border-radius:20px;">✓ Free-form text</span>
        <span style="background:rgba(59,130,246,0.12); color:{C['blue']}; font-size:11px;
                     font-weight:700; padding:3px 10px; border-radius:20px;">✓ File upload</span>
    </div>
</div>
""")

        with gr.Tabs(elem_classes=["bulk-tabs"]):

            # ── Tab 1: Paste text ────────────────────────────────
            with gr.Tab("✏️ Paste Text"):
                gr.HTML(f"""
<div style="font-size:12px; color:{C['text_dim']}; padding:8px 0 4px;">
    Paste your clinic list. Accepts CSV with or without headers,
    plain text (one per line), TSV, or any comma-separated format.
</div>""")
                csv_text = gr.Textbox(
                    label="",
                    lines=9,
                    value=_EXAMPLE_CSV,
                    placeholder="One clinic per line, or CSV format:\nSmith Dental, New York\nSunset Smiles, Los Angeles CA\n...",
                    elem_classes=["bulk-textarea"],
                )

            # ── Tab 2: Upload file ───────────────────────────────
            with gr.Tab("📁 Upload File"):
                gr.HTML(f"""
<div style="font-size:12px; color:{C['text_dim']}; padding:8px 0 4px;">
    Upload a .csv, .tsv, or .txt file. Format is detected automatically.
</div>""")
                csv_file = gr.File(
                    label="Select or drag your file",
                    file_types=[".csv", ".tsv", ".txt"],
                    file_count="single",
                )

        # Clinic preview
        preview_display = gr.HTML(
            value=_csv_preview_html(initial_items) if initial_items else ""
        )

        with gr.Row():
            btn_close = gr.Button(
                "✕ Cancel",
                variant="secondary",
                elem_classes=["gr-button", "secondary"],
                scale=1,
            )
            btn_confirm = gr.Button(
                f"🚀 Research {len(initial_items)} clinic{'s' if len(initial_items) != 1 else ''}"
                if initial_items else "🚀 Research All",
                variant="primary",
                elem_classes=["gr-button", "primary"],
                interactive=bool(initial_items),
                scale=2,
            )

        batch_log_box = gr.Textbox(
            value="",
            label="Bulk Research Log",
            lines=7,
            interactive=False,
            visible=False,
            elem_classes=["terminal-log"],
        )

    # ── Events ─────────────────────────────────────────────────

    def _refresh_preview(text: str):
        if not text or not text.strip():
            return "", [], gr.update(interactive=False, value="🚀 Research All")
        items = parse_csv(text)
        if not items:
            return (
                f'<div style="color:{C["text_dim"]}; font-size:13px; padding:8px 0;">'
                f'No clinics detected. Try a different format.</div>',
                [],
                gr.update(interactive=False, value="🚀 Research All"),
            )
        label = f"🚀 Research {len(items)} clinic{'s' if len(items) != 1 else ''}"
        return _csv_preview_html(items), items, gr.update(interactive=True, value=label)

    def _on_file_upload(file):
        if file is None:
            return "", [], gr.update(interactive=False, value="🚀 Research All")
        try:
            with open(file, "r", encoding="utf-8-sig", errors="replace") as f:
                text = f.read()
            return _refresh_preview(text)
        except Exception as e:
            return (
                f'<div style="color:{C["red"]}; font-size:13px; padding:8px 0;">⚠ Error reading file: {str(e)[:80]}</div>',
                [],
                gr.update(interactive=False, value="🚀 Research All"),
            )

    csv_text.change(
        fn=_refresh_preview,
        inputs=[csv_text],
        outputs=[preview_display, parsed_state, btn_confirm],
    )

    csv_file.change(
        fn=_on_file_upload,
        inputs=[csv_file],
        outputs=[preview_display, parsed_state, btn_confirm],
    )

    return batch_group, btn_close, btn_confirm, parsed_state, batch_log_box
