"""Customer Engagement Automation — web_quiz, email_automation_sequences, call_automation_log, lead_funnel_tracker, automation_rules."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field
from .base import MongoModel


# ---------------------------------------------------------------------------
# web_quiz — 30-question website quiz
# ---------------------------------------------------------------------------

class QuizContact(MongoModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None


class QuizAnswer(MongoModel):
    question_id: Optional[str] = None
    question_text: Optional[str] = None
    question_category: Optional[str] = None
    options: List[str] = Field(default_factory=list)
    selected_option: Optional[str] = None
    selected_index: Optional[int] = None
    score_weight: Optional[float] = None
    dimension: Optional[str] = None
    time_to_answer_ms: Optional[int] = None


class QuizScores(MongoModel):
    total_raw: Optional[float] = None
    normalised: Optional[float] = None
    percentile: Optional[float] = None
    by_dimension: Optional[Dict[str, float]] = None
    top_dimension: Optional[str] = None
    bottom_dimension: Optional[str] = None
    vertical_readiness: Optional[str] = None  # high | medium | low | very_low


class AIProfileSnapshot(MongoModel):
    personality_hint: Optional[str] = None
    top_traits: List[str] = Field(default_factory=list)
    concern_flags: List[str] = Field(default_factory=list)
    recommended_product: Optional[str] = None
    email_sequence_variant: Optional[str] = None
    generated_at: Optional[datetime] = None


class WebQuizDocument(MongoModel):
    """MongoDB collection: web_quiz"""
    id: Optional[str] = Field(None, alias="_id")
    quiz_session_token: Optional[str] = None
    user_id: Optional[str] = None
    vertical: Optional[str] = None
    sub_vertical: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: Optional[str] = None  # started | completed | abandoned
    source_url: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    device_type: Optional[str] = None
    contact: Optional[QuizContact] = None
    answers: List[QuizAnswer] = Field(default_factory=list)
    scores: Optional[QuizScores] = None
    ai_profile_snapshot: Optional[AIProfileSnapshot] = None


# ---------------------------------------------------------------------------
# email_automation_sequences — 10-day AI-personalised drip
# ---------------------------------------------------------------------------

class SequenceEmail(MongoModel):
    day: Optional[int] = None
    send_scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    email_type: Optional[str] = None
    subject: Optional[str] = None
    ai_generated_body: Optional[str] = None
    prompt_used: Optional[str] = None
    personalisation_tokens: Optional[Dict[str, Any]] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    cta_url: Optional[str] = None
    delivery_status: Optional[str] = None
    dimension_focus: Optional[str] = None
    insight_used: Optional[str] = None
    prior_open_signal_used: Optional[bool] = None


class SequenceAnalytics(MongoModel):
    total_sent: Optional[int] = None
    total_opened: Optional[int] = None
    total_clicked: Optional[int] = None
    open_rate: Optional[float] = None
    click_rate: Optional[float] = None
    last_engagement_at: Optional[datetime] = None


class EmailSequenceDocument(MongoModel):
    """MongoDB collection: email_automation_sequences"""
    id: Optional[str] = Field(None, alias="_id")
    quiz_id: Optional[str] = None
    user_id: Optional[str] = None
    email: Optional[str] = None
    vertical: Optional[str] = None
    variant: Optional[str] = None
    enrolment_status: Optional[str] = None  # active | paused | completed | unsubscribed | converted
    enrolled_at: Optional[datetime] = None
    converted_at: Optional[datetime] = None
    conversion_event: Optional[str] = None
    unsubscribed_at: Optional[datetime] = None
    emails: List[SequenceEmail] = Field(default_factory=list)
    analytics: Optional[SequenceAnalytics] = None


# ---------------------------------------------------------------------------
# call_automation_log
# ---------------------------------------------------------------------------

class CallContact(MongoModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    preferred_language: Optional[str] = None
    best_call_time: Optional[str] = None
    timezone: Optional[str] = None


class AICallBrief(MongoModel):
    quiz_score: Optional[float] = None
    top_trait: Optional[str] = None
    email_opens: Optional[int] = None
    email_clicks: Optional[int] = None
    last_email_subject: Optional[str] = None
    suggested_talking_points: List[str] = Field(default_factory=list)
    objection_handling: Optional[Dict[str, str]] = None


class PostCallActions(MongoModel):
    email_triggered: Optional[bool] = None
    email_id: Optional[str] = None
    next_call_scheduled_at: Optional[datetime] = None
    journey_stage_updated: Optional[str] = None
    counsellor_assigned: Optional[bool] = None


class CallRecording(MongoModel):
    file_url: Optional[str] = None
    transcript_url: Optional[str] = None
    ai_call_summary: Optional[str] = None


class CallAutomationDocument(MongoModel):
    """MongoDB collection: call_automation_log"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    quiz_id: Optional[str] = None
    journey_id: Optional[str] = None
    lead_stage: Optional[str] = None
    call_trigger: Optional[str] = None
    contact: Optional[CallContact] = None
    attempt_number: Optional[int] = None
    call_type: Optional[str] = None  # outbound_manual | outbound_auto | inbound
    called_by: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    dialled_at: Optional[datetime] = None
    connected: Optional[bool] = None
    not_connected_reason: Optional[str] = None
    duration_seconds: Optional[int] = None
    ai_brief: Optional[AICallBrief] = None
    outcome: Optional[str] = None  # interested | not_interested | callback_requested | registered | ...
    outcome_notes: Optional[str] = None
    callback_requested_at: Optional[datetime] = None
    objection_raised: Optional[str] = None
    objection_category: Optional[str] = None
    converted_on_call: Optional[bool] = None
    post_call: Optional[PostCallActions] = None
    recording: Optional[CallRecording] = None


