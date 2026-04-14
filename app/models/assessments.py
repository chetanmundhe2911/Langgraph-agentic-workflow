"""Collection: assessments — DISC, WPD, ANterbhaya quiz results, scores, answer snapshots."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field
from .base import MongoModel


class AssessmentQuestion(MongoModel):
    question_id: Optional[str] = None
    question_text: Optional[str] = None
    options: List[str] = Field(default_factory=list)
    selected_option: Optional[str] = None
    selected_index: Optional[int] = None
    dimension: Optional[str] = None
    time_to_answer_ms: Optional[int] = None


class AssessmentScores(MongoModel):
    raw_scores: Optional[Dict[str, Any]] = None
    normalized_scores: Optional[Dict[str, Any]] = None
    primary_type: Optional[str] = None
    secondary_type: Optional[str] = None
    overall_score: Optional[float] = None
    percentile: Optional[float] = None


class AssessmentDocument(MongoModel):
    """MongoDB collection: assessments"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    assessment_type: Optional[str] = None  # disc | wpd | anterbhaya | bandhan_quiz | pre_marriage_compat
    taken_at: Optional[datetime] = None
    time_taken_seconds: Optional[int] = None
    platform: Optional[str] = None  # web | mobile | in_person | ai_facilitated
    questions: List[AssessmentQuestion] = Field(default_factory=list)
    scores: Optional[AssessmentScores] = None
    attempt_number: Optional[int] = None
    previous_assessment_id: Optional[str] = None
    score_change: Optional[float] = None
    # Web quiz linkage
    web_quiz_id: Optional[str] = None
    pre_quiz_score: Optional[float] = None
    email_sequence_id: Optional[str] = None
