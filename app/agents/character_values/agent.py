"""
Character–Values Agent
Analyzes personal values, ethical frameworks, decision-making integrity, moral philosophy,
and long-term character stability to understand how values influence relationship compatibility.
"""
import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.state.state import AgentState
from app.prompts.character_values.system_prompt import CHARACTER_VALUES_SYSTEM_PROMPT
from app.knowledge.rag_helper import get_agent_specific_content


class CharacterValuesAgent:
    """
    Character–Values Agent specialized in analyzing personal values,
    ethical frameworks, integrity, and character stability.
    """
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-4"):
        """
        Initialize the Character–Values Agent.
        
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
        Build the LangGraph workflow for character-values analysis.
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_values", self._analyze_values)
        workflow.add_node("generate_profile", self._generate_profile)
        
        # Set entry point
        workflow.set_entry_point("analyze_values")
        
        # Define flow: analyze -> generate profile -> end
        workflow.add_edge("analyze_values", "generate_profile")
        workflow.add_edge("generate_profile", END)
        
        return workflow.compile()
    
    def _analyze_values(self, state: AgentState) -> AgentState:
        """
        Analyze character and values data to extract key insights.
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
            agent_domain="character_values",
            user_query=user_query
        )
        
        # Check if we have values/character data
        has_values_data = (
            "value" in kb_summary.lower() or
            "character" in kb_summary.lower() or
            "ethics" in kb_summary.lower() or
            "moral" in kb_summary.lower() or
            "integrity" in kb_summary.lower() or
            "philosophy" in kb_summary.lower() or
            "habit" in kb_summary.lower() or
            "hobby" in kb_summary.lower() or
            "RRI" in kb_summary or
            "PRI" in kb_summary or
            "7WPD" in kb_summary
        )
        
        if not has_values_data:
            # If no values data, inform user
            analysis_prompt = f"""Based on the available knowledge base data, identify if character and values data is available.

Knowledge Base Summary:
{kb_summary}

If character/values data is not available, inform the user that this agent requires value orientation assessments, RRI/PRI ethics markers, 7WPD value-driven dimensions, personal philosophy statements, and habits/lifestyle patterns to perform character-values analysis."""
        else:
            # Analyze available values data
            analysis_prompt = f"""Analyze the character and values data provided in the knowledge base.

Knowledge Base Summary:
{kb_summary}

Extract and summarize:
1. Value orientation assessments and value profile
2. RRI (Relationship Readiness Index) ethics markers
3. PRI (Personality Readiness Index) ethics markers
4. 7WPD (7 Dimensions of Personality Development) value-driven dimensions
5. Personal philosophy statements
6. Habits and lifestyle patterns (hobbies, food preferences, lifestyle choices)

Identify key character and values indicators that will be used for deep analysis."""
        
        # Use LLM to analyze
        messages = [
            SystemMessage(content=CHARACTER_VALUES_SYSTEM_PROMPT),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Store analysis in agent_data
        if "agent_data" not in state:
            state["agent_data"] = {}
        
        if "character_values" not in state["agent_data"]:
            state["agent_data"]["character_values"] = {}
        
        state["agent_data"]["character_values"]["preliminary_analysis"] = response.content
        
        return state
    
    def _generate_profile(self, state: AgentState) -> AgentState:
        """
        Generate comprehensive character-values profile.
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
            agent_domain="character_values",
            user_query=user_query
        )
        preliminary_analysis = state.get("agent_data", {}).get("character_values", {}).get("preliminary_analysis", "")
        
        # Check if we have the required data
        has_required_data = (
            "value" in kb_summary.lower() or
            "character" in kb_summary.lower() or
            "ethics" in kb_summary.lower() or
            "moral" in kb_summary.lower() or
            "integrity" in kb_summary.lower() or
            "philosophy" in kb_summary.lower() or
            "habit" in kb_summary.lower() or
            "hobby" in kb_summary.lower() or
            "RRI" in kb_summary or
            "PRI" in kb_summary or
            "7WPD" in kb_summary
        )
        
        if not has_required_data:
            profile_message = """I cannot generate a comprehensive character-values profile because the required values and character data is not available.

**Required Data:**
- Value orientation assessments
- RRI/PRI ethics markers
- 7WPD value-driven dimensions
- Personal philosophy statements
- Habits and lifestyle patterns (hobbies, food preferences, lifestyle choices)
- Values profile

Please ensure this information is included in the candidate's knowledge base before requesting character-values analysis."""
        else:
            # Generate comprehensive profile
            profile_prompt = f"""Generate a comprehensive CHARACTER–VALUES PROFILE based on the available character and values data.

Knowledge Base Summary:
{kb_summary}

Preliminary Analysis:
{preliminary_analysis}

Follow the output format specified in your system prompt:
1. EXECUTIVE SUMMARY
2. VALUE COMPATIBILITY REPORT
3. INTEGRITY AND CHARACTER ANALYSIS
4. RELATIONSHIP-VALUE ALIGNMENT INDICATORS
5. POTENTIAL FRICTION POINTS IN VALUE MISMATCH
6. HABITS AND LIFESTYLE ANALYSIS
7. COMPATIBILITY INDEX
8. RECOMMENDATIONS

Ensure all analysis is:
- Evidence-based with specific values and character data points
- Comprehensive and well-structured
- Balanced (value strengths and areas of concern)
- Actionable for relationship compatibility assessment
- Focused on rigid habits and inflexible value patterns risk tracking
- Uses RRI + 7WPD Values Matrix and Character & Values Index frameworks
- Deep in understanding moral foundations and ethical frameworks"""
            
            messages = [
                SystemMessage(content=CHARACTER_VALUES_SYSTEM_PROMPT),
                HumanMessage(content=profile_prompt)
            ]
            
            response = self.llm.invoke(messages)
            profile_message = response.content
            
            # Store the profile in agent_data
            if "character_values" not in state["agent_data"]:
                state["agent_data"]["character_values"] = {}
            state["agent_data"]["character_values"]["profile"] = profile_message
        
        # Add the profile as an AI message
        state["messages"].append(AIMessage(content=profile_message))
        
        return state
