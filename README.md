# 🦷 Mac Practice — Dental Prospector

Sistema de inteligencia de ventas con IA para el equipo comercial de Mac Practice. Automatiza el proceso completo de prospección: desde investigar una clínica dental hasta enviar un email de outreach personalizado.

## 📁 Arquitectura

```
MacPractice/
├── app/                          # Backend y lógica de negocio
│   ├── config.py                 # Variables de entorno centralizadas
│   ├── models/                   # Estructuras de datos
│   │   ├── prospect.py           # Modelo del prospecto (21 campos + metadata)
│   │   ├── competitor.py         # DB de 5 competidores
│   │   └── pipeline.py           # Estados del pipeline Kanban
│   ├── services/                 # Lógica de negocio
│   │   ├── research_service.py   # Orquestador de investigación (Gemini → Fallback)
│   │   ├── outreach_service.py   # Generación de email (Fase 3)
│   │   ├── email_service.py      # Envío real via Gmail (Fase 4)
│   │   ├── csv_service.py        # Parser de CSV (Fase 4)
│   │   └── storage_service.py    # Persistencia en memoria + JSON
│   ├── agents/                   # Conexiones a LLMs
│   │   ├── gemini_agent.py       # Google Gemini + Search Grounding (Fase 2)
│   │   ├── openai_agent.py       # OpenAI gpt-4o-mini fallback (Fase 2)
│   │   └── prompts.py            # Prompts del sistema
│   └── utils/                    # Utilidades
│       ├── json_parser.py        # Parser JSON robusto
│       └── logger.py             # Sistema de logs con timestamps
├── ui/                           # Frontend Gradio
│   ├── app.py                    # Punto de entrada (Agente B)
│   ├── theme.py                  # Design system CSS
│   ├── views/                    # Vistas principales
│   └── components/               # Componentes reutilizables
└── data/
    └── sample_clinics.csv        # 10 clínicas de ejemplo
```

## 🚀 Setup

```bash
# 1. Crear entorno virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
copy .env.development .env
# Editar .env con tus API keys reales

# 4. Ejecutar la aplicación
python ui/app.py
```

## 🔑 Variables de Entorno Requeridas

| Variable | Descripción |
|----------|-------------|
| `GEMINI_API_KEY` | API key de Google AI Studio (gratuita) |
| `OPENAI_API_KEY` | API key de OpenAI (fallback) |
| `GMAIL_SENDER_EMAIL` | Email de Gmail para envío |
| `GMAIL_APP_PASSWORD` | App password de Gmail |

## 📋 Stack Técnico

- **Frontend:** Gradio 4.x (UI interactiva)
- **IA Principal:** Google Gemini 1.5 Flash + Search Grounding
- **IA Fallback:** OpenAI gpt-4o-mini + DuckDuckGo search
- **Email:** smtplib con Gmail App Password
- **Persistencia:** JSON local + export CSV
