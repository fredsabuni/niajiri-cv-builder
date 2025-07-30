import unittest
import shutil
from pathlib import Path
from agents.conversation_manager import ConversationManager, Session, Message
from models.cv_data import CVData

class TestConversationManager(unittest.TestCase):
    def setUp(self):
        self.sessions_dir = Path("test_sessions/")
        self.manager = ConversationManager(sessions_dir=str(self.sessions_dir))
        self.session_id = "test_session_123"

    def tearDown(self):
        if self.sessions_dir.exists():
            shutil.rmtree(self.sessions_dir)

    def test_create_session(self):
        session = self.manager.create_session(self.session_id)
        self.assertEqual(session.session_id, self.session_id)
        self.assertEqual(len(session.messages), 0)
        self.assertIsInstance(session.cv_data, CVData)
        self.assertIsNone(session.current_section)

    def test_add_message(self):
        self.manager.create_session(self.session_id)
        self.manager.add_message("user", "Hello, let's start building my CV.")
        self.manager.add_message("assistant", "Great! Let's begin with your personal information.")
        history = self.manager.get_conversation_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].sender, "user")
        self.assertEqual(history[0].content, "Hello, let's start building my CV.")
        self.assertEqual(history[1].sender, "assistant")

    def test_set_current_section(self):
        self.manager.create_session(self.session_id)
        self.manager.set_current_section("personal_info")
        self.assertEqual(self.manager.active_session.current_section, "personal_info")

    def test_load_session(self):
        self.manager.create_session(self.session_id)
        self.manager.add_message("user", "Test message")
        self.manager.set_current_section("education")
        self.manager = ConversationManager(sessions_dir=str(self.sessions_dir))
        session = self.manager.load_session(self.session_id)
        self.assertIsNotNone(session)
        self.assertEqual(session.session_id, self.session_id)
        self.assertEqual(len(session.messages), 1)
        self.assertEqual(session.messages[0].content, "Test message")
        self.assertEqual(session.current_section, "education")

    def test_no_active_session(self):
        with self.assertRaises(ValueError):
            self.manager.add_message("user", "Test message")
        with self.assertRaises(ValueError):
            self.manager.get_conversation_history()

if __name__ == "__main__":
    unittest.main()