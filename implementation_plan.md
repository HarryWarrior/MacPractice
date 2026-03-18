# 🦷 Mac Practice Dental Prospector — Plan de Implementación MVP

> **Fuente:** [SPEC.md](file:///c:/Users/HarrysonDanielGuerre/Documents/MacPractice/SPEC.md)
> **Stack:** Python 3.10+ · Gradio · Gemini (Primary AI) · OpenAI+DDG (Fallback) · smtplib (Gmail)

---

## 📁 Estructura de Directorios Final (Clean Architecture)

```
MacPractice/
├── SPEC.md                          # Especificación (ya existe)
├── README.md                        # Documentación del proyecto
├── requirements.txt                 # Dependencias Python
├── .gitignore                       # Exclusiones de Git
├── .env.development                 # Variables de entorno (dev)
├── .env.production                  # Variables de entorno (prod)
│
├── app/                             # ===== BACKEND / LÓGICA =====
│   ├── main.py                      # Punto de entrada (si se usa FastAPI para API interna)
│   ├── config.py                    # Carga de .env y constantes globales
│   │
│   ├── models/                      # Estructuras de datos y persistencia
│   │   ├── prospect.py              # Clase/dict del Prospecto (21 campos + metadata)
│   │   ├── competitor.py            # Base de datos de 5 competidores (Dentrix, etc.)
│   │   └── pipeline.py              # Estados del pipeline (new, researched, etc.)
│   │
│   ├── services/                    # Lógica de negocio (el "cerebro")
│   │   ├── research_service.py      # Orquestador: Gemini → Fallback → JSON parse
│   │   ├── outreach_service.py      # Generación de email personalizado
│   │   ├── email_service.py         # Envío real via smtplib + Gmail App Password
│   │   ├── csv_service.py           # Parser de CSV/TSV para batch import
│   │   └── storage_service.py       # Persistencia local (JSON/dict en memoria + export CSV)
│   │
│   ├── agents/                      # Conexiones directas a LLMs
│   │   ├── gemini_agent.py          # SDK google-generativeai + Search Grounding
│   │   ├── openai_agent.py          # SDK openai gpt-4o-mini (fallback)
│   │   └── prompts.py               # RESEARCH_PROMPT + OUTREACH_PROMPT (texto completo)
│   │
│   └── utils/                       # Utilidades compartidas
│       ├── json_parser.py           # Extrae JSON de respuestas de LLM (regex + fallback)
│       └── logger.py                # Generador de logs con timestamp para UI
│
├── ui/                              # ===== FRONTEND GRADIO =====
│   ├── app.py                       # Punto de entrada principal de Gradio
│   ├── theme.py                     # Design system: colores, CSS, fuentes
│   ├── views/
│   │   ├── dashboard_view.py        # Tab 1: Pipeline / Kanban / Métricas
│   │   └── workflow_view.py         # Tab 2: Research & Outreach (Stepper de 6 etapas)
│   └── components/
│       ├── prospect_card.py         # Card visual de un prospecto
│       ├── score_ring.py            # SVG/HTML del fit score circular
│       ├── competitor_card.py       # Card de competidor con pains vs angles
│       └── batch_modal.py           # Upload de CSV con preview
│
└── data/
    └── sample_clinics.csv           # 10 clínicas de ejemplo para testing
```

---

## 🔄 División de Trabajo entre 2 Agentes

La idea es que **las fases NO se crucen**. Cada agente trabaja en archivos diferentes y en capas diferentes del sistema.

### 🤖 Agente A (YO — Antigravity)
> **Dominio: Backend, lógica de negocio, agentes IA, y estructura base**

### 🤖 Agente B (El otro agente)
> **Dominio: Frontend Gradio, UI, componentes visuales, theme**

---

## 🔴 FASE 1 — Esqueleto + Estructura de Datos

| Tarea | Agente | Archivos | Descripción |
|-------|--------|----------|-------------|
| 1.1 Estructura de directorios y archivos base | **A** | Todo el árbol `app/`, `data/`, config | Crear carpetas, [__init__.py](file:///c:/Users/HarrysonDanielGuerre/Documents/MacPractice/ui/__init__.py), `config.py`, `.env`, [.gitignore](file:///c:/Users/HarrysonDanielGuerre/Documents/MacPractice/.gitignore), [requirements.txt](file:///c:/Users/HarrysonDanielGuerre/Documents/MacPractice/requirements.txt) |
| 1.2 Modelos de datos | **A** | `app/models/prospect.py`, `competitor.py`, `pipeline.py` | Diccionarios/dataclasses de Prospecto, los 5 competidores, y estados del pipeline |
| 1.3 Prompts del sistema | **A** | `app/agents/prompts.py` | Texto completo del RESEARCH_PROMPT y OUTREACH_PROMPT |
| 1.4 Mock del research | **A** | `app/services/research_service.py` | Función `mock_research_generator()` con `yield` que simula pasos |
| 1.5 Utilidades | **A** | `app/utils/json_parser.py`, `logger.py` | Parser JSON y generador de logs con timestamp |
| 1.6 Layout de Gradio principal | **B** | [ui/app.py](file:///c:/Users/HarrysonDanielGuerre/Documents/MacPractice/ui/app.py), `ui/theme.py` | `Blocks()` con 2 tabs, design system CSS, fuentes Google |
| 1.7 Vista Dashboard (maqueta) | **B** | `ui/views/dashboard_view.py` | Métricas vacías, Kanban con 5 columnas, estado vacío |
| 1.8 Vista Workflow (maqueta) | **B** | `ui/views/workflow_view.py` | Stepper visual, Input con 5 modos, panel de logs |
| 1.9 Componentes base | **B** | `ui/components/` | `prospect_card.py`, `score_ring.py` (HTML/CSS) |
| 1.10 CSV de ejemplo | **A** | `data/sample_clinics.csv` | 10 clínicas de prueba |

> **✅ Validación Fase 1:** La UI abre, muestra las 2 tabs, el mock genera logs en tiempo real, los competidores se cargan desde el modelo.

---

## 🟡 FASE 2 — Motor de Investigación (Gemini + Fallback)

| Tarea | Agente | Archivos | Descripción |
|-------|--------|----------|-------------|
| 2.1 Agente Gemini | **A** | `app/agents/gemini_agent.py` | SDK `google-generativeai`, Search Grounding, rate limiting |
| 2.2 Agente OpenAI (fallback) | **A** | `app/agents/openai_agent.py` | `duckduckgo-search` + `gpt-4o-mini` como red de seguridad |
| 2.3 Orquestador Research | **A** | `app/services/research_service.py` | `do_research()`: try Gemini → except → fallback OpenAI. Fuerza JSON output |
| 2.4 Detección de competidor | **A** | `app/services/research_service.py` | Cruzar `current_software` contra la DB de competidores |
| 2.5 Storage service | **A** | `app/services/storage_service.py` | Guardar/cargar prospectos en memoria + export a CSV |
| 2.6 Conectar research a UI | **B** | `ui/views/workflow_view.py` | Reemplazar mock por llamada real. Mostrar los 6 pasos animados de progreso |
| 2.7 Renderizar Profile | **B** | `ui/views/workflow_view.py`, `ui/components/competitor_card.py` | Mostrar el perfil completo del prospecto: score, competidor, insights |

> **✅ Validación Fase 2:** Se escribe un nombre de clínica real, Gemini investiga, se ve el progreso en tiempo real, se muestra el perfil completo con fit score.

---

## 🔵 FASE 3 — Outreach + Human-in-the-Loop

| Tarea | Agente | Archivos | Descripción |
|-------|--------|----------|-------------|
| 3.1 Servicio de outreach | **A** | `app/services/outreach_service.py` | Genera email usando el OUTREACH_PROMPT + datos del research |
| 3.2 Template de fallback | **A** | `app/services/outreach_service.py` | Email genérico hardcoded si la API falla |
| 3.3 UI de Draft editable | **B** | `ui/views/workflow_view.py` | 3 subject lines clickeables, textarea editable, botones Aprobar/Rechazar |
| 3.4 Flujo Approve/Reject | **B** | `ui/views/workflow_view.py` | Reject → regenera. Approve → modo read-only con badge "APPROVED" |
| 3.5 Hooks de personalización | **B** | `ui/views/workflow_view.py` | Mostrar la card de personalization_hooks y tone_notes |

> **✅ Validación Fase 3:** Se investiga una clínica, se genera un email, se puede editar, rechazar (regenera), y aprobar.

---

## 🟢 FASE 4 — Gmail Real + Batch Processing

| Tarea | Agente | Archivos | Descripción |
|-------|--------|----------|-------------|
| 4.1 Email service (smtplib) | **A** | `app/services/email_service.py` | `send_real_email()` con Gmail App Password via `smtplib` |
| 4.2 CSV Parser | **A** | `app/services/csv_service.py` | `parse_csv()` con detección de headers inteligente |
| 4.3 Batch research loop | **A** | `app/services/research_service.py` | Loop secuencial con `time.sleep(5)`, progreso individual |
| 4.4 UI de envío (Send stage) | **B** | `ui/views/workflow_view.py` | Éxito → "Draft created!". Fallo → Clipboard fallback |
| 4.5 Batch Upload modal | **B** | `ui/components/batch_modal.py` | Drag & drop CSV, preview de clínicas, botón "Add N Prospects" |
| 4.6 Barra de progreso batch | **B** | `ui/views/dashboard_view.py` | "Batch researching: 3/10" con barra animada |
| 4.7 Kanban funcional | **B** | `ui/views/dashboard_view.py` | Cards con botones de mover entre columnas, métricas calculadas |

> **✅ Validación Fase 4:** Se sube un CSV, se procesan en batch, se envía un email real via Gmail, el pipeline refleja todo.

---

## 🚀 ¿Qué construiré yo primero? (Agente A — FASE 1)

Voy a empezar creando estos archivos en orden:

1. **`app/config.py`** — Carga de variables de entorno
2. **`app/models/competitor.py`** — Los 5 perfiles de competidores
3. **`app/models/prospect.py`** — Estructura del prospecto (21 campos + metadata)
4. **`app/models/pipeline.py`** — Estados del pipeline
5. **`app/agents/prompts.py`** — Los 2 prompts del sistema completos
6. **`app/utils/json_parser.py`** — Parser de JSON robusto
7. **`app/utils/logger.py`** — Generador de logs con timestamps
8. **`app/services/research_service.py`** — Mock research con `yield`
9. **`app/services/storage_service.py`** — Persistencia en memoria
10. **`data/sample_clinics.csv`** — 10 clínicas de ejemplo
11. **`.gitignore`**, **`.env.*`**, **`requirements.txt`**, **`README.md`** — Archivos de proyecto

> [!IMPORTANT]
> El otro agente (Agente B) debería empezar **simultáneamente** con:
> `ui/theme.py`, `ui/app.py`, `ui/views/dashboard_view.py`, `ui/views/workflow_view.py`, y `ui/components/`.
> **No tocará nada dentro de `app/`**. Solo importará funciones de `app/` cuando las necesite conectar.
