"""Collection: operational_data — Psychometrics, tone/behaviour, audio, elevator pitch, CV, photos."""
from typing import Optional, List
from datetime import datetime
from pydantic import Field
from .base import MongoModel


class DISCScores(MongoModel):
    D_score: Optional[float] = None
    I_score: Optional[float] = None
    S_score: Optional[float] = None
    C_score: Optional[float] = None
    primary_type: Optional[str] = None
    secondary_type: Optional[str] = None
    assessed_at: Optional[datetime] = None


class WPDScores(MongoModel):
    score: Optional[float] = None
    purpose_clarity: Optional[str] = None  # very_clear | clear | moderate | unclear | searching
    assessed_at: Optional[datetime] = None


class RelationshipReadiness(MongoModel):
    score: Optional[float] = None
    readiness_tier: Optional[str] = None  # not_ready | early_stage | ready | very_ready
    blockers: List[str] = Field(default_factory=list)


class AnterbhayaScores(MongoModel):
    score: Optional[float] = None
    primary_fears: List[str] = Field(default_factory=list)
    fear_impact: Optional[str] = None  # low | moderate | high | severe
    assessed_at: Optional[datetime] = None


class JeevanYogScores(MongoModel):
    score: Optional[float] = None
    life_path: Optional[str] = None


class PsychometricsData(MongoModel):
    disc: Optional[DISCScores] = None
    wpd: Optional[WPDScores] = None
    relationship_readiness: Optional[RelationshipReadiness] = None
    anterbhaya: Optional[AnterbhayaScores] = None
    jeevan_yog: Optional[JeevanYogScores] = None


class AudioRecording(MongoModel):
    recording_id: Optional[str] = None
    session_type: Optional[str] = None  # counselling | self_intro | elevator_pitch | roleplay | reference_call | meeting
    file_url: Optional[str] = None
    recorded_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    transcript_url: Optional[str] = None


class ToneAnalysis(MongoModel):
    anger_level: Optional[float] = None
    politeness_level: Optional[float] = None
    warmth_love_level: Optional[float] = None
    confidence_level: Optional[float] = None
    anxiety_level: Optional[float] = None
    dominance_level: Optional[float] = None
    empathy_level: Optional[float] = None
    communication_style: Optional[str] = None  # assertive | passive | aggressive | passive_aggressive | collaborative
    conflict_resolution_style: Optional[str] = None
    eq_score: Optional[float] = None
    analysed_at: Optional[datetime] = None


class ElevatorPitch(MongoModel):
    video_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    recorded_at: Optional[datetime] = None
    ai_feedback: Optional[str] = None


class BehaviorAnalysis(MongoModel):
    overall_behavior_tags: List[str] = Field(default_factory=list)
    conflict_resolution_style: Optional[str] = None
    emotional_arc: Optional[str] = None
    social_behavior_patterns: List[str] = Field(default_factory=list)


class CVData(MongoModel):
    file_url: Optional[str] = None
    parsed_skills: List[str] = Field(default_factory=list)
    parsed_summary: Optional[str] = None
    uploaded_at: Optional[datetime] = None


class PhotoEntry(MongoModel):
    url: Optional[str] = None
    photo_type: Optional[str] = None  # main | formal | casual | family | event
    ai_grooming_score: Optional[float] = None


class OperationalDataDocument(MongoModel):
    """MongoDB collection: operational_data"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    psychometrics: Optional[PsychometricsData] = None
    audio_recordings: List[AudioRecording] = Field(default_factory=list)
    tone_analysis: Optional[ToneAnalysis] = None
    elevator_pitch: Optional[ElevatorPitch] = None
    behavior: Optional[BehaviorAnalysis] = None
    cv: Optional[CVData] = None
    photos: List[PhotoEntry] = Field(default_factory=list)
