"""
Centralized session management utility for the CV Building Assistant.
This ensures all components (progress tracker, chat interface, streamlit app) 
work with the same session data.
"""

import streamlit as st
import json
import os
from typing import Dict, Any, Optional
from agents.conversation_manager import ConversationManager
from pathlib import Path


class SessionManager:
    """Centralized session data management for the CV Building Assistant."""
    
    def __init__(self, sessions_dir: str = "sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self._conversation_manager = None
    
    @property
    def conversation_manager(self) -> ConversationManager:
        """Lazy initialization of conversation manager."""
        if self._conversation_manager is None:
            self._conversation_manager = ConversationManager(str(self.sessions_dir))
        return self._conversation_manager
    
    def get_session_id(self) -> str:
        """Get or create a session ID."""
        if "session_id" not in st.session_state:
            st.session_state.session_id = f"user_session_{os.urandom(8).hex()}"
        return st.session_state.session_id
    
    def load_session_data(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Load CV data from session file and sync with streamlit session state."""
        if session_id is None:
            session_id = self.get_session_id()
        
        try:
            # Load session through conversation manager to ensure consistency
            session = self.conversation_manager.load_session(session_id)
            if session:
                cv_data_dict = session.cv_data.to_dict()
                # Sync with streamlit session state
                st.session_state.cv_data = cv_data_dict
                return cv_data_dict
            else:
                # Create new session if none exists
                session = self.conversation_manager.create_session(session_id)
                cv_data_dict = session.cv_data.to_dict()
                st.session_state.cv_data = cv_data_dict
                return cv_data_dict
        except Exception as e:
            st.error(f"Error loading session data: {str(e)}")
            # Return empty dict and sync with session state
            empty_dict = {}
            st.session_state.cv_data = empty_dict
            return empty_dict
    
    def save_session_data(self, session_id: Optional[str] = None) -> None:
        """Save current session data to file."""
        if session_id is None:
            session_id = self.get_session_id()
        
        try:
            # If we have CV data in streamlit session state, sync it to conversation manager
            if hasattr(st.session_state, 'cv_data') and st.session_state.cv_data:
                self.conversation_manager.update_cv_data(st.session_state.cv_data)
            
            # Save through conversation manager
            self.conversation_manager.save_session(session_id)
        except Exception as e:
            st.error(f"Error saving session data: {str(e)}")
    
    def get_cv_data(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current CV data, ensuring it's synchronized across all components."""
        if session_id is None:
            session_id = self.get_session_id()
        
        # First, load from conversation manager (source of truth)
        cv_data = self.load_session_data(session_id)
        
        # Ensure streamlit session state is up to date
        st.session_state.cv_data = cv_data
        
        return cv_data
    
    def update_cv_data(self, cv_data: Dict[str, Any], session_id: Optional[str] = None) -> None:
        """Update CV data and sync across all components."""
        if session_id is None:
            session_id = self.get_session_id()
        
        # Update streamlit session state
        st.session_state.cv_data = cv_data
        
        # Update conversation manager
        self.conversation_manager.update_cv_data(cv_data)
        
        # Save to file
        self.save_session_data(session_id)
    
    def has_section_data(self, cv_data: Dict[str, Any], section_key: str) -> bool:
        """Check if a CV section has meaningful data."""
        data = cv_data.get(section_key)
        if data is None:
            return False
        
        if section_key == "personal_info" and isinstance(data, dict):
            return any(str(v).strip() for v in data.values())
        
        if section_key == "summary" and isinstance(data, str):
            return bool(data.strip())
        
        if section_key in ["experience", "education", "projects", "certifications", "references"]:
            if isinstance(data, list):
                return any(
                    any(str(v).strip() for v in item.values()) if isinstance(item, dict) else False 
                    for item in data
                )
        
        if section_key == "skills":
            if isinstance(data, list):
                return any(str(skill).strip() for skill in data)
            elif isinstance(data, str):
                return bool(data.strip())
        
        return False


# Global instance for use across the application
_session_manager = None

def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
