# Mac Practice Dental Prospector — Especificación Funcional y Técnica Completa

## 1\. Visión General del Sistema

### 1.1 Qué es

Un sistema de inteligencia de ventas con IA diseñado específicamente para el equipo comercial de Mac Practice, una empresa de software de gestión de clínicas dentales y médicas con 20 años de historia y \~3,000 clientes. El sistema automatiza el proceso completo de prospección: desde investigar una clínica dental hasta enviar un email de outreach personalizado via Gmail.

### 1.2 Problema que resuelve

Un sales rep de Mac Practice actualmente gasta 30-45 minutos por prospecto: busca la clínica en Google, revisa su sitio web, busca al decision maker en LinkedIn, intenta averiguar qué software usan, redacta un email genérico. Con este sistema, ese proceso toma 60 segundos y produce inteligencia más profunda y outreach más personalizado.

### 

* ### 1.3 Stack técnico 
* 
* \- \*\*Frontend/Orquestación:\*\* Python 3.10+ con Gradio (UI interactiva, soporte de themes y generadores).
* \- \*\*Motor de IA Principal:\*\* Gemini 1.5 Flash / Pro (via `google-generativeai`).
* \- \*\*Investigación Web Principal:\*\* Google Search Grounding (nativo en Gemini, cero costo adicional).
* \- \*\*Motor Fallback (Plan B):\*\* OpenAI `gpt-4o-mini` + `duckduckgo-search` (en caso de que la API de Google falle).
* \- \*\*Email:\*\* `smtplib` y `email.mime` de Python con App Password de Gmail (envío directo sin fricción de OAuth).
* \- \*\*Persistencia:\*\* Almacenamiento en memoria (diccionarios/DataFrames de Pandas) y exportación a CSV durante la sesión.
* \- \*\*Diseño:\*\* Gradio `theme=gr.themes.Monochrome()` o `Soft()`, layout de columnas divididas (Inputs a la izquierda, Terminal de Logs a la derecha).

### 1.4 Arquitectura de alto nivel

El sistema tiene dos vistas principales y un modal:

