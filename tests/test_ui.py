import unittest
from unittest.mock import patch
from agents.cv_agent import CVAgent
from agents.conversation_manager import ConversationManager
from models.cv_data import CVData
import os
from pathlib import Path

class TestUI(unittest.TestCase):
    def setUp(self):
        self.sessions_dir = Path("test_sessions/")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.conversation_manager = ConversationManager(sessions_dir=str(self.sessions_dir))
        self.agent = CVAgent(self.conversation_manager)
        self.session_id = "test_ui_session"

    def tearDown(self):
        session_file = self.sessions_dir / f"{self.session_id}.json"
        if session_file.exists():
            session_file.unlink()
        if self.sessions_dir.exists():
            import shutil
            shutil.rmtree(self.sessions_dir)

    def test_initial_session(self):
        response = self.agent.start_session(self.session_id)
        self.assertIn("Welcome to the Niajiri CV Building Assistant", response)
        self.assertIn("Please provide your personal information", response)
        self.assertEqual(self.agent.get_current_section(self.session_id), "personal_info")

    def test_process_input(self):
        self.agent.start_session(self.session_id)
        response = self.agent.process_input(self.session_id, "John Doe, john@example.com, +1234567890, 123 Main St")
        self.assertIn("Personal information added successfully", response)
        self.assertIn("Please provide a brief professional summary", response)
        self.assertEqual(self.agent.get_current_section(self.session_id), "summary")

    def test_multiple_entries(self):
        self.agent.start_session(self.session_id)
        self.agent.process_input(self.session_id, "John Doe, john@example.com, +1234567890, 123 Main St")
        with patch('services.openai_service.OpenAIService.enhance_summary') as mock_enhance:
            mock_enhance.return_value = "Enhanced: Experienced software engineer with strong skills"
            self.agent.process_input(self.session_id, "Experienced software engineer")
        self.agent.process_input(self.session_id, "MIT, BSc Computer Science, 2020, Graduated with honors")
        response = self.agent.process_input(self.session_id, "Stanford, MSc Computer Science, 2022, Research focus")
        self.assertIn("Education entry added successfully", response)
        self.agent.process_input(self.session_id, "done")
        cv_data = self.conversation_manager.get_cv_data()
        self.assertEqual(len(cv_data.education), 2)
        self.assertEqual(self.agent.get_current_section(self.session_id), "experience")

    def test_review_cv(self):
        self.agent.start_session(self.session_id)
        self.agent.process_input(self.session_id, "John Doe, john@example.com, +1234567890, 123 Main St")
        with patch('services.openai_service.OpenAIService.enhance_summary') as mock_enhance:
            mock_enhance.return_value = "Enhanced: Experienced software engineer with strong skills"
            self.agent.process_input(self.session_id, "Experienced software engineer")
        cv_data = self.conversation_manager.get_cv_data()
        self.assertEqual(cv_data.personal_info["name"], "John Doe")
        self.assertEqual(cv_data.summary, "Enhanced: Experienced software engineer with strong skills")

    def test_export_cv_modern(self):
        self.agent.start_session(self.session_id)
        self.agent.process_input(self.session_id, "John Doe, john@example.com, +1234567890, 123 Main St")
        with patch('services.openai_service.OpenAIService.enhance_summary') as mock_enhance:
            mock_enhance.return_value = "Enhanced: Experienced software engineer with strong skills"
            self.agent.process_input(self.session_id, "Experienced software engineer")
        cv_data = self.conversation_manager.get_cv_data()
        with patch('reportlab.platypus.SimpleDocTemplate.build') as mock_build:
            from ui.streamlit_app import main
            # Mock 8 progress tracker buttons (False) + Review (False) + Export (True)
            with patch('streamlit.button', side_effect=[False] * 8 + [False, True]):
                with patch('streamlit.selectbox', return_value="Modern"):
                    with patch('builtins.open', create=True) as mock_open:
                        main()
                        mock_build.assert_called_once()
                        self.assertTrue(mock_open.called)
                        self.assertEqual(cv_data.personal_info["name"], "John Doe")

    def test_export_cv_classic(self):
        self.agent.start_session(self.session_id)
        self.agent.process_input(self.session_id, "John Doe, john@example.com, +1234567890, 123 Main St")
        with patch('services.openai_service.OpenAIService.enhance_summary') as mock_enhance:
            mock_enhance.return_value = "Enhanced: Experienced software engineer with strong skills"
            self.agent.process_input(self.session_id, "Experienced software engineer")
        cv_data = self.conversation_manager.get_cv_data()
        with patch('reportlab.platypus.SimpleDocTemplate.build') as mock_build:
            from ui.streamlit_app import main
            # Mock 8 progress tracker buttons (False) + Review (False) + Export (True)
            with patch('streamlit.button', side_effect=[False] * 8 + [False, True]):
                with patch('streamlit.selectbox', return_value="Classic"):
                    with patch('builtins.open', create=True) as mock_open:
                        main()
                        mock_build.assert_called_once()
                        self.assertTrue(mock_open.called)
                        self.assertEqual(cv_data.personal_info["name"], "John Doe")

    def test_export_cv_minimalist(self):
        self.agent.start_session(self.session_id)
        self.agent.process_input(self.session_id, "John Doe, john@example.com, +1234567890, 123 Main St")
        with patch('services.openai_service.OpenAIService.enhance_summary') as mock_enhance:
            mock_enhance.return_value = "Enhanced: Experienced software engineer with strong skills"
            self.agent.process_input(self.session_id, "Experienced software engineer")
        cv_data = self.conversation_manager.get_cv_data()
        with patch('reportlab.platypus.SimpleDocTemplate.build') as mock_build:
            from ui.streamlit_app import main
            # Mock 8 progress tracker buttons (False) + Review (False) + Export (True)
            with patch('streamlit.button', side_effect=[False] * 8 + [False, True]):
                with patch('streamlit.selectbox', return_value="Minimalist"):
                    with patch('builtins.open', create=True) as mock_open:
                        main()
                        mock_build.assert_called_once()
                        self.assertTrue(mock_open.called)
                        self.assertEqual(cv_data.personal_info["name"], "John Doe")

if __name__ == "__main__":
    unittest.main()