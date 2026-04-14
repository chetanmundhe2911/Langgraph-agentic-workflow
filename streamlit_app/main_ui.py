"""
Streamlit UI for Multi-Agent Counseling System
This is a separate UI layer for debugging and testing.
Can be deleted without affecting the core system.
"""
import os
import sys
from pathlib import Path

# Ensure stdout/stderr use UTF-8 with replacement so Unicode filenames/messages
# don't crash on Windows consoles configured with cp1252.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Get the project root directory (parent of streamlit_app)
# The file is at: E:\IKSC\streamlit_app\app.py
# We need to find E:\IKSC where the app/ directory is located

current_file = Path(__file__).resolve()  # E:\IKSC\streamlit_app\app.py
streamlit_app_dir = current_file.parent   # E:\IKSC\streamlit_app

# Start from the streamlit_app directory and go up until we find app/
# This handles cases where the path calculation might be off
project_root = None
search_path = streamlit_app_dir

# Search up to 3 levels (shouldn't need more)
for _ in range(3):
    parent = search_path.parent
    app_dir_check = parent / "app"
    if app_dir_check.exists() and app_dir_check.is_dir():
        # Found it! This is the project root
        project_root = parent.resolve()
        break
    search_path = parent

# If we still haven't found it, try current working directory
if project_root is None:
    cwd = Path(os.getcwd()).resolve()
    if (cwd / "app").exists() and (cwd / "app").is_dir():
        project_root = cwd
    else:
        # Fallback: use parent of streamlit_app (should be E:\IKSC)
        project_root = streamlit_app_dir.parent.resolve()

# Final verification
if project_root:
    project_root = project_root.resolve()

# Add project root to Python path BEFORE any imports
# This must be done before importing anything from 'app'
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# NOTE: Do NOT change working directory with os.chdir()
# This causes Streamlit to look for the script in the wrong location
# Instead, we rely on sys.path for imports and use absolute paths for file operations

# Import streamlit first (before trying to use st.error)
import streamlit as st

# Now import other dependencies
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.callbacks.openai_info import OpenAICallbackHandler

# Import from existing app structure (after path is set)
# Use absolute imports from project root
# The issue: when this file is named app.py, Python might confuse it with app/ directory
# Solution: Ensure project root is in path and verify app/ is a directory, not a file

try:
    # Verify app directory exists and is a directory (not a file)
    app_dir_path = project_root / "app"
    app_dir_path = app_dir_path.resolve()  # Resolve to absolute path
    
    # Debug: Show paths
    if not app_dir_path.exists():
        raise ImportError(f"app/ directory not found at {app_dir_path}\nProject root: {project_root}")
    
    if not app_dir_path.is_dir():
        raise ImportError(f"app/ exists but is not a directory at {app_dir_path}")
    
    # Verify app/__init__.py exists
    app_init_file = app_dir_path / "__init__.py"
    if not app_init_file.exists():
        raise ImportError(f"app/__init__.py not found at {app_init_file}")
    
    # CRITICAL: Remove any conflicting 'app' module from sys.modules
    # When this file is named app.py, Python might cache it as module 'app'
    # which conflicts with the app/ directory package
    if 'app' in sys.modules:
        app_module = sys.modules['app']
        # Check if it's the wrong module (file instead of package)
        if hasattr(app_module, '__file__') and app_module.__file__:
            module_file = Path(app_module.__file__)
            # If it's pointing to this file (app.py) instead of app/__init__.py, remove it
            if 'streamlit_app' in str(module_file) or module_file.name == 'app.py':
                del sys.modules['app']
                # Also remove any submodules that might have been cached
                modules_to_remove = [k for k in list(sys.modules.keys()) if k.startswith('app.')]
                for mod in modules_to_remove:
                    del sys.modules[mod]
    
    # Now do the imports
    from app.agents.orchestrator.orchestrator import Orchestrator
    from app.knowledge.loader import load_knowledge_base_from_reports, load_knowledge_base_from_mongodb, load_full_knowledge_base
    from app.state.state import AgentState
    