```
┌─────────────────────────────────────────────────────────┐
│                     DentalProspector                     │
│                  (Componente raíz / Router)               │
│                                                          │
│  Estado global:                                          │
│  - view: "dashboard" | "workflow"                        │
│  - prospects\[]: array persistido en storage              │
│  - activeProspect: objeto del prospecto activo           │
│  - stage: etapa actual del workflow                      │
│  - draft, approvedEmail, sendState                       │
│                                                          │
│  ┌────────────────────┐  ┌─────────────────────────────┐ │
│  │   Vista Dashboard   │  │      Vista Workflow          │ │
│  │   (view="dashboard")│  │   (view="workflow")          │ │
│  │                     │  │                              │ │
│  │ - Pipeline metrics  │  │  Stepper (← Pipeline | ①②③)│ │
│  │ - Kanban board      │  │                              │ │
│  │ - Batch progress    │  │  stage="input"    → Input    │ │
│  │                     │  │  stage="research" → Research │ │
│  │                     │  │  stage="profile"  → Profile  │ │
│  │                     │  │  stage="draft\_loading" → ⏳  │ │
│  │                     │  │  stage="draft"    → Draft    │ │
│  │                     │  │  stage="send"     → Send     │ │
│  └────────────────────┘  └─────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │           BatchUploadModal (overlay)                │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

\---

## 2\. Design System

### 2.1 Paleta de colores

```
C.bg         = "#070A0F"   → Fondo principal (casi negro azulado)
C.surface    = "#0E1219"   → Superficies elevadas
C.card       = "#141A23"   → Cards y contenedores
C.border     = "#1E2636"   → Bordes principales
C.borderLight= "#2A3348"   → Bordes secundarios
C.text       = "#EDF2F7"   → Texto principal (casi blanco)
C.textMuted  = "#8899AD"   → Texto secundario
C.textDim    = "#566577"   → Texto terciario / hints
C.accent     = "#10B981"   → Color primario (verde esmeralda)
C.accentLight= "#34D399"   → Variante clara del acento
C.accentGlow = rgba(16,185,129,0.12) → Glow / hover states
C.amber      = "#F59E0B"   → Warnings, leads warm
C.red        = "#EF4444"   → Errores, leads hot, competitor pains
C.blue       = "#3B82F6"   → Info, leads cold, Dentrix
C.purple     = "#8B5CF6"   → Eaglesoft, personalization hooks
C.cyan       = "#06B6D4"   → Open Dental, reviews insight
```

### 2.2 Tipografía

* **Plus Jakarta Sans** (300-800): toda la UI, headings, botones, labels
* **JetBrains Mono** (400-800): scores numéricos, datos técnicos, badges de fit

### 2.3 Animaciones

* `fadeUp`: entrada de componentes (opacity 0→1, translateY 12px→0, 0.4-0.5s)
* `spin`: spinners de loading (rotate 360deg, linear, 0.8-1s)
* `pulse`: indicadores activos (opacity 1→0.3→1, 1s)

### 2.4 Componentes reutilizables

**Badge:** Pill con texto, color configurable, variante `small`.
Props: `children, color, small`

**Card:** Contenedor con fondo, borde, border-radius 14px. Variante `glow` agrega box-shadow y borde verde.
Props: `children, style, glow, onClick`

**Btn:** Botón con variantes primary (fondo sólido) y outline (borde). Soporta loading spinner, icono, disabled.
Props: `children, onClick, primary, disabled, color, loading, icon, small`

**ScoreRing:** SVG circular que muestra el fit score (1-10). Colores adaptativos: verde ≥8, amber ≥5, rojo <5.
Props: `score, size`

**MetricCard:** Card de superficie con label uppercase, valor grande en mono, subtexto opcional.
Props: `label, value, sub, color`

\---

## 3\. Base de Datos de Competidores

El sistema tiene perfiles pre-construidos de 5 competidores. Cada perfil contiene:

### 3.1 Estructura

```javascript
{
  name: "Nombre del competidor",
  color: "#hex",         // Color para badges y UI
  pains: \[               // 4 pain points conocidos
    "Pain point 1",
    "Pain point 2",
    "Pain point 3",
    "Pain point 4"
  ],
  angles: \[              // 4 ángulos de Mac Practice
    "Advantage 1",
    "Advantage 2",
    "Advantage 3",
    "Advantage 4"
  ]
}
```

### 3.2 Competidores registrados

**Dentrix** (color: blue #3B82F6)

* Pains: Expensive licensing, Windows-only lock-in, Complex upgrade path, Poor customer support
* Angles: Mac-native advantage, Simpler pricing, 20 years expertise, Migration support included

**Eaglesoft** (color: purple #8B5CF6)

* Pains: Outdated UI, Patterson-bundled limitations, Limited customization, Slow feature releases
* Angles: Modern interface, Independent platform, Faster iteration, Open integration options

**Open Dental** (color: cyan #06B6D4)

* Pains: Requires technical setup, Community-dependent support, Security on clinic, No dedicated AM
* Angles: Turnkey solution, Professional support SLA, Enterprise security, Dedicated customer success

**Curve Dental** (color: amber #F59E0B)

* Pains: Limited offline, Newer less proven, Fewer integrations, Cloud-only concerns
* Angles: Hybrid option (cloud Q3), 20-year track record, Deep integrations, Flexible deployment

**Unknown/Paper** (color: gray #6B7280)

* Pains: Manual processes, Error-prone scheduling, No insurance automation, Difficult to scale
* Angles: Complete digital transformation, Insurance claim automation, Multi-location, Immediate ROI

### 3.3 Detección

El matching se hace por string inclusion en el campo `current\_software` de la respuesta de la IA:

```javascript
Object.entries(COMPETITORS).find((\[k]) => 
  data.current\_software?.toLowerCase().includes(k)
)
```

\---

## 4\. Capa de IA — Prompts del Sistema

### 4.1 RESEARCH\_PROMPT (Investigación Multi-Fuente)

**Rol:** Sales intelligence researcher para Mac Practice.

**Estrategia de búsqueda (8 pasos ordenados):**

1. CLINIC WEBSITE — Team page, servicios, tecnología mencionada, historia, jobs
2. GOOGLE BUSINESS / MAPS — Rating, review count, reviews recientes con pain points
3. LINKEDIN — Company page, employee count, posts recientes, personas clave
4. JOB POSTINGS — Indeed/Glassdoor, revelan software actual y señales de crecimiento
5. DENTAL DIRECTORIES — Healthgrades, Zocdoc, Vitals, ADA Find-a-Dentist
6. SOCIAL MEDIA — Facebook, Instagram, presencia y actividad
7. NEWS \& PRESS — Noticias locales, premios, expansiones, adquisiciones
8. COMPETITOR DETECTION — Cruzar nombre con "Dentrix", "Eaglesoft", etc.

**Output JSON esperado (21 campos):**

```json
{
  "clinic\_name": "String — nombre oficial completo",
  "location": "String — ciudad, estado",
  "type": "dental|medical|multi-specialty",
  "practitioners": "Number — cantidad de practitioners",
  "staff\_estimate": "Number — staff total estimado",
  "specialty": "String — especialidades",
  "services": \["Array de strings — servicios ofrecidos"],
  "years\_in\_practice": "Number — años en operación",
  "insurance\_accepted": \["Array — aseguradoras aceptadas"],
  "current\_software": "String — Dentrix|Eaglesoft|Open Dental|Curve Dental|Unknown|Paper-based",
  "software\_confidence": "high|medium|low",
  "software\_signals": "String — evidencia específica de la detección",
  "pain\_points": \["Array — pain points con fuente"],
  "growth\_signals": \["Array — señales de crecimiento con evidencia"],
  "decision\_maker": {
    "name": "String",
    "role": "String — Owner/Manager/etc",
    "linkedin": "String — URL",
    "email\_pattern": "String — patrón deducido"
  },
  "online\_presence": {
    "website": "String — URL",
    "google\_rating": "Number — 1-5",
    "review\_count": "Number",
    "social\_active": "Boolean",
    "facebook": "String — URL",
    "instagram": "String — handle"
  },
  "recent\_reviews\_summary": "String — resumen 2-3 oraciones de reviews",
  "hiring\_signals": \["Array — job postings activos y lo que revelan"],
  "fit\_score": "Number 1-10",
  "fit\_reasoning": "String — 2-3 oraciones con datos específicos",
  "priority": "hot|warm|cold",
  "best\_angle": "String — mejor ángulo basado en evidencia",
  "talking\_points": \["Array — 3 puntos referenciando datos reales"],
  "red\_flags": \["Array — preocupaciones sobre el prospecto"],
  "sources\_used": \["Array — lista de fuentes donde se encontró data"]
}
```

**Criterios de scoring (fit\_score 1-10):**

* Tamaño clínica: 3-15 practitioners = sweet spot
* Software actual: Competidor desactualizado = alta oportunidad
* Ubicación: US-based
* Growth signals: Hiring, expandiendo, nuevo equipo
* Pain points en reviews: Billing, scheduling, tecnología
* Accesibilidad del decision maker

### 4.2 OUTREACH\_PROMPT (Generación de Email)

**Rol:** Sales outreach specialist para Mac Practice.

**Reglas:**

* Tono genuinamente humano, NO templado
* Referenciar algo ESPECÍFICO de la clínica
* Liderar con su pain point, no features de Mac Practice
* Si hay competidor detectado, plantear semillas de switching sutilmente
* Body menor a 150 palabras
* CTA suave (no "book a demo")
* Cero buzzwords

**Output JSON esperado:**

```json
{
  "subject\_options": \["3 opciones de subject line"],
  "body": "String — cuerpo del email",
  "sender\_name": "String — nombre del sender",
  "sender\_title": "String — título y empresa",
  "follow\_up\_timing": "String — cuándo hacer follow-up",
  "personalization\_hooks": \["Array — qué lo hace específico"],
  "tone\_notes": "String — nota sobre el tono elegido"
}
```

#### 4.3 Arquitectura de Llamada a la API (Primary \& Fallback)



El sistema utiliza un bloque `try-except` robusto para garantizar la investigación:



\*\*Intento 1: API de Gemini (Primary)\*\*

\- \*\*Modelo:\*\* `gemini-1.5-flash` (Optimizado para velocidad y costo cero en AI Studio).

\- \*\*Tools:\*\* `tools="google\_search\_retrieval"` (Grounding activado).

\- \*\*Rate Limiting:\*\* Si se procesa un batch (CSV), implementar `time.sleep(5)` entre iteraciones para respetar el límite gratuito de 15 RPM (Requests Per Minute) de Google AI Studio.



\*\*Intento 2: OpenAI + DuckDuckGo (Fallback Automático)\*\*

\- Si Gemini lanza error (ej. `429 Too Many Requests` o timeout), el sistema captura la excepción y activa el fallback.

\- \*\*Búsqueda:\*\* Ejecuta `DDGS().text(query)` para extraer 5-10 fragmentos de la web.

\- \*\*Modelo:\*\* Llama a `gpt-4o-mini` inyectando los fragmentos de DuckDuckGo en el context prompt.



\### 4.4 Sistema de Logs en Tiempo Real (Show, Don't Tell)

Todas las funciones principales (research, redacción, envío) deben estar construidas como \*\*Generadores de Python\*\* usando la palabra clave `yield`. Esto alimenta una caja de texto en Gradio que simula una consola de terminal.



\*Ejemplo de output esperado en la UI:\*

`\[00:01] 🟢 Iniciando investigación para: Bright Smile Dental...`

`\[00:02] 🔎 Consultando Google Search via Gemini Grounding...`

`\[00:08] ⚠️ Advertencia: API de Google ocupada. Activando fallback: DuckDuckGo + OpenAI...`

`\[00:11] ✅ Competidor detectado en base de datos: Dentrix.`

`\[00:12] ✍️ Redactando borrador personalizado...`

### 4.4 Parser de JSON

```javascript
function parseJSON(text)
```

1. Limpia backticks de markdown (````json`)
2. Encuentra el primer objeto JSON con regex `\\{\[\\s\\S]\*\\}`
3. Lo parsea con `JSON.parse`
4. Si falla, lanza error para activar el fallback

