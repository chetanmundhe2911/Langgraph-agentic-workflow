"""Collection: tertiary_data — References from friends, colleagues, neighbours, teachers."""
from typing import Optional, List
from datetime import datetime
from pydantic import Field
from .base import MongoModel


class ReferenceResponse(MongoModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    question_category: Optional[str] = None  # character | habits | relationships | work_ethic | ...


class ReferenceEntry(MongoModel):
    ref_id: Optional[str] = None
    relationship_type: Optional[str] = None  # close_friend | colleague | neighbour | teacher | mentor | ...
    years_known: Optional[int] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    profession: Optional[str] = None
    how_they_know: Optional[str] = None
    # Contact & consent
    contact_status: Optional[str] = None  # pending | contacted | responded | declined | unreachable
    contact_method: Optional[str] = None  # phone_call | whatsapp | email | in_person
    contacted_at: Optional[datetime] = None
    consent_given: Optional[bool] = None
    # Interview
    interview_mode: Optional[str] = None  # written_form | phone_interview | video_interview | whatsapp_text
    interview_conducted_at: Optional[datetime] = None
    interview_duration_mins: Optional[int] = None
    interview_recording_url: Optional[str] = None
    interview_transcript: Optional[str] = None
    responses: List[ReferenceResponse] = Field(default_factory=list)
    # AI analysis
    ai_sentiment_score: Optional[float] = None
    ai_traits_mentioned: List[str] = Field(default_factory=list)
    ai_concerns_raised: List[str] = Field(default_factory=list)
    ai_credibility_score: Optional[float] = None
    ai_summary: Optional[str] = None


class AggregatedTertiaryInsights(MongoModel):
    total_references_requested: Optional[int] = None
    total_responded: Optional[int] = None
    response_rate_pct: Optional[float] = None
    avg_sentiment_score: Optional[float] = None
    most_common_traits: List[str] = Field(default_factory=list)
    common_concerns: List[str] = Field(default_factory=list)
    overall_tertiary_score: Optional[float] = None
    red_flags: List[str] = Field(default_factory=list)
    ai_synthesis: Optional[str] = None


class TertiaryDataDocument(MongoModel):
    """MongoDB collection: tertiary_data"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    references: List[ReferenceEntry] = Field(default_factory=list)
    aggregated: Optional[AggregatedTertiaryInsights] = None
