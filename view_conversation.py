"""
Utility script to view saved conversations
"""
import sys
import json
from conversation_storage import load_conversation, list_conversations


def view_conversation(filename: str):
    """View a conversation file"""
    try:
        data = load_conversation(filename)
        
        print(f"\n{'='*60}")
        print(f"CONVERSATION: {data.get('candidate_id', 'Unknown')}")
        print(f"{'='*60}")
        print(f"Saved at: {data.get('saved_at', 'Unknown')}")
        print(f"Stage: {data.get('conversation_stage', 'N/A')}")
        print(f"Focus Area: {data.get('current_focus_area', 'N/A')}")
        print(f"\n{'='*60}")
        print("QUESTIONS & ANSWERS")
        print(f"{'='*60}\n")
        
        qa_pairs = data.get('user_responses', [])
        if qa_pairs:
            for i, qa in enumerate(qa_pairs, 1):
                print(f"Q{i}: {qa.get('question', 'N/A')}")
                print(f"A{i}: {qa.get('response', 'N/A')}")
                print("-" * 60)
        else:
            print("No Q&A pairs found.")
        
        insights = data.get('insights_generated', [])
        if insights:
            print(f"\n{'='*60}")
            print("INSIGHTS & RECOMMENDATIONS")
            print(f"{'='*60}\n")
            for insight in insights:
                print(insight)
                print("-" * 60)
                
    except Exception as e:
        print(f"Error loading conversation: {e}")


def main():
    if len(sys.argv) > 1:
        # View specific file
        filename = sys.argv[1]
        view_conversation(filename)
    else:
        # List all conversations
        conversations = list_conversations()
        if not conversations:
            print("No saved conversations found in 'conversations' directory.")
            return
        
        print("\nSaved Conversations:")
        print("=" * 60)
        for i, conv_file in enumerate(conversations, 1):
            try:
                data = load_conversation(conv_file)
                candidate_id = data.get('candidate_id', 'Unknown')
                saved_at = data.get('saved_at', 'Unknown')
                qa_count = len(data.get('user_responses', []))
                print(f"{i}. {conv_file}")
                print(f"   Candidate: {candidate_id} | Q&A Pairs: {qa_count} | Saved: {saved_at}")
            except:
                print(f"{i}. {conv_file}")
        
        print("\nTo view a conversation, run:")
        print(f"  python view_conversation.py <filename>")


if __name__ == "__main__":
    main()