\---

## 5\. Persistencia de Datos

### 5.1 Storage API

```javascript
const STORAGE\_KEY = "mp-pipeline-data";

async function loadPipeline()
  // window.storage.get(STORAGE\_KEY) → JSON.parse(result.value)
  // Fallback: retorna array vacío si falla

async function savePipeline(prospects)
  // window.storage.set(STORAGE\_KEY, JSON.stringify(prospects))
```

### 5.2 Ciclo de vida

1. **Montaje:** `useEffect` llama `loadPipeline()`, carga prospects, marca `loaded=true`
2. **Cambios:** `useEffect` vigila `\[prospects, loaded]`, guarda automáticamente cuando hay cambios
3. **Datos guardados:** Array completo de prospects con todos sus campos de research

### 5.3 Estructura de un prospect persistido

```javascript
{
  // Identificación
  id: "p\_1711799400000\_a3kf9",     // Timestamp + random suffix
  input: "Bright Smile Dental, Austin TX",  // Input original del usuario
  
  // Data de research (21 campos del JSON de research)
  clinic\_name: "Bright Smile Dental",
  location: "Austin, TX",
  fit\_score: 8,
  priority: "hot",
  current\_software: "Dentrix",
  // ... todos los demás campos del research
  
  // Metadata de pipeline
  pipeline\_stage: "researched",        // new|researched|outreach\_sent|responded|meeting
  researched\_at: "2026-03-18T...",     // ISO timestamp
  outreach\_sent\_at: "2026-03-18T...", // ISO timestamp (si aplica)
  outreach\_subject: "Subject del email enviado"
}
```

