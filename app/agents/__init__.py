"""
Agentes de IA del sistema Mac Practice Dental Prospector.
"""

from app.agents.prompts import (
    RESEARCH_PROMPT,
    OUTREACH_PROMPT,
    QUERY_TEMPLATES,
    build_research_query,
)
from app.agents.gemini_agent import (
    call_gemini_research,
    call_gemini_outreach,
)
from app.agents.openai_agent import (
    call_openai_research,
    call_openai_outreach,
)

__all__ = [
    "RESEARCH_PROMPT",
    "OUTREACH_PROMPT",
    "QUERY_TEMPLATES",
    "build_research_query",
    "call_gemini_research",
    "call_gemini_outreach",
    "call_openai_research",
    "call_openai_outreach",
]
