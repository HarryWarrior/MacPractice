# ui/views/batch_review_view.py
# Batch Review Queue — generates & reviews outreach drafts for bulk-researched prospects.
# After bulk research completes, each prospect gets an outreach draft generated automatically.
# User can approve (marks as outreach_sent) or skip each one.

import html as _html
import urllib.parse
import gradio as gr

from ui.theme import C
from ui.views.workflow_view import _profile_html
from app.services.outreach_service import do_outreach
from app.services.email_service import send_real_email
from app.services.storage_service import storage
from app.models.prospect import Prospect


# ── HTML helpers ──────────────────────────────────────────────────────────────

def _progress_html(idx: int, total: int) -> str:
    pct = int((idx / total) * 100) if total else 0
    return f"""
<div style="background:{C['card']}; border:1px solid {C['border']}; border-radius:12px;
            padding:14px 18px; margin-bottom:12px;">
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
        <span style="font-size:14px; font-weight:700; color:{C['text']};">
            📋 Reviewing <span style="color:{C['accent']};">{idx}</span> of
            <span style="color:{C['accent']};">{total}</span>
        </span>
        <span style="font-size:12px; color:{C['text_dim']};">{pct}% complete</span>
    </div>
    <div style="height:6px; background:{C['surface']}; border-radius:3px; overflow:hidden;">
        <div style="height:100%; width:{pct}%; background:linear-gradient(90deg, {C['accent']}, {C['purple']});
                    border-radius:3px; transition:width 0.3s;"></div>
    </div>
</div>"""


def _done_html(total: int) -> str:
    return f"""
<div style="text-align:center; padding:40px 20px;">
    <div style="font-size:48px; margin-bottom:16px;">🎉</div>
    <div style="font-size:20px; font-weight:800; color:{C['accent']}; margin-bottom:8px;">
        Batch Review Complete!
    </div>
    <div style="font-size:14px; color:{C['text_dim']};">
        {total} prospect{'s' if total != 1 else ''} reviewed and added to your pipeline.
    </div>
</div>"""


def _prospect_summary_html(p: dict) -> str:
    name     = p.get("clinic_name") or p.get("input", "Unknown")
    location = p.get("location", "")
    score    = p.get("fit_score") or "—"
    priority = (p.get("priority") or "warm").upper()
    software = p.get("current_software") or "Unknown"

    priority_colors = {"HOT": C.get("red", "#ef4444"), "WARM": C.get("amber", "#f59e0b"), "COOL": C.get("blue", "#3b82f6"), "COLD": C.get("blue", "#3b82f6")}
    pcolor = priority_colors.get(priority, C["text_dim"])

    return f"""
<div style="background:{C['card']}; border:1px solid {C['border']}; border-radius:12px;
            padding:14px 18px; margin-bottom:12px; display:flex; align-items:center; gap:16px;">
    <div style="flex:1;">
        <div style="font-size:16px; font-weight:800; color:{C['text']};">{_html.escape(name)}</div>
        <div style="font-size:13px; color:{C['text_dim']}; margin-top:2px;">
            📍 {_html.escape(location)} &nbsp;·&nbsp; 💻 {_html.escape(software)}
        </div>
    </div>
    <div style="text-align:center;">
        <div style="font-size:22px; font-weight:900; color:{C['accent']};">{score}</div>
        <div style="font-size:10px; color:{C['text_dim']};">FIT SCORE</div>
    </div>
    <div style="background:rgba(0,0,0,0.2); border-radius:8px; padding:4px 10px;">
        <span style="font-size:11px; font-weight:800; color:{pcolor};">{priority}</span>
    </div>
</div>"""


def _send_status_html(sent: bool, recipient: str, error: str = "") -> str:
    if sent:
        return (
            f'<div style="background:rgba(16,185,129,0.12); border:1px solid {C["accent"]}; '
            f'border-radius:10px; padding:10px 14px; font-size:13px; color:{C["accent"]}; font-weight:600;">'
            f'✅ Email sent to <strong>{_html.escape(recipient)}</strong></div>'
        )
    return (
        f'<div style="background:rgba(245,158,11,0.1); border:1px solid {C["amber"]}; '
        f'border-radius:10px; padding:10px 14px; font-size:13px; color:{C["amber"]};">'
        f'⚠ Send failed — email saved. {_html.escape(error[:120])}</div>'
    )


