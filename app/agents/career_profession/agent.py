"""
Career-Profession Agent
Analyzes professional stability, career ambition, and work-life dynamics to assess relationship compatibility.
"""
import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.state.state import AgentState
from app.prompts.career_profession.system_prompt import CAREER_PROFESSION_SYSTEM_PROMPT
from app.knowledge.rag_helper import get_agent_specific_content


class CareerProfessionAgent:
    """
    Career-Profession Agent specialized in analyzing professional stability,
    career ambition, and work-life dynamics.
    """
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-4"):
        """
        Initialize the Career-Profession Agent.
        
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
        Build the LangGraph workflow for career-profession analysis.
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_career", self._analyze_career)
        workflow.add_node("generate_profile", self._generate_profile)
        
        # Set entry point
        workflow.set_entry_point("analyze_career")
        
        # Define flow: analyze -> generate profile -> end
        workflow.add_edge("analyze_career", "generate_profile")
        workflow.add_edge("generate_profile", END)
        
        return workflow.compile()
    
    def _analyze_career(self, state: AgentState) -> AgentState:
        """
        Analyze career and professional data to extract key insights.
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
            agent_domain="career_profession",
            user_query=user_query
        )
        
        # Check if we have career/professional data
        has_career_data = (
            "employment" in kb_summary.lower() or
            "job" in kb_summary.lower() or
            "career" in kb_summary.lower() or
            "profession" in kb_summary.lower() or
            "salary" in kb_summary.lower() or
            "income" in kb_summary.lower() or
            "work" in kb_summary.lower() or
            "PRI" in kb_summary or
            "RRI" in kb_summary
        )
        
        if not has_career_data:
            # If no career data, inform user
            analysis_prompt = f"""Based on the available knowledge base data, identify if career and professional data is available.

Knowledge Base Summary:
{kb_summary}

If career/professional data is not available, inform the user that this agent requires employment history, career information, PRI, and RRI data to perform career-profession analysis."""
        else:
            # Analyze available career data
            analysis_prompt = f"""Analyze the career and professional data provided in the knowledge base.

Knowledge Base Summary:
{kb_summary}

Extract and summarize:
1. Employment timeline and job change history
2. Salary information and income consistency
3. Work schedule and weekly work hours
4. Career goals and professional aspirations
5. Stress indicators and job-pressure responses
6. PRI professional behavior markers
7. RRI career-readiness and stability markers

Identify key professional indicators that will be used for deep analysis."""
        
        # Use LLM to analyze
        messages = [
            SystemMessage(content=CAREER_PROFESSION_SYSTEM_PROMPT),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Store analysis in agent_data
        if "agent_data" not in state:
            state["agent_data"] = {}
        
        if "career_profession" not in state["agent_data"]:
            state["agent_data"]["career_profession"] = {}
        
        state["agent_data"]["career_profession"]["preliminary_analysis"] = response.content
        
        return state
    
    def _generate_profile(self, state: AgentState) -> AgentState:
        """
        Generate comprehensive career-profession profile.
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
            agent_domain="career_profession",
            user_query=user_query
        )
        preliminary_analysis = state.get("agent_data", {}).get("career_profession", {}).get("preliminary_analysis", "")
        
        # Check if we have the required data
        has_required_data = (
            "employment" in kb_summary.lower() or
            "job" in kb_summary.lower() or
            "career" in kb_summary.lower() or
            "profession" in kb_summary.lower() or
            "salary" in kb_summary.lower() or
            "income" in kb_summary.lower() or
            "work" in kb_summary.lower() or
            "PRI" in kb_summary or
            "RRI" in kb_summary
        )
        
        if not has_required_data:
            profile_message = """I cannot generate a comprehensive career-profession profile because the required professional data is not available.

**Required Data:**
- Employment timeline and job change history
- Salary information and income consistency
- Work schedule and weekly work hours
- Career goals and professional aspirations
- Stress indicators and job-pressure responses
- PRI (Personality Readiness Index) professional behavior markers
- RRI (Relationship Readiness Index) career-readiness and stability markers

Please ensure this information is included in the candidate's knowledge base before requesting career-profession analysis."""
        else:
            # Generate comprehensive profile
            profile_prompt = f"""Generate a comprehensive CAREER-PROFESSION PROFILE based on the available career and professional data.

Knowledge Base Summary:
{kb_summary}

Preliminary Analysis:
{preliminary_analysis}

Follow the output format specified in your system prompt:
1. EXECUTIVE SUMMARY
2. CAREER STABILITY ANALYSIS
3. AMBITION AND GROWTH-ORIENTATION
4. WORK-LIFE BALANCE ASSESSMENT
5. STRESS FRICTION POINTS AND COPING
6. FINANCIAL RELIABILITY ANALYSIS
7. CAREER-RELATIONSHIP INTERACTION INSIGHTS
8. RISK ASSESSMENT
9. RECOMMENDATIONS

Ensure all analysis is:
- Evidence-based with specific data points
- Comprehensive and well-structured
- Balanced (strengths and areas for growth)
- Actionable for relationship compatibility assessment
- Focused on overwork and instability risk tracking
- Uses 7WPD Achievement and Stability dimensions where applicable"""
            
            messages = [
                SystemMessage(content=CAREER_PROFESSION_SYSTEM_PROMPT),
                HumanMessage(content=profile_prompt)
            ]
            
            response = self.llm.invoke(messages)
            profile_message = response.content
            
            # Store the profile in agent_data
            if "career_profession" not in state["agent_data"]:
                state["agent_data"]["career_profession"] = {}
            state["agent_data"]["career_profession"]["profile"] = profile_message
        
        # Add the profile as an AI message
        state["messages"].append(AIMessage(content=profile_message))
        
        return state
