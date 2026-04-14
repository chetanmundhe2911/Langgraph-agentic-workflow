"""
Utility module to save and load conversation data (questions & answers)
Provides persistence for conversation history
"""
import json
import os
from typing import Optional
from datetime import datetime
from agent_state import AgentState
from pre_marriage_counseling_agent import PreMarriageCounselingAgent


def save_conversation(agent: PreMarriageCounselingAgent, candidate_id: str, filename: Optional[str] = None) -> str:
    """
    Save conversation state to a JSON file
    
    Args:
        agent: PreMarriageCounselingAgent instance
        candidate_id: ID of the candidate
        filename: Optional custom filename. If None, auto-generates based on candidate_id and timestamp
        
    Returns:
        Path to the saved file
    """
    state = agent.get_full_state(candidate_id)
    if not state:
        raise ValueError(f"No conversation found for candidate_id: {candidate_id}")
    
    # Prepare data for JSON serialization
    conversation_data = {
        "candidate_id": state.get("candidate_id"),
        "conversation_stage": state.get("conversation_stage"),
        "current_focus_area": state.get("current_focus_area"),
        "knowledge_base_summary": state.get("knowledge_base_summary"),
        "questions_asked": state.get("questions_asked", []),
        "insights_generated": state.get("insights_generated", []),
        "user_responses": state.get("user_responses", []),
        "messages": [
            {
                "type": "human" if hasattr(msg, '__class__') and 'Human' in str(msg.__class__) else "ai",
                "content": msg.content if hasattr(msg, 'content') else str(msg)
            }
            for msg in state.get("messages", [])
        ],
        "saved_at": datetime.now().isoformat(),
    }
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversations/conversation_{candidate_id}_{timestamp}.json"
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, indent=2, ensure_ascii=False)
    
    return filename


def load_conversation(filename: str) -> dict:
    """
    Load conversation data from a JSON file
    
    Args:
        filename: Path to the JSON file
        
    Returns:
        Dictionary containing conversation data
    """
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_conversations(directory: str = "conversations") -> list:
    """
    List all saved conversation files
    
    Args:
        directory: Directory to search for conversation files
        
    Returns:
        List of conversation file paths
    """
    if not os.path.exists(directory):
        return []
    
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.startswith("conversation_") and f.endswith(".json")
    ]


def print_conversation_summary(agent: PreMarriageCounselingAgent, candidate_id: str):
    """
    Print a summary of the conversation including all Q&A pairs
    
    Args:
        agent: PreMarriageCounselingAgent instance
        candidate_id: ID of the candidate
    """
    state = agent.get_full_state(candidate_id)
    if not state:
        print(f"No conversation found for candidate_id: {candidate_id}")
        return
    
    print(f"\n{'='*60}")
    print(f"CONVERSATION SUMMARY - Candidate ID: {candidate_id}")
    print(f"{'='*60}")
    print(f"\nConversation Stage: {state.get('conversation_stage', 'N/A')}")
    print(f"Current Focus Area: {state.get('current_focus_area', 'N/A')}")
    print(f"\nQuestions Asked: {len(state.get('questions_asked', []))}")
    print(f"User Responses: {len(state.get('user_responses', []))}")
    
    print(f"\n{'='*60}")
    print("QUESTIONS & ANSWERS")
    print(f"{'='*60}\n")
    
    user_responses = state.get('user_responses', [])
    if user_responses:
        for i, qa in enumerate(user_responses, 1):
            print(f"Q{i}: {qa.get('question', 'N/A')}")
            print(f"A{i}: {qa.get('response', 'N/A')}")
            print(f"Focus Area: {qa.get('focus_area', 'N/A')}")
            print("-" * 60)
    else:
        print("No Q&A pairs saved yet.")
    
    # Show questions that haven't been answered yet
    questions_asked = state.get('questions_asked', [])
    if len(questions_asked) > len(user_responses):
        print(f"\nUnanswered Questions:")
        for q in questions_asked[len(user_responses):]:
            print(f"  - {q}")
    
    # Show insights if available
    insights = state.get('insights_generated', [])
    if insights:
        print(f"\n{'='*60}")
        print("INSIGHTS & RECOMMENDATIONS")
        print(f"{'='*60}\n")
        for insight in insights:
            print(insight)
            print("-" * 60)


def get_qanda_text(agent: PreMarriageCounselingAgent, candidate_id: str) -> str:
    """
    Get all questions and answers as formatted text
    
    Args:
        agent: PreMarriageCounselingAgent instance
        candidate_id: ID of the candidate
        
    Returns:
        Formatted text containing all Q&A pairs
    """
    state = agent.get_full_state(candidate_id)
    if not state:
        return f"No conversation found for candidate_id: {candidate_id}"
    
    lines = []
    lines.append(f"Conversation for Candidate: {candidate_id}")
    lines.append(f"Stage: {state.get('conversation_stage', 'N/A')}")
    lines.append("=" * 60)
    lines.append("")
    
    user_responses = state.get('user_responses', [])
    for i, qa in enumerate(user_responses, 1):
        lines.append(f"Q{i}: {qa.get('question', 'N/A')}")
        lines.append(f"A{i}: {qa.get('response', 'N/A')}")
        lines.append("")
    
    return "\n".join(lines)

