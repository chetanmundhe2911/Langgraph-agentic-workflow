"""
Helper functions for RAG-based knowledge retrieval in agents.

Data flow:
  Agent → get_agent_specific_content(state, domain, query)
    ├─ RAG store  → retrieves relevant PDF text chunks (existing)
    └─ Structured → renders MongoDB v5 fields relevant to this agent (new)
  Combined text is returned to the agent for its LLM prompt.
"""
from typing import Optional, Dict, Any


def get_agent_specific_content(
    state: Dict[str, Any],
    agent_domain: str,
    user_query: Optional[str] = None
) -> str:
    """
    Get domain-specific content from knowledge base using RAG + structured MongoDB data.

    Combines two sources (when available):
      1. RAG chunks from indexed PDF reports (existing behaviour, unchanged)
      2. Structured v5 MongoDB fields filtered by agent domain (new)

    Args:
        state: AgentState dictionary
        agent_domain: Domain of the agent (e.g., "behaviour_psychology")
        user_query: Optional user query to focus retrieval

    Returns:
        Combined relevant content for the agent

    Raises:
        ValueError: If neither RAG store nor structured data is available
    """
    knowledge_base = state.get("knowledge_base")

    if not knowledge_base:
        raise ValueError(
            f"Knowledge base not found in state. Cannot retrieve content for agent '{agent_domain}'."
        )

    parts = []

    # ── Source 1: RAG from PDF reports (existing, unchanged) ─────────
    if hasattr(knowledge_base, "rag_store") and knowledge_base.rag_store:
        rag_content = knowledge_base.rag_store.get_summary_for_agent(
            agent_domain=agent_domain,
            user_query=user_query or "",
        )
        if rag_content and rag_content.strip():
            parts.append(rag_content)

    # ── Source 2: Structured MongoDB v5 data (new) ───────────────────
    if hasattr(knowledge_base, "get_structured_context"):
        structured_content = knowledge_base.get_structured_context(
            agent_domain=agent_domain,
        )
        if structured_content and structured_content.strip():
            parts.append(structured_content)

    # ── Fallback: raw report content if neither RAG nor structured data ─
    if not parts:
        if hasattr(knowledge_base, "raw_report_content") and knowledge_base.raw_report_content:
            raw = knowledge_base.raw_report_content
            if len(raw) > 30000:
                raw = raw[:30000] + "\n[... truncated ...]"
            parts.append(raw)

    if not parts:
        raise ValueError(
            f"No data available for agent '{agent_domain}'. "
            "Ensure RAG store is loaded (use_rag=True) or structured data is populated."
        )

    return "\n\n".join(parts)
