"""Collection: ideal_usecase_data — IDISC, WPD, ANterbhaya ideal preferences for partner matching."""
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import Field
from .base import MongoModel


class IDISCIdeal(MongoModel):
    ideal_disc_type: Optional[str] = None
    disc_compatibility_matrix: Optional[Dict[str, float]] = None
    ideal_personality_traits: List[str] = Field(default_factory=list)
    dealbreaker_personalities: List[str] = Field(default_factory=list)


class WPDIdeal(MongoModel):
    ideal_wpd_range_min: Optional[float] = None
    ideal_wpd_range_max: Optional[float] = None
    work_life_balance_pref: Optional[str] = None
    ambition_level_pref: Optional[str] = None  # low | medium | high | very_high


class AnterbhayaIdeal(MongoModel):
    acceptable_fear_patterns: List[str] = Field(default_factory=list)
    ideal_anterbhaya_range_min: Optional[float] = None
    ideal_anterbhaya_range_max: Optional[float] = None


class ValuesIdeal(MongoModel):
    top_shared_values: List[str] = Field(default_factory=list)
    religion_openness: Optional[str] = None  # same_only | same_pref | open_to_all
    political_alignment_pref: Optional[str] = None
    philosophy_alignment: Optional[str] = None


class HabitsIdeal(MongoModel):
    diet_compatibility: List[str] = Field(default_factory=list)
    smoking_tolerance: Optional[str] = None  # none | occasional_ok | dont_care
    drinking_tolerance: Optional[str] = None  # none | occasional_ok | dont_care
    sleep_schedule_pref: Optional[str] = None
    hobbies_overlap: List[str] = Field(default_factory=list)


class AIIdealProfile(MongoModel):
    summary: Optional[str] = None
    generated_at: Optional[datetime] = None
    compatibility_algorithm_version: Optional[str] = None


class IdealUsecaseDocument(MongoModel):
    """MongoDB collection: ideal_usecase_data"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    idisc: Optional[IDISCIdeal] = None
    wpd: Optional[WPDIdeal] = None
    anterbhaya: Optional[AnterbhayaIdeal] = None
    values_ideal: Optional[ValuesIdeal] = None
    habits_ideal: Optional[HabitsIdeal] = None
    ai_ideal_profile: Optional[AIIdealProfile] = None