def _wa_li_html(draft: dict, phone_override: str = "") -> str:
    """WhatsApp + LinkedIn links from draft."""
    if not draft:
        return ""
    wa_msg  = draft.get("whatsapp_message", "")
    li_msg  = draft.get("linkedin_message", "")
    phone   = phone_override or draft.get("_phone", "")
    if not wa_msg and not li_msg:
        return ""

    phone_clean = "".join(c for c in phone if c.isdigit() or c == "+")

    wa_html = ""
    if wa_msg:
        wa_escaped = _html.escape(wa_msg)
        if phone_clean:
            wa_url = f"https://wa.me/{phone_clean}?text={urllib.parse.quote(wa_msg)}"
            wa_btn = (
                f'<a href="{wa_url}" target="_blank" rel="noopener noreferrer" '
                f'style="display:inline-flex; align-items:center; gap:8px; '
                f'background:#25D366; color:#fff; font-size:12px; font-weight:700; '
                f'padding:8px 14px; border-radius:8px; text-decoration:none; margin-bottom:8px;">'
                f'💬 Open in WhatsApp</a>'
            )
        else:
            wa_btn = '<div style="font-size:11px; color:#f59e0b; margin-bottom:6px;">⚠ No phone — copy message below</div>'
        wa_html = f"""
<div style="background:{C['card']}; border:1px solid {C['border']}; border-radius:10px; padding:12px; margin-bottom:10px;">
    <div style="font-size:11px; font-weight:700; color:#25D366; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">💬 WhatsApp</div>
    {wa_btn}
    <div style="font-size:12px; color:{C['text_dim']}; white-space:pre-wrap; line-height:1.5;
                background:{C['surface']}; padding:8px; border-radius:6px; margin-top:4px;">{wa_escaped}</div>
</div>"""

    li_html = ""
    if li_msg:
        li_escaped = _html.escape(li_msg)
        li_html = f"""
<div style="background:{C['card']}; border:1px solid {C['border']}; border-radius:10px; padding:12px;">
    <div style="font-size:11px; font-weight:700; color:#0A66C2; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">💼 LinkedIn DM</div>
    <div style="font-size:12px; color:{C['text_dim']}; white-space:pre-wrap; line-height:1.5;
                background:{C['surface']}; padding:8px; border-radius:6px;">{li_escaped}</div>
</div>"""

    return wa_html + li_html


# ── Main builder ──────────────────────────────────────────────────────────────

