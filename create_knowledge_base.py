"""
Utility script to help create a knowledge base for a candidate
Interactive script to gather all necessary information
"""
from knowledge_base import (
    CandidateKnowledgeBase,
    PrimaryData,
    SecondaryData,
    FamilyData,
    FamilyMember,
    TertiaryData,
    FriendColleague,
    OperationalData,
    PsychometricReport,
    MedicalReport,
    BodyLanguageAnalysis
)
import json
from typing import List


def get_input(prompt: str, required: bool = True, default: str = None) -> str:
    """Get user input with optional default value"""
    if default:
        response = input(f"{prompt} (default: {default}): ").strip()
        return response if response else default
    else:
        while True:
            response = input(f"{prompt}: ").strip()
            if response or not required:
                return response
            print("This field is required. Please provide a value.")


def get_list_input(prompt: str, separator: str = ",") -> List[str]:
    """Get a list of items from user input"""
    response = input(f"{prompt} (comma-separated): ").strip()
    if not response:
        return []
    return [item.strip() for item in response.split(separator) if item.strip()]


def create_knowledge_base_interactive() -> CandidateKnowledgeBase:
    """Interactive function to create a knowledge base"""
    print("\n" + "="*60)
    print("KNOWLEDGE BASE CREATION")
    print("="*60)
    print("\nThis will help you create a comprehensive knowledge base for pre-marriage counseling.")
    print("Please provide the following information:\n")
    
    # Primary Data
    print("\n--- PRIMARY DATA ---")
    primary_data = PrimaryData(
        name=get_input("Candidate Name", required=True),
        age=int(get_input("Age", required=True)),
        education_level=get_input("Education Level", required=True),
        qualifications=get_list_input("Qualifications (e.g., MBA, B.E.)"),
        profession=get_input("Profession", required=True),
        employment_status=get_input("Employment Status", required=True),
        income_range=get_input("Income Range", required=False),
        location=get_input("Location", required=False),
        bio_summary=get_input("Bio Summary", required=False)
    )
    
    # Secondary Data
    print("\n--- SECONDARY DATA (Social Media) ---")
    social_profiles = {}
    while True:
        platform = get_input("Social Media Platform (e.g., LinkedIn) - Press Enter when done", required=False)
        if not platform:
            break
        profile = get_input(f"{platform} Profile/URL", required=False)
        if profile:
            social_profiles[platform] = profile
    
    secondary_data = SecondaryData(
        social_media_profiles=social_profiles,
        interests=get_list_input("Interests"),
        hobbies=get_list_input("Hobbies"),
        social_activity_patterns=get_input("Social Activity Patterns", required=False),
        online_personality_traits=get_list_input("Online Personality Traits")
    )
    
    # Family Data
    print("\n--- FAMILY DATA ---")
    family_members = []
    while True:
        print("\nAdd Family Member (or press Enter to finish):")
        relationship = get_input("Relationship (father/mother/sibling/etc.)", required=False)
        if not relationship:
            break
        family_members.append(FamilyMember(
            relationship=relationship,
            name=get_input("Name", required=True),
            age=int(get_input("Age", required=False)) if get_input("Age", required=False) else None,
            profession=get_input("Profession", required=False),
            relationship_quality=get_input("Relationship Quality", required=False),
            influence_level=get_input("Influence Level", required=False)
        ))
    
    family_data = FamilyData(
        family_members=family_members,
        family_values=get_list_input("Family Values"),
        family_background=get_input("Family Background", required=False),
        cultural_background=get_input("Cultural Background", required=False),
        socioeconomic_status=get_input("Socioeconomic Status", required=False)
    )
    
    # Tertiary Data
    print("\n--- TERTIARY DATA (Friends & Colleagues) ---")
    friends_colleagues = []
    while True:
        print("\nAdd Friend/Colleague (or press Enter to finish):")
        name = get_input("Name", required=False)
        if not name:
            break
        friends_colleagues.append(FriendColleague(
            name=name,
            relationship_type=get_input("Relationship Type (friend/colleague/etc.)", required=True),
            known_duration=get_input("Known Duration", required=False),
            interaction_frequency=get_input("Interaction Frequency", required=False),
            feedback_summary=get_input("Feedback/Summary", required=False)
        ))
    
    tertiary_data = TertiaryData(
        friends_colleagues=friends_colleagues,
        personality_insights=get_list_input("Personality Insights"),
        social_behavior_patterns=get_list_input("Social Behavior Patterns"),
        relationship_history=get_input("Relationship History", required=False)
    )
    
    # Operational Data - Psychometric
    print("\n--- OPERATIONAL DATA ---")
    print("\nPsychometric Report:")
    psychometric_report = PsychometricReport(
        personality_type=get_input("Personality Type (e.g., ENFJ)", required=False),
        big_five_scores=None,  # Could be expanded to get scores
        emotional_intelligence_score=float(get_input("Emotional Intelligence Score (0-10)", required=False)) if get_input("Emotional Intelligence Score (0-10)", required=False) else None,
        communication_style=get_input("Communication Style", required=False),
        conflict_resolution_style=get_input("Conflict Resolution Style", required=False),
        relationship_readiness_score=float(get_input("Relationship Readiness Score (0-10)", required=False)) if get_input("Relationship Readiness Score (0-10)", required=False) else None,
        detailed_report=get_input("Detailed Report", required=False)
    )
    
    # Medical Report
    print("\nMedical Report:")
    medical_report = MedicalReport(
        general_health_status=get_input("General Health Status", required=True, default="Good"),
        medical_conditions=get_list_input("Medical Conditions (if any)"),
        mental_health_status=get_input("Mental Health Status", required=False),
        fitness_level=get_input("Fitness Level", required=False),
        health_notes=get_input("Health Notes", required=False)
    )
    
    # Body Language
    print("\nBody Language Analysis:")
    body_language = BodyLanguageAnalysis(
        communication_confidence=get_input("Communication Confidence", required=False),
        eye_contact_patterns=get_input("Eye Contact Patterns", required=False),
        posture_analysis=get_input("Posture Analysis", required=False),
        gesture_patterns=get_input("Gesture Patterns", required=False),
        overall_body_language_summary=get_input("Overall Body Language Summary", required=False)
    )
    
    operational_data = OperationalData(
        psychometric_report=psychometric_report,
        medical_report=medical_report,
        body_language=body_language
    )
    
    # Create knowledge base
    knowledge_base = CandidateKnowledgeBase(
        primary_data=primary_data,
        secondary_data=secondary_data,
        family_data=family_data,
        tertiary_data=tertiary_data,
        operational_data=operational_data
    )
    
    print("\n" + "="*60)
    print("Knowledge base created successfully!")
    print("="*60)
    
    return knowledge_base


def save_knowledge_base(knowledge_base: CandidateKnowledgeBase, filename: str = "knowledge_base.json"):
    """Save knowledge base to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base.model_dump(), f, indent=2, ensure_ascii=False)
    print(f"\nKnowledge base saved to {filename}")


def load_knowledge_base(filename: str = "knowledge_base.json") -> CandidateKnowledgeBase:
    """Load knowledge base from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return CandidateKnowledgeBase(**data)


if __name__ == "__main__":
    kb = create_knowledge_base_interactive()
    save_option = input("\nSave knowledge base to file? (y/n): ").strip().lower()
    if save_option == 'y':
        filename = input("Filename (default: knowledge_base.json): ").strip()
        if not filename:
            filename = "knowledge_base.json"
        save_knowledge_base(kb, filename)

