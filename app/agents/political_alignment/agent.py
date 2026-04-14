"""
Political Alignment Agent
Analyzes political orientation, belief strength, ideological behavior,
and civic-value alignment to determine how political stances influence relationship harmony.
"""
import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.state.state import AgentState
from app.prompts.political_alignment.system_prompt import POLITICAL_ALIGNMENT_SYSTEM_PROMPT
from app.knowledge.rag_helper import get_agent_specific_content


class PoliticalAlignmentAgent:
    """
    Political Alignment Agent specialized in analyzing political orientation,
    ideological behavior, and political compatibility.
    """
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-4"):
        """
        Initialize the Political Alignment Agent.
        
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
        Build the LangGraph workflow for political alignment analysis.
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_political", self._analyze_political)
        workflow.add_node("generate_profile", self._generate_profile)
        
        # Set entry point
        workflow.set_entry_point("analyze_political")
        
        # Define flow: analyze -> generate profile -> end
        workflow.add_edge("analyze_political", "generate_profile")
        workflow.add_edge("generate_profile", END)
        
        return workflow.compile()
    
    def _analyze_political(self, state: AgentState) -> AgentState:
        """
        Analyze political alignment data to extract key insights.
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
            agent_domain="political_alignment",
            user_query=user_query
        )
        
        # Check if we have political data
        has_political_data = (
            "political" in kb_summary.lower() or
            "politics" in kb_summary.lower() or
            "ideology" in kb_summary.lower() or
            "ideological" in kb_summary.lower() or
            "civic" in kb_summary.lower() or
            "governance" in kb_summary.lower() or
            "policy" in kb_summary.lower() or
            "social justice" in kb_summary.lower() or
            "left" in kb_summary.lower() or
            "right" in kb_summary.lower() or
            "center" in kb_summary.lower() or
            "opinion" in kb_summary.lower() or
            "affiliation" in kb_summary.lower() or
            "RRI" in kb_summary
        )
        
        if not has_political_data:
            # If no political data, inform user
            analysis_prompt = f"""Based on the available knowledge base data, identify if political alignment data is available.

Knowledge Base Summary:
{kb_summary}

If political alignment data is not available, inform the user that this agent requires political values questionnaire, responses to political opinion statements, political engagement behavior indicators, and RRI social-adaptability markers to perform political alignment analysis."""
        else:
            # Analyze available political data
            analysis_prompt = f"""Analyze the political alignment data provided in the knowledge base.

Knowledge Base Summary:
{kb_summary}

Extract and summarize:
1. Political values questionnaire responses
2. Responses to political opinion statements
3. Political engagement behavior indicators
4. RRI (Relationship Readiness Index) social-adaptability and worldview markers
5. Cultural and family influence indicators
6. Scenario-based political conflict responses
7. Political beliefs and tolerance information
8. Opinions and political affiliations data
9. Belief Questionnaire data

Identify key political alignment indicators that will be used for deep analysis."""
        
        # Use LLM to analyze
        messages = [
            SystemMessage(content=POLITICAL_ALIGNMENT_SYSTEM_PROMPT),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Store analysis in agent_data
        if "agent_data" not in state:
            state["agent_data"] = {}
        
        if "political_alignment" not in state["agent_data"]:
            state["agent_data"]["political_alignment"] = {}
        
        state["agent_data"]["political_alignment"]["preliminary_analysis"] = response.content
        
        return state
    
    def _generate_profile(self, state: AgentState) -> AgentState:
        """
        Generate comprehensive political alignment profile.
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
            agent_domain="political_alignment",
            user_query=user_query
        )
        preliminary_analysis = state.get("agent_data", {}).get("political_alignment", {}).get("preliminary_analysis", "")
        
        # Check if we have the required data
        has_required_data = (
            "political" in kb_summary.lower() or
            "politics" in kb_summary.lower() or
            "ideology" in kb_summary.lower() or
            "ideological" in kb_summary.lower() or
            "civic" in kb_summary.lower() or
            "governance" in kb_summary.lower() or
            "policy" in kb_summary.lower() or
            "social justice" in kb_summary.lower() or
            "left" in kb_summary.lower() or
            "right" in kb_summary.lower() or
            "center" in kb_summary.lower() or
            "opinion" in kb_summary.lower() or
            "affiliation" in kb_summary.lower() or
            "RRI" in kb_summary
        )
        
        if not has_required_data:
            profile_message = """I cannot generate a comprehensive political alignment profile because the required political data is not available.

**Required Data:**
- Political values questionnaire
- Responses to political opinion statements
- Political engagement behavior indicators
- RRI (Relationship Readiness Index) social-adaptability and worldview markers
- Cultural and family influence indicators
- Scenario-based political conflict responses
- Belief Questionnaire data

Please ensure this information is included in the candidate's knowledge base before requesting political alignment analysis."""
        else:
            # Generate comprehensive profile
            profile_prompt = f"""Generate a comprehensive POLITICAL ALIGNMENT PROFILE based on the available political alignment data.

Knowledge Base Summary:
{kb_summary}

Preliminary Analysis:
{preliminary_analysis}

Follow the output format specified in your system prompt:
1. EXECUTIVE SUMMARY
2. POLITICAL VALUES PROFILE
3. IDEOLOGY STRENGTH AND RIGIDITY ANALYSIS
4. OPENNESS-TO-DIFFERENCES SCORE
5. IMPACT OF POLITICAL WORLDVIEW ON RELATIONSHIP EXPECTATIONS
6. COMPATIBILITY RISKS LINKED TO POLITICAL DIFFERENCES
7. AREAS OF POTENTIAL MISUNDERSTANDING OR IDEOLOGICAL FRICTION
8. EXTREMISM RISK ASSESSMENT
9. RECOMMENDATIONS

Ensure all analysis is:
- Evidence-based with specific political alignment data points
- Comprehensive and well-structured
- Balanced (political strengths and areas of concern)
- Actionable for relationship compatibility assessment
- Focused on extremism and political compatibility risk tracking
- Uses Belief Questionnaire + RRI and Values-Morals Assessment frameworks
- Completely neutral and non-partisan
- Respectful of all political beliefs and ideologies"""
            
            messages = [
                SystemMessage(content=POLITICAL_ALIGNMENT_SYSTEM_PROMPT),
                HumanMessage(content=profile_prompt)
            ]
            
            response = self.llm.invoke(messages)
            profile_message = response.content
            
            # Store the profile in agent_data
            if "political_alignment" not in state["agent_data"]:
                state["agent_data"]["political_alignment"] = {}
            state["agent_data"]["political_alignment"]["profile"] = profile_message
        
        # Add the profile as an AI message
        state["messages"].append(AIMessage(content=profile_message))
        
        return state