except ImportError as e:
    # Show detailed error information
    error_msg = str(e)
    st.error(f"❌ Import error: {error_msg}")
    
    # Show path information
    st.info(f"**Project root (resolved):** `{project_root.resolve()}`")
    app_dir_check = project_root / "app"
    st.info(f"**App directory (expected):** `{app_dir_check.resolve()}`")
    st.info(f"**App directory exists:** {app_dir_check.exists()}")
    if app_dir_check.exists():
        st.info(f"**App directory is_dir:** {app_dir_check.is_dir()}")
        app_init = app_dir_check / "__init__.py"
        st.info(f"**app/__init__.py exists:** {app_init.exists()}")
    
    st.info(f"**Current file:** `{Path(__file__).resolve()}`")
    st.info(f"**Working directory:** `{os.getcwd()}`")
    st.info(f"**Python path (first 5):**")
    for i, path in enumerate(sys.path[:5], 1):
        st.code(f"{i}. {Path(path).resolve() if Path(path).exists() else path}")
    
    st.info("**Troubleshooting:**")
    st.markdown(f"""
    1. **Run from project root**: `streamlit run streamlit_app/main_ui.py` (not from streamlit_app folder)
    2. **Check app directory exists**: Should be at `{project_root.resolve()}/app/`
    3. **Verify app/__init__.py exists**: Required for Python package
    4. **Verify dependencies**: `pip install -r requirements.txt`
    5. **Test import manually**: 
       ```python
       import sys
       sys.path.insert(0, r'{project_root.resolve()}')
       from app.agents.orchestrator.orchestrator import Orchestrator
       print('OK')
       ```
    """)
    st.stop()

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Counseling System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = None
if "state" not in st.session_state:
    st.session_state.state = None
if "knowledge_base_loaded" not in st.session_state:
    st.session_state.knowledge_base_loaded = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "token_usage" not in st.session_state:
    st.session_state.token_usage = {
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0,
        "requests": []  # Store per-request breakdown
    }


