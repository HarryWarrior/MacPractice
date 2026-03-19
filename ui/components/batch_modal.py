# ui/components/batch_modal.py
# Batch Import modal — CSV upload, preview, y trigger de batch research.
# FASE 4: CSV import de múltiples clínicas para investigación automática.

import gradio as gr
from ui.theme import C
from app.services.csv_service import parse_csv


# ──────────────────────────────────────────────
#  HTML builders
# ──────────────────────────────────────────────

def _csv_preview_html(items: list) -> str:
    """Renderiza la tabla de preview de clínicas detectadas del CSV."""
    if not items:
        return ""

    rows_html = "".join(
        f'<div class="csv-preview-row">'
        f'<span class="csv-preview-num">{i + 1}</span>'
        f'<span>{item["input"]}</span>'
        f'</div>'
        for i, item in enumerate(items[:15])
    )
    remaining = len(items) - 15
    if remaining > 0:
        rows_html += (
            f'<div class="csv-preview-more">... and {remaining} more clinic(s)</div>'
        )

    return f"""
<div class="csv-preview-card">
    <div class="csv-preview-title">
        <span>📋</span>
        <span>{len(items)} clinic{'s' if len(items) != 1 else ''} detected</span>
    </div>
    {rows_html}
</div>
"""


# ──────────────────────────────────────────────
#  build_batch_section — componentes Gradio
# ──────────────────────────────────────────────

def build_batch_section() -> tuple:
    """
    Crea el modal de batch import CSV.
    Debe llamarse dentro de un gr.Blocks() activo.

    Returns:
        batch_group     : gr.Group — el modal (toggle visible=True para abrir)
        btn_close       : gr.Button — "Cancel"
        btn_confirm     : gr.Button — "Research All"
        parsed_state    : gr.State — list[dict] de items parseados
        batch_log_box   : gr.Textbox — log del batch research (terminal log)
    """
    parsed_state = gr.State([])

    with gr.Group(visible=False) as batch_group:
        gr.HTML(f"""
<div class="batch-modal">
    <div class="batch-modal-title">📂 Batch Import CSV</div>
    <div class="batch-modal-sub">
        Upload a CSV with clinic names and locations. We'll research each one automatically.
        <br>Expected columns: <code>name</code> + <code>location</code> (or <code>city</code>)
    </div>
</div>
""")

        csv_file = gr.File(
            label="Upload CSV / TSV",
            file_types=[".csv", ".tsv", ".txt"],
            file_count="single",
        )
        preview_display = gr.HTML(value="")

        with gr.Row():
            btn_close = gr.Button(
                "✕ Cancel",
                variant="secondary",
                elem_classes=["gr-button", "secondary"],
                scale=1,
            )
            btn_confirm = gr.Button(
                "🚀 Research All",
                variant="primary",
                elem_classes=["gr-button", "primary"],
                interactive=False,
                scale=2,
            )

        batch_log_box = gr.Textbox(
            value="",
            label="Batch Research Log",
            lines=7,
            interactive=False,
            visible=False,
            elem_classes=["terminal-log"],
        )

    # ── Events internos ─────────────────────────────────────

    def _on_file_upload(file):
        if file is None:
            return "", [], gr.update(interactive=False, value="🚀 Research All")
        try:
            with open(file, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            items = parse_csv(text)
            label = f"🚀 Research {len(items)} Clinic{'s' if len(items) != 1 else ''}"
            return _csv_preview_html(items), items, gr.update(interactive=True, value=label)
        except ValueError as e:
            err_html = (
                f'<div style="color:{C["red"]}; background:{C["card"]}; border:1px solid {C["red"]}; '
                f'border-radius:10px; padding:12px 16px; font-size:13px;">'
                f'⚠ {e}</div>'
            )
            return err_html, [], gr.update(interactive=False, value="🚀 Research All")

    csv_file.change(
        fn=_on_file_upload,
        inputs=[csv_file],
        outputs=[preview_display, parsed_state, btn_confirm],
    )

    return batch_group, btn_close, btn_confirm, parsed_state, batch_log_box
