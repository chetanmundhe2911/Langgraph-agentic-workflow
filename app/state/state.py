from typing import TypedDict, List, Annotated, Dict, Any, Union, Literal, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    Global state for the multi-agent system.
    
    Available agents:
    - behaviour_psychology: Psychological and behavioral analysis
    - career_profession: Career and professional stability analysis
    - medical_lifestyle: Medical history and lifestyle analysis
    - health_wellness: Health and wellness assessment
    - family_dynamics: Family structure and dynamics analysis
    - character_values: Character and values assessment
    - education_readiness: Educational background analysis
    - social_philosophy: Social worldview analysis
    - hygiene_lifestyle: Hygiene and lifestyle compatibility
    - life_philosophy: Life purpose and meaning analysis
    - religious_values: Religious beliefs and practices
    - political_alignment: Political orientation analysis
    """
    # Conversation history
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Current active agent (one of the 12 available agents)
    current_agent: str
    
    # Agent chain tracking for multi-agent workflows
    agent_chain: List[str]  # List of agents that have been executed in this request
    next_agents: List[str]  # List of agents to execute next (for chaining)
    should_continue: bool  # Whether to continue to next agent or end
    
    # Candidate ID for session management
    candidate_id: str
    
    # Shared context/knowledge base summary
    knowledge_base_summary: str
    
    # Knowledge base object (for RAG access)
    knowledge_base: Optional[Any]  # CandidateKnowledgeBase object (not serialized in state)
    
    # Agent-specific state storage (to keep global state clean)
    # Keys are agent names (e.g., "behaviour_psychology", "career_profession", etc.)
    # Values are dicts containing agent-specific state (e.g., {"preliminary_analysis": "...", "profile": "..."})
    agent_data: Dict[str, Any]

    # Legacy fields for backward compatibility
    # These can be used by agents that need them, but prefer storing in agent_data
    questions_asked: List[str]
    user_responses: List[Dict[str, str]]
    insights_generated: List[str]
    conversation_stage: str
    current_focus_area: str

    # ── New fields for MongoDB v5 schema integration (all optional) ──
    # User identity — ObjectId string from users collection
    user_id: Optional[str]
    # Orchestrator session tracking (written to orchestrator_sessions collection)
    session_id: Optional[str]
    # Case context (if user is evaluating a candidate)
    case_id: Optional[str]
    # What triggered this session: user_chat | report_generation | case_matching | counsellor_request
    trigger: Optional[str]
    # Individual journey phase: 1-4 (from individual_journey_tracker)
    journey_phase: Optional[int]
    # MongoDB service reference (not serialized)
    mongo_service: Optional[Any]