\---

## 6\. Parser de CSV

### 6.1 Lógica

```javascript
function parseCSV(text) → \[{input, mode}]
```

1. Separa por `\\n`, filtra vacíos
2. Requiere mínimo 2 líneas (header + 1 dato)
3. Parsea headers: busca columna con "name"/"clinic"/"practice" y "location"/"city"/"address"/"state"
4. Si no encuentra header de nombre, usa la primera columna
5. Combina nombre + location en un solo string: `"Bright Smile Dental, Austin TX"`
6. Limpia quotes simples y dobles

### 6.2 Formatos soportados

```csv
clinic\_name,location
"Bright Smile Dental","Austin, TX"

name,city,state
Bright Smile Dental,Austin,TX

practice,address
Mountain View Dental,Denver CO
```

\---

## 7\. Vista Dashboard

### 7.1 Componente: Dashboard

**Props:**

```javascript
{
  prospects: Array,              // Todos los prospects
  onAddProspect: Function,       // → view="workflow", stage="input"
  onViewProspect: Function,      // → abre prospect en workflow
  onMoveProspect: Function,      // → cambia pipeline\_stage
  onBatchUpload: Function,       // → muestra BatchUploadModal
  batchProgress: Object|null     // {current, total, currentName}
}
```

### 7.2 Barra superior

* Logo "MP" (verde, 20px, weight 800)
* Texto "Dental Prospector"
* Badge "PIPELINE"
* Botón "CSV Import"
* Botón "New Prospect" (primary)

### 7.3 Barra de progreso de batch

Visible solo cuando `batchProgress !== null`. Muestra:

* Spinner animado
* "Batch researching: 3/10"
* Nombre del prospecto actual
* Barra de progreso con ancho proporcional

### 7.4 Métricas del Pipeline (5 cards)

|Métrica|Cálculo|Color|
|-|-|-|
|Total prospects|`prospects.length`|blanco|
|Avg fit score|`sum(fit\_score) / count(has\_score)`|verde ≥7, amber ≥5, red <5|
|Competitors found|Count donde `current\_software` no es "unknown"/"paper-based"|purple|
|Outreach sent|Count con stage `outreach\_sent`, `responded`, o `meeting`|amber|
|Response rate|`responded\_count / sent\_count \* 100`|green|

### 7.5 Kanban Board

**5 columnas:**

|Columna|ID|Color|Significado|
|-|-|-|-|
|New|`new`|blue|Importado pero no investigado|
|Researched|`researched`|purple|IA completó investigación|
|Outreach Sent|`outreach\_sent`|amber|Email aprobado y enviado/copiado|
|Responded|`responded`|accentLight|Prospecto respondió|
|Meeting Booked|`meeting`|accent|Reunión agendada|

Cada columna muestra:

* Header con dot de color, nombre, y count badge
* Contenedor con ProspectCards o "No prospects"

### 7.6 ProspectCard (Kanban)

Muestra por cada prospecto:

* Nombre de la clínica (13px, bold)
* Fit score en mini-ring (28x28px, color por prioridad)
* Location y practitioners
* Badges: prioridad (HOT/WARM/COLD) + competidor si detectado
* **Botones de mover:** fila de mini-botones para mover a cualquier otra columna

### 7.7 Estado vacío

Si no hay prospects, muestra:

* Ícono 🎯 grande
* "Your pipeline is empty"
* Dos botones: "Import CSV" y "Research a Prospect"

\---

## 8\. Modal de Batch Upload

### 8.1 Componente: BatchUploadModal

**Props:** `onClose, onUpload`

### 8.2 Funcionalidad

* **Drop zone:** Drag \& drop de archivo CSV/TXT/TSV
* **File picker:** Click para abrir browser de archivos
* **Textarea manual:** Pegar CSV directamente
* **Auto-preview:** Muestra lista numerada de clínicas detectadas
* **Validación:** Cuenta clínicas, muestra "N clinics detected"
* **Submit:** Botón "Add N Prospects to Pipeline"

### 8.3 Flujo de batch research

1. Modal cierra, prospects se agregan como `pipeline\_stage: "new"` con `fit\_score: null`
2. Loop secuencial: para cada prospect, llama `callClaude(RESEARCH\_PROMPT, query, true)`
3. `batchProgress` se actualiza en cada iteración: `{current: i+1, total: N, currentName}`
4. Si research exitosa: prospect se actualiza con data completa, stage → "researched"
5. Si falla: prospect queda como `fit\_score: 3, priority: "cold", stage: "new"`
6. Al terminar: `batchProgress = null`

\---

## 9\. Vista Workflow (Pipeline de 6 Etapas)

### 9.1 Stepper

Barra superior con:

* Botón "← Pipeline" (vuelve al dashboard)
* Separador vertical
* 6 círculos numerados con estado: done (✓ verde), active (ring verde), pending (gris)
* Líneas conectoras entre círculos (verde si done, gris si no)

### 9.2 Etapa 1: Input (Multi-Fuente)

**5 modos de input:**

