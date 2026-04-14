"""
Education Readiness Agent
Analyzes intellectual orientation, learning patterns, academic maturity,
and educational aspirations to assess how education influences compatibility.
"""
import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.state.state import AgentState
from app.prompts.education_readiness.system_prompt import EDUCATION_READINESS_SYSTEM_PROMPT
from app.knowledge.rag_helper import get_agent_specific_content


class EducationReadinessAgent:
    """
    Education Readiness Agent specialized in analyzing educational background,
    intellectual compatibility, academic aspirations, and learning behavior patterns.
    """
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-4"):
        """
        Initialize the Education Readiness Agent.
        
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
        Build the LangGraph workflow for education readiness analysis.
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_education", self._analyze_education)
        workflow.add_node("generate_profile", self._generate_profile)
        
        # Set entry point
        workflow.set_entry_point("analyze_education")
        
        # Define flow: analyze -> generate profile -> end
        workflow.add_edge("analyze_education", "generate_profile")
        workflow.add_edge("generate_profile", END)
        
        return workflow.compile()
    
    def _analyze_education(self, state: AgentState) -> AgentState:
        """
        Analyze education and learning data to extract key insights.
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
            agent_domain="education_readiness",
            user_query=user_query
        )
        
        # Check if we have education/learning data
        has_education_data = (
            "education" in kb_summary.lower() or
            "academic" in kb_summary.lower() or
            "learning" in kb_summary.lower() or
            "study" in kb_summary.lower() or
            "qualification" in kb_summary.lower() or
            "degree" in kb_summary.lower() or
            "school" in kb_summary.lower() or
            "university" in kb_summary.lower() or
            "college" in kb_summary.lower() or
            "RRI" in kb_summary or
            "PRI" in kb_summary or
            "7WPD" in kb_summary
        )
        
        if not has_education_data:
            # If no education data, inform user
            analysis_prompt = f"""Based on the available knowledge base data, identify if education and learning data is available.

Knowledge Base Summary:
{kb_summary}

If education/learning data is not available, inform the user that this agent requires academic records, education timeline, future study intentions, learning readiness assessments, and RRI/PRI education markers to perform education readiness analysis."""
        else:
            # Analyze available education data
            analysis_prompt = f"""Analyze the education and learning data provided in the knowledge base.

Knowledge Base Summary:
{kb_summary}

Extract and summarize:
1. Academic records and educational qualifications
2. Education timeline and academic history
3. Future study intentions and educational plans
4. Learning readiness assessments
5. Study patterns and habits
6. Educational goals and aspirations
7. RRI (Relationship Readiness Index) education-related markers
8. PRI (Personality Readiness Index) learning-related markers

Identify key education and learning indicators that will be used for deep analysis."""
        
        # Use LLM to analyze
        messages = [
            SystemMessage(content=EDUCATION_READINESS_SYSTEM_PROMPT),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Store analysis in agent_data
        if "agent_data" not in state:
            state["agent_data"] = {}
        
        if "education_readiness" not in state["agent_data"]:
            state["agent_data"]["education_readiness"] = {}
        
        state["agent_data"]["education_readiness"]["preliminary_analysis"] = response.content
        
        return state
    
    def _generate_profile(self, state: AgentState) -> AgentState:
        """
        Generate comprehensive education readiness profile.
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
            agent_domain="education_readiness",
            user_query=user_query
        )
        preliminary_analysis = state.get("agent_data", {}).get("education_readiness", {}).get("preliminary_analysis", "")
        
        # Check if we have the required data
        has_required_data = (
            "education" in kb_summary.lower() or
            "academic" in kb_summary.lower() or
            "learning" in kb_summary.lower() or
            "study" in kb_summary.lower() or
            "qualification" in kb_summary.lower() or
            "degree" in kb_summary.lower() or
            "school" in kb_summary.lower() or
            "university" in kb_summary.lower() or
            "college" in kb_summary.lower() or
            "RRI" in kb_summary or
            "PRI" in kb_summary or
            "7WPD" in kb_summary
        )
        
        if not has_required_data:
            profile_message = """I cannot generate a comprehensive education readiness profile because the required education and learning data is not available.

**Required Data:**
- Academic records and educational qualifications
- Education timeline and academic history
- Future study intentions and educational plans
- Learning readiness assessments
- Study patterns and habits
- Educational goals and aspirations
- RRI/PRI education-related markers

Please ensure this information is included in the candidate's knowledge base before requesting education readiness analysis."""
        else:
            # Generate comprehensive profile
            profile_prompt = f"""Generate a comprehensive EDUCATION READINESS PROFILE based on the available education and learning data.

Knowledge Base Summary:
{kb_summary}

Preliminary Analysis:
{preliminary_analysis}

Follow the output format specified in your system prompt:
1. EXECUTIVE SUMMARY
2. EDUCATION READINESS SCORE
3. ACADEMIC BACKGROUND ANALYSIS
4. LEARNING BEHAVIOR PATTERNS
5. INTELLECTUAL COMPATIBILITY INDICATORS
6. EDUCATION–RELATIONSHIP ALIGNMENT RISKS
7. FRICTION ZONES
8. CAREER-EDUCATION ALIGNMENT
9. RECOMMENDATIONS

Ensure all analysis is:
- Evidence-based with specific education and learning data points
- Comprehensive and well-structured
- Balanced (educational strengths and areas of concern)
- Actionable for relationship compatibility assessment
- Focused on low adaptability and education compatibility risk tracking
- Uses RRI, PRI, Learning Style Matrix, DISC, 7WPD, and Learning Motivation Index frameworks
- Deep in understanding educational motivations and learning patterns"""
            
            messages = [
                SystemMessage(content=EDUCATION_READINESS_SYSTEM_PROMPT),
                HumanMessage(content=profile_prompt)
            ]
            
            response = self.llm.invoke(messages)
            profile_message = response.content
            
            # Store the profile in agent_data
            if "education_readiness" not in state["agent_data"]:
                state["agent_data"]["education_readiness"] = {}
            state["agent_data"]["education_readiness"]["profile"] = profile_message
        
        # Add the profile as an AI message
        state["messages"].append(AIMessage(content=profile_message))
        
        return state
