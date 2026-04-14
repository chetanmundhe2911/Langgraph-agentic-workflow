"""Bandhan Vertical — bandhan_product_context, marriage_compatibility, happiness, divorce, couple_sessions."""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import Field
from .base import MongoModel


# ---------------------------------------------------------------------------
# bandhan_product_context
# ---------------------------------------------------------------------------

class PreMarriageContext(MongoModel):
    individual_goal: Optional[str] = None
    is_managing_career_simultaneously: Optional[bool] = None
    cc_profile_id: Optional[str] = None
    family_approval_required: Optional[bool] = None
    urgency_level: Optional[str] = None  # low | medium | high | very_high


class CompatTestContext(MongoModel):
    couple_intake_date: Optional[datetime] = None
    relationship_duration_months: Optional[int] = None
    engagement_status: Optional[str] = None  # dating | engaged | pre_wedding
    primary_concern: Optional[str] = None
    test_completed_by_both: Optional[bool] = None


class HappinessIndexContext(MongoModel):
    marriage_date: Optional[date] = None
    years_married: Optional[float] = None
    children_count: Optional[int] = None
    living_arrangement: Optional[str] = None  # joint | nuclear | long_distance | separated_same_house
    previous_counselling: Optional[bool] = None
    self_assessed_happiness: Optional[int] = None
    partner_assessed_happiness: Optional[int] = None
    primary_improvement_area: Optional[str] = None


class DivorceCRContext(MongoModel):
    conflict_type: Optional[str] = None  # ongoing_conflict | separation_in_progress | legally_divorced | post_divorce_restart
    duration_of_conflict_months: Optional[int] = None
    legal_proceedings_started: Optional[bool] = None
    children_involved: Optional[bool] = None
    both_parties_willing: Optional[bool] = None
    goal: Optional[str] = None  # reconcile | amicable_separation | co_parenting | individual_restart
    individual_restart_track: Optional[bool] = None
    career_restart_needed: Optional[bool] = None


class BandhanContextDocument(MongoModel):
    """MongoDB collection: bandhan_product_context"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    bandhan_product: Optional[str] = None  # pre_marriage_prep | marriage_compatibility | marriage_happiness | divorce_conflict_resolution
    partner_user_id: Optional[str] = None
    relationship_status_at_intake: Optional[str] = None
    intake_date: Optional[datetime] = None
    active: Optional[bool] = None
    pre_marriage: Optional[PreMarriageContext] = None
    compat_test: Optional[CompatTestContext] = None
    happiness_index: Optional[HappinessIndexContext] = None
    divorce_cr: Optional[DivorceCRContext] = None


# ---------------------------------------------------------------------------
# marriage_compatibility_assessments
# ---------------------------------------------------------------------------

class CompatScores(MongoModel):
    overall: Optional[float] = None
    communication: Optional[float] = None
    values_alignment: Optional[float] = None
    financial: Optional[float] = None
    family_structure: Optional[float] = None
    intimacy_emotional: Optional[float] = None
    conflict_resolution: Optional[float] = None
    life_goals: Optional[float] = None
    parenting_philosophy: Optional[float] = None
    sexual_compatibility: Optional[float] = None
    astro: Optional[float] = None


class MarriageCompatibilityDocument(MongoModel):
    """MongoDB collection: marriage_compatibility_assessments"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    partner_user_id: Optional[str] = None
    bandhan_context_id: Optional[str] = None
    assessment_type: Optional[str] = None  # pre_marriage_compat | marriage_happiness_index | post_divorce_compat
    completed_at: Optional[datetime] = None
    person1_disc: Optional[Dict[str, Any]] = None
    person1_wpd: Optional[float] = None
    person1_anterbhaya: Optional[float] = None
    person1_values: List[str] = Field(default_factory=list)
    person2_disc: Optional[Dict[str, Any]] = None
    person2_wpd: Optional[float] = None
    person2_anterbhaya: Optional[float] = None
    person2_values: List[str] = Field(default_factory=list)
    compat_scores: Optional[CompatScores] = None
    strengths: List[str] = Field(default_factory=list)
    growth_areas: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    ai_recommendation: Optional[str] = None
    counsellor_recommendation: Optional[str] = None
    action_plan: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# marriage_happiness_index
# ---------------------------------------------------------------------------

class HappinessDimensions(MongoModel):
    emotional_connection: Optional[float] = None
    communication_quality: Optional[float] = None
    conflict_frequency: Optional[float] = None
    conflict_resolution_effectiveness: Optional[float] = None
    shared_activities: Optional[float] = None
    financial_harmony: Optional[float] = None
    parenting_alignment: Optional[float] = None
    intimacy_physical: Optional[float] = None
    intimacy_emotional: Optional[float] = None
    individual_growth_support: Optional[float] = None
    external_family_influence: Optional[float] = None
    trust_security: Optional[float] = None
    future_vision_alignment: Optional[float] = None


class HappinessAIInsights(MongoModel):
    primary_risk_areas: List[str] = Field(default_factory=list)
    positive_anchors: List[str] = Field(default_factory=list)
    trend: Optional[str] = None  # improving | stable | declining | volatile
    recommended_focus: Optional[str] = None
    intervention_urgency: Optional[str] = None  # low | medium | high | immediate