|Modo|Label|Placeholder|Hint|
|-|-|-|-|
|`name`|Clinic Name 🏥|"Bright Smile Dental, Austin TX"|Name + city for best results|
|`linkedin`|LinkedIn (in)|"linkedin.com/company/..."|Company or person profile URL|
|`website`|Website 🌐|"brightsmiledental.com"|The clinic's official website|
|`google`|Google Maps 📍|"google.com/maps/place/..."|Google Maps or Business URL|
|`phone`|Phone/NPI 📞|"(512) 555-0123 or NPI 1234567890"|US phone or NPI lookup|

**Auto-detección:** Mientras el usuario escribe/pega, el sistema analiza el input:

* Contiene `linkedin.com` → modo LinkedIn
* Contiene `google.com/maps` o `goo.gl` → modo Google Maps
* Matches URL pattern (`https://`, `.com`, `.dental`, etc.) → modo Website
* Matches phone `(XXX) XXX-XXXX` o NPI `XXXXXXXXXX` → modo Phone/NPI

**Panel de fuentes:** Muestra badges de todas las fuentes que el AI buscará:
Google Business, Clinic Website, LinkedIn, Job Postings, Healthgrades, Zocdoc, Facebook, Local News, ADA Directory, NPI Registry

**Ejemplos clickeables:** 4 ejemplos con ícono del modo, nombre, y subtítulo

### 9.3 Etapa 2: Research

**6 pasos de progreso animado:**

1. "Searching clinic website \& Google Business..."
2. "Scanning LinkedIn for company \& decision makers..."
3. "Checking job postings for software \& hiring signals..."
4. "Analyzing reviews on Healthgrades, Zocdoc, Google..."
5. "Detecting competitor software (Dentrix, Eaglesoft...)..."
6. "Scoring fit \& compiling intelligence report..."

Cada paso tiene: círculo con estado (pending/active/done), label con color adaptivo.
Los pasos avanzan con delays de 500-900ms entre cada uno para dar sensación de progreso real.

**Construcción del query por modo:**

|Modo|Query strategy|
|-|-|
|`name`|"Research thoroughly across multiple sources: website, Google Business, LinkedIn, job postings, Healthgrades/Zocdoc, local news"|
|`linkedin`|"Visit this LinkedIn URL first, then expand to website, Google reviews, job postings"|
|`website`|"Visit this website first, then search Google Business, LinkedIn, Indeed/Glassdoor, Healthgrades/Zocdoc"|
|`google`|"Start from Google Maps/Business listing, then expand to website, LinkedIn, job postings, directories"|
|`phone` (NPI)|"Search NPI registry at npidb.org/nppes.cms.hhs.gov, find provider, then research across all sources"|
|`phone` (number)|"Search Google for this phone number to find clinic, then research across all sources"|

### 9.4 Etapa 3: Profile (Análisis del Prospecto)

**Header card (glow):**

* Badges: prioridad (HOT/WARM/COLD) + tipo (dental/medical)
* Nombre de la clínica (20px, bold)
* Location, practitioners, staff, years in practice
* Google rating + review count
* Online presence badges: Website, Facebook, Instagram, LinkedIn, Socially active
* ScoreRing (88px) con fit score
* Fit reasoning en caja de texto

**Grid de 3 métricas:**

* Best angle (verde)
* Decision maker (amber)
* Current software (color del competidor)

**Card de competidor (si detectado):**

* Ícono con inicial del competidor + nombre + Badge "SWITCHING OPP."
* Confidence level + evidence signals
* Grid 2 columnas: "Their pains" (rojo) vs "Our angles" (verde)
* 4 items por columna con íconos −/+

**Grid de insights (2 columnas):**

* Growth signals (verde) — con ícono 📈
* Pain points (amber) — con ícono ⚡

**Patient reviews insight (cyan):**

* Resumen de 2-3 oraciones de lo que dicen pacientes en reviews recientes

**Hiring / job postings found (amber):**

* Lista de job postings activos y lo que revelan (ícono 💼)

**Research sources (verde):**

* Badges verdes con ✓ por cada fuente utilizada
* Count total de fuentes

**Acciones:** "← Pipeline" + "Generate Outreach →"

### 9.5 Etapa 4: Draft (Generación de Outreach)

**Loading state:** Spinner + "Crafting outreach..." + "Personalizing based on research and competitor analysis"

**Una vez generado:**

**Subject line selector:** 3 opciones clickeables. La seleccionada tiene fondo verde y borde.

**Email preview card:**

* Sender avatar (inicial en círculo verde) + nombre + título
* Subject: input editable
* Body: textarea editable
* Modo read-only después de aprobar

**Personalization hooks card (purple):**

* Lista de hooks con ícono 🎯
* Tone notes en itálica

**Acciones:**

* Pre-aprobación: "← Back" + "✗ Reject" (rojo) + "✓ Approve" (primary)
* Post-aprobación: "✏️ Edit" + "📧 Create Gmail Draft" (primary)
* Badge "✓ APPROVED" visible después de aprobar

**Reject:** Llama `doOutreach()` de nuevo → regenera completamente el draft con otra llamada a la API.

### 9.6 Etapa 5: Review (Human-in-the-Loop)

La etapa de review está integrada en el DraftStage. El flujo es:

1. Draft se genera → se muestra en modo edición
2. Usuario edita subject y/o body si quiere
3. Click "Approve" → cambia a modo read-only con badge "APPROVED"
4. Click "Create Gmail Draft" → procede al envío
5. Si "Reject" → API regenera el draft completo

**Garantías:**

