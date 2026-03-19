# Mac Practice Dental Prospector

An AI-powered sales intelligence platform that researches dental clinics, scores their fit, and generates personalized outreach emails — all in under 60 seconds per prospect.

Built for the sales team at **Mac Practice**, a dental practice management software company with 20+ years in the market and ~3,000 customers. The system replaces 30–45 minutes of manual prospect research with fully automated AI pipelines.

---

## What It Does

1. **Research** — Enter a clinic name, website, LinkedIn URL, Google Maps link, or phone number. The AI searches the real web across 8 source types (clinic website, Google Business, LinkedIn, job boards, dental directories, social media, news, competitor mentions) and compiles a structured 21-field intelligence profile.

2. **Score** — Each prospect receives a **Fit Score (1–10)** based on clinic size, current software, pain points, and growth signals. Priority is labeled HOT / WARM / COLD automatically.

3. **Detect Competitor** — The system identifies which practice management software the clinic currently uses (Dentrix, Eaglesoft, Open Dental, Curve Dental, etc.) and loads a competitor-specific sales playbook.

4. **Generate Outreach** — A personalized sales email is generated using the prospect's pain points, growth signals, decision maker name, and competitor context — with 3 subject line variants to choose from. WhatsApp and LinkedIn DM messages are also generated.

5. **Review & Send** — Edit the draft, approve it, and send directly via Gmail. If Gmail is not configured, the email is formatted for easy clipboard copy-paste.

6. **Pipeline Tracking** — All prospects are tracked on a Kanban board through 5 stages: New → Researched → Outreach Sent → Responded → Meeting Booked.

---

## Key Features

| Feature | Description |
|---|---|
| 🔍 Single prospect research | 5 input modes: clinic name, website, LinkedIn, Google Maps, phone |
| 🚀 Bulk CSV import | Upload hundreds of clinics — researched automatically in sequence with rate limiting |
| ✉️ Batch outreach review | After bulk research, review and approve each AI-generated draft in a queue |
| 📊 Kanban pipeline | Drag prospects across 5 pipeline stages |
| 🤖 AI executive summary | AI-generated summary of your entire pipeline with actionable insights |
| 💬 WhatsApp + LinkedIn DMs | Auto-generated messages alongside the email draft |
| 📧 Gmail send | One-click sending via Gmail SMTP — no OAuth required |
| 📋 Clipboard fallback | If Gmail is not configured, formats the email for copy-paste |
| 🧠 Outreach memory | Learns from your corrections and improves future drafts over time |
| 🏆 Competitor playbooks | 5 competitor-specific sales angles loaded automatically on detection |

---

## How the AI Works

The system uses two AI engines in a **primary → fallback** architecture. Every request tries the primary engine first. If it fails (rate limit, timeout, API error), the fallback activates automatically — no user action needed.

### Primary Engine: Google Gemini + Search Grounding

Gemini is called with its native **Google Search Grounding** capability. This means Gemini searches the real internet as part of generating its response — there is no separate scraping, no extra API calls, and no web parsing on our side. Google handles all of it internally.

**What happens at research time:**
- Gemini receives a detailed prompt instructing it to research the clinic across 8 source types
- It runs its own Google searches, reads real web pages, and synthesizes findings
- The console shows which Google queries were run and which URLs were analyzed
- Output is a structured JSON with 21 fields (clinic data, software detected, decision maker, scoring, talking points, and more)

**What happens at outreach time:**
- The full prospect profile is passed to Gemini
- It generates a personalized email using the competitor playbook, pain points, decision maker name, and growth signals
- Returns 3 subject line variants + complete email body + WhatsApp message + LinkedIn DM

**What happens for the executive summary:**
- All prospects in the pipeline are serialized to JSON and sent to Gemini
- It returns a natural-language summary with insights and recommended next actions

### Fallback Engine: OpenAI GPT-4o-mini + DuckDuckGo

Activated automatically when Gemini fails:

