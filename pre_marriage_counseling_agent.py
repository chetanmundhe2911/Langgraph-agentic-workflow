"""
Pre-Marriage Counseling Agent using LangGraph
Generates questions based on knowledge base and maintains conversation state
"""
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from agent_state import AgentState
from knowledge_base import CandidateKnowledgeBase


class PreMarriageCounselingAgent:
    """AI Agent for pre-marriage counseling using LangGraph"""
    
    def __init__(self, openai_api_key: str = None, model_name: str = "gpt-4"):
        """
        Initialize the counseling agent
        
        Args:
            openai_api_key: OpenAI API key (can also be set via environment variable)
            model_name: Name of the LLM model to use
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            api_key=openai_api_key
        )
        self.graph = self._build_graph()
        self.knowledge_base: CandidateKnowledgeBase = None
        self.state_store: dict[str, AgentState] = {}  # Store state per candidate
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_context", self._analyze_context_node)
        workflow.add_node("generate_question", self._generate_question_node)
        workflow.add_node("process_response", self._process_response_node)
        workflow.add_node("generate_insights", self._generate_insights_node)
        
        # Set entry point
        workflow.set_entry_point("analyze_context")
        
        # Add edges
        workflow.add_edge("analyze_context", "generate_question")
        workflow.add_conditional_edges(
            "generate_question",
            self._should_continue_conversation,
            {
                "continue": "process_response",
                "generate_insights": "generate_insights",
                "end": END,
                "wait": END  # Wait for user input
            }
        )
        workflow.add_conditional_edges(
            "process_response",
            self._should_continue_conversation,
            {
                "continue": "generate_question",
                "generate_insights": "generate_insights",
                "end": END
            }
        )
        workflow.add_edge("generate_insights", END)
        
        return workflow.compile()
    
    def _analyze_context_node(self, state: AgentState) -> AgentState:
        """Analyze current conversation context and determine focus area"""
        messages = state.get("messages", [])
        
        if not messages or len(messages) == 0:
            state["conversation_stage"] = "initial"
            state["current_focus_area"] = "introduction"
        else:
            # Analyze conversation to determine next focus
            analysis_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are analyzing a pre-marriage counseling conversation. 
                Based on the conversation history, determine:
                1. The current stage: "initial", "exploring", "deep_dive", or "recommendations"
                2. The focus area: "introduction", "values", "compatibility", "communication", 
                   "family_expectations", "lifestyle", "future_goals", or "recommendations"
                
                Respond with JSON: {{"stage": "...", "focus_area": "..."}}"""),
                MessagesPlaceholder(variable_name="messages")
            ])
            
            chain = analysis_prompt | self.llm
            try:
                response = chain.invoke({"messages": messages})
                # Parse response (simplified - in production, use proper JSON parsing)
                # For now, we'll use a simple heuristic
                if len(messages) < 2:
                    state["conversation_stage"] = "initial"
                    state["current_focus_area"] = "introduction"
                elif len(messages) < 6:
                    state["conversation_stage"] = "exploring"
                    state["current_focus_area"] = "values"
                elif len(messages) < 10:
                    state["conversation_stage"] = "deep_dive"
                    state["current_focus_area"] = "compatibility"
                else:
                    state["conversation_stage"] = "recommendations"
                    state["current_focus_area"] = "recommendations"
            except Exception as e:
                # Fallback logic
                state["conversation_stage"] = "exploring"
                state["current_focus_area"] = "values"
        
        return state
    
    def _generate_question_node(self, state: AgentState) -> AgentState:
        """Generate personalized questions based on knowledge base and conversation context"""
        if not self.knowledge_base:
            # Return a default question if knowledge base not set
            question = "Tell me about yourself and what you're looking for in a life partner."
            state["messages"].append(AIMessage(content=question))
            state["questions_asked"].append(question)
            return state
        
        kb_summary = self.knowledge_base.get_summary()
        conversation_stage = state.get("conversation_stage", "initial")
        focus_area = state.get("current_focus_area", "introduction")
        questions_asked = state.get("questions_asked", [])
        messages_history = state.get("messages", [])
        
        # Create prompt for question generation
        question_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional pre-marriage counselor AI agent. Your role is to help candidates 
            identify the right life partner for themselves through thoughtful, personalized questions.

            CANDIDATE INFORMATION:
            {knowledge_base}

            CONVERSATION CONTEXT:
            - Current Stage: {stage}
            - Focus Area: {focus}
            - Questions Already Asked: {questions_asked}

            Generate ONE thoughtful, personalized question that:
            1. Is relevant to the current focus area: {focus}
            2. Takes into account the candidate's background, personality, and data
            3. Hasn't been asked before
            4. Helps identify compatibility factors for finding the right partner
            5. Is conversational and empathetic, not clinical

            Focus areas can be:
            - introduction: Initial getting to know questions
            - values: Core values, beliefs, principles
            - compatibility: Interests, lifestyle, personality matching
            - communication: Communication style, conflict resolution
            - family_expectations: Family dynamics, expectations from in-laws
            - lifestyle: Daily routines, preferences, habits
            - future_goals: Career, family planning, life vision
            - recommendations: Providing insights and partner suggestions

            Generate only the question, no additional text."""),
        ])
        
        chain = question_prompt | self.llm
        
        try:
            response = chain.invoke({
                "knowledge_base": kb_summary,
                "stage": conversation_stage,
                "focus": focus_area,
                "questions_asked": "\n".join(questions_asked[-5:]) if questions_asked else "None"
            })
            
            question = response.content.strip()
            
            # Store question in state
            state["messages"].append(AIMessage(content=question))
            state["questions_asked"].append(question)
            
        except Exception as e:
            # Fallback question
            question = "What values are most important to you in a life partner?"
            state["messages"].append(AIMessage(content=question))
            state["questions_asked"].append(question)
        
        return state
    
    def _process_response_node(self, state: AgentState) -> AgentState:
        """Process user's response to the question"""
        messages = state.get("messages", [])
        
        if messages and isinstance(messages[-1], HumanMessage):
            user_response = messages[-1].content
            state["user_responses"].append({
                "question": state["questions_asked"][-1] if state["questions_asked"] else "",
                "response": user_response,
                "focus_area": state.get("current_focus_area", "")
            })
        
        return state
    
    def _generate_insights_node(self, state: AgentState) -> AgentState:
        """Generate final insights and recommendations"""
        kb_summary = self.knowledge_base.get_summary() if self.knowledge_base else "No knowledge base available"
        user_responses = state.get("user_responses", [])
        questions_asked = state.get("questions_asked", [])
        
        insights_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional pre-marriage counselor. Based on the candidate's complete profile 
            and conversation, generate comprehensive insights and recommendations for finding the right life partner.

            CANDIDATE PROFILE:
            {knowledge_base}

            CONVERSATION SUMMARY:
            Questions Asked: {questions}
            User Responses: {responses}

            Generate:
            1. Key insights about the candidate's personality, values, and needs
            2. Important compatibility factors to look for in a partner
            3. Potential challenges or areas to be aware of
            4. Recommendations for the type of partner that would be most suitable
            5. Next steps or action items

            Be specific, empathetic, and actionable."""),
        ])
        
        chain = insights_prompt | self.llm
        
        try:
            response = chain.invoke({
                "knowledge_base": kb_summary,
                "questions": "\n".join([f"- {q}" for q in questions_asked]),
                "responses": "\n".join([f"Q: {r['question']}\nA: {r['response']}" for r in user_responses])
            })
            
            insights = response.content
            state["insights_generated"].append(insights)
            state["messages"].append(AIMessage(content=f"\n{'='*50}\nCOUNSELING INSIGHTS & RECOMMENDATIONS\n{'='*50}\n\n{insights}"))
            
        except Exception as e:
            state["insights_generated"].append(f"Error generating insights: {str(e)}")
        
        return state
    
    def _should_continue_conversation(self, state: AgentState) -> Literal["continue", "generate_insights", "end", "wait"]:
        """Decide whether to continue conversation, generate insights, wait, or end"""
        conversation_stage = state.get("conversation_stage", "initial")
        questions_asked = state.get("questions_asked", [])
        messages = state.get("messages", [])
        
        # Check if the last message is from AI (question) - means we're waiting for user response
        if messages and isinstance(messages[-1], AIMessage):
            return "end"  # End here and wait for user input in next chat() call
        
        # Decision logic when we have a user response
        if conversation_stage == "recommendations":
            return "generate_insights"
        elif len(questions_asked) >= 12:  # After 12 questions, provide insights
            return "generate_insights"
        elif len(questions_asked) >= 15:  # Maximum limit
            return "end"
        else:
            return "continue"
    
    def set_knowledge_base(self, knowledge_base: CandidateKnowledgeBase):
        """Set the knowledge base for the candidate"""
        self.knowledge_base = knowledge_base
    
    def chat(self, user_input: str, candidate_id: str = "default") -> str:
        """
        Main chat interface for interacting with the agent
        
        Args:
            user_input: User's message/response
            candidate_id: Unique identifier for the candidate
            
        Returns:
            Agent's response
        """
        # Get or initialize state for this candidate
        if candidate_id not in self.state_store:
            # Initialize new state
            current_state: AgentState = {
                "messages": [],
                "candidate_id": candidate_id,
                "knowledge_base_summary": self.knowledge_base.get_summary() if self.knowledge_base else "",
                "current_focus_area": "introduction",
                "questions_asked": [],
                "insights_generated": [],
                "conversation_stage": "initial",
                "user_responses": []
            }
        else:
            # Get existing state (create a copy to avoid mutation issues)
            existing_state = self.state_store[candidate_id]
            current_state: AgentState = {
                "messages": existing_state["messages"][:],  # Copy list
                "candidate_id": existing_state["candidate_id"],
                "knowledge_base_summary": existing_state["knowledge_base_summary"],
                "current_focus_area": existing_state["current_focus_area"],
                "questions_asked": existing_state["questions_asked"][:],  # Copy list
                "insights_generated": existing_state["insights_generated"][:],  # Copy list
                "conversation_stage": existing_state["conversation_stage"],
                "user_responses": existing_state["user_responses"][:]  # Copy list
            }
        
        # Add user input if provided
        if user_input:
            current_state["messages"].append(HumanMessage(content=user_input))
        
        # Run the graph
        final_state = self.graph.invoke(current_state)
        
        # Store updated state
        self.state_store[candidate_id] = final_state
        
        # Get the last AI message
        messages = final_state.get("messages", [])
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, AIMessage):
                return last_message.content
        
        return "I'm here to help you with pre-marriage counseling. How can I assist you today?"
    
    def get_conversation_history(self, candidate_id: str = "default") -> list:
        """Get the conversation history for a candidate"""
        if candidate_id in self.state_store:
            return self.state_store[candidate_id].get("messages", [])
        return []
    
    def get_full_state(self, candidate_id: str = "default") -> AgentState:
        """Get the complete state for a candidate"""
        return self.state_store.get(candidate_id)
    
    def reset_conversation(self, candidate_id: str = "default"):
        """Reset conversation state for a candidate"""
        if candidate_id in self.state_store:
            del self.state_store[candidate_id]

