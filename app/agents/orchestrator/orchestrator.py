"""
Intelligent Orchestrator with Multi-Agent Chaining
Routes requests intelligently and chains multiple agents when needed.
"""
import os
import json
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from app.state.state import AgentState
from app.agents.behaviour_psychology.agent import BehaviourPsychologyAgent
from app.agents.career_profession.agent import CareerProfessionAgent
from app.agents.medical_lifestyle.agent import MedicalLifestyleAgent
from app.agents.health_wellness.agent import HealthWellnessAgent
from app.agents.family_dynamics.agent import FamilyDynamicsAgent
from app.agents.character_values.agent import CharacterValuesAgent
from app.agents.education_readiness.agent import EducationReadinessAgent
from app.agents.social_philosophy.agent import SocialPhilosophyAgent
from app.agents.hygiene_lifestyle.agent import HygieneLifestyleAgent
from app.agents.life_philosophy.agent import LifePhilosophyAgent
from app.agents.religious_values.agent import ReligiousValuesAgent
from app.agents.political_alignment.agent import PoliticalAlignmentAgent
from app.prompts.orchestrator.router_prompt import ROUTER_SYSTEM_PROMPT


class Orchestrator:
    """
    Intelligent Orchestrator Agent that routes tasks to specific sub-agents.
    Supports intelligent routing based on user messages and multi-agent chaining.
    """
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-4o"):
        """
        Initialize the Orchestrator with intelligent routing capabilities.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model_name: Model to use for routing and all agents (default: gpt-4o)
                       Use gpt-4o or gpt-4-turbo for higher token limits
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Store model name for passing to agents
        self.model_name = model_name
        
        # LLM for intelligent routing
        self.router_llm = ChatOpenAI(
            model=model_name,
            temperature=0.3,  # Lower temperature for more consistent routing
            api_key=api_key
        )
        
        # Initialize all agents with the same model
        self.behaviour_psychology_agent = BehaviourPsychologyAgent(api_key=api_key, model_name=model_name)
        self.career_profession_agent = CareerProfessionAgent(api_key=api_key, model_name=model_name)
        self.medical_lifestyle_agent = MedicalLifestyleAgent(api_key=api_key, model_name=model_name)
        self.health_wellness_agent = HealthWellnessAgent(api_key=api_key, model_name=model_name)
        self.family_dynamics_agent = FamilyDynamicsAgent(api_key=api_key, model_name=model_name)
        self.character_values_agent = CharacterValuesAgent(api_key=api_key, model_name=model_name)
        self.education_readiness_agent = EducationReadinessAgent(api_key=api_key, model_name=model_name)
        self.social_philosophy_agent = SocialPhilosophyAgent(api_key=api_key, model_name=model_name)
        self.hygiene_lifestyle_agent = HygieneLifestyleAgent(api_key=api_key, model_name=model_name)
        self.life_philosophy_agent = LifePhilosophyAgent(api_key=api_key, model_name=model_name)
        self.religious_values_agent = ReligiousValuesAgent(api_key=api_key, model_name=model_name)
        self.political_alignment_agent = PoliticalAlignmentAgent(api_key=api_key, model_name=model_name)
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow with intelligent routing and multi-agent chaining.
        """
        workflow = StateGraph(AgentState)

        # Define nodes for each agent
        workflow.add_node("behaviour_psychology_agent", self._run_behaviour_psychology_agent)
        workflow.add_node("career_profession_agent", self._run_career_profession_agent)
        workflow.add_node("medical_lifestyle_agent", self._run_medical_lifestyle_agent)
        workflow.add_node("health_wellness_agent", self._run_health_wellness_agent)
        workflow.add_node("family_dynamics_agent", self._run_family_dynamics_agent)
        workflow.add_node("character_values_agent", self._run_character_values_agent)
        workflow.add_node("education_readiness_agent", self._run_education_readiness_agent)
        workflow.add_node("social_philosophy_agent", self._run_social_philosophy_agent)
        workflow.add_node("hygiene_lifestyle_agent", self._run_hygiene_lifestyle_agent)
        workflow.add_node("life_philosophy_agent", self._run_life_philosophy_agent)
        workflow.add_node("religious_values_agent", self._run_religious_values_agent)
        workflow.add_node("political_alignment_agent", self._run_political_alignment_agent)
        
        # Entry point - intelligent router
        workflow.set_entry_point("router")
        
        # Router node (intelligent routing logic)
        workflow.add_node("router", self._intelligent_route)
        
        # Conditional edges from router to agents
        workflow.add_conditional_edges(
            "router",
            self._get_next_agent,
            {
                "behaviour_psychology": "behaviour_psychology_agent",
                "career_profession": "career_profession_agent",
                "medical_lifestyle": "medical_lifestyle_agent",
                "health_wellness": "health_wellness_agent",
                "family_dynamics": "family_dynamics_agent",
                "character_values": "character_values_agent",
                "education_readiness": "education_readiness_agent",
                "social_philosophy": "social_philosophy_agent",
                "hygiene_lifestyle": "hygiene_lifestyle_agent",
                "life_philosophy": "life_philosophy_agent",
                "religious_values": "religious_values_agent",
                "political_alignment": "political_alignment_agent",
                "end": END
            }
        )
        
        # After agents finish, check if we need to chain to next agent or end
        workflow.add_conditional_edges(
            "behaviour_psychology_agent",
            self._should_continue_chain,
            {"continue": "router", "end": END}
        )
        workflow.add_conditional_edges(
            "career_profession_agent",
            self._should_continue_chain,
            {"continue": "router", "end": END}
        )
        workflow.add_conditional_edges(
            "medical_lifestyle_agent",
            self._should_continue_chain,
            {"continue": "router", "end": END}
        )
        workflow.add_conditional_edges(
            "health_wellness_agent",
            self._should_continue_chain,
            {"continue": "router", "end": END}
        )
        workflow.add_conditional_edges(
            "family_dynamics_agent",
            self._should_continue_chain,
            {"continue": "router", "end": END}
        )
        workflow.add_conditional_edges(
            "character_values_agent",
            self._should_continue_chain,
            {"continue": "router", "end": END}
        )
        workflow.add_conditional_edges(
            "education_readiness_agent",
            self._should_continue_chain,
            {"continue": "router", "end": END}
        )
        workflow.add_conditional_edges(
            "social_philosophy_agent",
            self._should_continue_chain,
            {"continue": "router", "end": END}
        )
        workflow.add_conditional_edges(
            "hygiene_lifestyle_agent",
            self._should_continue_chain,
            {"continue": "router", "end": END}
        )
        workflow.add_conditional_edges(
            "life_philosophy_agent",
            self._should_continue_chain,
            {"continue": "router", "end": END}
        )
        workflow.add_conditional_edges(
            "religious_values_agent",
            self._should_continue_chain,
            {"continue": "router", "end": END}
        )
        workflow.add_conditional_edges(
            "political_alignment_agent",
            self._should_continue_chain,
            {"continue": "router", "end": END}
        )
        
        return workflow.compile()
    
    def _intelligent_route(self, state: AgentState) -> AgentState:
        """
        Intelligently route requests using LLM to analyze user messages.
        """
        # Initialize agent chain tracking if not present
        if "agent_chain" not in state:
            state["agent_chain"] = []
        if "next_agents" not in state:
            state["next_agents"] = []
        if "should_continue" not in state:
            state["should_continue"] = False
        
        # If we have a manually set current_agent, use it (backward compatibility)
        if state.get("current_agent") and not state.get("next_agents"):
            # Check if this agent was already executed
            if state["current_agent"] not in state["agent_chain"]:
                state["next_agents"] = [state["current_agent"]]
            else:
                state["next_agents"] = []
                state["should_continue"] = False
                return state
        
        # If we already have a queue of agents, use it
        if state.get("next_agents") and len(state["next_agents"]) > 0:
            return state
        
        # Intelligent routing: analyze user messages to determine which agent(s) to use
        messages = state.get("messages", [])
        
        # Get the latest user message
        user_message = None
        from langchain_core.messages import HumanMessage
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                user_message = msg.content
                break
        
        # If no user message, check if current_agent is set
        if not user_message:
            if state.get("current_agent"):
                state["next_agents"] = [state["current_agent"]]
                return state
            else:
                # Default to behaviour_psychology
                state["next_agents"] = ["behaviour_psychology"]
                return state
        
        # Use LLM to intelligently route
        routing_prompt = f"""Analyze the user's request and determine which agent(s) should handle it.

User Request: {user_message}

Conversation History (last 3 messages):
{self._format_recent_messages(messages[-3:])}

Agents Already Executed: {', '.join(state.get("agent_chain", []))}

Determine which agent(s) should handle this request. Consider:
1. The specific domain(s) mentioned in the request
2. Whether multiple agents need to work together
3. Whether agents have already been executed (avoid duplication unless explicitly requested)

Respond with ONLY a JSON object in this format:
{{"agents": ["agent_name_1", "agent_name_2"], "reasoning": "brief explanation"}}
"""
        
        try:
            router_messages = [
                SystemMessage(content=ROUTER_SYSTEM_PROMPT),
                HumanMessage(content=routing_prompt)
            ]
            
            response = self.router_llm.invoke(router_messages)
            response_text = response.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            routing_result = json.loads(response_text)
            selected_agents = routing_result.get("agents", [])
            
            # Filter out already executed agents unless explicitly requested again
            # (In a real scenario, you might want to allow re-execution)
            available_agents = [a for a in selected_agents if a not in state.get("agent_chain", [])]
            
            if not available_agents and selected_agents:
                # All selected agents already executed, use the first one anyway
                available_agents = [selected_agents[0]]
            
            if not available_agents:
                # Fallback to default
                available_agents = ["behaviour_psychology"]
            
            state["next_agents"] = available_agents
            state["should_continue"] = len(available_agents) > 0
            
        except Exception as e:
            # Fallback to default routing
            print(f"Warning: Intelligent routing failed: {e}. Using default routing.")
            if state.get("current_agent"):
                state["next_agents"] = [state["current_agent"]]
            else:
                state["next_agents"] = ["behaviour_psychology"]
            state["should_continue"] = True
        
        return state
    
    def _format_recent_messages(self, messages) -> str:
        """Format recent messages for context."""
        formatted = []
        for msg in messages:
            if hasattr(msg, 'content'):
                msg_type = "User" if not hasattr(msg, 'role') or hasattr(msg, 'content') else "Agent"
                formatted.append(f"{msg_type}: {msg.content}")
        return "\n".join(formatted) if formatted else "No previous messages"
    
    def _get_next_agent(self, state: AgentState) -> Literal["behaviour_psychology", "career_profession", "medical_lifestyle", "health_wellness", "family_dynamics", "character_values", "education_readiness", "social_philosophy", "hygiene_lifestyle", "life_philosophy", "religious_values", "political_alignment", "end"]:
        """
        Get the next agent to execute from the queue.
        """
        next_agents = state.get("next_agents", [])
        
        if not next_agents:
            return "end"
        
        # Get the first agent from queue
        next_agent = next_agents[0]
        
        # Set as current agent
        state["current_agent"] = next_agent
        
        # Add to chain
        if "agent_chain" not in state:
            state["agent_chain"] = []
        if next_agent not in state["agent_chain"]:
            state["agent_chain"].append(next_agent)
        
        return next_agent
    
    def _should_continue_chain(self, state: AgentState) -> Literal["continue", "end"]:
        """
        Determine if we should continue to the next agent in the chain or end.
        """
        next_agents = state.get("next_agents", [])
        agent_chain = state.get("agent_chain", [])
        
        # Remove the agent we just executed from the queue
        if next_agents and len(next_agents) > 0:
            next_agents.pop(0)
            state["next_agents"] = next_agents
        
        # If there are more agents in the queue, continue
        if next_agents and len(next_agents) > 0:
            state["should_continue"] = True
            return "continue"
        
        # Otherwise, end
        state["should_continue"] = False
        return "end"
    
    def _run_behaviour_psychology_agent(self, state: AgentState) -> AgentState:
        """Invokes the Behaviour-Psychology Agent."""
        result = self.behaviour_psychology_agent.graph.invoke(state)
        return result
    
    def _run_career_profession_agent(self, state: AgentState) -> AgentState:
        """Invokes the Career-Profession Agent."""
        result = self.career_profession_agent.graph.invoke(state)
        return result
    
    def _run_medical_lifestyle_agent(self, state: AgentState) -> AgentState:
        """Invokes the Medical Lifestyle Agent."""
        result = self.medical_lifestyle_agent.graph.invoke(state)
        return result
    
    def _run_health_wellness_agent(self, state: AgentState) -> AgentState:
        """Invokes the Health Wellness Agent."""
        result = self.health_wellness_agent.graph.invoke(state)
        return result
    
    def _run_family_dynamics_agent(self, state: AgentState) -> AgentState:
        """Invokes the Family Dynamics Agent."""
        result = self.family_dynamics_agent.graph.invoke(state)
        return result
    
    def _run_character_values_agent(self, state: AgentState) -> AgentState:
        """Invokes the Character–Values Agent."""
        result = self.character_values_agent.graph.invoke(state)
        return result
    
    def _run_education_readiness_agent(self, state: AgentState) -> AgentState:
        """Invokes the Education Readiness Agent."""
        result = self.education_readiness_agent.graph.invoke(state)
        return result
    
    def _run_social_philosophy_agent(self, state: AgentState) -> AgentState:
        """Invokes the Social Philosophy Agent."""
        result = self.social_philosophy_agent.graph.invoke(state)
        return result
    
    def _run_hygiene_lifestyle_agent(self, state: AgentState) -> AgentState:
        """Invokes the Hygiene–Lifestyle Agent."""
        result = self.hygiene_lifestyle_agent.graph.invoke(state)
        return result
    
    def _run_life_philosophy_agent(self, state: AgentState) -> AgentState:
        """Invokes the Life Philosophy Agent."""
        result = self.life_philosophy_agent.graph.invoke(state)
        return result
    
    def _run_religious_values_agent(self, state: AgentState) -> AgentState:
        """Invokes the Religious Values Agent."""
        result = self.religious_values_agent.graph.invoke(state)
        return result
    
    def _run_political_alignment_agent(self, state: AgentState) -> AgentState:
        """Invokes the Political Alignment Agent."""
        result = self.political_alignment_agent.graph.invoke(state)
        return result
