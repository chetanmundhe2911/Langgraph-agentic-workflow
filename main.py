import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.orchestrator.orchestrator import Orchestrator
from app.knowledge.loader import load_knowledge_base_from_reports, load_full_knowledge_base
from app.state.state import AgentState

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
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        else:
            print("Cannot proceed without API key. Exiting.")
            return
    
    # Initialize Orchestrator with gpt-4o (higher token limits)
    print("Initializing Multi-Agent Counseling System...")
    print("Using model: gpt-4o (for higher token limits)")
    orchestrator = Orchestrator(model_name="gpt-4o")
    
    # Load knowledge base from local Report/ folder (switch to MongoDB later)
    print("Loading candidate knowledge base from Report/ folder...")
    print("All reports will be indexed into RAG for intelligent retrieval based on queries.")
    knowledge_base = load_knowledge_base_from_reports(report_dir="Report", use_rag=True)

    kb_summary = knowledge_base.get_summary()  # Initial summary for state
    
    print("\n" + "="*60)
    print("MULTI-AGENT COUNSELING SYSTEM")
    print("="*60)
    print("\nAvailable Agents:")
    print("  - behaviour_psychology: Psychological and behavioral analysis")
    print("  - career_profession: Career and professional stability analysis")
    print("  - medical_lifestyle: Medical history and lifestyle analysis")
    print("  - health_wellness: Health and wellness assessment")
    print("  - family_dynamics: Family structure and dynamics analysis")
    print("  - character_values: Character and values assessment")
    print("  - education_readiness: Educational background analysis")
    print("  - social_philosophy: Social worldview analysis")
    print("  - hygiene_lifestyle: Hygiene and lifestyle compatibility")
    print("  - life_philosophy: Life purpose and meaning analysis")
    print("  - religious_values: Religious beliefs and practices")
    print("  - political_alignment: Political orientation analysis")
    print("\n🤖 Intelligent Routing Enabled: The system will automatically route your requests to the appropriate agent(s).")
    print("💬 Multi-Agent Chaining: Multiple agents can work together when needed.")
    print("📝 You can also manually set 'current_agent' in state to use a specific agent.")
    print("Type 'quit' or 'exit' to end the session.\n")
    
    # Initialize State
    # Note: All reports are indexed into RAG, so candidate_id is just for session tracking
    candidate_id = "candidate_001"
    state: AgentState = {
        "messages": [],
        "current_agent": "",  # Will be set by intelligent router
        "agent_chain": [],  # Track which agents have been executed
        "next_agents": [],  # Queue of agents to execute
        "should_continue": False,  # Whether to continue chaining
        "candidate_id": candidate_id,
        "knowledge_base_summary": kb_summary,
        "knowledge_base": knowledge_base,  # Store KB object for RAG access
        "agent_data": {},
        # Initialize legacy fields just in case (though we should rely on agent_data)
        "questions_asked": [],
        "user_responses": [],
        "insights_generated": [],
        "conversation_stage": "initial",
        "current_focus_area": "introduction"
    }
    
    # Interactive conversation loop
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nThank you for using the Multi-Agent Counseling System. Good luck!")
                break
            
            if not user_input:
                continue
                
            # Track message count before execution
            message_count_before = len(state["messages"])
            
            # Add user message to state
            state["messages"].append(HumanMessage(content=user_input))
            
            # Run orchestrator
            result = orchestrator.graph.invoke(state)
            state = result
            
            # Display new agent responses (only messages added in this execution)
            if state["messages"] and len(state["messages"]) > message_count_before:
                new_messages = state["messages"][message_count_before:]
                agent_chain = state.get("agent_chain", [])
                
                for i, msg in enumerate(new_messages):
                    if isinstance(msg, AIMessage):
                        # Determine which agent generated this message
                        agent_index = min(i, len(agent_chain) - 1) if agent_chain else -1
                        if agent_index >= 0:
                            agent_name = agent_chain[agent_index]
                            formatted_name = agent_name.replace('_', ' ').title()
                        else:
                            formatted_name = "System"
                        
                        print(f"\n🤖 {formatted_name}: {msg.content}\n")
                        
                        # Show separator if multiple agents were chained
                        if len(agent_chain) > 1 and i < len(new_messages) - 1:
                            print("─" * 60)
            
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            # import traceback
            # traceback.print_exc()
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    main()
