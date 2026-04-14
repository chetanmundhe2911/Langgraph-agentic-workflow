"""
Religious Values Agent
Assesses the impact of religious beliefs, faith practices, and cultural traditions
on relationship readiness and marital harmony.
"""
import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.state.state import AgentState
from app.prompts.religious_values.system_prompt import RELIGIOUS_VALUES_SYSTEM_PROMPT
from app.knowledge.rag_helper import get_agent_specific_content


class ReligiousValuesAgent:
    """
    Religious Values Agent specialized in assessing religious beliefs,
    faith practices, and cultural-religious alignment.
    """
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-4"):
        """
        Initialize the Religious Values Agent.
        
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
        Build the LangGraph workflow for religious values analysis.
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_religious", self._analyze_religious)
        workflow.add_node("generate_profile", self._generate_profile)
        
        # Set entry point
        workflow.set_entry_point("analyze_religious")
        
        # Define flow: analyze -> generate profile -> end
        workflow.add_edge("analyze_religious", "generate_profile")
        workflow.add_edge("generate_profile", END)
        
        return workflow.compile()
    
    def _analyze_religious(self, state: AgentState) -> AgentState:
        """
        Analyze religious values data to extract key insights.
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
            agent_domain="religious_values",
            user_query=user_query
        )
        
        # Check if we have religious data
        has_religious_data = (
            "religious" in kb_summary.lower() or
            "religion" in kb_summary.lower() or
            "faith" in kb_summary.lower() or
            "spiritual" in kb_summary.lower() or
            "ritual" in kb_summary.lower() or
            "prayer" in kb_summary.lower() or
            "worship" in kb_summary.lower() or
            "belief" in kb_summary.lower() or
            "temple" in kb_summary.lower() or
            "church" in kb_summary.lower() or
            "mosque" in kb_summary.lower() or
            "tradition" in kb_summary.lower() or
            "RRI" in kb_summary
        )
        
        if not has_religious_data:
            # If no religious data, inform user
            analysis_prompt = f"""Based on the available knowledge base data, identify if religious values data is available.

Knowledge Base Summary:
{kb_summary}

If religious values data is not available, inform the user that this agent requires religious values questionnaire, faith practice indicators, cultural tradition patterns, and RRI spiritual compatibility markers to perform religious values analysis."""
        else:
            # Analyze available religious data
            analysis_prompt = f"""Analyze the religious values data provided in the knowledge base.

Knowledge Base Summary:
{kb_summary}

Extract and summarize:
1. Religious values questionnaire responses
2. Faith practice indicators and religious observance patterns
3. Cultural tradition patterns and cultural-religious practices
4. RRI (Relationship Readiness Index) spiritual compatibility markers
5. Belief Questionnaire data
6. Religious practices and expectations information

Identify key religious values indicators that will be used for deep analysis."""
        
        # Use LLM to analyze
        messages = [
            SystemMessage(content=RELIGIOUS_VALUES_SYSTEM_PROMPT),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Store analysis in agent_data
        if "agent_data" not in state:
            state["agent_data"] = {}
        
        if "religious_values" not in state["agent_data"]:
            state["agent_data"]["religious_values"] = {}
        
        state["agent_data"]["religious_values"]["preliminary_analysis"] = response.content
        
        return state
    
    def _generate_profile(self, state: AgentState) -> AgentState:
        """
        Generate comprehensive religious values profile.
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
            agent_domain="religious_values",
            user_query=user_query
        )
        preliminary_analysis = state.get("agent_data", {}).get("religious_values", {}).get("preliminary_analysis", "")
        
        # Check if we have the required data
        has_required_data = (
            "religious" in kb_summary.lower() or
            "religion" in kb_summary.lower() or
            "faith" in kb_summary.lower() or
            "spiritual" in kb_summary.lower() or
            "ritual" in kb_summary.lower() or
            "prayer" in kb_summary.lower() or
            "worship" in kb_summary.lower() or
            "belief" in kb_summary.lower() or
            "temple" in kb_summary.lower() or
            "church" in kb_summary.lower() or
            "mosque" in kb_summary.lower() or
            "tradition" in kb_summary.lower() or
            "RRI" in kb_summary
        )
        
        if not has_required_data:
            profile_message = """I cannot generate a comprehensive religious values profile because the required religious data is not available.

**Required Data:**
- Religious values questionnaire
- Faith practice indicators
- Cultural tradition patterns
- RRI (Relationship Readiness Index) spiritual compatibility markers
- Belief Questionnaire data

Please ensure this information is included in the candidate's knowledge base before requesting religious values analysis."""
        else:
            # Generate comprehensive profile
            profile_prompt = f"""Generate a comprehensive RELIGIOUS VALUES PROFILE based on the available religious values data.

Knowledge Base Summary:
{kb_summary}

Preliminary Analysis:
{preliminary_analysis}

Follow the output format specified in your system prompt:
1. EXECUTIVE SUMMARY
2. RELIGIOUS VALUE PROFILE
3. FAITH-PRACTICE COMPATIBILITY ASSESSMENT
4. POTENTIAL RELIGIOUS FRICTION POINTS
5. INTERFAITH OR INTRAFAITH ALIGNMENT INDICATORS
6. ALIGNMENT SCORE & TOLERANCE REPORT
7. RELIGIOUS RIGIDITY RISK ASSESSMENT
8. RECOMMENDATIONS

Ensure all analysis is:
- Evidence-based with specific religious values data points
- Comprehensive and well-structured
- Balanced (religious strengths and areas of concern)
- Actionable for relationship compatibility assessment
- Focused on religious rigidity and compatibility risk tracking
- Uses Belief Questionnaire + RRI and Values & Belief Index frameworks
- Respectful of all religious beliefs and practices
- Non-judgmental and culturally sensitive"""
            
            messages = [
                SystemMessage(content=RELIGIOUS_VALUES_SYSTEM_PROMPT),
                HumanMessage(content=profile_prompt)
            ]
            
            response = self.llm.invoke(messages)
            profile_message = response.content
            
            # Store the profile in agent_data
            if "religious_values" not in state["agent_data"]:
                state["agent_data"]["religious_values"] = {}
            state["agent_data"]["religious_values"]["profile"] = profile_message
        
        # Add the profile as an AI message
        state["messages"].append(AIMessage(content=profile_message))
        
        return state
