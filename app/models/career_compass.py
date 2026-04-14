"""Career Compass Vertical — career_compass_profiles, career_sessions, career_reports."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field
from .base import MongoModel, TimestampMixin


# ---------------------------------------------------------------------------
# career_compass_profiles
# ---------------------------------------------------------------------------

class CurrentStatusCC(MongoModel):
    employment_status: Optional[str] = None  # studying | unemployed | employed | self_employed | freelance | on_break
    institution_or_company: Optional[str] = None
    class_or_designation: Optional[str] = None
    location: Optional[str] = None
    years_in_current_role: Optional[float] = None


class AcademicsCC(MongoModel):
    board: Optional[str] = None
    current_class_or_year: Optional[str] = None
    stream: Optional[str] = None
    percentage_last_exam: Optional[float] = None
    subjects: List[str] = Field(default_factory=list)
    preferred_career_domains: List[str] = Field(default_factory=list)


class CertificationEntry(MongoModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    year: Optional[int] = None
    url: Optional[str] = None


class SkillsCC(MongoModel):
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    certifications: List[CertificationEntry] = Field(default_factory=list)
    skill_gap_identified: List[str] = Field(default_factory=list)
    skill_gap_analysis_at: Optional[datetime] = None


class CourseEntry(MongoModel):
    course_name: Optional[str] = None
    provider: Optional[str] = None
    mode: Optional[str] = None  # online | offline | hybrid
    status: Optional[str] = None  # enrolled | completed | dropped
    completion_pct: Optional[float] = None
    grade_score: Optional[str] = None
    certificate_url: Optional[str] = None


class CareerGoals(MongoModel):
    short_term_goal: Optional[str] = None
    long_term_goal: Optional[str] = None
    preferred_industries: List[str] = Field(default_factory=list)
    preferred_roles: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    salary_expectation_inr: Optional[int] = None
    open_to_relocation: Optional[bool] = None
    open_to_remote: Optional[bool] = None


class CareerCompassProfileDocument(TimestampMixin):
    """MongoDB collection: career_compass_profiles"""
    user_id: Optional[str] = None
    segment: Optional[str] = None  # student_school | student_college | unemployed_seeking | working_professional | ...
    sub_segment: Optional[str] = None
    vertical: Optional[str] = None  # career_compass | bandhan
    current_status: Optional[CurrentStatusCC] = None
    academics: Optional[AcademicsCC] = None
    skills: Optional[SkillsCC] = None
    courses: List[CourseEntry] = Field(default_factory=list)
    career_goals: Optional[CareerGoals] = None


# ---------------------------------------------------------------------------
# career_sessions
# ---------------------------------------------------------------------------

class MockInterview(MongoModel):
    questions_asked: List[str] = Field(default_factory=list)
    answers_summary: List[str] = Field(default_factory=list)
    ai_feedback: Optional[str] = None
    score: Optional[float] = None


class CareerSessionDocument(MongoModel):
    """MongoDB collection: career_sessions"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    counsellor_id: Optional[str] = None
    session_type: Optional[str] = None  # initial_assessment | skill_gap_review | interview_prep | career_planning | mock_interview
    session_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    platform: Optional[str] = None
    agenda: Optional[str] = None
    session_notes: Optional[str] = None
    topics_covered: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    resources_shared: List[Dict[str, Any]] = Field(default_factory=list)
    mock_interview: Optional[MockInterview] = None
    outcome: Optional[str] = None
    next_session_date: Optional[datetime] = None
    profile_updated: Optional[bool] = None


# ---------------------------------------------------------------------------
# career_reports
# ---------------------------------------------------------------------------

class SkillGapReport(MongoModel):
    current_skills: List[str] = Field(default_factory=list)
    required_skills_for_goal: List[str] = Field(default_factory=list)
    gap_list: List[str] = Field(default_factory=list)
    priority_order: List[str] = Field(default_factory=list)
    estimated_learning_weeks: Optional[int] = None
    recommended_courses: List[Dict[str, Any]] = Field(default_factory=list)


class CareerPathReport(MongoModel):
    paths: List[Dict[str, Any]] = Field(default_factory=list)
    market_demand_data: Optional[Dict[str, Any]] = None
    salary_benchmarks: Optional[Dict[str, Any]] = None


class MarketFitReport(MongoModel):
    overall_score: Optional[float] = None
    strengths_in_demand: List[str] = Field(default_factory=list)
    low_demand_skills: List[str] = Field(default_factory=list)
    competitive_positioning: Optional[str] = None


class CareerReportDocument(MongoModel):
    """MongoDB collection: career_reports"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    report_type: Optional[str] = None  # career_readiness | skill_gap | career_path | interview_prep | market_fit | wpd_cc | disc_cc
    generated_at: Optional[datetime] = None
    status: Optional[str] = None  # draft | complete | delivered
    skill_gap_report: Optional[SkillGapReport] = None
    career_path_report: Optional[CareerPathReport] = None
    market_fit_report: Optional[MarketFitReport] = None
    pdf_url: Optional[str] = None
    delivered_at: Optional[datetime] = None
    viewed_at: Optional[datetime] = None
