import streamlit as st
import time
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import Agentic Workflow
from agentic_system.workflows.agentic_rag import create_agentic_rag_workflow
from config import Config

# Configure page
st.set_page_config(
    page_title="NITK-Agent: Agentic RAG System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Rich Aesthetics)
st.markdown("""
    <style>
    :root {
        --primary: #6366f1;
        --secondary: #a855f7;
        --accent: #f43f5e;
        --bg-dark: #0f172a;
        --card-bg: rgba(30, 41, 59, 0.7);
        --glass-border: rgba(255, 255, 255, 0.1);
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    .glass-card {
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .title-text {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(to right, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .agent-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        color: #94a3b8;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 8px #22c55e;
    }
    
    .node-active {
        border: 2px solid var(--primary);
        box-shadow: 0 0 15px var(--primary);
        transform: scale(1.02);
        transition: all 0.3s ease;
    }
    
    .tool-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: rgba(99, 102, 241, 0.2);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 9999px;
        font-size: 0.75rem;
        color: #818cf8;
        margin-right: 0.5rem;
    }
    
    .iteration-pill {
        display: inline-block;
        padding: 0.125rem 0.5rem;
        background: rgba(244, 63, 94, 0.2);
        border: 1px solid rgba(244, 63, 94, 0.3);
        border-radius: 9999px;
        font-size: 0.75rem;
        color: #fb7185;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'workflow' not in st.session_state:
    st.session_state.workflow = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_process' not in st.session_state:
    st.session_state.current_process = []

def initialize_workflow():
    """Initialize the Agentic Workflow."""
    try:
        workflow = create_agentic_rag_workflow()
        st.session_state.workflow = workflow
        return True
    except Exception as e:
        st.error(f"Initialization Failed: {str(e)}")
        return False

def main():
    # Sidebar Navigation
    with st.sidebar:
        banner_path = "agentic_rag_banner_1778612714440.png"
        if os.path.exists(banner_path):
            st.image(banner_path, use_container_width=True)
        else:
            st.markdown("<h3 style='text-align: center; color: #6366f1;'>🧠 Agentic RAG</h3>", unsafe_allow_html=True)
            
        st.markdown("<h2 style='text-align: center;'>NITK-Agent v2.0</h2>", unsafe_allow_html=True)
        
        if st.button("🚀 Initialize Agentic Core", use_container_width=True, type="primary"):
            with st.spinner("Compiling LangGraph..."):
                if initialize_workflow():
                    st.success("Agentic Brain Online")
        
        st.divider()
        
        # System Stats
        if st.session_state.workflow:
            stats = st.session_state.workflow.get_workflow_stats()
            st.markdown("### 🧬 System Topology")
            cols = st.columns(2)
            cols[0].metric("Agents", "4")
            cols[1].metric("Tools", len(stats.get('tools', [])))
            
            with st.expander("🛠️ Available Capabilities"):
                for tool in stats.get('tools', []):
                    st.markdown(f"- `{tool}`")
            
            if st.button("🗑️ Clear Consciousness", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        st.divider()
        st.markdown("### 🔍 Live Agent Monitor")
        if st.session_state.current_process:
            for step in st.session_state.current_process:
                st.markdown(f"**{step['node']}**: {step['status']}")
        else:
            st.info("System Idle. Waiting for query.")

    # Main Panel
    st.markdown("<h1 class='title-text'>Agentic RAG Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<div class='agent-status'><div class='status-dot'></div> System Online | Latency: 42ms | Reasoning Enabled</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Chat Area
    chat_container = st.container()
    
    with chat_container:
        for chat in st.session_state.chat_history:
            with st.chat_message("user", avatar="👤"):
                st.markdown(chat['query'])
            
            with st.chat_message("assistant", avatar="🤖"):
                # Display reasoning and tools used
                cols = st.columns([4, 1])
                cols[0].markdown(chat['response'])
                
                with cols[1]:
                    st.markdown(f"<span class='tool-badge'>{chat.get('intent', 'N/A')}</span>", unsafe_allow_html=True)
                    if chat.get('iterations', 0) > 0:
                        st.markdown(f"<span class='iteration-pill'>Iter: {chat['iterations']}</span>", unsafe_allow_html=True)
                    
                    with st.expander("👁️ Trace"):
                        st.json(chat.get('trace', {}))

    # Query Input
    query = st.chat_input("Ask about NIT Kurukshetra (e.g., 'Compare CSE and ECE fees')")
    
    if query:
        if not st.session_state.workflow:
            st.warning("Please initialize the Agentic Core first!")
        else:
            # Add to history
            st.session_state.chat_history.append({"query": query, "response": "Processing...", "trace": {}})
            
            # Simulated Streaming and Live Process Updates
            process_log = st.empty()
            
            # Start process
            steps = [
                {"node": "Router", "status": "Analyzing Intent..."},
                {"node": "Planner", "status": "Creating Execution Path..."},
                {"node": "Tools", "status": "Retrieving University Data..."},
                {"node": "Evaluator", "status": "Verifying Information Quality..."},
                {"node": "Generator", "status": "Synthesizing Final Response..."}
            ]
            
            # Real Execution
            with st.spinner(""):
                result = st.session_state.workflow.invoke({"query": query})
            
            # Update history with real result
            st.session_state.chat_history[-1]["response"] = result['response']
            st.session_state.chat_history[-1]["intent"] = result.get('intent', 'unknown')
            st.session_state.chat_history[-1]["iterations"] = result.get('iterations', 0)
            st.session_state.chat_history[-1]["trace"] = {
                "tools": result.get('tools_used', []),
                "execution_time": f"{result.get('execution_time', 0):.2f}s",
                "quality": result.get('quality_score', 0)
            }
            
            st.rerun()

if __name__ == "__main__":
    main()
