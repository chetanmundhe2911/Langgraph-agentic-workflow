"""Collection: users — Core user/customer profile with auth, basic info, system metadata."""
from typing import Optional, List
from datetime import datetime, date
from pydantic import Field
from .base import MongoModel, TimestampMixin, Gender, StatusEnum


class AuthInfo(MongoModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password_hash: Optional[str] = None
    role: Optional[str] = None  # customer | counsellor | admin
    last_login: Optional[datetime] = None


class ProfileInfo(MongoModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[date] = None
    age: Optional[int] = None
    mother_tongue: Optional[str] = None
    languages_known: List[str] = Field(default_factory=list)
    religion: Optional[str] = None
    caste: Optional[str] = None
    sub_caste: Optional[str] = None
    gotra: Optional[str] = None


class LocationInfo(MongoModel):
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    country: Optional[str] = None
    native_place: Optional[str] = None
    pin_code: Optional[str] = None
    willing_to_relocate: Optional[bool] = None


class SubscriptionInfo(MongoModel):
    plan: Optional[str] = None  # free | basic | premium | enterprise
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    payment_status: Optional[str] = None  # paid | pending | failed
    dashboard_access: Optional[bool] = None


class UserDocument(TimestampMixin):
    """MongoDB collection: users"""
    status: Optional[str] = None
    auth: Optional[AuthInfo] = None
    profile: Optional[ProfileInfo] = None
    location: Optional[LocationInfo] = None
    subscription: Optional[SubscriptionInfo] = None
    counsellor_id: Optional[str] = None
    counsellor_notes: Optional[str] = None
    journey_stage: Optional[str] = None
    test_completed: Optional[bool] = None
    ai_profile_ready: Optional[bool] = None
