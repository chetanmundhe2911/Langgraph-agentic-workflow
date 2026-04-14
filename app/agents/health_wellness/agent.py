"""
Health Wellness Agent
Evaluates physical health, lifestyle patterns, and wellness indicators
to assess health status and how health factors may influence relationship compatibility.
"""
import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.state.state import AgentState
from app.prompts.health_wellness.system_prompt import HEALTH_WELLNESS_SYSTEM_PROMPT
from app.knowledge.rag_helper import get_agent_specific_content


class HealthWellnessAgent:
    """
    Health Wellness Agent specialized in evaluating physical health,
    lifestyle patterns, and wellness indicators.
    """
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-4"):
        """
        Initialize the Health Wellness Agent.
        
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
        Build the LangGraph workflow for health wellness analysis.
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_wellness", self._analyze_wellness)
        workflow.add_node("generate_report", self._generate_report)
        
        # Set entry point
        workflow.set_entry_point("analyze_wellness")
        
        # Define flow: analyze -> generate report -> end
        workflow.add_edge("analyze_wellness", "generate_report")
        workflow.add_edge("generate_report", END)
        
        return workflow.compile()
    
    def _analyze_wellness(self, state: AgentState) -> AgentState:
        """
        Analyze health and wellness data to extract key insights.
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
            agent_domain="health_wellness",
            user_query=user_query
        )
        
        # Check if we have health/wellness data
        has_health_data = (
            "health" in kb_summary.lower() or
            "wellness" in kb_summary.lower() or
            "fitness" in kb_summary.lower() or
            "diet" in kb_summary.lower() or
            "exercise" in kb_summary.lower() or
            "nutrition" in kb_summary.lower() or
            "lifestyle" in kb_summary.lower() or
            "medical" in kb_summary.lower() or
            "HRI" in kb_summary
        )
        
        if not has_health_data:
            # If no health data, inform user
            analysis_prompt = f"""Based on the available knowledge base data, identify if health and wellness data is available.

Knowledge Base Summary:
{kb_summary}

If health/wellness data is not available, inform the user that this agent requires health reports, lifestyle routines, health questionnaires, and HRI data to perform health wellness analysis."""
        else:
            # Analyze available health data
            analysis_prompt = f"""Analyze the health and wellness data provided in the knowledge base.

Knowledge Base Summary:
{kb_summary}

Extract and summarize:
1. Health reports (general health status, medical conditions, fitness level, health notes)
2. Lifestyle routines (daily routines, exercise, dietary patterns, sleep, health maintenance)
3. Health lifestyle questionnaire responses
4. HRI (Health Readiness Index) indicators

Identify key health and wellness indicators that will be used for deep analysis."""
        
        # Use LLM to analyze
        messages = [
            SystemMessage(content=HEALTH_WELLNESS_SYSTEM_PROMPT),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Store analysis in agent_data
        if "agent_data" not in state:
            state["agent_data"] = {}
        
        if "health_wellness" not in state["agent_data"]:
            state["agent_data"]["health_wellness"] = {}
        
        state["agent_data"]["health_wellness"]["preliminary_analysis"] = response.content
        
        return state
    
    def _generate_report(self, state: AgentState) -> AgentState:
        """
        Generate comprehensive health wellness analysis report.
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
            agent_domain="health_wellness",
            user_query=user_query
        )
        preliminary_analysis = state.get("agent_data", {}).get("health_wellness", {}).get("preliminary_analysis", "")
        
        # Check if we have the required data
        has_required_data = (
            "health" in kb_summary.lower() or
            "wellness" in kb_summary.lower() or
            "fitness" in kb_summary.lower() or
            "diet" in kb_summary.lower() or
            "exercise" in kb_summary.lower() or
            "nutrition" in kb_summary.lower() or
            "lifestyle" in kb_summary.lower() or
            "medical" in kb_summary.lower() or
            "HRI" in kb_summary
        )
        
        if not has_required_data:
            report_message = """I cannot generate a comprehensive health wellness analysis report because the required health and wellness data is not available.

**Required Data:**
- Health reports (general health status, medical conditions, fitness level)
- Lifestyle routines (daily routines, exercise, dietary patterns, sleep)
- Health lifestyle questionnaire responses
- HRI (Health Readiness Index) indicators

Please ensure this information is included in the candidate's knowledge base before requesting health wellness analysis."""
        else:
            # Generate comprehensive report
            report_prompt = f"""Generate a comprehensive HEALTH WELLNESS ANALYSIS REPORT based on the available health and wellness data.

Knowledge Base Summary:
{kb_summary}

Preliminary Analysis:
{preliminary_analysis}

Follow the output format specified in your system prompt:
1. EXECUTIVE SUMMARY
2. WELLNESS SCORE BREAKDOWN
3. PHYSICAL HEALTH ASSESSMENT
4. DIET ANALYSIS
5. EXERCISE & FITNESS ANALYSIS
6. MEDICAL HISTORY EVALUATION
7. LIFESTYLE PATTERN ASSESSMENT
8. HEALTH RISKS IDENTIFICATION
9. HEALTH READINESS INDEX ASSESSMENT
10. RELATIONSHIP COMPATIBILITY INSIGHTS
11. RECOMMENDATIONS

Ensure all analysis is:
- Evidence-based with specific health data points
- Comprehensive and well-structured
- Balanced (health strengths and areas for improvement)
- Actionable for relationship compatibility assessment
- Focused on smoking and addiction risk tracking
- Uses Health Readiness Index (HRI) framework
- Health-accurate and non-judgmental"""
            
            messages = [
                SystemMessage(content=HEALTH_WELLNESS_SYSTEM_PROMPT),
                HumanMessage(content=report_prompt)
            ]
            
            response = self.llm.invoke(messages)
            report_message = response.content
            
            # Store the report in agent_data
            if "health_wellness" not in state["agent_data"]:
                state["agent_data"]["health_wellness"] = {}
            state["agent_data"]["health_wellness"]["report"] = report_message
        
        # Add the report as an AI message
        state["messages"].append(AIMessage(content=report_message))
        
        return state
