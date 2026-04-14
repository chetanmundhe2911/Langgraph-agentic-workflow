"""
Agents package - Contains all specialized agents for relationship compatibility analysis
"""

from app.agents.behaviour_psychology.agent import BehaviourPsychologyAgent
from app.agents.career_profession.agent import CareerProfessionAgent
from app.agents.medical_lifestyle.agent import MedicalLifestyleAgent
from app.agents.health_wellness.agent import HealthWellnessAgent
from app.agents.family_dynamics.agent import FamilyDynamicsAgent
from app.agents.character_values.agent import CharacterValuesAgent
from app.agents.education_readiness.agent import EducationReadinessAgent
from app.agents.social_philosophy.agent import SocialPhilosophyAgent
from app.agents.hygiene_lifestyle.agent import HygieneLifestyleAgent
from app.agents.life_philosophy.agent import LifePhilosophyAgent
from app.agents.religious_values.agent import ReligiousValuesAgent
from app.agents.political_alignment.agent import PoliticalAlignmentAgent

__all__ = [
    "BehaviourPsychologyAgent",
    "CareerProfessionAgent",
    "MedicalLifestyleAgent",
    "HealthWellnessAgent",
    "FamilyDynamicsAgent",
    "CharacterValuesAgent",
    "EducationReadinessAgent",
    "SocialPhilosophyAgent",
    "HygieneLifestyleAgent",
    "LifePhilosophyAgent",
    "ReligiousValuesAgent",
    "PoliticalAlignmentAgent",
]