1. **DuckDuckGo** searches for the clinic name (wrapped in quotes for exact match)
2. Up to 8 web result snippets (title + URL + excerpt) are collected
3. The snippets are injected as context into the system prompt
4. **GPT-4o-mini** analyzes the snippets and generates the same structured JSON output as Gemini

Both engines produce the exact same output format — the rest of the system is completely engine-agnostic.

---

## Pipeline Stages

| Stage | Color | Meaning |
|---|---|---|
| **New** | Blue | Imported, not yet investigated |
| **Researched** | Purple | AI completed the intelligence profile |
| **Outreach Sent** | Amber | Email approved and sent (or copied) |
| **Responded** | Green | Prospect replied to outreach |
| **Meeting Booked** | Emerald | Meeting scheduled |

---

## Competitor Detection

The system automatically detects 5 competitor software categories and loads the corresponding sales playbook:

| Competitor | Detection signals | Mac Practice angle |
|---|---|---|
| **Dentrix** | Job postings, website mentions, reviews | Mac-native, simpler pricing, migration support |
| **Eaglesoft** | Patterson references, UI complaints | Modern interface, fully independent vendor |
| **Open Dental** | Open-source mentions, self-hosting setups | Turnkey solution, professional SLA, dedicated support |
| **Curve Dental** | Cloud-only references, SaaS mentions | Hybrid option, 20-year track record, proven reliability |
| **Unknown / Paper** | No software detected, manual processes | Digital transformation pitch, immediate ROI |

