# Pre-Marriage Counseling Agent

An AI-powered pre-marriage counseling agent built with LangGraph that helps candidates identify the right life partner through personalized questions based on comprehensive data analysis.

## Features

- **Comprehensive Knowledge Base**: Stores and analyzes multiple types of data:
  - **Primary Data**: Education, bio data, profession
  - **Secondary Data**: Social media information, interests, hobbies
  - **Family Data**: Father, mother, and close relatives information
  - **Tertiary Data**: Insights from friends and colleagues
  - **Operational Data**: Psychometric reports, medical reports, body language analysis

- **LangGraph State Management**: Maintains conversation history and context throughout the counseling session

- **Personalized Question Generation**: Generates contextual questions based on the candidate's complete profile

- **Intelligent Conversation Flow**: Adapts questioning based on conversation stage and focus areas

- **Insights & Recommendations**: Provides comprehensive insights and partner compatibility recommendations

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to `.env`:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
   Or export it as an environment variable:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

## Usage

### Interactive Mode

Run the main script for an interactive counseling session:

```bash
python main.py
```

### Demo Mode

Run a demo conversation without user input:

```bash
python main.py demo
```

### Programmatic Usage

```python
from pre_marriage_counseling_agent import PreMarriageCounselingAgent
from knowledge_base import CandidateKnowledgeBase, PrimaryData, SecondaryData, ...

# Initialize agent
agent = PreMarriageCounselingAgent(openai_api_key="your_key", model_name="gpt-4")

# Create knowledge base
knowledge_base = CandidateKnowledgeBase(
    primary_data=PrimaryData(...),
    secondary_data=SecondaryData(...),
    # ... other data
)

# Set knowledge base
agent.set_knowledge_base(knowledge_base)

# Start conversation
response = agent.chat("Hello, I'm ready to start", candidate_id="user_001")
print(response)
```

## Knowledge Base Structure

### Primary Data
- Name, age, education level, qualifications
- Profession, employment status, income
- Location, bio summary

### Secondary Data
- Social media profiles
- Interests and hobbies
- Social activity patterns
- Online personality traits

### Family Data
- Family members (father, mother, relatives)
- Family values and background
- Cultural background
- Socioeconomic status

### Tertiary Data
- Friends and colleagues information
- Personality insights
- Social behavior patterns
- Relationship history

### Operational Data
- **Psychometric Report**: Personality type, Big Five scores, emotional intelligence
- **Medical Report**: Health status, conditions, fitness level
- **Body Language Analysis**: Communication confidence, eye contact, posture

## Conversation Flow

The agent uses LangGraph to manage conversation state through different stages:

1. **Initial**: Introduction and basic questions
2. **Exploring**: Deeper value and compatibility questions
3. **Deep Dive**: Detailed lifestyle and expectation questions
4. **Recommendations**: Generating insights and partner suggestions

Focus areas include:
- Introduction
- Values
- Compatibility
- Communication
- Family Expectations
- Lifestyle
- Future Goals
- Recommendations

## Project Structure

```
.
├── pre_marriage_counseling_agent.py  # Main agent with LangGraph workflow
├── agent_state.py                     # State management definitions
├── knowledge_base.py                  # Data models and knowledge base structure
├── main.py                           # Entry point and example usage
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
└── README.md                         # This file
```

## Requirements

- Python 3.8+
- OpenAI API key
- See `requirements.txt` for package dependencies

## State Management

The agent uses LangGraph's state management to store:
- Conversation messages (history)
- Candidate ID
- Knowledge base summary
- Current focus area
- Questions asked
- Generated insights
- Conversation stage
- User responses with context

All conversation information is persisted in the LangGraph state throughout the session.

## Customization

You can customize the agent by:
1. Modifying the knowledge base structure in `knowledge_base.py`
2. Adjusting conversation flow logic in `pre_marriage_counseling_agent.py`
3. Changing question generation prompts to suit your needs
4. Adding new nodes or edges to the LangGraph workflow

## Notes

- The agent uses GPT-4 by default (configurable)
- Maximum conversation length is 15 questions before generating insights
- All conversation data is stored in the LangGraph state
- The agent generates personalized questions based on the complete knowledge base

## License

This project is provided as-is for educational and development purposes.

