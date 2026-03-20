"""
Agente de OpenAI + DuckDuckGo — Motor Fallback.
Ref: SPEC.md § 4.3, § 16.2.

Se activa automáticamente cuando Gemini falla (429, timeout, etc.).
Usa DuckDuckGo para obtener fragmentos web y se los inyecta a gpt-4o-mini.
"""

from typing import Generator

from openai import OpenAI
from ddgs import DDGS

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.agents.prompts import RESEARCH_PROMPT, OUTREACH_PROMPT, EXECUTIVE_SUMMARY_PROMPT
from app.utils.logger import LogAccumulator


def _get_openai_client() -> OpenAI:
    """Crea un cliente de OpenAI con la API key configurada."""
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY not configured. "
            "Add it to your .env file"
        )
    return OpenAI(api_key=OPENAI_API_KEY)


def _search_duckduckgo(
    query: str,
    max_results: int = 8,
    log: LogAccumulator | None = None,
) -> str:
    """
    Busca en DuckDuckGo y retorna los fragmentos concatenados
    como contexto para inyectar en el prompt de OpenAI.

    Args:
        query: Texto de búsqueda.
        max_results: Número máximo de resultados (5-10 recomendado).
        log: Logger para actualizar la UI.

    Returns:
        String con los fragmentos de búsqueda formateados.
    """
    print(f"\n{'='*60}")
    print(f"[DUCKDUCKGO ▶ ENTRADA]")
    print(f"  Query exacto enviado: {repr(query)}")
    print(f"  Máximo resultados:    {max_results}")
    print(f"{'='*60}")

    if log:
        log.add("search", "Searching via DuckDuckGo...")

    try:
        results = DDGS().text(query, max_results=max_results)
    except Exception as e:
        print(f"[DUCKDUCKGO ✗ ERROR]: {e}")
        if log:
            log.add("search", "Web search unavailable, using cached context.")
        return "No web search results available."

    if not results:
        print("[DUCKDUCKGO ✗ SALIDA]: Sin resultados.")
        if log:
            log.add("search", "No web results found, proceeding with AI analysis.")
        return "No web search results available."

    print(f"\n[DUCKDUCKGO ◀ SALIDA] {len(results)} resultados:")
    print(f"{'-'*60}")
    fragments = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "") or "(sin título)"
        body  = r.get("body", "")  or ""
        href  = r.get("href", "")  or ""
        print(f"  [{i:02d}] TÍTULO:  {title}")
        print(f"        URL:     {href}")
        if body:
            print(f"        SNIPPET: {body.replace(chr(10), ' ')}")
        print()
        fragments.append(
            f"[Source {i}] {title}\n"
            f"URL: {href}\n"
            f"{body}\n"
        )

    context = "\n---\n".join(fragments)
    print(f"{'-'*60}")
    print(f"[DUCKDUCKGO] Total chars enviados a OpenAI: {len(context)}")
    print(f"{'='*60}\n")

    if log:
        log.add("success", f"DuckDuckGo: {len(results)} results found.")

    return context


def call_openai_research(
    query: str,
    log: LogAccumulator,
    ddg_query: str | None = None,
) -> Generator[tuple[str, str | None], None, None]:
    """
    Fallback: Busca con DDG + genera análisis con gpt-4o-mini.

    Args:
        query: Query completo para OpenAI (contexto con instrucciones).
        log: Logger acumulador.
        ddg_query: Query limpio para DuckDuckGo (sin instrucciones).
                   Si es None, usa `query` directamente.

    Yields:
        (log_text, raw_response | None)

    Raises:
        Exception: Si OpenAI también falla.
    """
    yield log.add("search", "Searching web sources..."), None

    # Step 1: Search with DuckDuckGo
    search_q = ddg_query if ddg_query else query
    web_context = _search_duckduckgo(search_q, max_results=8, log=log)
    yield log.text, None

    # Step 2: Inject web context and call OpenAI
    print(f"[OPENAI] Sending {len(web_context)} chars of web context to {OPENAI_MODEL}...")

    yield log.add("search", f"Analyzing with {OPENAI_MODEL}..."), None

    client = _get_openai_client()

    augmented_prompt = (
        f"{RESEARCH_PROMPT}\n\n"
        f"## WEB SEARCH RESULTS (use these as your primary source):\n\n"
        f"{web_context}"
    )

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": augmented_prompt},
            {"role": "user", "content": query},
        ],
        temperature=0.3,
        max_tokens=4000,
    )

    raw_text = response.choices[0].message.content

    if not raw_text:
        raise ValueError("OpenAI no devolvió contenido.")

    print(f"[OPENAI] Respuesta recibida: {len(raw_text)} caracteres")

    yield log.add("success", f"Analysis complete ({len(raw_text)} chars)."), raw_text


def call_openai_outreach(
    prospect_json: str,
    log: LogAccumulator,
) -> Generator[tuple[str, str | None], None, None]:
    """
    Fallback para generación de outreach con OpenAI.
    NO necesita búsqueda web — los datos ya están en el prospect.

    Yields:
        (log_text, raw_response | None)
    """
    yield log.add("write", "Generating email with backup AI engine..."), None

    client = _get_openai_client()

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": OUTREACH_PROMPT},
            {"role": "user", "content": prospect_json},
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    raw_text = response.choices[0].message.content

    if not raw_text:
        raise ValueError("OpenAI no devolvió contenido para el outreach.")

    yield log.add("success", f"Email generated ({len(raw_text)} chars)."), raw_text


def call_openai_summary(
    pipeline_json: str,
    log: LogAccumulator,
) -> Generator[tuple[str, str | None], None, None]:
    """
    Fallback: Genera el resumen ejecutivo del pipeline con OpenAI.

    Yields:
        (log_text, raw_response | None)
    """
    yield log.add("search", "Generating executive summary..."), None

    client = _get_openai_client()

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": EXECUTIVE_SUMMARY_PROMPT},
            {"role": "user", "content": pipeline_json},
        ],
        temperature=0.5,
        max_tokens=800,
    )

    raw_text = response.choices[0].message.content

    if not raw_text:
        raise ValueError("OpenAI no devolvió contenido para el resumen ejecutivo.")

    yield log.add("success", f"Summary generated ({len(raw_text)} chars)."), raw_text
