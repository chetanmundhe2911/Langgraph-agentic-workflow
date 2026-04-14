"""Collection: primary_data — CV, education, jobs, financials, travel, documents."""
from typing import Optional, List
from datetime import date, datetime
from pydantic import Field
from .base import MongoModel


class IdentityInfo(MongoModel):
    full_name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    mother_tongue: Optional[str] = None
    languages_spoken: List[str] = Field(default_factory=list)
    nationality: Optional[str] = None
    pan_number_hash: Optional[str] = None
    aadhaar_last4: Optional[str] = None


class EducationEntry(MongoModel):
    level: Optional[str] = None  # 10th | 12th | Diploma | UG | PG | PhD | Professional
    degree_name: Optional[str] = None
    institution: Optional[str] = None
    board_university: Optional[str] = None
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    marks_pct: Optional[float] = None
    grade_cgpa: Optional[str] = None
    subjects_major: List[str] = Field(default_factory=list)
    certificate_url: Optional[str] = None
    verified: Optional[bool] = None
    verification_notes: Optional[str] = None


class CurrentJob(MongoModel):
    company_name: Optional[str] = None
    designation: Optional[str] = None
    job_role_description: Optional[str] = None
    department: Optional[str] = None
    industry: Optional[str] = None
    employment_type: Optional[str] = None  # full_time | part_time | contract | self_employed | govt | PSU
    start_date: Optional[date] = None
    total_exp_years: Optional[float] = None
    work_location_city: Optional[str] = None
    work_mode: Optional[str] = None  # office | remote | hybrid
    annual_ctc_inr: Optional[int] = None
    take_home_monthly_inr: Optional[int] = None
    income_band: Optional[str] = None  # <3L | 3-6L | 6-10L | 10-20L | 20-50L | >50L
    offer_letter_url: Optional[str] = None
    salary_slip_url: Optional[str] = None


class PastJob(MongoModel):
    company_name: Optional[str] = None
    designation: Optional[str] = None
    industry: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason_for_leaving: Optional[str] = None


class FinancialInfo(MongoModel):
    net_worth_inr: Optional[int] = None
    savings_monthly_inr: Optional[int] = None
    investment_types: List[str] = Field(default_factory=list)
    property_owned: Optional[bool] = None
    property_details: Optional[str] = None
    loans_active: Optional[bool] = None
    loan_details: Optional[str] = None
    monthly_emi_inr: Optional[int] = None
    financial_support_to_family: Optional[bool] = None
    family_support_amount_inr: Optional[int] = None


class ForeignTravelEntry(MongoModel):
    country: Optional[str] = None
    purpose: Optional[str] = None  # work | study | travel | immigration
    year: Optional[int] = None
    duration_months: Optional[int] = None
    visa_type: Optional[str] = None


class Achievement(MongoModel):
    title: Optional[str] = None
    category: Optional[str] = None  # academic | professional | sports | cultural | other
    year: Optional[int] = None
    description: Optional[str] = None
    certificate_url: Optional[str] = None


class DocumentEntry(MongoModel):
    doc_type: Optional[str] = None  # cv | aadhaar | pan | passport | marksheet | certificate | other
    file_url: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    verified: Optional[bool] = None


class PrimaryDataDocument(MongoModel):
    """MongoDB collection: primary_data"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    completeness_score: Optional[float] = None
    identity: Optional[IdentityInfo] = None
    education: List[EducationEntry] = Field(default_factory=list)
    current_job: Optional[CurrentJob] = None
    past_jobs: List[PastJob] = Field(default_factory=list)
    financials: Optional[FinancialInfo] = None
    foreign_travel: List[ForeignTravelEntry] = Field(default_factory=list)
    achievements: List[Achievement] = Field(default_factory=list)
    documents: List[DocumentEntry] = Field(default_factory=list)