* Todo email pasa por revisión humana antes de cualquier acción
* El usuario ve exactamente qué personalization hooks usó la IA
* El usuario puede editar libremente cualquier texto
* Hay audit trail visible (badge de aprobación)

### 9.7 Etapa 6: Send (Gmail Draft)

**Flujo de envío:**

1. Prospect se actualiza: `pipeline\_stage → "outreach\_sent"`, timestamp, subject guardado
2. Intenta crear draft via Gmail MCP:

```javascript
   callClaude(systemPrompt, userMsg, false, 
     \[{ type: "url", url: "https://gmail.mcp.claude.com/mcp", name: "Gmail" }])
   ```

3. **Si éxito:** Muestra ✓ verde, "Draft created!", "Open Gmail to review and send"
4. **Si falla (OAuth):** Muestra 📋 amber, "Draft saved locally", preview del email, botón "Copy to Clipboard"

**Graceful degradation:** La falla de Gmail no rompe nada. El email queda disponible para copiar y el prospect se marca como outreach\_sent de todas formas.

**Post-envío:** Botón "← Back to Pipeline" retorna al dashboard.

\---

## 10\. Flujo de Datos Completo

### 10.1 Flujo de un prospect individual

```
\[Usuario] 
  → Input: "Bright Smile Dental, Austin TX" (mode: name)
    → doResearch(input, mode)
      → setView("workflow"), setStage("research")
      → Construir query según modo
      → callClaude(RESEARCH\_PROMPT, query, useSearch=true)
        → Claude busca web: Google, LinkedIn, Indeed, Healthgrades...
        → Retorna JSON con 21 campos
      → parseJSON(response) → data
      → Crear prospect: {...data, id, input, pipeline\_stage: "researched", researched\_at}
      → setProspects(prev => \[...prev, prospect])  // triggers auto-save
      → setActiveProspect(prospect)
      → setStage("profile")

\[Usuario ve Profile]
  → Click "Generate Outreach"
    → doOutreach()
      → setStage("draft\_loading")
      → callClaude(OUTREACH\_PROMPT, JSON.stringify(activeProspect), useSearch=false)
        → Claude genera email personalizado basado en research
        → Retorna JSON con subject\_options, body, hooks, tone\_notes
      → parseJSON(response) → draft
      → setDraft(draft)
      → setStage("draft")

\[Usuario edita y aprueba]
  → Click "Approve"
    → doSend({subject, body, sender, title})
      → setApprovedEmail(email)
      → return (no email.send = true aún)
  → Click "Create Gmail Draft"
    → doSend({...email, send: true})
      → updateProspect(id, {pipeline\_stage: "outreach\_sent", outreach\_sent\_at, outreach\_subject})
      → setStage("send")
      → callClaude(gmailPrompt, emailContent, false, \[Gmail MCP])
      → Success → setSendState({sent: true})
      → Fail → setSendState({error: "..."}) → muestra clipboard fallback

\[Usuario] → "Back to Pipeline" → backToDashboard()
```

### 10.2 Flujo de batch

```
\[Usuario] → Click "CSV Import"
  → setShowBatch(true) → muestra BatchUploadModal

\[En modal]
  → Drop/paste CSV → parseCSV(text) → \[{input, mode}]
  → Click "Add N Prospects to Pipeline"
    → doBatchUpload(items)
      → setShowBatch(false)
      → Crear N prospects con pipeline\_stage: "new", fit\_score: null
      → setProspects(prev => \[...prev, ...newProspects])
      → Loop i = 0..N-1:
        → setBatchProgress({current: i+1, total: N, currentName})
        → callClaude(RESEARCH\_PROMPT, multiSourceQuery, useSearch=true)
        → parseJSON → data
        → updateProspect(id, {...data, pipeline\_stage: "researched"})
      → setBatchProgress(null)
```

### 10.3 Flujo de navegación

```
Dashboard:
  "New Prospect"     → view="workflow", stage="input", activeProspect=null
  Click ProspectCard → Si tiene score: view="workflow", stage="profile"
                       Si no: doResearch(prospect.input, "name", prospect.id)
  Move buttons       → updateProspect(id, {pipeline\_stage: newStage})
  "CSV Import"       → showBatch=true

Workflow:
  "← Pipeline"       → backToDashboard() → view="dashboard", reset all states
  Stepper             → visual only (no click navigation)
  "← Back" en Draft   → setStage("profile")
  "Reject" en Draft   → doOutreach() (regenera)
  "Back to Pipeline"  → backToDashboard()
```

\---

## 11\. Manejo de Errores

### 11.1 Falla de API (callClaude)

Si `data.content` no existe, lanza error con `data.error?.message || "API error"`.

### 11.2 Falla de parsing JSON

Si `parseJSON` no encuentra JSON válido en la respuesta, el catch crea un fallback object:

```javascript
{
  clinic\_name: input,
  location: "Unknown",
  fit\_score: 5,
  priority: "warm",
  fit\_reasoning: raw.substring(0, 300),  // primeros 300 chars de la respuesta
  best\_angle: "General outreach",
  // ... arrays vacíos para el resto
  sources\_used: \["Web search (partial results)"]
}
```

### 11.3 Falla de research completa

Si `callClaude` lanza excepción, se crea un prospect de fallback:

```javascript
{
  clinic\_name: input,
  location: "Research failed",
  fit\_score: 5,
  priority: "warm",
  fit\_reasoning: err.message,
  pipeline\_stage: "new"  // NO avanza a "researched"
}
```