def build_batch_review(prospects_state):
    """
    Creates the Batch Review panel (initially hidden).
    Returns: (batch_review_group, batch_queue_state, btn_finish_review)
    """
    batch_queue_state = gr.State([])
    batch_idx_state   = gr.State(0)
    batch_draft_state = gr.State(None)

    with gr.Group(visible=False) as batch_review_group:

        gr.HTML(f"""
<div style="background:linear-gradient(135deg, {C['surface']} 0%, {C['card']} 100%);
            border:1px solid {C['border']}; border-radius:16px; padding:20px 24px 16px;
            margin-bottom:16px;">
    <div style="display:flex; align-items:center; gap:12px;">
        <span style="font-size:28px;">✉️</span>
        <div>
            <div style="font-size:18px; font-weight:800; color:{C['text']};">Batch Outreach Review</div>
            <div style="font-size:13px; color:{C['text_muted']}; margin-top:2px;">
                AI-generated drafts for each researched prospect — approve or skip
            </div>
        </div>
    </div>
</div>""")

        progress_html_display   = gr.HTML(value="")
        prospect_summary_display = gr.HTML(value="")

        # ── Live generation log ──────────────────────────────
        gen_log = gr.Textbox(
            label="",
            lines=4,
            interactive=False,
            visible=False,
            elem_classes=["terminal-log"],
        )

        # ── Draft area (shown after generation) ─────────────
        with gr.Group(visible=False) as draft_area_group:
            with gr.Row():
                # Left: email content
                with gr.Column(scale=2):
                    subject_radio = gr.Radio(
                        label="📌 Subject line",
                        choices=[],
                        value=None,
                        interactive=True,
                    )
                    draft_body_input = gr.Textbox(
                        label="📝 Email body",
                        lines=14,
                        interactive=True,
                        elem_classes=["mp-input"],
                    )

                # Right: actions
                with gr.Column(scale=1):
                    wa_phone_input = gr.Textbox(
                        label="📱 WhatsApp number",
                        placeholder="+1 (555) 123-4567",
                        lines=1,
                        elem_classes=["mp-input"],
                    )
                    recipient_input = gr.Textbox(
                        label="📧 To (MVP: use your personal email)",
                        placeholder="your_email@gmail.com",
                        lines=1,
                        elem_classes=["mp-input"],
                    )
                    wa_li_display = gr.HTML(value="")

                    send_status_display = gr.HTML(value="")

                    gr.HTML(f'<div style="height:8px;"></div>')

                    with gr.Row():
                        btn_skip = gr.Button(
                            "⏭ Skip",
                            variant="secondary",
                            elem_classes=["gr-button", "secondary"],
                        )
                        btn_approve = gr.Button(
                            "✅ Approve & Send",
                            variant="primary",
                            elem_classes=["gr-button", "primary"],
                        )

        # ── Done state ───────────────────────────────────────
        with gr.Group(visible=False) as done_group:
            done_html_display = gr.HTML(value="")
            btn_finish_review = gr.Button(
                "← Back to Pipeline",
                variant="primary",
                elem_classes=["gr-button", "primary"],
            )

    # ── Event helpers ────────────────────────────────────────────────────────

    _GEN_OUTPUTS = [
        progress_html_display,
        prospect_summary_display,
        gen_log,
        draft_area_group,
        done_group,
        done_html_display,
        subject_radio,
        draft_body_input,
        batch_draft_state,
        wa_li_display,
        wa_phone_input,
        send_status_display,
    ]

    def _gen_draft(queue, idx):
        """Generator: streams outreach generation for prospect at queue[idx]."""
        if not queue or idx >= len(queue):
            total = len(queue) if queue else 0
            yield (
                gr.update(value=""),   # clear progress
                gr.update(value=""),   # clear profile
                gr.update(visible=False, value=""),
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(value=_done_html(total)),
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(value=""),
                gr.update(value=""),
                gr.update(value=""),
            )
            return

        total         = len(queue)
        prospect_dict = queue[idx]
        prospect      = Prospect.from_dict(prospect_dict)
        profile       = _profile_html(prospect_dict)

        # Show prospect profile + loading state
        yield (
            gr.update(value=_progress_html(idx + 1, total)),
            gr.update(value=profile),
            gr.update(visible=True, value=f"Generating outreach for {prospect.clinic_name}..."),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(),
            gr.update(choices=[], value=None),
            gr.update(value=""),
            gr.update(value=None),
            gr.update(value=""),
            gr.update(value=""),
            gr.update(value=""),
        )

        # Stream outreach generation — profile stays visible
        draft_data = None
        for log_text, draft in do_outreach(prospect):
            if draft is not None:
                draft_data = draft
            yield (
                gr.update(),
                gr.update(),           # keep profile unchanged
                gr.update(value=log_text),
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(value=draft_data),
                gr.update(),
                gr.update(),
                gr.update(),
            )

        # Show draft — profile stays visible above
        if draft_data:
            subjects      = draft_data.get("subject_options", [])
            first_subject = subjects[0] if subjects else ""
            body          = draft_data.get("body", "")
            phone         = draft_data.get("_phone", "")
            yield (
                gr.update(),
                gr.update(),           # keep profile
                gr.update(visible=False, value=""),
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(),
                gr.update(choices=subjects, value=first_subject),
                gr.update(value=body),
                gr.update(value=draft_data),
                gr.update(value=_wa_li_html(draft_data)),
                gr.update(value=phone),
                gr.update(value=""),
            )
        else:
            # Fallback: skip to next
            yield (
                gr.update(),
                gr.update(),
                gr.update(visible=False, value=""),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(value=None),
                gr.update(value=""),
                gr.update(value=""),
                gr.update(value=""),
            )

    def _approve_and_send(queue, idx, draft, subject, body, recipient, prospects):
        """
        Generator: sends email, updates pipeline stage, advances index.
        Outputs: (prospects_state, batch_idx_state, send_status_display)
        """
        recipient = (recipient or "").strip()

        # ── Update pipeline stage ──────────────────────────────
        if draft and queue and idx < len(queue):
            prospect_dict = queue[idx]
            pid = prospect_dict.get("id", "")
            updated_prospects = []
            for p in (prospects or []):
                if p.get("id") == pid:
                    p = dict(p)
                    p["pipeline_stage"] = "outreach_sent"
                    p["outreach_subject"] = subject or ""
                    storage.update_prospect(pid, p)
                updated_prospects.append(p)
            new_idx = idx + 1
        else:
            updated_prospects = list(prospects or [])
            new_idx = idx + 1

        # ── Send email if recipient provided ───────────────────
        if recipient:
            yield updated_prospects, new_idx, gr.update(value="<div style='font-size:13px; color:#94a3b8;'>📤 Sending email...</div>")
            email_result = None
            for _, result in send_real_email(
                recipient=recipient,
                subject=subject or "(no subject)",
                body=body or "",
                sender_name="Mac Practice Sales",
            ):
                if result is not None:
                    email_result = result

            if email_result:
                status_html = _send_status_html(
                    email_result.sent,
                    recipient,
                    email_result.error,
                )
            else:
                status_html = _send_status_html(False, recipient, "No response from email service.")

            yield updated_prospects, new_idx, gr.update(value=status_html)
        else:
            yield updated_prospects, new_idx, gr.update(
                value='<div style="font-size:12px; color:#94a3b8; padding:6px 0;">ℹ No recipient set — email not sent.</div>'
            )

    def _skip(idx):
        return idx + 1

    def _update_wa_phone(phone, draft):
        if not draft:
            return gr.update()
        return _wa_li_html(draft, phone_override=phone)

    # ── Wire events ──────────────────────────────────────────────────────────

    # When queue is loaded: reset index + show section, then gen first draft
    batch_queue_state.change(
        fn=lambda q: (0, gr.update(visible=bool(q))),
        inputs=[batch_queue_state],
        outputs=[batch_idx_state, batch_review_group],
    ).then(
        fn=_gen_draft,
        inputs=[batch_queue_state, batch_idx_state],
        outputs=_GEN_OUTPUTS,
    )

    # Approve → send email + save + advance → gen next
    btn_approve.click(
        fn=_approve_and_send,
        inputs=[batch_queue_state, batch_idx_state, batch_draft_state,
                subject_radio, draft_body_input, recipient_input, prospects_state],
        outputs=[prospects_state, batch_idx_state, send_status_display],
    ).then(
        fn=_gen_draft,
        inputs=[batch_queue_state, batch_idx_state],
        outputs=_GEN_OUTPUTS,
    )

    # Skip → advance → gen next
    btn_skip.click(
        fn=_skip,
        inputs=[batch_idx_state],
        outputs=[batch_idx_state],
        queue=False,
    ).then(
        fn=_gen_draft,
        inputs=[batch_queue_state, batch_idx_state],
        outputs=_GEN_OUTPUTS,
    )

    # WhatsApp phone change → regenerate WA/LinkedIn links
    wa_phone_input.change(
        fn=_update_wa_phone,
        inputs=[wa_phone_input, batch_draft_state],
        outputs=[wa_li_display],
    )

    # Finish review → hide panel
    btn_finish_review.click(
        fn=lambda: gr.update(visible=False),
        outputs=[batch_review_group],
    )

    return batch_review_group, batch_queue_state, btn_finish_review