def initialize_system():
    """Initialize the orchestrator and knowledge base."""
    try:
        with st.spinner("Initializing Multi-Agent Counseling System..."):
            # Check API key
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                st.error("⚠️ OPENAI_API_KEY not found in environment variables.")
                st.info("Please set OPENAI_API_KEY in your .env file or environment variables.")
                return False
            
            # Get model name from session state or use default
            model_name = st.session_state.get("model_name", "gpt-4o")
            
            # Initialize Orchestrator with gpt-4o (higher token limits)
            st.session_state.orchestrator = Orchestrator(api_key=api_key, model_name=model_name)
            
            # Load knowledge base from selected source
            data_source = st.session_state.get("data_source", "local")

            if data_source == "mongodb":
                with st.spinner("Fetching reports from MongoDB and indexing into RAG store..."):
                    mongo_cfg = {
                        "mongodb_uri": st.session_state.get("mongodb_uri") or None,
                        "db_name": st.session_state.get("mongodb_db") or None,
                        "collection_name": st.session_state.get("mongodb_collection") or None,
                        "storage_mode": st.session_state.get("mongodb_storage_mode", "gridfs"),
                    }
                    user_id = st.session_state.get("user_id") or None
                    knowledge_base = load_full_knowledge_base(
                        user_id=user_id,
                        use_rag=True,
                        **mongo_cfg,
                    )
            else:
                with st.spinner("Loading reports from local Report/ folder and indexing into RAG store..."):
                    report_dir = st.session_state.get("report_dir", "Report")
                    knowledge_base = load_knowledge_base_from_reports(
                        report_dir=report_dir,
                        use_rag=True,
                    )

            kb_summary = knowledge_base.get_summary()
            
            # Initialize State
            # Note: All reports are indexed into RAG, candidate_id is just for session tracking
            candidate_id = st.session_state.get("candidate_id", "candidate_001")
            st.session_state.state: AgentState = {
                "messages": [],
                "current_agent": "",
                "agent_chain": [],
                "next_agents": [],
                "should_continue": False,
                "candidate_id": candidate_id,
                "knowledge_base_summary": kb_summary,
                "knowledge_base": knowledge_base,  # Store KB object for RAG access
                "agent_data": {},
                "questions_asked": [],
                "user_responses": [],
                "insights_generated": [],
                "conversation_stage": "initial",
                "current_focus_area": "introduction"
            }
            
            st.session_state.knowledge_base_loaded = True
            st.session_state.messages = []
            return True
            
    except Exception as e:
        st.error(f"❌ Error initializing system: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return False


def process_user_input(user_input: str):
    """Process user input through the orchestrator."""
    if not st.session_state.orchestrator or not st.session_state.state:
        st.error("System not initialized. Please click 'Initialize System' first.")
        return
    
    # Initialize error tracking in session state
    if "last_error" not in st.session_state:
        st.session_state.last_error = None
    
    try:
        # Track message count and agent chain before execution
        message_count_before = len(st.session_state.state["messages"])
        agent_chain_before = len(st.session_state.state.get("agent_chain", []))
        
        # Add user message to state
        st.session_state.state["messages"].append(HumanMessage(content=user_input))
        
        # Add user message to chat UI
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Clear any previous errors
        st.session_state.last_error = None
        
        # Initialize callback handler for token tracking
        callback_handler = OpenAICallbackHandler()
        
        # Run orchestrator with callback handler
        with st.spinner("🤖 Processing request..."):
            result = st.session_state.orchestrator.graph.invoke(
                st.session_state.state,
                config={"callbacks": [callback_handler]}
            )
            st.session_state.state = result
            
            # Store token usage for this request
            request_usage = {
                "prompt_tokens": callback_handler.prompt_tokens,
                "completion_tokens": callback_handler.completion_tokens,
                "total_tokens": callback_handler.total_tokens,
                "total_cost": callback_handler.total_cost,
                "model": st.session_state.get("model_name", "gpt-4o")
            }
            
            # Update cumulative totals
            st.session_state.token_usage["total_prompt_tokens"] += callback_handler.prompt_tokens
            st.session_state.token_usage["total_completion_tokens"] += callback_handler.completion_tokens
            st.session_state.token_usage["total_tokens"] += callback_handler.total_tokens
            st.session_state.token_usage["total_cost"] += callback_handler.total_cost
            st.session_state.token_usage["requests"].append(request_usage)
        
        # Check if we got new messages
        message_count_after = len(st.session_state.state["messages"])
        new_message_count = message_count_after - message_count_before
        
        # Debug: Log what happened
        agent_chain = st.session_state.state.get("agent_chain", [])
        if agent_chain:
            st.info(f"✅ Agent(s) executed: {', '.join([a.replace('_', ' ').title() for a in agent_chain])}")
        
        # Display new agent responses
        if new_message_count > 0:
            new_messages = st.session_state.state["messages"][message_count_before:]
            agent_chain = st.session_state.state.get("agent_chain", [])
            
            # Get only the agents that were executed in THIS request
            # agent_chain is cumulative, so we need to get only the new agents
            agents_in_this_request = agent_chain[agent_chain_before:] if agent_chain_before < len(agent_chain) else agent_chain
            
            response_added = False
            ai_message_index = 0  # Track which AIMessage we're on (not overall message index)
            
            for msg in new_messages:
                if isinstance(msg, AIMessage):
                    # Map this AIMessage to the corresponding agent that executed in this request
                    if agents_in_this_request and ai_message_index < len(agents_in_this_request):
                        # Get the agent at this position in the current request's agent chain
                        agent_name = agents_in_this_request[ai_message_index]
                        formatted_name = agent_name.replace('_', ' ').title()
                    else:
                        # Fallback: try to get the last agent from current request or use "System"
                        if agents_in_this_request:
                            agent_name = agents_in_this_request[-1]
                            formatted_name = agent_name.replace('_', ' ').title()
                        elif agent_chain:
                            # Ultimate fallback: use last agent from full chain
                            agent_name = agent_chain[-1]
                            formatted_name = agent_name.replace('_', ' ').title()
                        else:
                            formatted_name = "System"
                    
                    # Add agent response to chat UI
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": msg.content,
                        "agent": formatted_name
                    })
                    response_added = True
                    ai_message_index += 1  # Increment only for AIMessages
            
            # If no AIMessage was found, show a warning
            if not response_added:
                message_types = [type(msg).__name__ for msg in new_messages]
                st.session_state.last_error = f"No AI response generated. Found {new_message_count} new message(s) of types: {', '.join(message_types)}"
                st.warning("⚠️ No response generated. Check debug information below.")
                with st.expander("🔍 Message Details"):
                    for i, msg in enumerate(new_messages):
                        st.text(f"Message {i+1}: {type(msg).__name__}")
                        if hasattr(msg, 'content'):
                            st.text(f"Content preview: {str(msg.content)[:200]}...")
        else:
            # No new messages at all
            st.session_state.last_error = f"No new messages were added. Agent chain: {agent_chain if agent_chain else 'None'}"
            st.warning("⚠️ No response generated. The agent may not have processed the request.")
            with st.expander("🔍 State Information"):
                st.json({
                    "messages_before": message_count_before,
                    "messages_after": message_count_after,
                    "agent_chain": agent_chain,
                    "next_agents": st.session_state.state.get("next_agents", []),
                    "current_agent": st.session_state.state.get("current_agent", ""),
                })
                    
    except Exception as e:
        error_msg = f"❌ Error processing request: {str(e)}"
        st.session_state.last_error = error_msg
        st.error(error_msg)
        import traceback
        with st.expander("🔍 Full Error Details", expanded=True):
            st.code(traceback.format_exc())


