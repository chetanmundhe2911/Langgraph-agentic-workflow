from app.knowledge.knowledge_base import (
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

def create_sample_knowledge_base() -> CandidateKnowledgeBase:
    """Create a sample knowledge base for testing"""
    
    # Primary Data
    primary_data = PrimaryData(
        name="John Doe",
        age=28,
        education_level="Master's Degree",
        qualifications=["MBA", "Bachelor's in Engineering"],
        profession="Software Engineer",
        employment_status="Employed",
        income_range="50k-75k",
        location="New York",
        bio_summary="Tech professional with passion for innovation and personal growth"
    )
    
    # Secondary Data
    secondary_data = SecondaryData(
        social_media_profiles={
            "LinkedIn": "linkedin.com/in/johndoe",
            "Instagram": "@johndoe"
        },
        interests=["Technology", "Travel", "Reading", "Fitness"],
        hobbies=["Photography", "Cooking", "Hiking"],
        social_activity_patterns="Moderate social media usage, prefers quality over quantity",
        online_personality_traits=["Thoughtful", "Professional", "Engaging"]
    )
    
    # Family Data
    family_data = FamilyData(
        family_members=[
            FamilyMember(
                relationship="father",
                name="Robert Doe",
                age=55,
                profession="Business Consultant",
                relationship_quality="Close and supportive",
                influence_level="High"
            ),
            FamilyMember(
                relationship="mother",
                name="Mary Doe",
                age=52,
                profession="Teacher",
                relationship_quality="Very close",
                influence_level="High"
            )
        ],
        family_values=["Education", "Respect", "Family Unity", "Hard Work"],
        family_background="Middle-class, educated family with strong traditional values",
        cultural_background="Mixed cultural heritage",
        socioeconomic_status="Middle class"
    )
    
    # Tertiary Data
    tertiary_data = TertiaryData(
        friends_colleagues=[
            FriendColleague(
                name="Mike Smith",
                relationship_type="friend",
                known_duration="10 years",
                interaction_frequency="Weekly",
                feedback_summary="Described as loyal, dependable, and good listener"
            ),
            FriendColleague(
                name="Sarah Johnson",
                relationship_type="colleague",
                known_duration="3 years",
                interaction_frequency="Daily",
                feedback_summary="Professional, collaborative, and detail-oriented"
            )
        ],
        personality_insights=[
            "Genuine and authentic in relationships",
            "Values deep connections over surface-level interactions",
            "Balances work and personal life well"
        ],
        social_behavior_patterns=[
            "Selective about close friendships",
            "Active in professional networks",
            "Enjoys group activities and one-on-one conversations equally"
        ],
        relationship_history="Previous long-term relationship ended amicably 2 years ago"
    )
    
    # Operational Data
    psychometric_report = PsychometricReport(
        personality_type="ENFJ - The Protagonist",
        big_five_scores={
            "Openness": 0.75,
            "Conscientiousness": 0.80,
            "Extraversion": 0.70,
            "Agreeableness": 0.85,
            "Neuroticism": 0.30
        },
        emotional_intelligence_score=8.5,
        communication_style="Assertive and empathetic",
        conflict_resolution_style="Collaborative problem-solving",
        relationship_readiness_score=8.0,
        detailed_report="High emotional intelligence, strong communication skills, ready for committed relationship"
    )
    
    medical_report = MedicalReport(
        general_health_status="Good",
        medical_conditions=[],
        mental_health_status="Healthy",
        fitness_level="Active",
        health_notes="Regular exercise routine, balanced diet"
    )
    
    body_language = BodyLanguageAnalysis(
        communication_confidence="High",
        eye_contact_patterns="Maintains good eye contact, appears engaged",
        posture_analysis="Open and welcoming posture",
        gesture_patterns="Uses hand gestures appropriately, animated when passionate",
        overall_body_language_summary="Confident, approachable, and authentic in communication"
    )
    
    operational_data = OperationalData(
        psychometric_report=psychometric_report,
        medical_report=medical_report,
        body_language=body_language
    )
    
    return CandidateKnowledgeBase(
        primary_data=primary_data,
        secondary_data=secondary_data,
        family_data=family_data,
        tertiary_data=tertiary_data,
        operational_data=operational_data
    )