### 11.4 Falla de outreach

Si la generación falla, se usa un template de fallback hardcoded con nombre de clínica y location interpolados.

### 11.5 Falla de Gmail

Se muestra UI de clipboard con el email completo listo para copiar.

### 11.6 Falla de storage

`loadPipeline` retorna `\[]`, `savePipeline` logea error pero no bloquea la app.

### 11.7 Falla en batch

Cada prospect falla independientemente. Los que fallan quedan como `fit\_score: 3, priority: "cold", pipeline\_stage: "new"`. Los demás continúan.

\---

## 12\. Archivos del Proyecto

```
prospector-v2.jsx     → Aplicación completa (1213 líneas, single-file React)
README.md             → Documentación, setup, arquitectura, criterios de evaluación
WRITEUP.md            → Design decisions, tradeoffs, future improvements
sample-clinics.csv    → 10 clínicas de ejemplo para batch import
SPEC.md               → Este documento
```

\---

## 13\. Inventario de Componentes (16 componentes)

|#|Componente|Línea|Props|Descripción|
|-|-|-|-|-|
|1|Badge|159|children, color, small|Pill con texto coloreado|
|2|Card|170|children, style, glow, onClick|Contenedor con borde|
|3|Btn|181|children, onClick, primary, disabled, color, loading, icon, small|Botón multi-variante|
|4|ScoreRing|200|score, size|SVG circular de score|
|5|MetricCard|220|label, value, sub, color|Card de métrica dashboard|
|6|ProspectCard|231|prospect, onClick, onMove|Card de prospecto en kanban|
|7|BatchUploadModal|291|onClose, onUpload|Modal de CSV upload|
|8|Dashboard|393|prospects, onAdd, onView, onMove, onBatch, batchProgress|Vista principal pipeline|
|9|Stepper|528|current, onBack|Barra de progreso del workflow|
|10|InputStage|573|onSubmit|Input multi-fuente con auto-detect|
|11|ResearchStage|684|steps|Progreso animado de investigación|
|12|ProfileStage|715|data, onGenerateOutreach, onBack|Análisis completo del prospect|
|13|DraftStage|860|draft, onApprove, onReject, onBack|Review y edición de outreach|
|14|SendStage|944|email, sending, sent, error, onDone|Envío a Gmail o clipboard|
|15|DentalProspector|981|(root)|Componente raíz, router, state manager|

\---

## 14\. Inventario de Funciones Utilitarias (6 funciones)

|Función|Línea|Propósito|
|-|-|-|
|callClaude|103|Llama API de Anthropic con web search y/o MCP opcional|
|parseJSON|119|Extrae y parsea JSON de respuesta de Claude|
|loadPipeline|129|Lee prospects de persistent storage|
|savePipeline|136|Guarda prospects en persistent storage|
|parseCSV|143|Parsea texto CSV a array de prospects|
|INPUT\_MODES|565|Constante con 5 modos de input|

\---

## 15\. Estado Global (DentalProspector)

|State|Tipo|Default|Propósito|
|-|-|-|-|
|view|string|"dashboard"|Vista activa (dashboard/workflow)|
|prospects|array|\[]|Todos los prospects del pipeline|
|activeProspect|object|null|Prospect actualmente seleccionado|
|stage|string|"input"|Etapa del workflow|
|researchSteps|array|\[]|Pasos de progreso del research|
|draft|object|null|Draft de outreach generado|
|approvedEmail|object|null|Email aprobado por el usuario|
|sendState|object|{sending,sent,error}|Estado de envío a Gmail|
|showBatch|boolean|false|Visibilidad del modal de CSV|
|batchProgress|object|null|Progreso del batch research|
|loaded|boolean|false|Flag de carga inicial desde storage|

\---

## 16\. Integraciones Externas





#### &#x20;16.1 Google Generative AI (Gemini)

\- Requiere: `GEMINI\_API\_KEY` (Gratuita via Google AI Studio).

\- Uso: Análisis integral y búsqueda web nativa sin necesidad de scrapers.



#### &#x20;16.2 OpenAI API \& DuckDuckGo (Fallback System)

\- Requiere: `OPENAI\_API\_KEY` y librería `duckduckgo-search` o ddgs.

\- Uso: Red de seguridad. Garantiza que el agente nunca falle en una demo en vivo si Google rechaza la petición.



#### 16.3 Integración de Gmail (Fricción Cero)

\- Requiere: `GMAIL\_SENDER\_EMAIL` y `GMAIL\_APP\_PASSWORD` (Configuradas en Hugging Face Secrets o `.env`).

\- Uso: Envío de correos reales a los evaluadores (Mateo/Elizabeth) usando el módulo nativo `smtplib` de Python. No requiere que el usuario final haga login ni apruebe pantallas de consentimiento de Google Cloud.

### 16.4 Google Fonts CDN

* Plus Jakarta Sans: 300-800 weights
* JetBrains Mono: 400-800 weights
* Carga via `<link>` en el render del componente raíz

### 16.5 Artifact Persistent Storage

* API: `window.storage.get(key)`, `window.storage.set(key, value)`
* Key: `"mp-pipeline-data"`
* Value: JSON stringified array de prospects
* Scope: Personal (no compartido)

\---