def main():
    """Main Streamlit app."""
    # Title
    st.title("🤖 Multi-Agent Counseling System")
    st.markdown("**Intelligent Routing & Multi-Agent Chaining Enabled**")

    # ----------------------------------------------------------------
    # Counseling Chat
    # ----------------------------------------------------------------
    if True:
        # Sidebar
        with st.sidebar:
            st.header("⚙️ System Control")
            
            # Initialize button
            if st.button("🔄 Initialize System", type="primary", use_container_width=True):
                if initialize_system():
                    st.success("✅ System initialized successfully!")
                    st.rerun()
            
            # Reset button
            if st.button("🗑️ Reset Session", use_container_width=True):
                st.session_state.messages = []
                if st.session_state.state:
                    st.session_state.state["messages"] = []
                    st.session_state.state["agent_chain"] = []
                    st.session_state.state["next_agents"] = []
                st.rerun()
            
            st.divider()
            
            # System status
            st.subheader("📊 System Status")
            if st.session_state.knowledge_base_loaded:
                st.success("✅ System Ready")
                if st.session_state.state:
                    agent_chain = st.session_state.state.get("agent_chain", [])
                    if agent_chain:
                        st.info(f"**Agents Executed:** {len(agent_chain)}")
                        for agent in agent_chain:
                            st.text(f"  • {agent.replace('_', ' ').title()}")
            else:
                st.warning("⚠️ System Not Initialized")
            
            st.divider()
            
            # Token Usage & Cost Tracking
            st.subheader("💰 Token Usage & Cost")
            if st.session_state.knowledge_base_loaded:
                usage = st.session_state.token_usage
                
                # Current model
                current_model = st.session_state.get("model_name", "gpt-4o")
                st.caption(f"Model: **{current_model}**")
                
                # Display cumulative totals
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Input Tokens",
                        f"{usage['total_prompt_tokens']:,}",
                        help="Total prompt tokens used across all requests"
                    )
                
                with col2:
                    st.metric(
                        "Output Tokens",
                        f"{usage['total_completion_tokens']:,}",
                        help="Total completion tokens generated"
                    )
                
                with col3:
                    st.metric(
                        "Total Cost",
                        f"${usage['total_cost']:.4f}",
                        help="Total cost in USD"
                    )
                
                # Total tokens
                st.info(f"**Total Tokens:** {usage['total_tokens']:,} | **Requests:** {len(usage['requests'])}")
                
                # Show last request details
                if usage['requests']:
                    last_request = usage['requests'][-1]
                    with st.expander("📋 Last Request Details"):
                        st.json({
                            "Model": last_request['model'],
                            "Prompt Tokens": f"{last_request['prompt_tokens']:,}",
                            "Completion Tokens": f"{last_request['completion_tokens']:,}",
                            "Total Tokens": f"{last_request['total_tokens']:,}",
                            "Cost": f"${last_request['total_cost']:.4f}"
                        })
                
                # Reset button for token tracking
                if st.button("🔄 Reset Token Tracking", use_container_width=True):
                    st.session_state.token_usage = {
                        "total_prompt_tokens": 0,
                        "total_completion_tokens": 0,
                        "total_tokens": 0,
                        "total_cost": 0.0,
                        "requests": []
                    }
                    st.rerun()
            else:
                st.info("Initialize system to start tracking token usage")
            
            st.divider()
            
            # Available agents info
            st.subheader("📋 Available Agents")
            agents_info = [
                ("behaviour_psychology", "Psychological & Behavioral Analysis"),
                ("career_profession", "Career & Professional Stability"),
                ("medical_lifestyle", "Medical History & Lifestyle"),
                ("health_wellness", "Health & Wellness Assessment"),
                ("family_dynamics", "Family Structure & Dynamics"),
                ("character_values", "Character & Values Assessment"),
                ("education_readiness", "Educational Background"),
                ("social_philosophy", "Social Worldview Analysis"),
                ("hygiene_lifestyle", "Hygiene & Lifestyle Compatibility"),
                ("life_philosophy", "Life Purpose & Meaning"),
                ("religious_values", "Religious Beliefs & Practices"),
                ("political_alignment", "Political Orientation"),
            ]
            
            with st.expander("View All Agents"):
                for agent_id, description in agents_info:
                    st.text(f"• {agent_id.replace('_', ' ').title()}")
                    st.caption(f"  {description}")
            
            st.divider()
            
            # Data Source Settings
            st.subheader("🗄️ Data Source")

            if "data_source" not in st.session_state:
                st.session_state.data_source = "local"

            st.session_state.data_source = st.radio(
                "Load reports from:",
                options=["local", "mongodb"],
                format_func=lambda x: "Local Report/ folder" if x == "local" else "MongoDB",
                index=0 if st.session_state.data_source == "local" else 1,
                disabled=st.session_state.knowledge_base_loaded,
            )

            if st.session_state.data_source == "local":
                if "report_dir" not in st.session_state:
                    st.session_state.report_dir = "Report"
                st.session_state.report_dir = st.text_input(
                    "Report folder path",
                    value=st.session_state.report_dir,
                    help="Relative or absolute path to folder containing PDF reports",
                    disabled=st.session_state.knowledge_base_loaded,
                )
                st.info("PDF reports are loaded from the local folder and indexed into RAG.")
            else:
                if "mongodb_uri" not in st.session_state:
                    st.session_state.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
                if "mongodb_db" not in st.session_state:
                    st.session_state.mongodb_db = os.getenv("MONGODB_DB_NAME", "premarriage")
                if "mongodb_collection" not in st.session_state:
                    st.session_state.mongodb_collection = os.getenv("MONGODB_COLLECTION", "reports")
                if "mongodb_storage_mode" not in st.session_state:
                    st.session_state.mongodb_storage_mode = "gridfs"

                with st.expander("Configure MongoDB", expanded=not st.session_state.knowledge_base_loaded):
                    st.session_state.mongodb_uri = st.text_input(
                        "Connection URI",
                        value=st.session_state.mongodb_uri,
                        type="password",
                        help="MongoDB connection string (e.g. mongodb+srv://user:pass@cluster.mongodb.net)",
                    )
                    st.session_state.mongodb_db = st.text_input(
                        "Database Name",
                        value=st.session_state.mongodb_db,
                    )
                    st.session_state.mongodb_collection = st.text_input(
                        "Collection / Bucket Name",
                        value=st.session_state.mongodb_collection,
                        help="GridFS bucket name or collection name where PDFs are stored",
                    )
                    st.session_state.mongodb_storage_mode = st.selectbox(
                        "Storage Mode",
                        options=["gridfs", "collection"],
                        index=0 if st.session_state.mongodb_storage_mode == "gridfs" else 1,
                        help="GridFS for standard file storage; Collection for PDFs stored as binary field",
                    )
                st.info("PDF reports are fetched from MongoDB and indexed into RAG.")
            
            st.divider()
            
            # Model selection
            st.subheader("🤖 Model Selection")
            if "model_name" not in st.session_state:
                st.session_state.model_name = "gpt-4o"
            
            model_options = {
                "gpt-4o": "GPT-4 Omni (Recommended - Higher token limits)",
                "gpt-4-turbo": "GPT-4 Turbo (Higher token limits)",
                "gpt-4": "GPT-4 (Standard - Lower token limits)"
            }
            
            selected_model = st.selectbox(
                "Select Model:",
                options=list(model_options.keys()),
                format_func=lambda x: model_options[x],
                key="model_select",
                disabled=st.session_state.knowledge_base_loaded  # Disable if system already initialized
            )
            
            if selected_model != st.session_state.get("model_name", "gpt-4o"):
                st.session_state.model_name = selected_model
                if st.session_state.knowledge_base_loaded:
                    st.warning("⚠️ Model change will take effect after re-initializing the system.")
            
            st.caption(f"Current: {model_options.get(st.session_state.model_name, st.session_state.model_name)}")
            
            st.divider()
            
            # Manual agent selection (for testing)
            st.subheader("🔧 Manual Agent Selection")
            st.caption("Override intelligent routing (for testing)")
            selected_agent = st.selectbox(
                "Select Agent:",
                ["Auto (Intelligent Routing)"] + [agent_id for agent_id, _ in agents_info],
                key="manual_agent"
            )
            
            if selected_agent != "Auto (Intelligent Routing)" and st.session_state.state:
                st.session_state.state["current_agent"] = selected_agent
                st.info(f"Manual agent set to: {selected_agent}")

        # Main content area
        if not st.session_state.knowledge_base_loaded:
            st.warning("⚠️ Please initialize the system first using the sidebar.")
            st.info("Click '🔄 Initialize System' in the sidebar to begin.")
            
            # Show instructions
            with st.expander("📖 How to Use"):
                st.markdown("""
                ### Getting Started
                
                1. **Initialize System**: Click the "🔄 Initialize System" button in the sidebar
                2. **Ask Questions**: Type your questions in the chat input below
                3. **Intelligent Routing**: The system will automatically route to appropriate agent(s)
                4. **Multi-Agent Chaining**: Multiple agents can work together for complex requests
                
                ### Example Queries
                
                - "Tell me about their personality and behavior"
                - "Analyze their career and health"
                - "Give me a comprehensive analysis"
                - "What are their values and religious beliefs?"
                
                ### Features
                
                - 🤖 **Intelligent Routing**: Automatically selects relevant agents
                - 🔗 **Multi-Agent Chaining**: Chains multiple agents when needed
                - 📊 **System Status**: View which agents have been executed
                - 🔧 **Manual Override**: Test specific agents manually
                """)
            return

        # Chat interface
        st.subheader("💬 Chat Interface")
        
        # Show persistent error if any
        if st.session_state.get("last_error"):
            st.error(st.session_state.last_error)
            with st.expander("🔍 Debug Information"):
                if st.session_state.state:
                    st.json({
                        "total_messages": len(st.session_state.state.get("messages", [])),
                        "agent_chain": st.session_state.state.get("agent_chain", []),
                        "next_agents": st.session_state.state.get("next_agents", []),
                        "current_agent": st.session_state.state.get("current_agent", ""),
                    })
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant" and "agent" in message:
                    st.caption(f"🤖 Generated by: {message['agent']}")
        
        # User input
        user_input = st.chat_input("Ask a question about the candidate...")
        
        if user_input:
            process_user_input(user_input)
            st.rerun()
        
        # Debug information (collapsible)
        with st.expander("🔍 Debug Information"):
            if st.session_state.state:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.json({
                        "current_agent": st.session_state.state.get("current_agent", ""),
                        "agent_chain": st.session_state.state.get("agent_chain", []),
                        "next_agents": st.session_state.state.get("next_agents", []),
                        "should_continue": st.session_state.state.get("should_continue", False),
                        "candidate_id": st.session_state.state.get("candidate_id", ""),
                    })
                
                with col2:
                    st.json({
                        "total_messages": len(st.session_state.state.get("messages", [])),
                        "agent_data_keys": list(st.session_state.state.get("agent_data", {}).keys()),
                    })
                
                # Show agent data
                if st.session_state.state.get("agent_data"):
                    st.subheader("Agent Data")
                    for agent_name, agent_data in st.session_state.state["agent_data"].items():
                        with st.expander(f"Agent: {agent_name}"):
                            st.json(agent_data)


if __name__ == "__main__":
    main()
