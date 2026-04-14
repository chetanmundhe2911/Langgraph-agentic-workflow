# Architecture Overview

## System Architecture

The Pre-Marriage Counseling Agent is built using a **LangGraph-based state machine architecture** that orchestrates an AI conversation flow. The system follows a modular design with clear separation of concerns.

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                            │
│                  (main.py, CLI)                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              PreMarriageCounselingAgent                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            LangGraph Workflow                        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │   │
│  │  │ Analyze  │─▶│ Generate │─▶│ Process  │         │   │
│  │  │ Context  │  │ Question │  │ Response │         │   │
│  │  └──────────┘  └──────────┘  └──────────┘         │   │
│  │       │              │              │              │   │
│  │       └──────────────┴──────────────┘              │   │
│  │                    │                                │   │
│  │                    ▼                                │   │
│  │            ┌──────────────┐                        │   │
│  │            │  Generate    │                        │   │
│  │            │  Insights    │                        │   │
│  │            └──────────────┘                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            State Store (Per Candidate)               │   │
│  │  {candidate_id: AgentState}                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Knowledge Base Reference                  │   │
│  │  (CandidateKnowledgeBase)                            │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Knowledge Base                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Primary    │  │  Secondary   │  │   Family     │     │
│  │    Data      │  │    Data      │  │    Data      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │  Tertiary    │  │ Operational  │                       │
│  │    Data      │  │    Data      │                       │
│  └──────────────┘  └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. **Knowledge Base Layer** (`knowledge_base.py`)

This is the **data foundation** of the system. It stores all information about the candidate in a structured format.

#### Data Categories:

- **Primary Data** (`PrimaryData`): 
  - Education, qualifications, profession
  - Employment status, income, location
  - Basic biographical information

- **Secondary Data** (`SecondaryData`):
  - Social media profiles and activity
  - Interests, hobbies
  - Online personality traits

- **Family Data** (`FamilyData`):
  - Family members (father, mother, relatives)
  - Family values and background
  - Cultural and socioeconomic information

- **Tertiary Data** (`TertiaryData`):
  - Information from friends and colleagues
  - Personality insights from external sources
  - Social behavior patterns
  - Relationship history

- **Operational Data** (`OperationalData`):
  - **Psychometric Report**: Personality assessments, Big Five scores, emotional intelligence
  - **Medical Report**: Health status, conditions, fitness level
  - **Body Language Analysis**: Communication patterns, posture, gestures

**Key Feature**: The `CandidateKnowledgeBase` class aggregates all data types and provides a `get_summary()` method that generates a comprehensive text summary for use by the LLM.

---

### 2. **State Management Layer** (`agent_state.py`)

Defines the **LangGraph state structure** that maintains conversation context throughout the session.

#### State Fields:

```python
AgentState:
  - messages: List[dict]              # Full conversation history
  - candidate_id: str                 # Unique identifier
  - knowledge_base_summary: str       # Cached KB summary
  - current_focus_area: str           # Current topic (values, compatibility, etc.)
  - questions_asked: List[str]        # Track all questions
  - insights_generated: List[str]     # Generated recommendations
  - conversation_stage: str           # Stage: initial/exploring/deep_dive/recommendations
  - user_responses: List[dict]        # Structured Q&A pairs
```

**Key Feature**: Uses `Annotated[List[...], add]` for automatic list merging when state is updated, ensuring conversation history accumulates correctly.

---

### 3. **Agent Layer** (`pre_marriage_counseling_agent.py`)

The **core orchestration engine** using LangGraph to manage conversation flow.

#### Architecture Components:

##### A. **LangGraph Workflow**

The workflow consists of 4 main nodes:

1. **`analyze_context` Node**:
   - Analyzes conversation history
   - Determines current conversation stage
   - Sets focus area based on progress
   - Stages: `initial` → `exploring` → `deep_dive` → `recommendations`

2. **`generate_question` Node**:
   - Generates personalized questions using LLM
   - Considers:
     - Knowledge base summary
     - Current focus area
     - Previously asked questions
     - Conversation stage
   - Appends question to state as `AIMessage`

3. **`process_response` Node**:
   - Processes user's response
   - Extracts response from `HumanMessage`
   - Stores Q&A pair with context
   - Tracks which focus area the response relates to

4. **`generate_insights` Node**:
   - Generates final recommendations
   - Uses complete conversation history
   - Considers all knowledge base data
   - Produces partner compatibility insights

##### B. **Decision Logic** (`_should_continue_conversation`)

Controls workflow routing based on:
- **Message type**: If last message is `AIMessage`, end (wait for user)
- **Question count**: After 12 questions → generate insights
- **Conversation stage**: If "recommendations" → generate insights
- **Maximum limit**: 15 questions → end

##### C. **State Persistence**

- **Per-Candidate Storage**: `state_store: dict[str, AgentState]`
- **State Isolation**: Each candidate has independent conversation state
- **State Restoration**: On each `chat()` call, state is loaded, updated, and saved

---

## Data Flow

### Initialization Flow:

