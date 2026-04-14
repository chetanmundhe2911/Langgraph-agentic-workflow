"""Pre-Marriage Individual Journey collections — journey tracker, session scripts, bio data, meeting prep, candidate bio, meeting sessions, proposal decisions."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field
from .base import MongoModel, TimestampMixin


# ---------------------------------------------------------------------------
# individual_journey_tracker — Master journey doc: phases 1-4
# ---------------------------------------------------------------------------

class Phase1SelfUnderstanding(MongoModel):
    status: Optional[str] = None  # not_started | in_progress | completed
    test_completed: Optional[bool] = None
    test_completed_at: Optional[datetime] = None
    assessment_ids: List[str] = Field(default_factory=list)
    reports_generated: List[str] = Field(default_factory=list)
    reports_read_at: Optional[datetime] = None
    self_study_videos_watched: List[str] = Field(default_factory=list)
    videos_completed_at: Optional[datetime] = None


class Phase2CounsellorTraining(MongoModel):
    status: Optional[str] = None
    counselling_session_ids: List[str] = Field(default_factory=list)
    total_sessions: Optional[int] = None
    ai_profile_trained: Optional[bool] = None
    ai_profile_trained_at: Optional[datetime] = None
    bio_data_id: Optional[str] = None
    bio_data_finalised: Optional[bool] = None
    meeting_prep_training_id: Optional[str] = None
    meeting_prep_completed: Optional[bool] = None


class Phase3CandidateEvaluation(MongoModel):
    status: Optional[str] = None
    active_case_ids: List[str] = Field(default_factory=list)
    total_cases_evaluated: Optional[int] = None
    cases_accepted: Optional[int] = None
    cases_rejected: Optional[int] = None
    cases_pending: Optional[int] = None


class Phase4Decision(MongoModel):
    status: Optional[str] = None  # not_started | in_progress | concluded
    final_case_id: Optional[str] = None
    pre_marriage_compat_test_id: Optional[str] = None
    concluded_at: Optional[datetime] = None
    outcome: Optional[str] = None  # matched | not_matched | paused | on_hold


class IndividualJourneyDocument(TimestampMixin):
    """MongoDB collection: individual_journey_tracker"""
    user_id: Optional[str] = None
    gender: Optional[str] = None
    vertical: Optional[str] = None
    phase1: Optional[Phase1SelfUnderstanding] = None
    phase2: Optional[Phase2CounsellorTraining] = None
    phase3: Optional[Phase3CandidateEvaluation] = None
    phase4: Optional[Phase4Decision] = None


# ---------------------------------------------------------------------------
# counsellor_session_scripts — Diarised transcripts with emotion tagging
# ---------------------------------------------------------------------------

class ScriptTurn(MongoModel):
    turn_number: Optional[int] = None
    speaker: Optional[str] = None  # counsellor | candidate | both
    speaker_id: Optional[str] = None
    start_time_sec: Optional[float] = None
    end_time_sec: Optional[float] = None
    text: Optional[str] = None
    emotion_detected: Optional[str] = None
    emotion_confidence: Optional[float] = None
    key_topic: Optional[str] = None
    is_key_insight: Optional[bool] = None
    is_action_item: Optional[bool] = None


class ScriptAIAnalysis(MongoModel):
    key_insights: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    dominant_topics: List[str] = Field(default_factory=list)
    emotional_arc: Optional[str] = None
    candidate_openness_score: Optional[float] = None
    counsellor_effectiveness_score: Optional[float] = None
    red_flags_surfaced: List[str] = Field(default_factory=list)
    profile_updates_suggested: List[Dict[str, Any]] = Field(default_factory=list)


class CorpusMetadata(MongoModel):
    is_approved_for_training: Optional[bool] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    anonymised: Optional[bool] = None
    anonymised_text_url: Optional[str] = None
    training_tags: List[str] = Field(default_factory=list)


class TranscriptInfo(MongoModel):
    raw_text: Optional[str] = None
    language: Optional[str] = None
    generated_at: Optional[datetime] = None
    word_error_rate: Optional[float] = None


class SessionScriptDocument(MongoModel):
    """MongoDB collection: counsellor_session_scripts"""
    id: Optional[str] = Field(None, alias="_id")
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    counsellor_id: Optional[str] = None
    journey_id: Optional[str] = None
    session_sequence_number: Optional[int] = None
    session_type: Optional[str] = None
    recorded_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    transcript: Optional[TranscriptInfo] = None
    script: List[ScriptTurn] = Field(default_factory=list)
    ai_analysis: Optional[ScriptAIAnalysis] = None
    corpus: Optional[CorpusMetadata] = None


# ---------------------------------------------------------------------------
# bio_data_profiles — AI-managed versioned bio data
# ---------------------------------------------------------------------------

class BioDataContent(MongoModel):
    full_name: Optional[str] = None
    dob: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    complexion: Optional[str] = None
    religion: Optional[str] = None
    caste: Optional[str] = None
    gotra: Optional[str] = None
    native_place: Optional[str] = None
    current_location: Optional[str] = None
    education_summary: Optional[str] = None
    profession_summary: Optional[str] = None
    income_range: Optional[str] = None
    family_summary: Optional[str] = None
    about_me: Optional[str] = None
    hobbies: List[str] = Field(default_factory=list)
    partner_expectations: Optional[str] = None
    photo_urls: List[str] = Field(default_factory=list)
    contact_for_bio: Optional[str] = None


class AISuggestion(MongoModel):
    suggestion_id: Optional[str] = None
    field_path: Optional[str] = None
    original_text: Optional[str] = None
    suggested_text: Optional[str] = None
    reason: Optional[str] = None
    personality_alignment_score: Optional[float] = None
    status: Optional[str] = None  # pending | accepted | rejected | modified
    candidate_response: Optional[str] = None
    resolved_at: Optional[datetime] = None


class AIAuthenticity(MongoModel):
    personality_match_score: Optional[float] = None
    gaps_identified: List[str] = Field(default_factory=list)
    overstatements: List[str] = Field(default_factory=list)
    analysed_at: Optional[datetime] = None


class CounsellorReview(MongoModel):
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    notes: Optional[str] = None
    approved: Optional[bool] = None


class BioDataProfileDocument(MongoModel):
    """MongoDB collection: bio_data_profiles"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    journey_id: Optional[str] = None
    version: Optional[int] = None
    is_current: Optional[bool] = None
    created_at: Optional[datetime] = None
    status: Optional[str] = None  # draft | ai_reviewed | candidate_reviewed | counsellor_approved | finalised
    content: Optional[BioDataContent] = None
    ai_suggestions: List[AISuggestion] = Field(default_factory=list)
    ai_authenticity: Optional[AIAuthenticity] = None
    counsellor_review: Optional[CounsellorReview] = None


