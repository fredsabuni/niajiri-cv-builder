import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import json
import tempfile
import shutil

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the functions we want to test
from ui.streamlit_app import has_data_check, load_cv_data


class TestStreamlitButtonFunctionality(unittest.TestCase):
    """Test the disabled button functionality for Download CV and Improve CV"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_sessions_dir = tempfile.mkdtemp()
        self.test_session_id = "test_button_session"
        
        # Mock CV data with different completion levels
        self.empty_cv_data = {}
        
        self.partial_cv_data = {
            "personal_info": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "location": "New York, NY"
            },
            "summary": "Experienced software engineer"
        }
        
        self.complete_cv_data = {
            "personal_info": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "location": "New York, NY"
            },
            "summary": "Experienced software engineer with 5+ years of experience",
            "experience": [
                {
                    "position": "Software Engineer",
                    "company": "Tech Corp",
                    "duration": "2020-2023",
                    "description": "Developed web applications"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "MIT",
                    "year": "2020",
                    "grade": "3.8 GPA"
                }
            ],
            "skills": ["Python", "JavaScript", "React", "Node.js"]
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_sessions_dir, ignore_errors=True)
    
    def test_has_data_check_personal_info(self):
        """Test has_data_check function for personal_info section"""
        # Test with complete personal info
        personal_info_complete = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "location": "New York, NY"
        }
        self.assertTrue(has_data_check({"personal_info": personal_info_complete}, "personal_info"))
        
        # Test with partial personal info
        personal_info_partial = {
            "name": "John Doe",
            "email": "",
            "phone": "",
            "location": ""
        }
        self.assertTrue(has_data_check({"personal_info": personal_info_partial}, "personal_info"))
        
        # Test with empty personal info
        personal_info_empty = {
            "name": "",
            "email": "",
            "phone": "",
            "location": ""
        }
        self.assertFalse(has_data_check({"personal_info": personal_info_empty}, "personal_info"))
        
        # Test with None
        self.assertFalse(has_data_check({"personal_info": None}, "personal_info"))
        self.assertFalse(has_data_check({}, "personal_info"))
    
    def test_has_data_check_summary(self):
        """Test has_data_check function for summary section"""
        # Test with valid summary
        self.assertTrue(has_data_check({"summary": "Experienced engineer"}, "summary"))
        
        # Test with empty summary
        self.assertFalse(has_data_check({"summary": ""}, "summary"))
        self.assertFalse(has_data_check({"summary": "   "}, "summary"))
        self.assertFalse(has_data_check({"summary": None}, "summary"))
        self.assertFalse(has_data_check({}, "summary"))
    
    def test_has_data_check_experience(self):
        """Test has_data_check function for experience section"""
        # Test with valid experience
        experience_valid = [
            {
                "position": "Software Engineer",
                "company": "Tech Corp",
                "duration": "2020-2023",
                "description": "Developed applications"
            }
        ]
        self.assertTrue(has_data_check({"experience": experience_valid}, "experience"))
        
        # Test with partial experience
        experience_partial = [
            {
                "position": "Engineer",
                "company": "",
                "duration": "",
                "description": ""
            }
        ]
        self.assertTrue(has_data_check({"experience": experience_partial}, "experience"))
        
        # Test with empty experience
        experience_empty = [
            {
                "position": "",
                "company": "",
                "duration": "",
                "description": ""
            }
        ]
        self.assertFalse(has_data_check({"experience": experience_empty}, "experience"))
        
        # Test with empty list
        self.assertFalse(has_data_check({"experience": []}, "experience"))
        self.assertFalse(has_data_check({"experience": None}, "experience"))
        self.assertFalse(has_data_check({}, "experience"))
    
    def test_has_data_check_education(self):
        """Test has_data_check function for education section"""
        # Test with valid education
        education_valid = [
            {
                "degree": "BSc Computer Science",
                "institution": "MIT",
                "year": "2020",
                "grade": "3.8"
            }
        ]
        self.assertTrue(has_data_check({"education": education_valid}, "education"))
        
        # Test with empty education
        education_empty = [
            {
                "degree": "",
                "institution": "",
                "year": "",
                "grade": ""
            }
        ]
        self.assertFalse(has_data_check({"education": education_empty}, "education"))
        
        # Test with empty list
        self.assertFalse(has_data_check({"education": []}, "education"))
    
    def test_has_data_check_skills(self):
        """Test has_data_check function for skills section"""
        # Test with skills as list
        self.assertTrue(has_data_check({"skills": ["Python", "JavaScript"]}, "skills"))
        self.assertFalse(has_data_check({"skills": ["", "  "]}, "skills"))
        self.assertFalse(has_data_check({"skills": []}, "skills"))
        
        # Test with skills as string
        self.assertTrue(has_data_check({"skills": "Python, JavaScript"}, "skills"))
        self.assertFalse(has_data_check({"skills": ""}, "skills"))
        self.assertFalse(has_data_check({"skills": "   "}, "skills"))
    
    def test_required_sections_completion_empty(self):
        """Test completion check with empty CV data"""
        required_sections = ["personal_info", "summary", "experience", "education", "skills"]
        completed_required = sum(1 for section in required_sections if has_data_check(self.empty_cv_data, section))
        all_required_completed = completed_required >= 5
        
        self.assertEqual(completed_required, 0)
        self.assertFalse(all_required_completed)
    
    def test_required_sections_completion_partial(self):
        """Test completion check with partial CV data"""
        required_sections = ["personal_info", "summary", "experience", "education", "skills"]
        completed_required = sum(1 for section in required_sections if has_data_check(self.partial_cv_data, section))
        all_required_completed = completed_required >= 5
        
        self.assertEqual(completed_required, 2)  # personal_info and summary
        self.assertFalse(all_required_completed)
    
    def test_required_sections_completion_complete(self):
        """Test completion check with complete CV data"""
        required_sections = ["personal_info", "summary", "experience", "education", "skills"]
        completed_required = sum(1 for section in required_sections if has_data_check(self.complete_cv_data, section))
        all_required_completed = completed_required >= 5
        
        self.assertEqual(completed_required, 5)  # All required sections
        self.assertTrue(all_required_completed)
    
    def test_button_state_logic_incomplete(self):
        """Test button state logic when CV is incomplete"""
        # Simulate the logic from streamlit_app.py
        cv_data = self.partial_cv_data
        required_sections = ["personal_info", "summary", "experience", "education", "skills"]
        completed_required = sum(1 for section in required_sections if has_data_check(cv_data, section))
        all_required_completed = completed_required >= 5
        
        # Test button states
        download_help = "Download CV" if all_required_completed else "Complete all mandatory sections first"
        improve_help = "Improve CV" if all_required_completed else "Complete all mandatory sections first"
        
        self.assertFalse(all_required_completed)
        self.assertEqual(download_help, "Complete all mandatory sections first")
        self.assertEqual(improve_help, "Complete all mandatory sections first")
    
    def test_button_state_logic_complete(self):
        """Test button state logic when CV is complete"""
        # Simulate the logic from streamlit_app.py
        cv_data = self.complete_cv_data
        required_sections = ["personal_info", "summary", "experience", "education", "skills"]
        completed_required = sum(1 for section in required_sections if has_data_check(cv_data, section))
        all_required_completed = completed_required >= 5
        
        # Test button states
        download_help = "Download CV" if all_required_completed else "Complete all mandatory sections first"
        improve_help = "Improve CV" if all_required_completed else "Complete all mandatory sections first"
        
        self.assertTrue(all_required_completed)
        self.assertEqual(download_help, "Download CV")
        self.assertEqual(improve_help, "Improve CV")
    
    def test_temp_message_content(self):
        """Test the temporary message content"""
        expected_message = "Please complete all mandatory sections (Personal Info, Summary, Experience, Education, Skills)"
        
        # This would be the message shown when buttons are clicked while disabled
        self.assertEqual(
            expected_message,
            "Please complete all mandatory sections (Personal Info, Summary, Experience, Education, Skills)"
        )
    
    def test_missing_sections_identification(self):
        """Test identification of missing sections"""
        required_sections = ["personal_info", "summary", "experience", "education", "skills"]
        
        # Test with partial data
        missing_sections = [section for section in required_sections if not has_data_check(self.partial_cv_data, section)]
        expected_missing = ["experience", "education", "skills"]
        self.assertEqual(missing_sections, expected_missing)
        
        # Test with complete data
        missing_sections_complete = [section for section in required_sections if not has_data_check(self.complete_cv_data, section)]
        self.assertEqual(missing_sections_complete, [])
        
        # Test with empty data
        missing_sections_empty = [section for section in required_sections if not has_data_check(self.empty_cv_data, section)]
        self.assertEqual(missing_sections_empty, required_sections)


class TestStreamlitButtonIntegration(unittest.TestCase):
    """Integration tests for button functionality with mocked Streamlit components"""
    
    @patch('ui.streamlit_app.get_session_manager')
    def test_button_click_behavior_incomplete(self, mock_session_manager):
        """Test button click behavior when CV is incomplete"""
        # Mock session manager to return incomplete CV data
        mock_manager = MagicMock()
        mock_manager.get_cv_data.return_value = {
            "personal_info": {"name": "John Doe", "email": "john@example.com"},
            "summary": "Brief summary"
        }
        mock_session_manager.return_value = mock_manager
        
        # Import and test the logic
        from ui.streamlit_app import load_cv_data, has_data_check
        
        cv_data = load_cv_data()
        required_sections = ["personal_info", "summary", "experience", "education", "skills"]
        completed_required = sum(1 for section in required_sections if has_data_check(cv_data, section))
        all_required_completed = completed_required >= 5
        
        # Verify buttons should be disabled
        self.assertFalse(all_required_completed)
        self.assertEqual(completed_required, 2)
    
    @patch('ui.streamlit_app.get_session_manager')
    def test_button_click_behavior_complete(self, mock_session_manager):
        """Test button click behavior when CV is complete"""
        # Mock session manager to return complete CV data
        complete_data = {
            "personal_info": {"name": "John Doe", "email": "john@example.com", "phone": "123", "location": "NYC"},
            "summary": "Experienced professional with strong background",
            "experience": [{"position": "Engineer", "company": "Tech Corp", "duration": "2020-2023", "description": "Worked on projects"}],
            "education": [{"degree": "BSc", "institution": "MIT", "year": "2020", "grade": "3.8"}],
            "skills": ["Python", "JavaScript", "React"]
        }
        
        mock_manager = MagicMock()
        mock_manager.get_cv_data.return_value = complete_data
        mock_session_manager.return_value = mock_manager
        
        # Import and test the logic
        from ui.streamlit_app import load_cv_data, has_data_check
        
        cv_data = load_cv_data()
        required_sections = ["personal_info", "summary", "experience", "education", "skills"]
        completed_required = sum(1 for section in required_sections if has_data_check(cv_data, section))
        all_required_completed = completed_required >= 5
        
        # Verify buttons should be enabled
        self.assertTrue(all_required_completed)
        self.assertEqual(completed_required, 5)


if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add all test methods
    test_suite.addTest(unittest.makeSuite(TestStreamlitButtonFunctionality))
    test_suite.addTest(unittest.makeSuite(TestStreamlitButtonIntegration))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print(f"\n✅ All tests passed successfully!")
    else:
        print(f"\n❌ Some tests failed!")