# ---------------------------------------------------------------------------
# lead_funnel_tracker
# ---------------------------------------------------------------------------

class EmailStats(MongoModel):
    total_sent: Optional[int] = None
    total_opened: Optional[int] = None
    total_clicked: Optional[int] = None
    last_opened_at: Optional[datetime] = None
    last_clicked_at: Optional[datetime] = None
    sequence_id: Optional[str] = None


class CallStats(MongoModel):
    total_attempts: Optional[int] = None
    total_connected: Optional[int] = None
    last_call_at: Optional[datetime] = None
    last_call_outcome: Optional[str] = None
    next_call_at: Optional[datetime] = None
    do_not_call: Optional[bool] = None


class LeadFunnelDocument(MongoModel):
    """MongoDB collection: lead_funnel_tracker"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    quiz_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    vertical: Optional[str] = None
    lead_source: Optional[str] = None
    created_at: Optional[datetime] = None
    current_stage: Optional[str] = None
    stage_updated_at: Optional[datetime] = None
    is_registered: Optional[bool] = None
    registered_at: Optional[datetime] = None
    has_paid: Optional[bool] = None
    paid_at: Optional[datetime] = None
    has_taken_full_test: Optional[bool] = None
    test_taken_at: Optional[datetime] = None
    has_booked_session: Optional[bool] = None
    session_booked_at: Optional[datetime] = None
    quiz_score: Optional[float] = None
    quiz_vertical_readiness: Optional[str] = None
    quiz_top_dimension: Optional[str] = None
    quiz_recommended_product: Optional[str] = None
    email_variant: Optional[str] = None
    email_stats: Optional[EmailStats] = None
    call_stats: Optional[CallStats] = None
    lead_score: Optional[float] = None
    lead_priority: Optional[str] = None  # hot | warm | cold | lost
    lead_score_updated_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    converted: Optional[bool] = None
    lost_reason: Optional[str] = None


# ---------------------------------------------------------------------------
# automation_rules
# ---------------------------------------------------------------------------

class RuleTrigger(MongoModel):
    event: Optional[str] = None
    condition: Optional[Dict[str, Any]] = None
    delay_minutes: Optional[int] = None
    day_in_sequence: Optional[int] = None


class RuleAction(MongoModel):
    type: Optional[str] = None  # send_email | schedule_call | assign_counsellor | update_stage | ...
    email_template_id: Optional[str] = None
    call_script_id: Optional[str] = None
    stage_update_to: Optional[str] = None
    assign_to: Optional[str] = None
    lead_score_delta: Optional[float] = None


class AutomationRuleDocument(MongoModel):
    """MongoDB collection: automation_rules"""
    id: Optional[str] = Field(None, alias="_id")
    rule_name: Optional[str] = None
    rule_code: Optional[str] = None
    vertical: Optional[str] = None  # career_compass | bandhan | both
    active: Optional[bool] = None
    priority: Optional[int] = None
    trigger: Optional[RuleTrigger] = None
    action: Optional[RuleAction] = None
    executions_total: Optional[int] = None
    executions_last_at: Optional[datetime] = None
    conversion_rate_pct: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