## 17\. Criterios de Evaluación vs. Implementación

|Criterio|Qué buscan|Cómo se cumple|
|-|-|-|
|**Relevancia**|Entender clínicas reales|Competidor DB con Dentrix/Eaglesoft/Open Dental/Curve. Scoring basado en ICP real (3-15 practitioners, Mac users, insurance processing). Research busca en directorios dentales reales (Healthgrades, Zocdoc, ADA).|
|**Calidad del agente**|Multi-step, edge cases, errores|Pipeline de 6 etapas con fallbacks en cada punto. Batch processing con manejo individual de errores. Graceful degradation de Gmail a clipboard. Parser JSON con fallback a data parcial.|
|**Shipping instinct**|Funciona de verdad|Web search real, Gmail real, persistent storage real, CSV import funcional. No hay datos hardcodeados en el flujo principal.|
|**Creatividad**|Ángulo inesperado|Competitor detector + switching playbook. Pipeline dashboard con Kanban (no pidieron CRM). Batch CSV (no pidieron escala). Multi-source input con auto-detect (no pidieron NPI/phone). Sources panel de transparencia.|

### Bonus implementados

|Bonus|Estado|Implementación|
|-|-|-|
|Deploy live (URL pública)|✅|Artifact en Claude.ai|
|Human-in-the-loop|✅|Full edit/approve/reject cycle con audit trail|
|Multi-agent chaining|⚠️ Parcial|Research agent → Outreach agent (2 llamadas API separadas con contexto completo)|
|Integración real: Gmail|✅|Gmail MCP para drafts|
|Integración real: Web Search|✅|8 fuentes de búsqueda|
|Evaluation/feedback loop|⚠️ Parcial|Pipeline metrics (response rate) sirven como feedback de qué funciona|





#### &#x20;18. Plan de Ejecución Iterativa (Instrucciones para Agentes de Desarrollo)



Para evitar alucinaciones, código cortado y conflictos estructurales, el desarrollo se dividirá en 4 iteraciones estrictas. El agente de IA no debe avanzar a la siguiente fase hasta que el usuario apruebe y valide la fase actual.



\### 🔴 FASE 1: Esqueleto de Interfaz y Estructura de Datos (Frontend Gradio)

\*\*Objetivo:\*\* Crear la UI interactiva sin conectar las APIs reales todavía.

1\. Construir el layout de Gradio usando `Blocks()`.

2\. Crear dos pestañas principales: "Pipeline / Dashboard" y "Research \& Outreach".

3\. Implementar la interfaz dividida: Columna izquierda (Inputs: URL, Nombre de Clínica, botón de Submit) y Columna derecha (Terminal de Logs interactivo usando `gr.Textbox(interactive=False)`).

4\. Configurar la base de datos local en código (diccionario con los perfiles de competidores: Dentrix, Eaglesoft, etc.).

5\. Crear una función `mock\_research\_generator()` que use `yield` para simular los pasos de investigación y texto falso, verificando que la UI se actualiza en tiempo real.



\### 🟡 FASE 2: Integración del Motor Híbrido de Investigación (Gemini + Fallback)

\*\*Objetivo:\*\* Conectar el "Cerebro" del agente investigador.

1\. Implementar la función `call\_gemini\_research(query)` configurando el SDK de Google y activando la tool de Search Grounding.

2\. Implementar la función `call\_fallback\_research(query)` usando `duckduckgo-search` y `openai`.

3\. Crear el orquestador `do\_research\_agent(clinic\_info)` que intente ejecutar Gemini primero; si falla, atrape la excepción, actualice el log visual (`yield "Fallo Gemini, usando OpenAI..."`) y use el fallback.

4\. Asegurar que el output sea forzado a formato JSON para extraer los campos (fit\_score, pain\_points, current\_software).

5\. Validar conectando esta función a la interfaz creada en la Fase 1.



\### 🔵 FASE 3: Generación de Outreach y Sistema "Human-in-the-Loop"

\*\*Objetivo:\*\* Tomar los datos investigados y convertirlos en un email editable.

1\. Crear el prompt del agente redactor (Outreach Agent) que tome el JSON generado en la Fase 2 y la base de competidores.

2\. En la UI de Gradio, habilitar un bloque debajo del log que contenga:

&#x20;  - Un `gr.Textbox` editable para el Asunto (Subject).

&#x20;  - Un `gr.TextArea` editable para el Cuerpo del correo.

&#x20;  - Un botón de "Aprobar y Preparar Envío".

3\. Conectar la generación del LLM a estos campos para que el usuario (el comercial) pueda leer, modificar y dar el visto bueno final.



\### 🟢 FASE 4: Integración de Envío Real y Batch Processing

\*\*Objetivo:\*\* Conectar el mundo exterior (Gmail real) y procesar múltiples clientes.

1\. Escribir la función `send\_real\_email(destinatario, asunto, cuerpo)` utilizando `smtplib`, manejando la autenticación mediante credenciales de entorno.

2\. Conectar el botón de la Fase 3 ("Aprobar y Enviar") a esta función, actualizando el log con el resultado de éxito o error.

3\. Crear la pestaña "CSV Batch Import" en Gradio.

4\. Implementar una función iterativa que lea un CSV subido, ejecute el agente investigador para cada fila con un `time.sleep(5)` entre filas, y devuelva un dataframe consolidado descargable.