```
1. User creates/loads Knowledge Base
   ↓
2. Initialize PreMarriageCounselingAgent
   - Create LLM instance (ChatOpenAI)
   - Build LangGraph workflow
   - Initialize state_store
   ↓
3. Set Knowledge Base: agent.set_knowledge_base(kb)
   ↓
4. Ready to chat
```

### Conversation Flow (Single Turn):

```
User Input
   ↓
chat(user_input, candidate_id)
   ↓
Load/Initialize State for candidate_id
   ↓
Add HumanMessage to state.messages
   ↓
Invoke LangGraph workflow:
   │
   ├─▶ analyze_context
   │      │
   │      └─▶ Determines stage & focus area
   │
   ├─▶ generate_question
   │      │
   │      ├─▶ Uses KB summary
   │      ├─▶ Uses conversation context
   │      ├─▶ Calls LLM to generate question
   │      └─▶ Appends AIMessage to state
   │
   ├─▶ _should_continue_conversation
   │      │
   │      └─▶ Routes to:
   │             - END (if waiting for user)
   │             - process_response (if has user response)
   │             - generate_insights (if ready)
   │
   ├─▶ process_response (if applicable)
   │      │
   │      └─▶ Stores Q&A pair
   │             │
   │             └─▶ Routes back to generate_question
   │
   └─▶ generate_insights (if ready)
          │
          └─▶ Final recommendations
   ↓
Save updated state to state_store
   ↓
Return last AI message to user
```

### Multi-Turn Conversation:

```
Turn 1:
  chat("", candidate_id="user_001")
  → State initialized
  → Question generated
  → State saved

Turn 2:
  chat("I value honesty...", candidate_id="user_001")
  → State loaded from store
  → Response processed
  → New question generated
  → State saved

Turn N:
  chat("...", candidate_id="user_001")
  → State persists across all turns
  → Full conversation history maintained
```

---

## LangGraph Workflow Structure

```
                    START
                     │
                     ▼
            ┌─────────────────┐
            │ analyze_context │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │generate_question│
            └────────┬────────┘
                     │
          ┌──────────┼──────────┐
          │          │          │
          ▼          ▼          ▼
    [continue] [generate]   [end/wait]
          │      insights      │
          │          │         │
          ▼          │         │
    ┌─────────────┐  │         │
    │process_     │  │         │
    │response     │  │         │
    └──────┬──────┘  │         │
           │          │         │
           └──────────┼─────────┘
                      │
                      ▼
            ┌─────────────────┐
            │generate_insights│
            └────────┬────────┘
                     │
                     ▼
                    END
```

---

## Key Design Patterns

### 1. **State Machine Pattern**
- LangGraph implements a state machine where each node represents a state
- Transitions are controlled by conditional edges
- State is immutable between nodes (copied and updated)

### 2. **Strategy Pattern**
- Different question generation strategies based on focus area
- Adaptable conversation flow based on stage

### 3. **Repository Pattern**
- `state_store` acts as a repository for conversation states
- Encapsulates state persistence logic

### 4. **Template Method Pattern**
- Each node follows a pattern: read state → process → update state → return

---

## State Management Details

### State Persistence:

1. **In-Memory Storage**: `state_store` dictionary in agent instance
2. **Per-Candidate Isolation**: Each `candidate_id` has independent state
3. **State Copying**: Deep copying of lists to avoid mutation issues
4. **Automatic Merging**: LangGraph's `Annotated[List, add]` merges lists automatically

### State Lifecycle:

```
1. Creation: First chat() call creates new state
2. Update: Each graph invocation updates state
3. Persistence: Updated state saved to state_store
4. Retrieval: Subsequent calls load from state_store
5. Reset: reset_conversation() clears state for candidate
```

---

## Integration Points

### 1. **LLM Integration**
- Uses `ChatOpenAI` from LangChain
- Prompts are constructed with context from:
  - Knowledge base summary
  - Conversation history
  - Current focus area
  - Previous questions

### 2. **Knowledge Base Integration**
- KB is set once per agent instance
- KB summary is cached in state
- Used in question generation and insights generation

### 3. **User Interface Integration**
- `chat()` method is the main interface
- Returns string response (last AI message)
- State management is transparent to caller

---

## Extensibility Points

1. **Custom Nodes**: Add new nodes to workflow for additional functionality
2. **Knowledge Base**: Extend data models to include new information types
3. **Decision Logic**: Customize routing logic for different conversation flows
4. **State Fields**: Add new fields to `AgentState` for additional tracking
5. **LLM Models**: Swap out LLM provider/model via LangChain abstraction

---

## Error Handling

- **LLM Failures**: Fallback questions when LLM calls fail
- **State Corruption**: State initialization on errors
- **Missing Data**: Graceful handling of missing knowledge base fields
- **Edge Cases**: Handling empty conversations, missing user input, etc.

---

This architecture ensures:
- ✅ **Separation of Concerns**: Each layer has a specific responsibility
- ✅ **State Persistence**: Conversation context maintained across turns
- ✅ **Scalability**: Multiple candidates can be handled simultaneously
- ✅ **Maintainability**: Clear structure makes updates easy
- ✅ **Extensibility**: Easy to add features or modify behavior

