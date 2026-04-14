"""Collections: ai_agents_log, orchestrator_sessions, counselling_sessions."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field
from .base import MongoModel


# ---------------------------------------------------------------------------
# ai_agents_log — Execution logs for all AI agents
# ---------------------------------------------------------------------------

class AgentLogDocument(MongoModel):
    """MongoDB collection: ai_agents_log"""
    id: Optional[str] = Field(None, alias="_id")
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    agent_name: Optional[str] = None  # HealthAgent | PsychologyAgent | etc.
    agent_version: Optional[str] = None
    execution_start: Optional[datetime] = None
    execution_end: Optional[datetime] = None
    duration_ms: Optional[int] = None
    status: Optional[str] = None  # running | success | failed | skipped
    input_data_sources: List[str] = Field(default_factory=list)
    input_snapshot: Optional[Dict[str, Any]] = None
    output_result: Optional[Dict[str, Any]] = None
    prompt_id: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    agent_type_ref: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None
    fallback_used: Optional[bool] = None


# ---------------------------------------------------------------------------
# orchestrator_sessions — Session orchestration, agent chains, decision gate
# ---------------------------------------------------------------------------

class AgentChainEntry(MongoModel):
    agent_name: Optional[str] = None
    log_id: Optional[str] = None
    order: Optional[int] = None
    outcome: Optional[str] = None


class DecisionGate(MongoModel):
    input_summary: Optional[str] = None
    action_taken: Optional[str] = None  # generate_report | request_more_data | escalate_to_counsellor | match_candidate
    confidence_score: Optional[float] = None
    reasoning: Optional[str] = None


class OrchestratorOutput(MongoModel):
    reports_generated: List[str] = Field(default_factory=list)
    final_summary: Optional[str] = None
    action_items: List[str] = Field(default_factory=list)


class OrchestratorSessionDocument(MongoModel):
    """MongoDB collection: orchestrator_sessions"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    case_id: Optional[str] = None
    trigger: Optional[str] = None  # report_generation | case_matching | counsellor_request | user_chat
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: Optional[str] = None  # running | completed | failed | partial
    agent_chain: List[AgentChainEntry] = Field(default_factory=list)
    decision_gate: Optional[DecisionGate] = None
    output: Optional[OrchestratorOutput] = None
    memory_chunks_used: List[str] = Field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# counselling_sessions — Session notes, audio, action items, outcomes
# ---------------------------------------------------------------------------

class SessionRecording(MongoModel):
    file_url: Optional[str] = None
    transcript_url: Optional[str] = None
    ai_summary: Optional[str] = None
    consent_given: Optional[bool] = None


class CounsellingSessionDocument(MongoModel):
    """MongoDB collection: counselling_sessions"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    counsellor_id: Optional[str] = None
    session_type: Optional[str] = None  # initial | followup | case_review | face_to_face_prep | post_meeting
    session_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    platform: Optional[str] = None  # in_person | phone | video_call
    agenda: Optional[str] = None
    session_notes: Optional[str] = None
    key_insights: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    next_session_date: Optional[datetime] = None
    recording: Optional[SessionRecording] = None
    outcome_rating: Optional[int] = None
    user_satisfaction: Optional[int] = None
    profile_update_triggered: Optional[bool] = None
    reports_updated: List[str] = Field(default_factory=list)
