"""Collections: customer_journey, communications, external_memory."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field
from .base import MongoModel


# ---------------------------------------------------------------------------
# customer_journey — Full funnel: Website → Quiz → Payment → Meetings → Completed
# ---------------------------------------------------------------------------

class WebsiteInfo(MongoModel):
    first_visit_at: Optional[datetime] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None


class QuizJourneyInfo(MongoModel):
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    assessment_id: Optional[str] = None
    quiz_id: Optional[str] = None
    quiz_started_at: Optional[datetime] = None
    quiz_completed_at: Optional[datetime] = None
    quiz_score: Optional[float] = None
    vertical_readiness: Optional[str] = None  # high | medium | low


class EmailJourneyInfo(MongoModel):
    initial_static_sent_at: Optional[datetime] = None
    customised_score_email_sent_at: Optional[datetime] = None
    last_email_sent_at: Optional[datetime] = None
    last_email_replied_at: Optional[datetime] = None


class EmailAutomationInfo(MongoModel):
    sequence_id: Optional[str] = None
    current_day: Optional[int] = None
    total_opens: Optional[int] = None
    total_clicks: Optional[int] = None


class RegistrationInfo(MongoModel):
    registered_at: Optional[datetime] = None


class PaymentInfo(MongoModel):
    payment_made_at: Optional[datetime] = None
    plan_purchased: Optional[str] = None
    amount_inr: Optional[int] = None


class DashboardInfo(MongoModel):
    full_access_granted_at: Optional[datetime] = None


class JourneyMilestones(MongoModel):
    test_completed_at: Optional[datetime] = None
    reports_downloaded_at: Optional[datetime] = None
    self_study_viewed_at: Optional[datetime] = None
    counselling_booked_at: Optional[datetime] = None
    first_case_created_at: Optional[datetime] = None
    first_meeting_at: Optional[datetime] = None
    pre_marriage_test_at: Optional[datetime] = None
    feedback_shared_at: Optional[datetime] = None


class FollowupTracking(MongoModel):
    next_followup_date: Optional[datetime] = None
    days_since_last_contact: Optional[int] = None
    followup_count: Optional[int] = None


class CustomerJourneyDocument(MongoModel):
    """MongoDB collection: customer_journey"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    started_at: Optional[datetime] = None
    current_stage: Optional[str] = None
    website: Optional[WebsiteInfo] = None
    quiz: Optional[QuizJourneyInfo] = None
    emails: Optional[EmailJourneyInfo] = None
    email_automation: Optional[EmailAutomationInfo] = None
    registration: Optional[RegistrationInfo] = None
    payment: Optional[PaymentInfo] = None
    dashboard: Optional[DashboardInfo] = None
    milestones: Optional[JourneyMilestones] = None
    followup: Optional[FollowupTracking] = None
    general_followup_cycle_months: Optional[int] = None


# ---------------------------------------------------------------------------
# communications — Emails, calls, WhatsApp, follow-ups
# ---------------------------------------------------------------------------

class EmailComm(MongoModel):
    subject: Optional[str] = None
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    template_id: Optional[str] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None


class CallComm(MongoModel):
    called_by: Optional[str] = None
    duration_seconds: Optional[int] = None
    outcome: Optional[str] = None  # connected | no_answer | callback_requested | voicemail
    notes: Optional[str] = None
    recording_url: Optional[str] = None


class AIGeneration(MongoModel):
    prompt_id: Optional[str] = None
    context_used: List[str] = Field(default_factory=list)
    personalization_score: Optional[float] = None


class CommunicationDocument(MongoModel):
    """MongoDB collection: communications"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    journey_id: Optional[str] = None
    channel: Optional[str] = None  # email | sms | whatsapp | phone_call | in_app
    direction: Optional[str] = None  # outbound | inbound | internal
    comm_type: Optional[str] = None  # static | ai_generated | manual | automated_followup
    sent_at: Optional[datetime] = None
    email: Optional[EmailComm] = None
    call: Optional[CallComm] = None
    ai_generation: Optional[AIGeneration] = None
    delivery_status: Optional[str] = None  # sent | delivered | bounced | failed | spam
    bounce_reason: Optional[str] = None
    next_comm_scheduled_at: Optional[datetime] = None
    # Automation linkage
    sequence_id: Optional[str] = None
    sequence_day: Optional[int] = None
    quiz_id: Optional[str] = None
    automation_rule_id: Optional[str] = None
    call_log_id: Optional[str] = None
    lead_funnel_id: Optional[str] = None


# ---------------------------------------------------------------------------
# external_memory — Vector store references, embedding pointers, RAG chunks
# ---------------------------------------------------------------------------

class ExternalMemoryDocument(MongoModel):
    """MongoDB collection: external_memory"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    memory_type: Optional[str] = None  # user_profile | conversation | report_insight | knowledge_base | case_context
    content_text: Optional[str] = None
    content_summary: Optional[str] = None
    source_collection: Optional[str] = None
    source_document_id: Optional[str] = None
    embedding_model: Optional[str] = None
    embedding_vector: Optional[List[float]] = None
    vector_db_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    relevance_domain: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    access_count: Optional[int] = None
    ttl_days: Optional[int] = None
    is_active: Optional[bool] = None
