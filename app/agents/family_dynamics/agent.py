"""
Family Dynamics Agent
Analyzes family background, bonding patterns, support structures, conflict tendencies,
and cultural expectations to understand how family dynamics influence relationship readiness.
"""
import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.state.state import AgentState
from app.prompts.family_dynamics.system_prompt import FAMILY_DYNAMICS_SYSTEM_PROMPT
from app.knowledge.rag_helper import get_agent_specific_content


class FamilyDynamicsAgent:
    """
    Family Dynamics Agent specialized in analyzing family structure,
    bonding patterns, parental influence, and cultural family dynamics.
    """
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-4"):
        """
        Initialize the Family Dynamics Agent.
        
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
        Build the LangGraph workflow for family dynamics analysis.
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_family", self._analyze_family)
        workflow.add_node("generate_profile", self._generate_profile)
        
        # Set entry point
        workflow.set_entry_point("analyze_family")
        
        # Define flow: analyze -> generate profile -> end
        workflow.add_edge("analyze_family", "generate_profile")
        workflow.add_edge("generate_profile", END)
        
        return workflow.compile()
    
    def _analyze_family(self, state: AgentState) -> AgentState:
        """
        Analyze family dynamics data to extract key insights.
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
            agent_domain="family_dynamics",
            user_query=user_query
        )
        
        # Check if we have family data
        has_family_data = (
            "family" in kb_summary.lower() or
            "parent" in kb_summary.lower() or
            "sibling" in kb_summary.lower() or
            "upbringing" in kb_summary.lower() or
            "cultural" in kb_summary.lower() or
            "attachment" in kb_summary.lower() or
            "bonding" in kb_summary.lower() or
            "RRI" in kb_summary
        )
        
        if not has_family_data:
            # If no family data, inform user
            analysis_prompt = f"""Based on the available knowledge base data, identify if family dynamics data is available.

Knowledge Base Summary:
{kb_summary}

If family dynamics data is not available, inform the user that this agent requires family background questionnaire, relationship with parents & siblings, family values, conflict resolution observations, and RRI family-readiness markers to perform family dynamics analysis."""
        else:
            # Analyze available family data
            analysis_prompt = f"""Analyze the family dynamics data provided in the knowledge base.

Knowledge Base Summary:
{kb_summary}

Extract and summarize:
1. Family background questionnaire responses
2. Relationship with parents & siblings details
3. Family values and culture data
4. Conflict resolution observations
5. RRI (Relationship Readiness Index) family-readiness markers
6. Family Role Questionnaire data
7. Family structure and responsibilities

Identify key family dynamics indicators that will be used for deep analysis."""
        
        # Use LLM to analyze
        messages = [
            SystemMessage(content=FAMILY_DYNAMICS_SYSTEM_PROMPT),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Store analysis in agent_data
        if "agent_data" not in state:
            state["agent_data"] = {}
        
        if "family_dynamics" not in state["agent_data"]:
            state["agent_data"]["family_dynamics"] = {}
        
        state["agent_data"]["family_dynamics"]["preliminary_analysis"] = response.content
        
        return state
    
    def _generate_profile(self, state: AgentState) -> AgentState:
        """
        Generate comprehensive family dynamics profile.
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
            agent_domain="family_dynamics",
            user_query=user_query
        )
        preliminary_analysis = state.get("agent_data", {}).get("family_dynamics", {}).get("preliminary_analysis", "")
        
        # Check if we have the required data
        has_required_data = (
            "family" in kb_summary.lower() or
            "parent" in kb_summary.lower() or
            "sibling" in kb_summary.lower() or
            "upbringing" in kb_summary.lower() or
            "cultural" in kb_summary.lower() or
            "attachment" in kb_summary.lower() or
            "bonding" in kb_summary.lower() or
            "RRI" in kb_summary
        )
        
        if not has_required_data:
            profile_message = """I cannot generate a comprehensive family dynamics profile because the required family data is not available.

**Required Data:**
- Family background questionnaire
- Relationship with parents & siblings
- Family values and culture data
- Conflict resolution observations
- RRI (Relationship Readiness Index) family-readiness markers
- Family Role Questionnaire data

Please ensure this information is included in the candidate's knowledge base before requesting family dynamics analysis."""
        else:
            # Generate comprehensive profile
            profile_prompt = f"""Generate a comprehensive FAMILY DYNAMICS PROFILE based on the available family data.

Knowledge Base Summary:
{kb_summary}

Preliminary Analysis:
{preliminary_analysis}

Follow the output format specified in your system prompt:
1. EXECUTIVE SUMMARY
2. FAMILY ECOSYSTEM PROFILE
3. ATTACHMENT AND BONDING ANALYSIS
4. FAMILY FRICTION POINTS
5. MARRIAGE IMPACT INDICATORS
6. COMPATIBILITY RISKS LINKED TO FAMILY EXPECTATIONS
7. READINESS FOR JOINT/NUCLEAR FAMILY
8. COMPATIBILITY SCORE
9. RECOMMENDATIONS

Ensure all analysis is:
- Evidence-based with specific family data points
- Comprehensive and well-structured
- Balanced (family strengths and areas of concern)
- Actionable for relationship compatibility assessment
- Focused on rigid attitudes and inflexible expectations risk tracking
- Uses DISC Public/Private Concept and RRI frameworks
- Culturally sensitive and emotionally aware"""
            
            messages = [
                SystemMessage(content=FAMILY_DYNAMICS_SYSTEM_PROMPT),
                HumanMessage(content=profile_prompt)
            ]
            
            response = self.llm.invoke(messages)
            profile_message = response.content
            
            # Store the profile in agent_data
            if "family_dynamics" not in state["agent_data"]:
                state["agent_data"]["family_dynamics"] = {}
            state["agent_data"]["family_dynamics"]["profile"] = profile_message
        
        # Add the profile as an AI message
        state["messages"].append(AIMessage(content=profile_message))
        
        return state
