"""
Main entry point for Pre-Marriage Counseling Agent
Example usage and interaction interface
"""
import os
try:
    from dotenv import load_dotenv
except ImportError:
    # dotenv is optional - environment variables can be set directly
    def load_dotenv():
        pass

from pre_marriage_counseling_agent import PreMarriageCounselingAgent
from conversation_storage import save_conversation, print_conversation_summary, get_qanda_text
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


def main():
    """Main function to run the counseling agent"""
    # Load environment variables
    load_dotenv()
    
    # Get OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("Please set it in a .env file or export it as an environment variable.")
        api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
        if not api_key:
            print("Cannot proceed without API key. Exiting.")
            return
    
    # Initialize agent
    print("Initializing Pre-Marriage Counseling Agent...")
    agent = PreMarriageCounselingAgent(openai_api_key=api_key, model_name="gpt-4")
    
    # Load knowledge base
    print("Loading candidate knowledge base...")
    knowledge_base = create_sample_knowledge_base()
    agent.set_knowledge_base(knowledge_base)
    
    print("\n" + "="*60)
    print("PRE-MARRIAGE COUNSELING AGENT")
    print("="*60)
    print("\nAgent is ready to help with pre-marriage counseling.")
    print("The agent will ask you questions based on your profile.")
    print("Type 'quit' or 'exit' to end the session.\n")
    
    # Interactive conversation loop
    candidate_id = "john_doe_001"
    user_input = None
    is_first_turn = True
    
    while True:
        try:
            # On first turn, start with empty input to let agent ask first question
            # On subsequent turns, use user's response
            if is_first_turn:
                response = agent.chat("", candidate_id=candidate_id)
                is_first_turn = False
            else:
                response = agent.chat(user_input, candidate_id=candidate_id)
            
            # Display agent's response
            print(f"\n🤖 Agent: {response}\n")
            
            # Check if session should end
            if "INSIGHTS" in response or "RECOMMENDATIONS" in response:
                print("\n" + "="*60)
                print("Counseling session completed. Thank you!")
                print("="*60)
                
                # Save conversation before ending
                try:
                    saved_file = save_conversation(agent, candidate_id)
                    print(f"\n✅ Conversation saved to: {saved_file}")
                except Exception as e:
                    print(f"\n⚠️  Could not save conversation: {e}")
                
                break
            
            # Get user input
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                # Save conversation before quitting
                try:
                    saved_file = save_conversation(agent, candidate_id)
                    print(f"\n✅ Conversation saved to: {saved_file}")
                except Exception as e:
                    print(f"\n⚠️  Could not save conversation: {e}")
                
                print("\nThank you for using the Pre-Marriage Counseling Agent. Good luck!")
                break
            
            # Special commands
            if user_input.lower() in ['/summary', '/show']:
                print_conversation_summary(agent, candidate_id)
                user_input = "[Showing summary]"
                continue
            elif user_input.lower() == '/save':
                try:
                    saved_file = save_conversation(agent, candidate_id)
                    print(f"\n✅ Conversation saved to: {saved_file}")
                except Exception as e:
                    print(f"\n⚠️  Could not save conversation: {e}")
                user_input = "[Saving conversation]"
                continue
            
            if not user_input:
                user_input = "[No response]"
                
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try again or type 'quit' to exit.")
            user_input = "[Error occurred]"


def demo_conversation():
    """Run a demo conversation without user input"""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Please set OPENAI_API_KEY in .env file")
        return
    
    agent = PreMarriageCounselingAgent(openai_api_key=api_key)
    knowledge_base = create_sample_knowledge_base()
    agent.set_knowledge_base(knowledge_base)
    
    print("Running demo conversation...\n")
    
    # Simulate a conversation
    responses = [
        "Hello, I'm ready to start the counseling session.",
        "I value honesty, communication, and shared goals in a relationship.",
        "I prefer someone who shares my interests in technology and travel, but also has their own passions.",
        "I believe in open communication and prefer to discuss issues calmly and find solutions together.",
        "My family is very important to me, and I'd want my partner to get along with them, but we'd also maintain our independence.",
        "I have a busy work schedule but I make time for relationships. I'd want someone understanding of my career."
    ]
    
    user_input = None
    for i, response in enumerate(responses):
        print(f"\n{'='*60}")
        agent_response = agent.chat(user_input or "", candidate_id="demo_001")
        print(f"🤖 Agent: {agent_response}\n")
        
        user_input = response
        print(f"👤 User: {user_input}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_conversation()
    else:
        main()

