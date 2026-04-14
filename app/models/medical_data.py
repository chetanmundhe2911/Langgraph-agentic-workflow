"""Collection: medical_data — Blood, physical stats, fitness, chronic conditions, allergies, medications, mental health."""
from typing import Optional, List
from datetime import datetime
from pydantic import Field
from .base import MongoModel


class BloodInfo(MongoModel):
    group: Optional[str] = None  # A+ | A- | B+ | B- | AB+ | AB- | O+ | O-
    rh_factor: Optional[str] = None  # positive | negative


class PhysicalInfo(MongoModel):
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    body_type: Optional[str] = None  # slim | athletic | average | heavyset
    complexion: Optional[str] = None
    eye_colour: Optional[str] = None
    hair_colour: Optional[str] = None
    distinguishing_marks: Optional[str] = None
    disability: Optional[str] = None  # none | minor | moderate | severe
    disability_details: Optional[str] = None
    spectacles_contact: Optional[str] = None  # none | spectacles | contact_lenses | both
    hearing: Optional[str] = None  # normal | hearing_aid | impaired


class FitnessLifestyle(MongoModel):
    level: Optional[str] = None  # sedentary | low | moderate | active | athlete
    exercise_routine: Optional[str] = None
    exercise_frequency_per_week: Optional[int] = None
    diet_type: Optional[str] = None  # vegetarian | non_vegetarian | eggetarian | vegan | jain | other
    diet_restrictions: List[str] = Field(default_factory=list)
    smoking: Optional[str] = None  # never | quit | occasional | regular
    drinking: Optional[str] = None  # never | quit | occasional | social | regular
    tobacco: Optional[str] = None  # never | occasional | regular
    recreational_drugs: Optional[str] = None  # never | occasional | regular


class ChronicCondition(MongoModel):
    condition: Optional[str] = None
    icd_code: Optional[str] = None
    diagnosed_year: Optional[int] = None
    severity: Optional[str] = None  # mild | moderate | severe | managed | in_remission
    management: Optional[str] = None
    specialist_treating: Optional[str] = None


class AllergyEntry(MongoModel):
    allergen: Optional[str] = None
    type: Optional[str] = None  # food | drug | environmental | insect | contact | other
    severity: Optional[str] = None  # mild | moderate | severe | anaphylactic
    reaction: Optional[str] = None
    carries_epipen: Optional[bool] = None


class Medication(MongoModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    purpose: Optional[str] = None
    since: Optional[str] = None
    prescribing_doctor: Optional[str] = None


class MentalHealthInfo(MongoModel):
    self_reported_status: Optional[str] = None  # excellent | good | moderate | struggling | needs_support
    diagnosed_conditions: List[str] = Field(default_factory=list)
    therapy_history: Optional[str] = None  # never | past | current
    stress_coping_mechanism: Optional[str] = None
    sleep_quality: Optional[str] = None  # excellent | good | average | poor | insomnia
    avg_sleep_hours: Optional[float] = None


class HereditaryRisk(MongoModel):
    condition: Optional[str] = None
    relation: Optional[str] = None  # father | mother | grandparent | sibling
    severity: Optional[str] = None
    notes: Optional[str] = None


class HygieneInfo(MongoModel):
    personal_grooming_score: Optional[float] = None
    dental_hygiene: Optional[str] = None
    skin_care: Optional[str] = None
    body_odour_flag: Optional[bool] = None
    overall_hygiene_notes: Optional[str] = None
    counsellor_hygiene_notes: Optional[str] = None


class MedicalDataDocument(MongoModel):
    """MongoDB collection: medical_data"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    blood: Optional[BloodInfo] = None
    physical: Optional[PhysicalInfo] = None
    fitness: Optional[FitnessLifestyle] = None
    chronic_conditions: List[ChronicCondition] = Field(default_factory=list)
    has_chronic_condition: Optional[bool] = None
    allergies: List[AllergyEntry] = Field(default_factory=list)
    has_allergies: Optional[bool] = None
    medications: List[Medication] = Field(default_factory=list)
    mental_health: Optional[MentalHealthInfo] = None
    hereditary_risks: List[HereditaryRisk] = Field(default_factory=list)
    hygiene: Optional[HygieneInfo] = None
