"""
Knowledge Base for Pre-Marriage Counseling Agent
Stores different types of data about the candidate
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PrimaryData(BaseModel):
    """Primary Data: Education and Bio Data"""
    name: str
    age: int
    education_level: str
    qualifications: List[str]
    profession: str
    employment_status: str
    income_range: Optional[str] = None
    location: Optional[str] = None
    bio_summary: Optional[str] = None


class SecondaryData(BaseModel):
    """Secondary Data: Social Media Information"""
    social_media_profiles: Dict[str, str] = Field(default_factory=dict)
    interests: List[str] = Field(default_factory=list)
    hobbies: List[str] = Field(default_factory=list)
    social_activity_patterns: Optional[str] = None
    online_personality_traits: List[str] = Field(default_factory=list)


class FamilyMember(BaseModel):
    """Family Member Information"""
    relationship: str  # father, mother, sibling, etc.
    name: str
    age: Optional[int] = None
    profession: Optional[str] = None
    relationship_quality: Optional[str] = None
    influence_level: Optional[str] = None


class FamilyData(BaseModel):
    """Family Data: Father, Mother, Close Relatives"""
    family_members: List[FamilyMember] = Field(default_factory=list)
    family_values: List[str] = Field(default_factory=list)
    family_background: Optional[str] = None
    cultural_background: Optional[str] = None
    socioeconomic_status: Optional[str] = None


class FriendColleague(BaseModel):
    """Friend or Colleague Information"""
    name: str
    relationship_type: str  # friend, colleague, mentor, etc.
    known_duration: Optional[str] = None
    interaction_frequency: Optional[str] = None
    feedback_summary: Optional[str] = None


class TertiaryData(BaseModel):
    """Tertiary Data: Information from Friends and Colleagues"""
    friends_colleagues: List[FriendColleague] = Field(default_factory=list)
    personality_insights: List[str] = Field(default_factory=list)
    social_behavior_patterns: List[str] = Field(default_factory=list)
    relationship_history: Optional[str] = None


class PsychometricReport(BaseModel):
    """Psychometric Assessment Report"""
    personality_type: Optional[str] = None
    big_five_scores: Optional[Dict[str, float]] = None
    emotional_intelligence_score: Optional[float] = None
    communication_style: Optional[str] = None
    conflict_resolution_style: Optional[str] = None
    relationship_readiness_score: Optional[float] = None
    detailed_report: Optional[str] = None


class MedicalReport(BaseModel):
    """Medical Report"""
    general_health_status: str
    medical_conditions: List[str] = Field(default_factory=list)
    mental_health_status: Optional[str] = None
    fitness_level: Optional[str] = None
    health_notes: Optional[str] = None


class BodyLanguageAnalysis(BaseModel):
    """Body Language Analysis"""
    communication_confidence: Optional[str] = None
    eye_contact_patterns: Optional[str] = None
    posture_analysis: Optional[str] = None
    gesture_patterns: Optional[str] = None
    overall_body_language_summary: Optional[str] = None


class OperationalData(BaseModel):
    """Operational Data: Psychometric, Medical, Body Language"""
    psychometric_report: PsychometricReport
    medical_report: MedicalReport
    body_language: BodyLanguageAnalysis


class CandidateKnowledgeBase(BaseModel):
    """Complete Knowledge Base for a Candidate"""
    primary_data: PrimaryData
    secondary_data: SecondaryData
    family_data: FamilyData
    tertiary_data: TertiaryData
    operational_data: OperationalData

    def get_summary(self) -> str:
        """Generate a comprehensive summary of all data"""
        summary_parts = [
            f"PRIMARY DATA:\nName: {self.primary_data.name}, Age: {self.primary_data.age}",
            f"Education: {self.primary_data.education_level}, Profession: {self.primary_data.profession}",
            f"\nSECONDARY DATA:\nInterests: {', '.join(self.secondary_data.interests)}",
            f"Hobbies: {', '.join(self.secondary_data.hobbies)}",
            f"\nFAMILY DATA:\nFamily Members: {len(self.family_data.family_members)}",
            f"Family Values: {', '.join(self.family_data.family_values)}",
            f"\nTERTIARY DATA:\nPersonality Insights: {', '.join(self.tertiary_data.personality_insights)}",
            f"\nOPERATIONAL DATA:\nPersonality Type: {self.operational_data.psychometric_report.personality_type}",
            f"Health Status: {self.operational_data.medical_report.general_health_status}",
        ]
        return "\n".join(summary_parts)

