import json
import os
from pathlib import Path
from models.cv_data import CVData
from typing import Optional, List, Dict

class Session:
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
        self.current_section: Optional[str] = None
        self.cv_data = CVData()

class ConversationManager:
    def __init__(self, sessions_dir: str):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[Session] = None

    def create_session(self, session_id: str) -> Session:
        """Create a new session."""
        self.current_session = Session()
        return self.current_session

    def save_session(self, session_id: str) -> None:
        """Save the session to a file."""
        if not self.current_session:
            self.current_session = self.create_session(session_id)
        session_file = self.sessions_dir / f"{session_id}.json"
        try:
            with session_file.open("w") as f:
                json.dump({
                    "messages": self.current_session.messages,
                    "current_section": self.current_session.current_section,
                    "cv_data": self.current_session.cv_data.to_dict()
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving session {session_id}: {e}")
            raise

    def load_session(self, session_id: str) -> Optional[Session]:
        """Load a session from a file."""
        session_file = self.sessions_dir / f"{session_id}.json"
        try:
            if session_file.exists():
                with session_file.open("r") as f:
                    data = json.load(f)
                session = Session()
                session.messages = data.get("messages", [])
                session.current_section = data.get("current_section")
                session.cv_data = CVData.from_dict(data.get("cv_data", {}))
                self.current_session = session
                return session
            return None
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the current session."""
        if not self.current_session:
            self.current_session = Session()
        self.current_session.messages.append({"role": role, "content": content})

    def set_current_section(self, section: str) -> None:
        """Set the current section for the session."""
        if not self.current_session:
            self.current_session = Session()
        self.current_session.current_section = section

    def get_cv_data(self) -> CVData:
        """Get the CV data for the session."""
        if not self.current_session:
            self.current_session = Session()
        return self.current_session.cv_data
    
    def get_cv_data_dict(self) -> Dict:
        """Get the CV data as a dictionary for UI display."""
        if not self.current_session:
            self.current_session = Session()
        return self.current_session.cv_data.to_dict()
    
    def update_cv_data(self, cv_data_dict: Dict) -> None:
        """Update CV data from a dictionary (for external updates)."""
        if not self.current_session:
            self.current_session = Session()
        self.current_session.cv_data = CVData.from_dict(cv_data_dict)