# ---------------------------------------------------------------------------
# meeting_preparation_training — AI trains candidate for meetings
# ---------------------------------------------------------------------------

class QuestionToAsk(MongoModel):
    question_id: Optional[str] = None
    question_text: Optional[str] = None
    category: Optional[str] = None  # family | finance | career | values | health | lifestyle | religion | ...
    priority: Optional[str] = None  # must_ask | should_ask | nice_to_have
    why_important: Optional[str] = None
    red_flag_probe: Optional[bool] = None
    ai_source: Optional[str] = None
    practiced: Optional[bool] = None


class AnswerPattern(MongoModel):
    question_id: Optional[str] = None
    green_flag_answers: List[str] = Field(default_factory=list)
    yellow_flag_answers: List[str] = Field(default_factory=list)
    red_flag_answers: List[str] = Field(default_factory=list)
    follow_up_if_yellow: Optional[str] = None


class PracticeSession(MongoModel):
    practice_id: Optional[str] = None
    practiced_at: Optional[datetime] = None
    mode: Optional[str] = None  # text_chat | voice | video
    questions_practiced: List[str] = Field(default_factory=list)
    ai_feedback: Optional[str] = None
    confidence_score: Optional[float] = None
    areas_for_improvement: List[str] = Field(default_factory=list)
    recording_url: Optional[str] = None


class MeetingGuidance(MongoModel):
    setting_tips: List[str] = Field(default_factory=list)
    opening_script: Optional[str] = None
    body_language_tips: List[str] = Field(default_factory=list)
    topics_to_avoid: List[str] = Field(default_factory=list)
    how_to_close: Optional[str] = None
    ai_confidence_rating: Optional[float] = None


class TrainingSummary(MongoModel):
    questions_mastered: Optional[int] = None
    questions_still_weak: Optional[int] = None
    overall_readiness: Optional[str] = None  # not_ready | needs_more_practice | ready | very_ready
    completed_at: Optional[datetime] = None


