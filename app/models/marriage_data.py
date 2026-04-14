"""Collection: marriage_data — BIO data, Kundali, horoscope, matrimony profiles, photos/videos."""
from typing import Optional, List
from datetime import date, datetime
from pydantic import Field
from .base import MongoModel


class BioData(MongoModel):
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    complexion: Optional[str] = None  # very_fair | fair | wheatish | dusky | dark
    body_type: Optional[str] = None  # slim | athletic | average | heavyset
    spectacles: Optional[bool] = None
    diet: Optional[str] = None  # vegetarian | non_vegetarian | eggetarian | vegan | jain
    smoking: Optional[str] = None  # never | occasional | regular | quit
    drinking: Optional[str] = None  # never | occasional | social | regular | quit
    about_me_bio: Optional[str] = None
    hobbies_for_bio: List[str] = Field(default_factory=list)


class KundaliInfo(MongoModel):
    birth_date: Optional[date] = None
    birth_time: Optional[str] = None
    birth_place: Optional[str] = None
    rashi: Optional[str] = None
    nakshatra: Optional[str] = None
    nakshatra_pada: Optional[int] = None
    lagna: Optional[str] = None
    manglik_status: Optional[str] = None  # non_manglik | manglik | anshik_manglik | partial_manglik
    manglik_details: Optional[str] = None
    gotra: Optional[str] = None
    pravara: Optional[str] = None
    kuldevi: Optional[str] = None
    file_url: Optional[str] = None
    ai_analysis: Optional[str] = None
    astrologer_notes: Optional[str] = None


class HoroscopeInfo(MongoModel):
    sun_sign: Optional[str] = None
    chinese_year: Optional[str] = None
    horoscope_file_url: Optional[str] = None


class MatrimonyProfile(MongoModel):
    site_name: Optional[str] = None
    profile_id: Optional[str] = None
    profile_url: Optional[str] = None
    active: Optional[bool] = None
    created_at: Optional[date] = None
    last_active: Optional[date] = None
    responses_received: Optional[int] = None
    ai_profile_review: Optional[str] = None


class PartnerPreferences(MongoModel):
    age_range_min: Optional[int] = None
    age_range_max: Optional[int] = None
    height_range_min_cm: Optional[int] = None
    height_range_max_cm: Optional[int] = None
    preferred_education: List[str] = Field(default_factory=list)
    preferred_professions: List[str] = Field(default_factory=list)
    preferred_income_band: Optional[str] = None
    preferred_locations: List[str] = Field(default_factory=list)
    preferred_religion: Optional[str] = None
    preferred_caste: List[str] = Field(default_factory=list)
    manglik_preference: Optional[str] = None
    diet_preference: Optional[str] = None
    key_values: List[str] = Field(default_factory=list)
    dealbreakers: List[str] = Field(default_factory=list)
    marriage_timeline: Optional[str] = None


class ProfileMedia(MongoModel):
    main_photo_url: Optional[str] = None
    additional_photos: List[str] = Field(default_factory=list)
    family_photo_url: Optional[str] = None
    intro_video_url: Optional[str] = None


class MarriageDataDocument(MongoModel):
    """MongoDB collection: marriage_data"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    bio: Optional[BioData] = None
    kundali: Optional[KundaliInfo] = None
    horoscope: Optional[HoroscopeInfo] = None
    matrimony_profiles: List[MatrimonyProfile] = Field(default_factory=list)
    partner_pref: Optional[PartnerPreferences] = None
    profile_media: Optional[ProfileMedia] = None
