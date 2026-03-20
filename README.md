---
title: Mac Practice Dental Prospector
emoji: 🦷
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: "4.44.1"
python_version: "3.10"
app_file: run.py
pinned: false
---

# Mac Practice Dental Prospector

An AI-powered sales intelligence platform that researches dental clinics, scores their fit, and generates personalized outreach across **email, WhatsApp, and LinkedIn** — all in under 60 seconds per prospect.

Built for the sales team at **Mac Practice**, a dental practice management software company with 20+ years in the market and ~3,000 customers.

---

## Write-Up — Track B: Sales & Outreach Agent

The core problem I set out to solve was simple but painful: Mac Practice's sales reps were spending 30–45 minutes per prospect just doing research — manually searching clinic websites, scrolling LinkedIn, guessing what software they use, and then writing an email from scratch that often felt generic. At that pace, personalized outreach at scale was impossible. I built this agent to compress the entire discovery-to-draft workflow into under 60 seconds, with output that reads like a rep did the work themselves — because the AI is grounding every sentence in real signals: the clinic's job postings, their Google reviews, their decision maker's LinkedIn, and the specific pain points of whichever competitor software they're currently using.

For the architecture, I chose Google Gemini with native Search Grounding as the primary engine — Gemini searches the real web internally, which means zero scraping infrastructure and results that are current. I paired it with an OpenAI + DuckDuckGo fallback that activates transparently when Gemini hits its limits. The competitor detection layer is a key design decision: instead of a generic pitch, every generated email automatically loads a playbook specific to Dentrix, Eaglesoft, Open Dental, or Curve Dental — turning competitor pain points into Mac Practice's opening angle.

The natural next steps: integrating with HubSpot so researched prospects sync into the CRM automatically; connecting to the WhatsApp Business API so the system sends the AI-generated message directly from the company's or rep's registered number — no copy-paste; a remarketing engine that re-sends follow-up emails or WhatsApp messages to prospects who haven't responded after a configurable number of days, each follow-up generated with a different angle; and a sales rep chatbot that lets reps ask "what should I say to this clinic?" and get coaching grounded in the prospect's actual profile.

---

## What It Does

1. **Research** — Enter a clinic name, website, LinkedIn URL, Google Maps link, or phone. The AI searches the real web across 8 source types and compiles a 21-field intelligence profile.
2. **Score** — Each prospect gets a **Fit Score (1–10)** and a HOT / WARM / COLD priority label automatically.
3. **Detect Competitor** — Identifies which practice management software the clinic uses and loads a competitor-specific sales playbook.
4. **Generate Outreach** — Produces a **sales email** (3 subject variants), a **WhatsApp message** with a one-click send button pre-filled with the prospect's number, and a **LinkedIn DM** — all in one shot, grounded in real data.
5. **Review & Send** — Edit any draft, approve, and send via Gmail SMTP. WhatsApp opens pre-filled. If Gmail isn't configured, the email is formatted for clipboard copy-paste.
6. **Pipeline Tracking** — Kanban board across 5 stages: New → Researched → Outreach Sent → Responded → Meeting Booked.

---

## How to Use (Step by Step)

### Research a single clinic

1. Click the **＋ Research Prospect** button at the top of the dashboard.
2. Type a clinic name in the search box — e.g. `Bright Smile Dental, Austin TX`. You can also paste a website URL, LinkedIn page, Google Maps link, or phone number — the system detects the type automatically. Or click any of the **Quick Example** buttons to pre-fill one.
3. Click **Research Clinic →** and watch the live log on the right as the AI works through 6 research steps.
4. Review the full profile that appears: fit score, decision maker found, competitor software detected, pain points, and growth signals.
5. Click **Generate Outreach →** — the AI writes a personalized email (pick from 3 subject lines), a WhatsApp message, and a LinkedIn DM in one shot.
6. In the **To (email)** field, type your own email address (MVP mode — do not email real prospects yet).
7. Edit the subject or body if needed, then click **✓ Approve**.
8. Click **Create Gmail Draft** to send. For WhatsApp, click the green **Open WhatsApp** button — it opens a pre-filled chat instantly.
9. When done, click **← Pipeline** to return to the dashboard.

### Bulk research (many clinics at once)

1. Click **🚀 Bulk Research** on the dashboard.
2. Paste a list of clinic names — one per line, or in CSV format with name and location columns. Click **Research N Clinics**.
3. Wait while each clinic is researched automatically. A progress bar shows the queue.
4. When finished, a review queue opens automatically. For each prospect: read the AI-generated draft, edit if needed, type your test email in **To**, then click **✅ Approve & Send** or **⏭ Skip**.
5. Approved prospects move to **Outreach Sent** on the Kanban board automatically.

---

## Tech Stack & Environment Variables

| Layer | Technology |
|---|---|
| UI | Gradio 4.x |
| Backend | Python 3.10+ |
| Primary AI | Google Gemini 1.5 Flash (Search Grounding built-in) |
| Fallback AI | OpenAI GPT-4o-mini + DuckDuckGo |
| Email | Gmail SMTP via App Password |
| Data | JSON file + in-memory dict |

### Environment variables

Create a `.env` file in the project root. Here is what each variable does and what happens without it:

| Variable | Required | Effect if missing |
|---|---|---|
| `GEMINI_API_KEY` | **Yes** | All research fails — no AI engine available |
| `OPENAI_API_KEY` | Recommended | Fallback disabled — if Gemini fails, research stops |
| `GMAIL_SENDER_EMAIL` | Optional | Email sending disabled; clipboard copy-paste fallback activates |
| `GMAIL_APP_PASSWORD` | Optional | Same — email sending disabled, clipboard fallback activates |
| `GEMINI_MODEL` | Optional | Defaults to `gemini-1.5-flash` |
| `OPENAI_MODEL` | Optional | Defaults to `gpt-4o-mini` |
| `BATCH_DELAY_SECONDS` | Optional | Defaults to `5` — increase to `10`+ if you get 429 rate-limit errors |

```env
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GMAIL_SENDER_EMAIL=you@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

> **Gmail App Password:** This is a 16-character code from Google Account → Security → 2-Step Verification → App Passwords. It is NOT your regular Gmail password. If your Google account doesn't support App Passwords (e.g. Workspace with restrictions), email sending will fall back to clipboard copy-paste automatically.

---

## Setup

```bash
git clone <repo-url>
cd MacPractice
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
# Create .env with your API keys (see above)
python run.py
```

Open [http://127.0.0.1:7860](http://127.0.0.1:7860) in your browser.

Get your keys:
- **Gemini:** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) — free tier, 15 req/min
- **OpenAI:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys) — pay per token
- **Gmail App Password:** [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) — free