When a competitor is detected, the AI automatically uses that competitor's specific pain points and Mac Practice's counter-angles in the generated email — no configuration needed.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI Framework | [Gradio](https://gradio.app) 4.x |
| Backend | Python 3.10+ |
| Primary AI | Google Gemini 1.5 Flash (`google-genai` SDK) |
| Web Search (primary) | Google Search Grounding — built into Gemini |
| Fallback AI | OpenAI GPT-4o-mini |
| Fallback Web Search | DuckDuckGo (`duckduckgo-search`) |
| Email Delivery | Gmail SMTP via App Password (`smtplib`) |
| Data Storage | JSON file + in-memory dictionary |
| CSV Parsing | Custom multi-format parser + `pandas` |
| Config Management | `python-dotenv` |

---

## Project Structure

```
MacPractice/
├── app/
│   ├── agents/
│   │   ├── gemini_agent.py       # Gemini API: research, outreach, executive summary
│   │   ├── openai_agent.py       # OpenAI + DuckDuckGo fallback
│   │   └── prompts.py            # All system prompts and query builders
│   ├── models/
│   │   ├── prospect.py           # Prospect dataclass (21 research fields + pipeline metadata)
│   │   ├── competitor.py         # Competitor database and auto-detection logic
│   │   └── pipeline.py           # Pipeline stage definitions
│   ├── services/
│   │   ├── research_service.py   # Research orchestrator (Gemini → fallback → JSON → Prospect)
│   │   ├── outreach_service.py   # Email generation + outreach memory system
│   │   ├── email_service.py      # Gmail SMTP sending + clipboard fallback
│   │   ├── csv_service.py        # Multi-format CSV/TSV/plain-text parser
│   │   └── storage_service.py    # In-memory storage with JSON persistence
│   ├── utils/
│   │   ├── json_parser.py        # Robust LLM JSON extraction with fallback
│   │   └── logger.py             # Real-time streaming logger with icons
│   └── config.py                 # Environment variable loader
├── ui/
│   ├── views/
│   │   ├── workflow_view.py      # 6-stage research & outreach workflow
│   │   ├── dashboard_view.py     # Kanban board + sales funnel + executive summary
│   │   └── batch_review_view.py  # Bulk CSV import + outreach review queue
│   ├── components/
│   │   ├── prospect_card.py      # Kanban prospect card
│   │   ├── competitor_card.py    # Competitor profile card
│   │   ├── score_ring.py         # Circular fit score SVG indicator
│   │   └── batch_modal.py        # Bulk upload modal
│   ├── app.py                    # Main Gradio layout, global state wiring
│   └── theme.py                  # Design system (colors, CSS, HTML helpers)
├── data/
│   └── sample_clinics.csv        # Sample clinics for demo and testing
├── run.py                        # Entry point
├── requirements.txt
└── .env                          # API keys and config (not committed to git)
```

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd MacPractice

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
# AI Engines
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Gmail (for email sending)
GMAIL_SENDER_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16char_app_password

# Models (optional — these are the defaults)
GEMINI_MODEL=gemini-1.5-flash
OPENAI_MODEL=gpt-4o-mini

# Server (optional)
GRADIO_SERVER_NAME=127.0.0.1
GRADIO_SERVER_PORT=7860

# Batch rate limiting (optional)
BATCH_DELAY_SECONDS=5
```

### 4. Get your API keys

| Key | Where to get it | Cost |
|---|---|---|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/app/apikey) | Free tier — 15 req/min |
| `OPENAI_API_KEY` | [OpenAI Platform](https://platform.openai.com/api-keys) | Pay per token |
| `GMAIL_APP_PASSWORD` | Google Account → Security → 2-Step Verification → App Passwords | Free |

> **Gmail note:** `GMAIL_APP_PASSWORD` is a 16-character code generated by Google — it is NOT your regular Gmail password. You must have **2-Step Verification enabled** first. Generate it at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).
>
> **MVP note:** The "To" email field is intentionally left empty when generating outreach drafts. Fill it with your own email address to test sending without emailing real prospects.

### 5. Run the application

```bash
python run.py
```

Open [http://127.0.0.1:7860](http://127.0.0.1:7860) in your browser.

---

## Usage

### Research a single prospect

1. Click **＋ Research Prospect**
2. Enter a clinic name — e.g., `Bright Smile Dental, Austin TX`
   - The system auto-detects the input type: paste a LinkedIn URL, website, Google Maps link, or phone number and it adapts automatically
3. Watch the live research log as the AI works
4. Review the full intelligence profile: software detected, decision maker, pain points, fit score
5. Click **Generate Outreach** to create a personalized email automatically
6. Edit subject and body if needed, enter your test email in the **To** field, click **Send**

### Bulk research

1. Click **🚀 Bulk Research**
2. Paste a list of clinics — any CSV format is accepted (see below)
3. Click **Research N Clinics** and wait while each clinic is processed sequentially
4. When research finishes, the **Batch Outreach Review** panel opens automatically
5. For each prospect: review the AI-generated draft, edit if needed, then click **✅ Approve & Next** or **⏭ Skip**
6. Approved prospects are automatically moved to **Outreach Sent** in the pipeline

### CSV format

The parser accepts any of these formats — headers are optional:

```
# Plain list (one clinic per line)
Bright Smile Dental, Austin TX
Summit Dental Group, Salt Lake City UT

# CSV with headers
clinic_name,location
"Bright Smile Dental","Austin, TX"
"Summit Dental Group","Salt Lake City, UT"

# No headers — first column is name, second is location
Bright Smile Dental,Austin TX
Summit Dental Group,Salt Lake City UT
```

TSV (tab-separated) and semicolon-separated formats are also detected automatically.

---

## Notes

- **Rate limiting:** The free Gemini tier allows 15 requests per minute. Batch research uses a 5-second delay between prospects by default (`BATCH_DELAY_SECONDS`). Increase this value if you encounter 429 errors.
- **Outreach memory:** The system saves learned corrections to `app/agents/outreach_memory.txt`. This file is injected into future outreach prompts, so the AI improves over time based on your edits and rejections.
- **Automatic fallback:** If Gemini hits its rate limit or fails for any reason, the system switches to OpenAI + DuckDuckGo automatically and transparently.
- **No OAuth required:** Email sending uses Gmail's App Password over SMTP — no Google Cloud project, service account, or OAuth consent screen is needed.
