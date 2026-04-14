"""
LangGraph State Management for Pre-Marriage Counseling Agent
Stores conversation history and context
"""
from typing import TypedDict, List, Annotated
from operator import add


class AgentState(TypedDict):
    """
    State structure for the LangGraph agent
    Stores all conversation information and context
    """
    messages: Annotated[List[dict], add]  # Conversation history
    candidate_id: str  # Unique identifier for the candidate
    knowledge_base_summary: str  # Summary of candidate's data
    current_focus_area: str  # Current counseling focus (e.g., "compatibility", "values", "communication")
    questions_asked: Annotated[List[str], add]  # Track questions already asked
    insights_generated: Annotated[List[str], add]  # Generated insights and recommendations
    conversation_stage: str  # Current stage: "initial", "exploring", "deep_dive", "recommendations"
    user_responses: Annotated[List[dict], add]  # Store user responses with context

