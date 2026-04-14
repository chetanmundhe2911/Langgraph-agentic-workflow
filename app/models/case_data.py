"""Collection: case_data — Candidate proposals, compatibility scores, meetings, decisions."""
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import Field
from .base import MongoModel, TimestampMixin


class CandidateBio(MongoModel):
    bio_data_url: Optional[str] = None
    kundali_url: Optional[str] = None
    horoscope_details: Optional[str] = None
    matrimony_site: Optional[str] = None
    matrimony_profile_id: Optional[str] = None
    photos: List[Dict[str, str]] = Field(default_factory=list)
    intro_video_url: Optional[str] = None


class CandidateSecondary(MongoModel):
    social_media: List[Dict[str, str]] = Field(default_factory=list)
    ai_analysis_summary: Optional[str] = None


class CompatibilityScores(MongoModel):
    overall_score: Optional[float] = None
    disc_compatibility: Optional[float] = None
    values_score: Optional[float] = None
    family_score: Optional[float] = None
    financial_score: Optional[float] = None
    health_score: Optional[float] = None
    lifestyle_score: Optional[float] = None
    astro_score: Optional[float] = None
    breakdown_notes: Optional[str] = None


class MeetingEntry(MongoModel):
    meeting_type: Optional[str] = None  # telephonic | video | face_to_face
    meeting_date: Optional[datetime] = None
    location: Optional[str] = None
    outcome: Optional[str] = None
    report_id: Optional[str] = None


class DiscussionQuestion(MongoModel):
    question: Optional[str] = None
    category: Optional[str] = None  # values | family | finance | health | lifestyle
    is_practiced: Optional[bool] = None


class CaseDecision(MongoModel):
    go_ahead: Optional[bool] = None
    decided_at: Optional[datetime] = None
    reason: Optional[str] = None
    next_step: Optional[str] = None


class CaseDataDocument(TimestampMixin):
    """MongoDB collection: case_data"""
    case_number: Optional[str] = None
    user_id: Optional[str] = None
    candidate_user_id: Optional[str] = None
    candidate_name: Optional[str] = None
    status: Optional[str] = None  # active | paused | archived | matched | rejected | completed
    counsellor_id: Optional[str] = None
    candidate_bio: Optional[CandidateBio] = None
    candidate_secondary: Optional[CandidateSecondary] = None
    compatibility: Optional[CompatibilityScores] = None
    meetings: List[MeetingEntry] = Field(default_factory=list)
    discussion_questions: List[DiscussionQuestion] = Field(default_factory=list)
    decision: Optional[CaseDecision] = None
    received_bio_id: Optional[str] = None
