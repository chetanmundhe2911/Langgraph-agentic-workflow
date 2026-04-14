"""
Medical Lifestyle Agent
Analyzes medical history, health risks, treatment adherence, and long-term health implications
to assess how medical and lifestyle factors influence relationship dynamics.
"""
import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.state.state import AgentState
from app.prompts.medical_lifestyle.system_prompt import MEDICAL_LIFESTYLE_SYSTEM_PROMPT
from app.knowledge.rag_helper import get_agent_specific_content


class MedicalLifestyleAgent:
    """
    Medical Lifestyle Agent specialized in analyzing medical history,
    chronic conditions, treatment adherence, and health-lifestyle interactions.
    """
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-4"):
        """
        Initialize the Medical Lifestyle Agent.
        
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
        Build the LangGraph workflow for medical lifestyle analysis.
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_medical", self._analyze_medical)
        workflow.add_node("generate_profile", self._generate_profile)
        
        # Set entry point
        workflow.set_entry_point("analyze_medical")
        
        # Define flow: analyze -> generate profile -> end
        workflow.add_edge("analyze_medical", "generate_profile")
        workflow.add_edge("generate_profile", END)
        
        return workflow.compile()
    
    def _analyze_medical(self, state: AgentState) -> AgentState:
        """
        Analyze medical and health data to extract key insights.
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
            agent_domain="medical_lifestyle",
            user_query=user_query
        )
        
        # Check if we have medical/health data
        has_medical_data = (
            "medical" in kb_summary.lower() or
            "health" in kb_summary.lower() or
            "condition" in kb_summary.lower() or
            "treatment" in kb_summary.lower() or
            "medication" in kb_summary.lower() or
            "chronic" in kb_summary.lower() or
            "diagnosis" in kb_summary.lower() or
            "RRI" in kb_summary or
            "HRI" in kb_summary
        )
        
        if not has_medical_data:
            # If no medical data, inform user
            analysis_prompt = f"""Based on the available knowledge base data, identify if medical and health data is available.

Knowledge Base Summary:
{kb_summary}

If medical/health data is not available, inform the user that this agent requires health history, medical conditions, treatment information, RRI, and HRI data to perform medical lifestyle analysis."""
        else:
            # Analyze available medical data
            analysis_prompt = f"""Analyze the medical and health data provided in the knowledge base.

Knowledge Base Summary:
{kb_summary}

Extract and summarize:
1. Health history forms and medical condition disclosures
2. Treatment logs or medication data
3. Preventive screening details
4. Lifestyle–medical interaction responses
5. RRI (Relationship Readiness Index) health-related readiness markers
6. HRI (Health Readiness Index) indicators

Identify key medical and health indicators that will be used for deep analysis."""
        
        # Use LLM to analyze
        messages = [
            SystemMessage(content=MEDICAL_LIFESTYLE_SYSTEM_PROMPT),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Store analysis in agent_data
        if "agent_data" not in state:
            state["agent_data"] = {}
        
        if "medical_lifestyle" not in state["agent_data"]:
            state["agent_data"]["medical_lifestyle"] = {}
        
        state["agent_data"]["medical_lifestyle"]["preliminary_analysis"] = response.content
        
        return state
    
    def _generate_profile(self, state: AgentState) -> AgentState:
        """
        Generate comprehensive medical lifestyle profile.
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
            agent_domain="medical_lifestyle",
            user_query=user_query
        )
        preliminary_analysis = state.get("agent_data", {}).get("medical_lifestyle", {}).get("preliminary_analysis", "")
        
        # Check if we have the required data
        has_required_data = (
            "medical" in kb_summary.lower() or
            "health" in kb_summary.lower() or
            "condition" in kb_summary.lower() or
            "treatment" in kb_summary.lower() or
            "medication" in kb_summary.lower() or
            "chronic" in kb_summary.lower() or
            "diagnosis" in kb_summary.lower() or
            "RRI" in kb_summary or
            "HRI" in kb_summary
        )
        
        if not has_required_data:
            profile_message = """I cannot generate a comprehensive medical lifestyle profile because the required health and medical data is not available.

**Required Data:**
- Health history forms
- Medical condition disclosures
- Treatment logs or medication data
- Preventive screening details
- Lifestyle–medical interaction responses
- RRI (Relationship Readiness Index) health-related readiness markers
- HRI (Health Readiness Index) indicators

Please ensure this information is included in the candidate's knowledge base before requesting medical lifestyle analysis."""
        else:
            # Generate comprehensive profile
            profile_prompt = f"""Generate a comprehensive MEDICAL LIFESTYLE PROFILE based on the available medical and health data.

Knowledge Base Summary:
{kb_summary}

Preliminary Analysis:
{preliminary_analysis}

Follow the output format specified in your system prompt:
1. EXECUTIVE SUMMARY
2. MEDICAL STABILITY REPORT
3. LONG-TERM RISK INTERPRETATION
4. TREATMENT ADHERENCE ANALYSIS
5. MEDICAL–RELATIONSHIP FRICTION INDICATORS
6. COMPATIBILITY CONSIDERATIONS FOR CHRONIC CONDITIONS
7. PREVENTIVE HEALTH EVALUATION
8. HEALTH RISK ASSESSMENT
9. RECOMMENDATIONS

Ensure all analysis is:
- Evidence-based with specific medical data points
- Comprehensive and well-structured
- Balanced (health strengths and areas requiring attention)
- Actionable for relationship compatibility assessment
- Focused on undisclosed issues and health risk tracking
- Uses Lifestyle Health Index framework where applicable
- Medically ethical and non-judgmental"""
            
            messages = [
                SystemMessage(content=MEDICAL_LIFESTYLE_SYSTEM_PROMPT),
                HumanMessage(content=profile_prompt)
            ]
            
            response = self.llm.invoke(messages)
            profile_message = response.content
            
            # Store the profile in agent_data
            if "medical_lifestyle" not in state["agent_data"]:
                state["agent_data"]["medical_lifestyle"] = {}
            state["agent_data"]["medical_lifestyle"]["profile"] = profile_message
        
        # Add the profile as an AI message
        state["messages"].append(AIMessage(content=profile_message))
        
        return state
