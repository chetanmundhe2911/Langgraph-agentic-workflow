# Quick Start Guide

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set OpenAI API Key**
   
   Create a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
   
   Or set it as an environment variable:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

## Creating a Knowledge Base

### Option 1: Interactive Creation
```bash
python create_knowledge_base.py
```
This will guide you through creating a knowledge base interactively.

### Option 2: Programmatic Creation
See `main.py` for an example of how to create a knowledge base programmatically.

### Option 3: Load from JSON
```python
from create_knowledge_base import load_knowledge_base

kb = load_knowledge_base("knowledge_base.json")
```

## Running the Agent

### Interactive Mode
```bash
python main.py
```

The agent will:
1. Load the knowledge base
2. Start asking personalized questions based on the candidate's profile
3. Maintain conversation state throughout the session
4. Generate insights and recommendations after sufficient questions

### Demo Mode
```bash
python main.py demo
```

Runs a pre-configured demo conversation.

## Programmatic Usage

```python
from pre_marriage_counseling_agent import PreMarriageCounselingAgent
from knowledge_base import CandidateKnowledgeBase

# Initialize agent
agent = PreMarriageCounselingAgent(openai_api_key="your_key")

# Load knowledge base
kb = create_sample_knowledge_base()  # Or load from file
agent.set_knowledge_base(kb)

# Start conversation
response = agent.chat("", candidate_id="user_001")  # Empty string to start
print(response)

# Continue conversation
response = agent.chat("I value honesty and communication", candidate_id="user_001")
print(response)

# Get conversation history
history = agent.get_conversation_history(candidate_id="user_001")

# Get full state
state = agent.get_full_state(candidate_id="user_001")
```

## Knowledge Base Structure

The knowledge base includes:

- **Primary Data**: Education, profession, bio
- **Secondary Data**: Social media, interests, hobbies
- **Family Data**: Family members, values, background
- **Tertiary Data**: Friends/colleagues insights, personality traits
- **Operational Data**: 
  - Psychometric report
  - Medical report
  - Body language analysis

## Conversation Flow

1. **Initial Stage**: Introduction and basic questions
2. **Exploring Stage**: Values and compatibility questions
3. **Deep Dive Stage**: Lifestyle and expectations
4. **Recommendations**: Insights and partner suggestions

The agent automatically transitions between stages based on conversation progress.

## State Management

All conversation data is stored in LangGraph state:
- Conversation messages
- Questions asked
- User responses
- Generated insights
- Current focus area
- Conversation stage

State persists across multiple `chat()` calls for the same `candidate_id`.

## Tips

- The agent generates questions based on the knowledge base, so ensure it's comprehensive
- State is maintained per `candidate_id` - use unique IDs for different candidates
- The agent will generate insights after 12 questions or when conversation stage reaches "recommendations"
- You can reset a conversation with `agent.reset_conversation(candidate_id)`

