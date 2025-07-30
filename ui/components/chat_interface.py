import streamlit as st
from agents.cv_agent import CVAgent
from utils.session_manager import get_session_manager

def chat_interface(agent: CVAgent):
    """Render the chat interface for user interaction."""
    session_manager = get_session_manager()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input box for user message
    user_input = st.chat_input("Enter your response:")
    if user_input:
        # Process input through CVAgent
        response = agent.process_input(st.session_state.session_id, user_input)
        
        # Update session state
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Sync CV data after processing
        session_manager.get_cv_data()
        
        # Rerun to update the UI
        st.rerun()