class MeetingPrepDocument(MongoModel):
    """MongoDB collection: meeting_preparation_training"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    journey_id: Optional[str] = None
    case_id: Optional[str] = None
    training_type: Optional[str] = None  # general_prep | case_specific_prep | post_meeting_debrief_prep
    created_at: Optional[datetime] = None
    status: Optional[str] = None
    questions_to_ask: List[QuestionToAsk] = Field(default_factory=list)
    answer_patterns: List[AnswerPattern] = Field(default_factory=list)
    practice_sessions: List[PracticeSession] = Field(default_factory=list)
    meeting_guidance: Optional[MeetingGuidance] = None
    summary: Optional[TrainingSummary] = None


# ---------------------------------------------------------------------------
# candidate_bio_received — Received opposite-party bio with AI extraction & social scraping
# ---------------------------------------------------------------------------

class RawBioInput(MongoModel):
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    manual_text: Optional[str] = None


class ExtractedBioFields(MongoModel):
    full_name: Optional[str] = None
    dob_or_age: Optional[str] = None
    height: Optional[str] = None
    complexion: Optional[str] = None
    religion: Optional[str] = None
    caste: Optional[str] = None
    gotra: Optional[str] = None
    nakshatra: Optional[str] = None
    rashi: Optional[str] = None
    manglik: Optional[str] = None
    native_place: Optional[str] = None
    current_location: Optional[str] = None
    education: Optional[str] = None
    profession: Optional[str] = None
    income_range: Optional[str] = None
    family_description: Optional[str] = None
    hobbies: List[str] = Field(default_factory=list)
    partner_expectations: Optional[str] = None
    contact_info: Optional[str] = None
    photos_extracted: List[str] = Field(default_factory=list)
    extraction_confidence: Optional[float] = None
    extraction_issues: List[str] = Field(default_factory=list)
    extracted_at: Optional[datetime] = None


class SocialScrapeData(MongoModel):
    scrape_initiated_at: Optional[datetime] = None
    scrape_completed_at: Optional[datetime] = None
    platforms_scraped: List[str] = Field(default_factory=list)
    facebook: Optional[Dict[str, Any]] = None
    instagram: Optional[Dict[str, Any]] = None
    linkedin: Optional[Dict[str, Any]] = None
    digital_presence_score: Optional[float] = None
    authenticity_score: Optional[float] = None
    consistency_score: Optional[float] = None
    red_flags: List[str] = Field(default_factory=list)
    ai_summary: Optional[str] = None


class OneToOneComparison(MongoModel):
    match_score: Optional[float] = None
    field_comparisons: Optional[Dict[str, Any]] = None
    compatibility_highlights: List[str] = Field(default_factory=list)
    compatibility_concerns: List[str] = Field(default_factory=list)
    ai_recommendation: Optional[str] = None
    compared_at: Optional[datetime] = None


class CandidateBioReceivedDocument(MongoModel):
    """MongoDB collection: candidate_bio_received"""
    id: Optional[str] = Field(None, alias="_id")
    case_id: Optional[str] = None
    submitted_by_user_id: Optional[str] = None
    candidate_registered: Optional[bool] = None
    candidate_user_id: Optional[str] = None
    received_at: Optional[datetime] = None
    source: Optional[str] = None  # matrimony_site | family_contact | self_submitted | social_media | counsellor_suggested
    raw_bio: Optional[RawBioInput] = None
    extracted: Optional[ExtractedBioFields] = None
    social_scrape: Optional[SocialScrapeData] = None
    comparison: Optional[OneToOneComparison] = None


# ---------------------------------------------------------------------------
# meeting_sessions — AI-listened meetings: transcripts, Q coverage, flags
# ---------------------------------------------------------------------------

class AIListening(MongoModel):
    audio_url: Optional[str] = None
    recording_consent_given: Optional[bool] = None
    transcript: Optional[TranscriptInfo] = None


class MeetingScriptTurn(MongoModel):
    turn_number: Optional[int] = None
    speaker: Optional[str] = None  # user | candidate | both
    start_time_sec: Optional[float] = None
    end_time_sec: Optional[float] = None
    text: Optional[str] = None
    emotion: Optional[str] = None
    question_from_prep: Optional[str] = None
    flag_type: Optional[str] = None  # none | green_flag | yellow_flag | red_flag
    flag_note: Optional[str] = None


class QuestionCoverage(MongoModel):
    question_id: Optional[str] = None
    asked: Optional[bool] = None
    answer_received: Optional[str] = None
    flag: Optional[str] = None  # green | yellow | red | not_asked
    follow_up_needed: Optional[bool] = None


class MeetingAIAnalysis(MongoModel):
    overall_meeting_vibe: Optional[str] = None
    chemistry_score: Optional[float] = None
    user_confidence_score: Optional[float] = None
    candidate_openness_score: Optional[float] = None
    questions_asked_count: Optional[int] = None
    questions_skipped: List[str] = Field(default_factory=list)
    topics_naturally_covered: List[str] = Field(default_factory=list)
    green_flags: List[str] = Field(default_factory=list)
    yellow_flags: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    meeting_narrative: Optional[str] = None


class PostMeetingData(MongoModel):
    additional_data_needed: List[Dict[str, Any]] = Field(default_factory=list)
    data_requested_from_candidate: Optional[bool] = None


class MeetingSessionDocument(MongoModel):
    """MongoDB collection: meeting_sessions"""
    id: Optional[str] = Field(None, alias="_id")
    case_id: Optional[str] = None
    user_id: Optional[str] = None
    candidate_bio_id: Optional[str] = None
    journey_id: Optional[str] = None
    meeting_number: Optional[int] = None
    meeting_type: Optional[str] = None  # audio_call | face_to_face | video_call
    meeting_date: Optional[datetime] = None
    location: Optional[str] = None
    duration_minutes: Optional[int] = None
    prep_training_id: Optional[str] = None
    ai_listening: Optional[AIListening] = None
    script: List[MeetingScriptTurn] = Field(default_factory=list)
    questions_coverage: List[QuestionCoverage] = Field(default_factory=list)
    ai_analysis: Optional[MeetingAIAnalysis] = None
    post_meeting: Optional[PostMeetingData] = None


# ---------------------------------------------------------------------------
# proposal_decisions — Multi-meeting summary, AI recommendation, user decision
# ---------------------------------------------------------------------------

class YellowFlagResolved(MongoModel):
    flag: Optional[str] = None
    resolved: Optional[str] = None


class AIFinalAssessment(MongoModel):
    overall_score: Optional[float] = None
    confidence: Optional[float] = None
    recommendation: Optional[str] = None  # strongly_proceed | proceed | proceed_with_caution | do_not_proceed
    key_strengths: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)
    narrative: Optional[str] = None
    generated_at: Optional[datetime] = None


class CounsellorInput(MongoModel):
    counsellor_id: Optional[str] = None
    recommendation: Optional[str] = None  # proceed | do_not_proceed | more_meetings | user_decision
    notes: Optional[str] = None
    sessions_held_for_this_case: Optional[int] = None


class UserDecision(MongoModel):
    decision: Optional[str] = None  # accept | reject | more_meetings_needed | on_hold
    decided_at: Optional[datetime] = None
    reason: Optional[str] = None
    family_approval: Optional[bool] = None
    family_approval_notes: Optional[str] = None


class AdditionalMeeting(MongoModel):
    meeting_number: Optional[int] = None
    focus_areas: List[str] = Field(default_factory=list)
    new_prep_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class ProposalDecisionDocument(MongoModel):
    """MongoDB collection: proposal_decisions"""
    id: Optional[str] = Field(None, alias="_id")
    case_id: Optional[str] = None
    user_id: Optional[str] = None
    journey_id: Optional[str] = None
    created_at: Optional[datetime] = None
    meetings_held: Optional[int] = None
    meeting_ids: List[str] = Field(default_factory=list)
    cumulative_green_flags: List[str] = Field(default_factory=list)
    cumulative_yellow_flags: List[str] = Field(default_factory=list)
    cumulative_red_flags: List[str] = Field(default_factory=list)
    yellow_flags_resolved: List[YellowFlagResolved] = Field(default_factory=list)
    yellow_flags_unresolved: List[str] = Field(default_factory=list)
    ai_final: Optional[AIFinalAssessment] = None
    counsellor_input: Optional[CounsellorInput] = None
    user_decision: Optional[UserDecision] = None
    additional_meeting: Optional[AdditionalMeeting] = None
    final_outcome: Optional[str] = None  # proposal_accepted | proposal_rejected | on_hold | awaiting_third_party | archived
    final_outcome_at: Optional[datetime] = None
    next_step: Optional[str] = None  # engagement_planning | pre_marriage_compat_test | archived
    pre_marriage_compat_test_triggered: Optional[bool] = None
    best_practices_documented: Optional[str] = None
    case_archived_at: Optional[datetime] = None
