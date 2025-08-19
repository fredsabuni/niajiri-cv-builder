import streamlit as st
from agents.cv_agent import CVAgent
from utils.session_manager import get_session_manager

def chat_interface(agent: CVAgent):
    """Render a sticky-bottom chat input optimized for mobile; message rendering is handled by the page."""
    session_manager = get_session_manager()

    # Minimal CSS to make the chat input sticky, flush to bottom, and mobile-friendly
    st.markdown(
        """
        <style>
            /* Sticky, full-width chat input with no bottom margin */
            [data-testid="stChatInput"] {
                position: fixed !important;
                bottom: 0;
                left: 0;
                right: 0;
                margin: 0 !important;
                padding: 12px 16px !important;
                background: #2d2d2d; /* match app footer */
                border-top: 1px solid #404040;
                z-index: 1002;
            }
            /* Center input content and keep a comfortable max width */
            [data-testid="stChatInput"] > div {
                max-width: 800px;
                margin: 0 auto;
            }
            /* Mobile tweaks */
            @media (max-width: 768px) {
                [data-testid="stChatInput"] { padding: 8px 12px !important; }
                [data-testid="stChatInput"] > div { max-width: 100%; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Input box only (messages are displayed by the caller)
    user_input = st.chat_input("💬 Type your message here...", key="mobile_chat_input")

    if user_input:
        # Show a lightweight typing indicator
        with st.chat_message("assistant"):
            typing_placeholder = st.empty()
            typing_placeholder.markdown("🤔 Thinking…")

        try:
            response = agent.process_input(st.session_state.session_id, user_input)

            # Update session state
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Sync CV data after processing
            session_manager.get_cv_data()

            typing_placeholder.empty()
            st.rerun()
        except Exception as e:
            typing_placeholder.empty()
            st.error(f"Sorry, I encountered an error: {str(e)}")
            st.error("Please try again or rephrase your message.")