class ImprovementPlan(MongoModel):
    goals: List[str] = Field(default_factory=list)
    exercises_assigned: List[Dict[str, Any]] = Field(default_factory=list)
    next_checkin_date: Optional[datetime] = None
    counselling_sessions_recommended: Optional[int] = None


class MarriageHappinessDocument(MongoModel):
    """MongoDB collection: marriage_happiness_index"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    partner_user_id: Optional[str] = None
    bandhan_context_id: Optional[str] = None
    assessment_date: Optional[datetime] = None
    assessment_number: Optional[int] = None
    dimensions: Optional[HappinessDimensions] = None
    happiness_index_score: Optional[float] = None
    happiness_tier: Optional[str] = None  # thriving | stable | needs_work | at_risk | critical
    person1_self_rating: Optional[int] = None
    person2_self_rating: Optional[int] = None
    person1_satisfaction_narrative: Optional[str] = None
    person2_satisfaction_narrative: Optional[str] = None
    ai_insights: Optional[HappinessAIInsights] = None
    improvement_plan: Optional[ImprovementPlan] = None
    previous_assessment_id: Optional[str] = None
    score_change_from_last: Optional[float] = None
    milestones_achieved: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# divorce_conflict_resolution
# ---------------------------------------------------------------------------

class ChildrenInfo(MongoModel):
    count: Optional[int] = None
    ages: List[int] = Field(default_factory=list)
    custody_preference_p1: Optional[str] = None
    custody_preference_p2: Optional[str] = None
    coparenting_plan_agreed: Optional[bool] = None
    children_counselling_needed: Optional[bool] = None


class RootCauseAnalysis(MongoModel):
    disc_incompatibility_score: Optional[float] = None
    communication_breakdown_score: Optional[float] = None
    financial_conflict_score: Optional[float] = None
    trust_deficit_score: Optional[float] = None
    family_interference_score: Optional[float] = None
    individual_mental_health_flags: List[str] = Field(default_factory=list)
    ai_narrative: Optional[str] = None


class ReconciliationPath(MongoModel):
    sessions_completed: Optional[int] = None
    readiness_score_p1: Optional[float] = None
    readiness_score_p2: Optional[float] = None
    milestones: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)


class SeparationPath(MongoModel):
    asset_mediation_engaged: Optional[bool] = None
    mutual_agreement_reached: Optional[bool] = None
    best_practices_documented: Optional[str] = None
    case_archived_at: Optional[datetime] = None


class IndividualRestart(MongoModel):
    restart_goals: List[str] = Field(default_factory=list)
    emotional_recovery_score: Optional[float] = None
    career_restart_needed: Optional[bool] = None
    cc_profile_id: Optional[str] = None


class DivorceConflictDocument(MongoModel):
    """MongoDB collection: divorce_conflict_resolution"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    partner_user_id: Optional[str] = None
    bandhan_context_id: Optional[str] = None
    created_at: Optional[datetime] = None
    conflict_type: Optional[str] = None
    conflict_duration_months: Optional[int] = None
    conflict_root_causes: List[str] = Field(default_factory=list)
    conflict_root_causes_ai: List[str] = Field(default_factory=list)
    violence_or_abuse_reported: Optional[bool] = None
    legal_status: Optional[str] = None
    children: Optional[ChildrenInfo] = None
    root_cause_analysis: Optional[RootCauseAnalysis] = None
    goal: Optional[str] = None
    goal_alignment: Optional[bool] = None
    goal_narrative: Optional[str] = None
    reconciliation: Optional[ReconciliationPath] = None
    separation: Optional[SeparationPath] = None
    individual_restart: Optional[IndividualRestart] = None


# ---------------------------------------------------------------------------
# couple_sessions
# ---------------------------------------------------------------------------

class CoupleSessionRecording(MongoModel):
    file_url: Optional[str] = None
    transcript_url: Optional[str] = None
    ai_summary: Optional[str] = None
    consent_both: Optional[bool] = None


class CoupleSessionDocument(MongoModel):
    """MongoDB collection: couple_sessions"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    partner_user_id: Optional[str] = None
    bandhan_context_id: Optional[str] = None
    counsellor_id: Optional[str] = None
    session_type: Optional[str] = None  # compatibility_review | happiness_debrief | conflict_mediation | ...
    session_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    both_attended: Optional[bool] = None
    platform: Optional[str] = None
    primary_topic: Optional[str] = None
    emotions_identified: List[str] = Field(default_factory=list)
    breakthroughs: List[str] = Field(default_factory=list)
    unresolved_issues: List[str] = Field(default_factory=list)
    exercises_done: List[str] = Field(default_factory=list)
    homework_assigned: List[Dict[str, Any]] = Field(default_factory=list)
    recording: Optional[CoupleSessionRecording] = None
    session_outcome: Optional[str] = None  # productive | stalled | breakthrough | tense | neutral
    person1_satisfaction: Optional[int] = None
    person2_satisfaction: Optional[int] = None
    counsellor_notes: Optional[str] = None
    next_session_date: Optional[datetime] = None
    assessment_triggered: Optional[bool] = None
