"""
Agente de OpenAI + DuckDuckGo — Motor Fallback.
Ref: SPEC.md § 4.3, § 16.2.

Se activa automáticamente cuando Gemini falla (429, timeout, etc.).
Usa DuckDuckGo para obtener fragmentos web y se los inyecta a gpt-4o-mini.
"""

from typing import Generator

from openai import OpenAI
from duckduckgo_search import DDGS

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.agents.prompts import RESEARCH_PROMPT, OUTREACH_PROMPT
from app.utils.logger import LogAccumulator


def _get_openai_client() -> OpenAI:
    """Crea un cliente de OpenAI con la API key configurada."""
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY no está configurada. "
            "Agrégala a tu archivo .env"
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
    if log:
        log.add("search", "Buscando en DuckDuckGo...")

    try:
        results = DDGS().text(query, max_results=max_results)
    except Exception as e:
        if log:
            log.add("warning", f"DuckDuckGo falló: {e}")
        return "No web search results available."

    if not results:
        if log:
            log.add("warning", "DuckDuckGo no devolvió resultados.")
        return "No web search results available."

    # Formatear los resultados como contexto
    fragments = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        body = r.get("body", "")
        href = r.get("href", "")
        fragments.append(
            f"[Source {i}] {title}\n"
            f"URL: {href}\n"
            f"{body}\n"
        )

    context = "\n---\n".join(fragments)

    if log:
        log.add("success", f"DuckDuckGo: {len(results)} resultados encontrados.")

    return context


def call_openai_research(
    query: str,
    log: LogAccumulator,
) -> Generator[tuple[str, str | None], None, None]:
    """
    Fallback: Busca con DDG + genera análisis con gpt-4o-mini.

    Yields:
        (log_text, raw_response | None)

    Raises:
        Exception: Si OpenAI también falla.
    """
    yield log.add(
        "warning",
        "Activando fallback: DuckDuckGo + OpenAI..."
    ), None

    # Paso 1: Buscar con DuckDuckGo
    web_context = _search_duckduckgo(query, max_results=8, log=log)
    yield log.text, None

    # Paso 2: Inyectar contexto web en el prompt y llamar a OpenAI
    yield log.add(
        "search",
        f"Enviando contexto a {OPENAI_MODEL}..."
    ), None

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

    yield log.add(
        "success",
        f"OpenAI respondió ({len(raw_text)} caracteres)."
    ), raw_text


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
    yield log.add(
        "warning",
        "Generando email con OpenAI (fallback)..."
    ), None

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

    yield log.add(
        "success",
        f"Email generado con OpenAI ({len(raw_text)} caracteres)."
    ), raw_text
