"""
Behaviour-Psychology Agent
Analyzes psychometric assessments (RRI, PRI, AntarBahya) to generate comprehensive psychological profiles.
"""
import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.state.state import AgentState
from app.prompts.behaviour_psychology.system_prompt import BEHAVIOUR_PSYCHOLOGY_SYSTEM_PROMPT
from app.knowledge.rag_helper import get_agent_specific_content


class BehaviourPsychologyAgent:
    """
    Behaviour-Psychology Agent specialized in deep psychological decoding
    and behavioral analysis through psychometric assessments.
    """
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-4"):
        """
        Initialize the Behaviour-Psychology Agent.
        
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
        Build the LangGraph workflow for psychological analysis.
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_psychology", self._analyze_psychology)
        workflow.add_node("generate_profile", self._generate_profile)
        
        # Set entry point
        workflow.set_entry_point("analyze_psychology")
        
        # Define flow: analyze -> generate profile -> end
        workflow.add_edge("analyze_psychology", "generate_profile")
        workflow.add_edge("generate_profile", END)
        
        return workflow.compile()
    
    def _analyze_psychology(self, state: AgentState) -> AgentState:
        """
        Analyze psychometric data and extract key psychological insights.
        """
        # Get user query if available
        messages = state.get("messages", [])
        user_query = ""
        for msg in reversed(messages):
            if hasattr(msg, 'content') and not isinstance(msg, AIMessage):
                user_query = msg.content
                break
        
        # Get domain-specific content using RAG if available
        kb_summary = get_agent_specific_content(
            state=state,
            agent_domain="behaviour_psychology",
            user_query=user_query
        )
        
        # Check if we have psychometric data
        if not kb_summary or ("RRI" not in kb_summary and "PRI" not in kb_summary and "AntarBahya" not in kb_summary):
            # If no psychometric data, inform user
            analysis_prompt = f"""Based on the available knowledge base data, identify if psychometric assessment data (RRI, PRI, AntarBahya) is available.

Knowledge Base Summary:
{kb_summary}

If psychometric data is not available, inform the user that this agent requires RRI, PRI, and AntarBahya assessment data to perform psychological analysis."""
        else:
            # Analyze available psychometric data
            analysis_prompt = f"""Analyze the psychometric assessment data provided in the knowledge base.

Knowledge Base Summary:
{kb_summary}

Extract and summarize:
1. RRI (Relationship Readiness Index) data and scores
2. PRI (Personality Readiness Index) data and scores  
3. AntarBahya assessment data and patterns

Identify key psychological indicators that will be used for deep analysis."""
        
        # Use LLM to analyze
        messages = [
            SystemMessage(content=BEHAVIOUR_PSYCHOLOGY_SYSTEM_PROMPT),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Store analysis in agent_data
        if "agent_data" not in state:
            state["agent_data"] = {}
        
        if "behaviour_psychology" not in state["agent_data"]:
            state["agent_data"]["behaviour_psychology"] = {}
        
        state["agent_data"]["behaviour_psychology"]["preliminary_analysis"] = response.content
        
        return state
    
    def _generate_profile(self, state: AgentState) -> AgentState:
        """
        Generate comprehensive psychological behaviour profile.
        """
        # Get user query if available
        messages = state.get("messages", [])
        user_query = ""
        for msg in reversed(messages):
            if hasattr(msg, 'content'):
                # Check if it's a HumanMessage (not AIMessage)
                from langchain_core.messages import HumanMessage
                if isinstance(msg, HumanMessage):
                    user_query = msg.content
                    break
        
        # Get domain-specific content using RAG if available
        kb_summary = get_agent_specific_content(
            state=state,
            agent_domain="behaviour_psychology",
            user_query=user_query
        )
        preliminary_analysis = state.get("agent_data", {}).get("behaviour_psychology", {}).get("preliminary_analysis", "")
        
        # Check if we have the required data
        has_required_data = (
            "RRI" in kb_summary or "Relationship Readiness" in kb_summary or
            "PRI" in kb_summary or "Personality Readiness" in kb_summary or
            "AntarBahya" in kb_summary or "Antar" in kb_summary or "Bahya" in kb_summary
        )
        
        if not has_required_data:
            profile_message = """I cannot generate a comprehensive psychological behaviour profile because the required psychometric assessment data is not available.

**Required Assessments:**
- RRI (Relationship Readiness Index)
- PRI (Personality Readiness Index)  
- AntarBahya Assessment

Please ensure these assessments are included in the candidate's knowledge base before requesting psychological analysis."""
        else:
            # Generate comprehensive profile
            profile_prompt = f"""Generate a comprehensive PSYCHOLOGICAL BEHAVIOUR PROFILE based on the psychometric assessment data.

Knowledge Base Summary:
{kb_summary}

Preliminary Analysis:
{preliminary_analysis}

Follow the output format specified in your system prompt:
1. EXECUTIVE SUMMARY
2. COMMUNICATION ANALYSIS
3. EMOTIONAL DYNAMICS ANALYSIS
4. BEHAVIORAL PATTERN ANALYSIS
5. RISK ASSESSMENT - VOLATILITY TRACKING
6. RELATIONSHIP READINESS ASSESSMENT
7. COMPATIBILITY BEHAVIORAL INSIGHTS
8. RECOMMENDATIONS

Ensure all analysis is:
- Evidence-based with specific data points
- Comprehensive and well-structured
- Balanced (strengths and areas for growth)
- Actionable for relationship compatibility assessment
- Focused on volatility tracking and risk assessment"""
            
            messages = [
                SystemMessage(content=BEHAVIOUR_PSYCHOLOGY_SYSTEM_PROMPT),
                HumanMessage(content=profile_prompt)
            ]
            
            response = self.llm.invoke(messages)
            profile_message = response.content
            
            # Store the profile in agent_data
            if "behaviour_psychology" not in state["agent_data"]:
                state["agent_data"]["behaviour_psychology"] = {}
            state["agent_data"]["behaviour_psychology"]["profile"] = profile_message
        
        # Add the profile as an AI message
        state["messages"].append(AIMessage(content=profile_message))
        
        return state
