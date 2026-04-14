"""
Life Philosophy Agent
Evaluates purpose orientation, long-term vision, meaning-making style,
and life-direction compatibility to understand how life philosophy influences long-term partnership harmony.
"""
import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.state.state import AgentState
from app.prompts.life_philosophy.system_prompt import LIFE_PHILOSOPHY_SYSTEM_PROMPT
from app.knowledge.rag_helper import get_agent_specific_content


class LifePhilosophyAgent:
    """
    Life Philosophy Agent specialized in evaluating purpose orientation,
    long-term vision, meaning-making style, and life-direction compatibility.
    """
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-4"):
        """
        Initialize the Life Philosophy Agent.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model_name: Model to use (default: gpt-4)
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            api_key=api_key
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow for life philosophy analysis.
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_philosophy", self._analyze_philosophy)
        workflow.add_node("generate_profile", self._generate_profile)
        
        # Set entry point
        workflow.set_entry_point("analyze_philosophy")
        
        # Define flow: analyze -> generate profile -> end
        workflow.add_edge("analyze_philosophy", "generate_profile")
        workflow.add_edge("generate_profile", END)
        
        return workflow.compile()
    
    def _analyze_philosophy(self, state: AgentState) -> AgentState:
        """
        Analyze life philosophy data to extract key insights.
        """
        # Get user query if available
        messages = state.get("messages", [])
        user_query = ""
        for msg in reversed(messages):
            if hasattr(msg, 'content'):
                from langchain_core.messages import HumanMessage
                if isinstance(msg, HumanMessage):
                    user_query = msg.content
                    break
        
        # Get domain-specific content using RAG
        kb_summary = get_agent_specific_content(
            state=state,
            agent_domain="life_philosophy",
            user_query=user_query
        )
        
        # Check if we have life philosophy data
        has_philosophy_data = (
            "purpose" in kb_summary.lower() or
            "meaning" in kb_summary.lower() or
            "philosophy" in kb_summary.lower() or
            "spiritual" in kb_summary.lower() or
            "worldview" in kb_summary.lower() or
            "mission" in kb_summary.lower() or
            "vision" in kb_summary.lower() or
            "growth" in kb_summary.lower() or
            "resilience" in kb_summary.lower() or
            "narrative" in kb_summary.lower() or
            "RRI" in kb_summary or
            "PRI" in kb_summary or
            "7WPD" in kb_summary
        )
        
        if not has_philosophy_data:
            # If no philosophy data, inform user
            analysis_prompt = f"""Based on the available knowledge base data, identify if life philosophy data is available.

Knowledge Base Summary:
{kb_summary}

If life philosophy data is not available, inform the user that this agent requires life purpose questionnaire, RRI life-direction indicators, personal mission statements, meaning-making responses, narratives, and values to perform life philosophy analysis."""
        else:
            # Analyze available philosophy data
            analysis_prompt = f"""Analyze the life philosophy data provided in the knowledge base.

Knowledge Base Summary:
{kb_summary}

Extract and summarize:
1. Life purpose questionnaire responses
2. RRI (Relationship Readiness Index) life-direction indicators
3. Personal mission statements and life purpose declarations
4. Meaning-making responses and existential reflections
5. Narratives about life purpose and meaning
6. Values and philosophical orientation data
7. PRI (Personality Readiness Index) life philosophy markers

Identify key life philosophy indicators that will be used for deep analysis."""
        
        # Use LLM to analyze
        messages = [
            SystemMessage(content=LIFE_PHILOSOPHY_SYSTEM_PROMPT),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Store analysis in agent_data
        if "agent_data" not in state:
            state["agent_data"] = {}
        
        if "life_philosophy" not in state["agent_data"]:
            state["agent_data"]["life_philosophy"] = {}
        
        state["agent_data"]["life_philosophy"]["preliminary_analysis"] = response.content
        
        return state
    
    def _generate_profile(self, state: AgentState) -> AgentState:
        """
        Generate comprehensive life philosophy profile.
        """
        # Get user query if available
        messages = state.get("messages", [])
        user_query = ""
        for msg in reversed(messages):
            if hasattr(msg, 'content'):
                from langchain_core.messages import HumanMessage
                if isinstance(msg, HumanMessage):
                    user_query = msg.content
                    break
        
        # Get domain-specific content using RAG
        kb_summary = get_agent_specific_content(
            state=state,
            agent_domain="life_philosophy",
            user_query=user_query
        )
        preliminary_analysis = state.get("agent_data", {}).get("life_philosophy", {}).get("preliminary_analysis", "")
        
        # Check if we have the required data
        has_required_data = (
            "purpose" in kb_summary.lower() or
            "meaning" in kb_summary.lower() or
            "philosophy" in kb_summary.lower() or
            "spiritual" in kb_summary.lower() or
            "worldview" in kb_summary.lower() or
            "mission" in kb_summary.lower() or
            "vision" in kb_summary.lower() or
            "growth" in kb_summary.lower() or
            "resilience" in kb_summary.lower() or
            "narrative" in kb_summary.lower() or
            "RRI" in kb_summary or
            "PRI" in kb_summary or
            "7WPD" in kb_summary
        )
        
        if not has_required_data:
            profile_message = """I cannot generate a comprehensive life philosophy profile because the required life philosophy data is not available.

**Required Data:**
- Life purpose questionnaire
- RRI (Relationship Readiness Index) life-direction indicators
- Personal mission statements
- Meaning-making responses
- Narratives about life purpose and meaning
- Values and philosophical orientation data
- PRI life philosophy markers

Please ensure this information is included in the candidate's knowledge base before requesting life philosophy analysis."""
        else:
            # Generate comprehensive profile
            profile_prompt = f"""Generate a comprehensive LIFE PHILOSOPHY PROFILE based on the available life philosophy data.

Knowledge Base Summary:
{kb_summary}

Preliminary Analysis:
{preliminary_analysis}

Follow the output format specified in your system prompt:
1. EXECUTIVE SUMMARY
2. LIFE PHILOSOPHY PROFILE
3. PURPOSE-ALIGNMENT SCORE
4. GROWTH-ALIGNMENT ANALYSIS
5. POTENTIAL LONG-TERM COMPATIBILITY RISKS
6. PHILOSOPHY ALIGNMENT
7. NIHILISM RISK ASSESSMENT
8. RECOMMENDATIONS

Ensure all analysis is:
- Evidence-based with specific life philosophy data points
- Comprehensive and well-structured
- Balanced (life philosophy strengths and areas of concern)
- Actionable for relationship compatibility assessment
- Focused on nihilism and long-term compatibility risk tracking
- Uses PRI + Value Matrix and 7WPD Purpose Driver frameworks
- Deep and respectful of individual worldviews
- Sensitive to personal philosophical perspectives"""
            
            messages = [
                SystemMessage(content=LIFE_PHILOSOPHY_SYSTEM_PROMPT),
                HumanMessage(content=profile_prompt)
            ]
            
            response = self.llm.invoke(messages)
            profile_message = response.content
            
            # Store the profile in agent_data
            if "life_philosophy" not in state["agent_data"]:
                state["agent_data"]["life_philosophy"] = {}
            state["agent_data"]["life_philosophy"]["profile"] = profile_message
        
        # Add the profile as an AI message
        state["messages"].append(AIMessage(content=profile_message))
        
        return state
