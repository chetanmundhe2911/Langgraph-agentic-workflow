"""
Hygiene–Lifestyle Agent
Assesses hygiene discipline, lifestyle routine stability, personal maintenance habits,
and home-organization tendencies to evaluate practical day-to-day compatibility factors.
"""
import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.state.state import AgentState
from app.prompts.hygiene_lifestyle.system_prompt import HYGIENE_LIFESTYLE_SYSTEM_PROMPT
from app.knowledge.rag_helper import get_agent_specific_content


class HygieneLifestyleAgent:
    """
    Hygiene–Lifestyle Agent specialized in assessing hygiene discipline,
    lifestyle routine stability, and personal maintenance behaviors.
    """
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-4"):
        """
        Initialize the Hygiene–Lifestyle Agent.
        
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
        Build the LangGraph workflow for hygiene-lifestyle analysis.
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_hygiene", self._analyze_hygiene)
        workflow.add_node("generate_profile", self._generate_profile)
        
        # Set entry point
        workflow.set_entry_point("analyze_hygiene")
        
        # Define flow: analyze -> generate profile -> end
        workflow.add_edge("analyze_hygiene", "generate_profile")
        workflow.add_edge("generate_profile", END)
        
        return workflow.compile()
    
    def _analyze_hygiene(self, state: AgentState) -> AgentState:
        """
        Analyze hygiene and lifestyle data to extract key insights.
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
            agent_domain="hygiene_lifestyle",
            user_query=user_query
        )
        
        # Check if we have hygiene/lifestyle data
        has_hygiene_data = (
            "hygiene" in kb_summary.lower() or
            "grooming" in kb_summary.lower() or
            "cleanliness" in kb_summary.lower() or
            "routine" in kb_summary.lower() or
            "lifestyle" in kb_summary.lower() or
            "habit" in kb_summary.lower() or
            "daily" in kb_summary.lower() or
            "sleep" in kb_summary.lower() or
            "food" in kb_summary.lower() or
            "organization" in kb_summary.lower() or
            "RRI" in kb_summary
        )
        
        if not has_hygiene_data:
            # If no hygiene data, inform user
            analysis_prompt = f"""Based on the available knowledge base data, identify if hygiene and lifestyle data is available.

Knowledge Base Summary:
{kb_summary}

If hygiene/lifestyle data is not available, inform the user that this agent requires lifestyle questionnaire, daily routine summaries, hygiene habit indicators, and RRI lifestyle-readiness dimension to perform hygiene-lifestyle analysis."""
        else:
            # Analyze available hygiene data
            analysis_prompt = f"""Analyze the hygiene and lifestyle data provided in the knowledge base.

Knowledge Base Summary:
{kb_summary}

Extract and summarize:
1. Lifestyle questionnaire responses
2. Daily routine summaries and daily schedule information
3. Hygiene habit indicators and hygiene practices
4. RRI (Relationship Readiness Index) lifestyle-readiness dimension
5. Hygiene Questionnaire data
6. Routine habits and lifestyle pattern information

Identify key hygiene and lifestyle indicators that will be used for deep analysis."""
        
        # Use LLM to analyze
        messages = [
            SystemMessage(content=HYGIENE_LIFESTYLE_SYSTEM_PROMPT),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Store analysis in agent_data
        if "agent_data" not in state:
            state["agent_data"] = {}
        
        if "hygiene_lifestyle" not in state["agent_data"]:
            state["agent_data"]["hygiene_lifestyle"] = {}
        
        state["agent_data"]["hygiene_lifestyle"]["preliminary_analysis"] = response.content
        
        return state
    
    def _generate_profile(self, state: AgentState) -> AgentState:
        """
        Generate comprehensive hygiene-lifestyle profile.
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
            agent_domain="hygiene_lifestyle",
            user_query=user_query
        )
        preliminary_analysis = state.get("agent_data", {}).get("hygiene_lifestyle", {}).get("preliminary_analysis", "")
        
        # Check if we have the required data
        has_required_data = (
            "hygiene" in kb_summary.lower() or
            "grooming" in kb_summary.lower() or
            "cleanliness" in kb_summary.lower() or
            "routine" in kb_summary.lower() or
            "lifestyle" in kb_summary.lower() or
            "habit" in kb_summary.lower() or
            "daily" in kb_summary.lower() or
            "sleep" in kb_summary.lower() or
            "food" in kb_summary.lower() or
            "organization" in kb_summary.lower() or
            "RRI" in kb_summary
        )
        
        if not has_required_data:
            profile_message = """I cannot generate a comprehensive hygiene-lifestyle profile because the required hygiene and lifestyle data is not available.

**Required Data:**
- Lifestyle questionnaire responses
- Daily routine summaries
- Hygiene habit indicators
- RRI (Relationship Readiness Index) lifestyle-readiness dimension
- Hygiene Questionnaire data

Please ensure this information is included in the candidate's knowledge base before requesting hygiene-lifestyle analysis."""
        else:
            # Generate comprehensive profile
            profile_prompt = f"""Generate a comprehensive HYGIENE–LIFESTYLE PROFILE based on the available hygiene and lifestyle data.

Knowledge Base Summary:
{kb_summary}

Preliminary Analysis:
{preliminary_analysis}

Follow the output format specified in your system prompt:
1. EXECUTIVE SUMMARY
2. HYGIENE PROFILE
3. LIFESTYLE COMPATIBILITY INDICATORS
4. ROUTINE-STRENGTHS AND HABIT GAPS
5. RELATIONSHIP FRICTION INDICATORS FROM LIFESTYLE BEHAVIORS
6. DAILY LIFESTYLE STRUCTURE ANALYSIS
7. HOME-ORGANIZATION ASSESSMENT
8. POOR HYGIENE RISK ASSESSMENT
9. RECOMMENDATIONS

Ensure all analysis is:
- Evidence-based with specific hygiene and lifestyle data points
- Comprehensive and well-structured
- Balanced (lifestyle strengths and areas for improvement)
- Actionable for relationship compatibility assessment
- Focused on poor hygiene and lifestyle compatibility risk tracking
- Uses Hygiene Questionnaire and Habit-Behaviour Matrix frameworks
- Neutral and non-judgmental in approach
- Practical and focused on daily living compatibility"""
            
            messages = [
                SystemMessage(content=HYGIENE_LIFESTYLE_SYSTEM_PROMPT),
                HumanMessage(content=profile_prompt)
            ]
            
            response = self.llm.invoke(messages)
            profile_message = response.content
            
            # Store the profile in agent_data
            if "hygiene_lifestyle" not in state["agent_data"]:
                state["agent_data"]["hygiene_lifestyle"] = {}
            state["agent_data"]["hygiene_lifestyle"]["profile"] = profile_message
        
        # Add the profile as an AI message
        state["messages"].append(AIMessage(content=profile_message))
        
        return state
