"""Collection: family_data — Comprehensive family tree: parents, grandparents, siblings, ancestry."""
from typing import Optional, List
from datetime import date
from pydantic import Field
from .base import MongoModel


class ParentProfile(MongoModel):
    full_name: Optional[str] = None
    is_living: Optional[bool] = None
    dob: Optional[date] = None
    age: Optional[int] = None
    education: Optional[str] = None
    occupation: Optional[str] = None
    income_or_pension_inr: Optional[int] = None
    health_status: Optional[str] = None
    location: Optional[str] = None
    birth_place: Optional[str] = None
    ancestral_origin: Optional[str] = None
    maiden_name: Optional[str] = None  # mother only


class GrandparentProfile(MongoModel):
    full_name: Optional[str] = None
    is_living: Optional[bool] = None
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    origin: Optional[str] = None
    location: Optional[str] = None


class SiblingProfile(MongoModel):
    full_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    birth_order: Optional[int] = None
    marital_status: Optional[str] = None  # single | married | divorced | widowed
    education: Optional[str] = None
    occupation: Optional[str] = None
    location: Optional[str] = None
    relationship_quality: Optional[str] = None  # very_close | close | normal | distant | estranged
    spouse_details: Optional[str] = None
    children_count: Optional[int] = None


class CloseRelative(MongoModel):
    relationship: Optional[str] = None  # uncle | aunt | cousin | etc.
    full_name: Optional[str] = None
    side: Optional[str] = None  # paternal | maternal
    occupation: Optional[str] = None
    location: Optional[str] = None
    influence_on_candidate: Optional[str] = None


class AncestryInfo(MongoModel):
    family_surname_origin: Optional[str] = None
    gotra: Optional[str] = None
    pravara: Optional[str] = None
    kuldevi: Optional[str] = None
    kuldevta: Optional[str] = None
    veda: Optional[str] = None
    original_village: Optional[str] = None
    migration_history: Optional[str] = None
    caste_history: Optional[str] = None
    notable_ancestors: Optional[str] = None


class FamilyFinancials(MongoModel):
    family_net_worth_inr: Optional[int] = None
    family_property_details: Optional[str] = None
    parents_monthly_income_inr: Optional[int] = None
    financial_support_from_candidate: Optional[bool] = None
    financial_support_amount_inr: Optional[int] = None
    family_loans_or_liabilities: Optional[str] = None


class UpbringingInfo(MongoModel):
    upbringing_city: Optional[str] = None
    upbringing_type: Optional[str] = None  # joint | nuclear | single_parent | hostel
    family_values_emphasis: List[str] = Field(default_factory=list)
    discipline_style: Optional[str] = None  # strict | moderate | lenient
    communication_style_in_family: Optional[str] = None
    religious_practice_frequency: Optional[str] = None
    post_marriage_expectation: Optional[str] = None  # joint | nuclear | flexible


class FamilyDataDocument(MongoModel):
    """MongoDB collection: family_data"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    father: Optional[ParentProfile] = None
    mother: Optional[ParentProfile] = None
    paternal_grandfather: Optional[GrandparentProfile] = None
    paternal_grandmother: Optional[GrandparentProfile] = None
    maternal_grandfather: Optional[GrandparentProfile] = None
    maternal_grandmother: Optional[GrandparentProfile] = None
    siblings: List[SiblingProfile] = Field(default_factory=list)
    close_relatives: List[CloseRelative] = Field(default_factory=list)
    ancestry: Optional[AncestryInfo] = None
    family_financials: Optional[FamilyFinancials] = None
    upbringing: Optional[UpbringingInfo] = None
