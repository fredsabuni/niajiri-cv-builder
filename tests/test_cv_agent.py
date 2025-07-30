import unittest
import shutil
from pathlib import Path
from agents.cv_agent import CVAgent
from agents.conversation_manager import ConversationManager
from models.cv_data import CVData
import os
from unittest.mock import patch
from datetime import datetime

class TestCVAgent(unittest.TestCase):
    def setUp(self):
        self.sessions_dir = Path("test_sessions/")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.conversation_manager = ConversationManager(sessions_dir=str(self.sessions_dir))
        self.agent = CVAgent(self.conversation_manager)
        self.session_id = "test_session_456"

    def tearDown(self):
        session_file = self.sessions_dir / f"{self.session_id}.json"
        if session_file.exists():
            session_file.unlink()
        if self.sessions_dir.exists():
            shutil.rmtree(self.sessions_dir)

    def test_start_new_session(self):
        response = self.agent.start_session(self.session_id) 
        self.assertIn("Hello! I'm your CV Building Assistant", response)
        self.assertEqual(self.agent.get_current_section(self.session_id), "personal_info")

    def test_process_personal_info_structured(self):
        self.agent.start_session(self.session_id)
        response = self.agent.process_input(self.session_id, "John Doe, john@example.com, +1234567890, 123 Main St")
        self.assertIn("Personal information added successfully", response)
        self.assertIn("Please provide a brief professional summary", response)
        cv_data = self.conversation_manager.get_cv_data()
        self.assertEqual(cv_data.personal_info["name"], "John Doe")
        self.assertEqual(self.agent.get_current_section(self.session_id), "summary")

    def test_process_personal_info_natural(self):
        self.agent.start_session(self.session_id)
        with patch('services.openai_service.OpenAIService.parse_natural_language') as mock_parse:
            mock_parse.return_value = (
                {"name": "John Doe", "email": "john@example.com", "phone": "+1234567890", "address": "123 Main St"},
                ""
            )
            response = self.agent.process_input(self.session_id, "My name is John Doe, my email is john@example.com, phone is +1234567890, and I live at 123 Main St.")
            self.assertIn("Personal information added successfully", response)
            self.assertIn("Please provide a brief professional summary", response)
            cv_data = self.conversation_manager.get_cv_data()
            self.assertEqual(cv_data.personal_info["name"], "John Doe")

    def test_process_education(self):
        self.agent.start_session(self.session_id)
        self.agent.process_input(self.session_id, "John Doe, john@example.com, +1234567890, 123 Main St")
        with patch('services.openai_service.OpenAIService.enhance_summary') as mock_enhance:
            mock_enhance.return_value = "Enhanced: Experienced software engineer"
            response = self.agent.process_input(self.session_id, "Experienced software engineer")
            self.assertIn("Summary added successfully", response)
        response = self.agent.process_input(self.session_id, "MIT, BSc Computer Science, 2020, Graduated with honors")
        self.assertIn("Education entry added successfully", response)
        self.assertIn("Add another or type 'done'", response)
        cv_data = self.conversation_manager.get_cv_data()
        self.assertEqual(cv_data.education[0]["institution"], "MIT")
        self.assertEqual(self.agent.get_current_section(self.session_id), "education")

    def test_multiple_education_entries(self):
        self.agent.start_session(self.session_id)
        self.agent.process_input(self.session_id, "John Doe, john@example.com, +1234567890, 123 Main St")
        with patch('services.openai_service.OpenAIService.enhance_summary') as mock_enhance:
            mock_enhance.return_value = "Enhanced: Experienced software engineer"
            self.agent.process_input(self.session_id, "Experienced software engineer")
        self.agent.process_input(self.session_id, "MIT, BSc Computer Science, 2020, Graduated with honors")
        response = self.agent.process_input(self.session_id, "Stanford, MSc Computer Science, 2022, Research focus")
        self.assertIn("Education entry added successfully", response)
        self.assertIn("Add another or type 'done'", response)
        response = self.agent.process_input(self.session_id, "done")
        self.assertIn("entries completed", response)
        cv_data = self.conversation_manager.get_cv_data()
        self.assertEqual(len(cv_data.education), 2)
        self.assertEqual(cv_data.education[1]["institution"], "Stanford")
        self.assertEqual(self.agent.get_current_section(self.session_id), "experience")

    def test_invalid_input_email(self):
        self.agent.start_session(self.session_id)
        response = self.agent.process_input(self.session_id, "John Doe, invalid_email, +1234567890, 123 Main St")
        self.assertIn("Invalid email format", response)
        self.assertIn("Please provide your personal information", response)
        self.assertEqual(self.agent.get_current_section(self.session_id), "personal_info")

    def test_invalid_input_date(self):
        self.agent.start_session(self.session_id)
        self.agent.process_input(self.session_id, "John Doe, john@example.com, +1234567890, 123 Main St")
        with patch('services.openai_service.OpenAIService.enhance_summary') as mock_enhance:
            mock_enhance.return_value = "Enhanced: Experienced software engineer"
            self.agent.process_input(self.session_id, "Experienced software engineer")
        
        current_year = datetime.now().year
        
        response = self.agent.process_input(self.session_id, "MIT, BSc Computer Science, 2026, Graduated with honors")
        self.assertIn("Year must be a valid number between 1900 and 2025", response)
        self.assertEqual(self.agent.get_current_section(self.session_id), "education")

    def test_skip_section(self):
        self.agent.start_session(self.session_id)
        self.agent.process_input(self.session_id, "John Doe, john@example.com, +1234567890, 123 Main St")
        with patch('services.openai_service.OpenAIService.enhance_summary') as mock_enhance:
            mock_enhance.return_value = "Enhanced: Experienced software engineer"
            self.agent.process_input(self.session_id, "Experienced software engineer")
        self.agent.process_input(self.session_id, "MIT, BSc Computer Science, 2020, Graduated with honors")
        self.agent.process_input(self.session_id, "done")
        self.agent.process_input(self.session_id, "Acme Corp, Software Engineer, 01/2021, 12/2023, Developed web apps")
        self.agent.process_input(self.session_id, "done")
        self.agent.process_input(self.session_id, "Portfolio Site, Personal website, Python, Flask")
        self.agent.process_input(self.session_id, "done")
        with patch('services.openai_service.OpenAIService.parse_natural_language') as mock_parse:
            mock_parse.return_value = (
                {"skills": ["Python", "JavaScript"]},
                ""
            )
            response = self.agent.process_input(self.session_id, "Python, JavaScript")
            self.assertIn("Skills added successfully", response)
            self.assertIn("Please add a certification", response)
            cv_data = self.conversation_manager.get_cv_data()
            self.assertEqual(cv_data.skills, ["Python", "JavaScript"])
            self.assertEqual(self.agent.get_current_section(self.session_id), "certifications")
        response = self.agent.process_input(self.session_id, "skip")
        self.assertIn("skipped, retaining existing data", response)
        self.assertEqual(self.agent.get_current_section(self.session_id), "references")

    def test_resume_session(self):
        self.agent.start_session(self.session_id)
        self.agent.process_input(self.session_id, "John Doe, john@example.com, +1234567890, 123 Main St")
        self.conversation_manager.save_session(self.session_id)
        self.agent = CVAgent(ConversationManager(sessions_dir=str(self.sessions_dir)))
        response = self.agent.start_session(self.session_id)
        self.assertIn("Welcome back", response)
        self.assertIn("Please provide a brief professional summary", response)
        self.assertEqual(self.agent.get_current_section(self.session_id), "summary")

    def test_summary_enhancement(self):
        self.agent.start_session(self.session_id)
        self.agent.process_input(self.session_id, "John Doe, john@example.com, +1234567890, 123 Main St")
        with patch('services.openai_service.OpenAIService.enhance_summary') as mock_enhance:
            mock_enhance.return_value = "Enhanced: Experienced software engineer with strong skills"
            response = self.agent.process_input(self.session_id, "Experienced software engineer")
            self.assertIn("Summary added successfully: Enhanced: Experienced software engineer with strong skills", response)
            cv_data = self.conversation_manager.get_cv_data()
            self.assertEqual(cv_data.summary, "Enhanced: Experienced software engineer with strong skills")


if __name__ == "__main__":
    unittest.main()
