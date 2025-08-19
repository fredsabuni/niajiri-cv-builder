#!/usr/bin/env python3
"""
Integration test that simulates a user completing all 5 required sections
and downloading a CV through the actual application flow
"""

import sys
import os
import json
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.cv_agent import CVAgent
from agents.conversation_manager import ConversationManager
from utils.session_manager import get_session_manager
from services.pdf_generator import CVPDFGenerator


class CVIntegrationTest:
    """Integration test that simulates real user interaction"""
    
    def __init__(self):
        self.session_manager = get_session_manager()
        self.agent = CVAgent(self.session_manager.conversation_manager)
        self.session_id = "integration_test_session"
        
    def simulate_user_conversation(self):
        """Simulate a complete user conversation to build CV"""
        print("🗣️  Simulating user conversation...")
        
        # Conversation flow that covers all 5 required sections
        conversation_steps = [
            {
                "message": "Hi, I want to create a professional CV",
                "description": "Initial greeting"
            },
            {
                "message": "My name is Sarah Johnson, email sarah.johnson@email.com, phone +1-555-987-6543, I live in San Francisco, CA",
                "description": "Personal information"
            },
            {
                "message": "I'm a Senior Data Scientist with 6 years of experience in machine learning and analytics. I specialize in developing predictive models and data-driven solutions that drive business growth.",
                "description": "Professional summary"
            },
            {
                "message": "I worked as Senior Data Scientist at DataTech Corp from 2020 to present. I lead machine learning projects, built recommendation systems serving 2M+ users, and improved model accuracy by 25%. I also mentored junior data scientists.",
                "description": "Current work experience"
            },
            {
                "message": "Before that, I was a Data Analyst at Analytics Inc from 2018 to 2020. I performed statistical analysis, created dashboards using Tableau, and collaborated with business teams to identify insights.",
                "description": "Previous work experience"
            },
            {
                "message": "I have a Master's degree in Data Science from Stanford University, graduated in 2018 with a 3.9 GPA.",
                "description": "Education"
            },
            {
                "message": "My technical skills include Python, R, SQL, TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy, Matplotlib, Tableau, AWS, Docker, and Git.",
                "description": "Technical skills"
            },
            {
                "message": "I also have experience with machine learning algorithms, statistical modeling, data visualization, big data technologies like Spark, and cloud platforms.",
                "description": "Additional skills"
            }
        ]
        
        # Start session
        start_response = self.agent.start_session(self.session_id)
        print(f"  🤖 Agent: {start_response[:100]}...")
        
        # Process each conversation step
        for i, step in enumerate(conversation_steps, 1):
            print(f"\n  👤 User ({step['description']}): {step['message']}")
            
            try:
                response = self.agent.process_message(step['message'])
                print(f"  🤖 Agent: {response[:100]}...")
                
                # Small delay to simulate realistic conversation
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ❌ Error processing message {i}: {str(e)}")
                return False
        
        print("\n  ✅ Conversation simulation completed")
        return True
    
    def verify_cv_data_structure(self):
        """Verify that the CV data has the correct structure after conversation"""
        print("\n🔍 Verifying CV data structure...")
        
        cv_data = self.session_manager.get_cv_data()
        
        if not cv_data:
            print("  ❌ No CV data found")
            return False
        
        # Check structure of each section
        checks = []
        
        # Personal info structure
        personal_info = cv_data.get("personal_info", {})
        personal_valid = (
            isinstance(personal_info, dict) and
            personal_info.get("name") and
            personal_info.get("email")
        )
        checks.append(("Personal info structure", personal_valid))
        
        # Summary structure
        summary = cv_data.get("summary", "")
        summary_valid = isinstance(summary, str) and len(summary.strip()) > 20
        checks.append(("Summary structure", summary_valid))
        
        # Experience structure
        experience = cv_data.get("experience", [])
        experience_valid = (
            isinstance(experience, list) and
            len(experience) > 0 and
            all(isinstance(exp, dict) and exp.get("position") and exp.get("company") 
                for exp in experience)
        )
        checks.append(("Experience structure", experience_valid))
        
        # Education structure
        education = cv_data.get("education", [])
        education_valid = (
            isinstance(education, list) and
            len(education) > 0 and
            all(isinstance(edu, dict) and edu.get("degree") and edu.get("institution")
                for edu in education)
        )
        checks.append(("Education structure", education_valid))
        
        # Skills structure
        skills = cv_data.get("skills", [])
        skills_valid = (
            (isinstance(skills, list) and len(skills) >= 3) or
            (isinstance(skills, str) and len(skills.split(",")) >= 3)
        )
        checks.append(("Skills structure", skills_valid))
        
        # Print results
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
        
        all_valid = all(check[1] for check in checks)
        print(f"\n  📊 Structure validation: {'✅ PASSED' if all_valid else '❌ FAILED'}")
        
        return all_valid
    
    def test_download_readiness(self):
        """Test if CV is ready for download (mirrors streamlit_app.py logic)"""
        print("\n📥 Testing download readiness...")
        
        cv_data = self.session_manager.get_cv_data()
        
        # Required sections check (same as streamlit_app.py)
        def has_data_check(cv_data, section_key):
            data = cv_data.get(section_key) if cv_data else None
            if data is None:
                return False
            if section_key == "personal_info" and isinstance(data, dict):
                return any(str(v).strip() for v in data.values())
            if section_key == "summary" and isinstance(data, str):
                return bool(data.strip())
            if section_key in ["experience", "education", "projects", "certifications", "references"] and isinstance(data, list):
                return any(any(str(v).strip() for v in item.values()) if isinstance(item, dict) else False for item in data)
            if section_key == "skills" and (isinstance(data, list) or isinstance(data, str)):
                return bool(data.strip()) if isinstance(data, str) else any(str(skill).strip() for skill in data)
            return False
        
        required_sections = ["personal_info", "summary", "experience", "education", "skills"]
        completed_required = sum(1 for section in required_sections if has_data_check(cv_data, section))
        all_required_completed = completed_required >= 5
        
        print(f"  📊 Required sections completed: {completed_required}/5")
        for section in required_sections:
            has_data = has_data_check(cv_data, section)
            status = "✅" if has_data else "❌"
            print(f"    {status} {section}")
        
        if all_required_completed:
            print("  ✅ CV is ready for download!")
        else:
            print("  ❌ CV is not ready for download - missing required sections")
        
        return all_required_completed
    
    def test_pdf_generation(self):
        """Test actual PDF generation with the current CV data"""
        print("\n📄 Testing PDF generation with real data...")
        
        cv_data = self.session_manager.get_cv_data()
        
        if not cv_data:
            print("  ❌ No CV data available for PDF generation")
            return False
        
        pdf_generator = CVPDFGenerator()
        templates = ["Modern", "Classic", "Minimal"]
        
        success_count = 0
        
        for template in templates:
            try:
                print(f"  🎨 Generating {template} PDF...")
                pdf_buffer = pdf_generator.generate_pdf(cv_data, template)
                
                if pdf_buffer and len(pdf_buffer.getvalue()) > 1000:
                    print(f"    ✅ {template}: {len(pdf_buffer.getvalue()):,} bytes")
                    success_count += 1
                    
                    # Save a test copy
                    test_file = project_root / f"test_cv_{template.lower()}.pdf"
                    with open(test_file, 'wb') as f:
                        f.write(pdf_buffer.getvalue())
                    print(f"    💾 Saved test copy: {test_file}")
                else:
                    print(f"    ❌ {template}: Failed or empty PDF")
                    
            except Exception as e:
                print(f"    ❌ {template}: Error - {str(e)}")
        
        print(f"  📊 PDF generation: {success_count}/{len(templates)} successful")
        return success_count == len(templates)
    
    def run_integration_test(self):
        """Run the complete integration test"""
        print("🧪 Starting CV Integration Test")
        print("=" * 60)
        
        test_results = {}
        
        # Step 1: Simulate conversation
        print("STEP 1: Simulating user conversation")
        conversation_success = self.simulate_user_conversation()
        test_results["conversation"] = conversation_success
        
        if not conversation_success:
            print("❌ Conversation simulation failed - aborting test")
            return False, test_results
        
        # Step 2: Verify data structure
        print("\nSTEP 2: Verifying data structure")
        structure_valid = self.verify_cv_data_structure()
        test_results["data_structure"] = structure_valid
        
        # Step 3: Test download readiness
        print("\nSTEP 3: Testing download readiness")
        download_ready = self.test_download_readiness()
        test_results["download_readiness"] = download_ready
        
        # Step 4: Test PDF generation
        print("\nSTEP 4: Testing PDF generation")
        pdf_success = self.test_pdf_generation()
        test_results["pdf_generation"] = pdf_success
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        for test_name, passed in test_results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name:.<35} {status}")
        
        overall_success = all(test_results.values())
        
        print("-" * 60)
        if overall_success:
            print("🎉 INTEGRATION TEST PASSED!")
            print("✅ Users can successfully complete all 5 required sections")
            print("✅ CV data is properly structured and stored") 
            print("✅ Download functionality works correctly")
            print("✅ PDF generation works for all templates")
        else:
            print("⚠️  INTEGRATION TEST FAILED!")
            print("❌ Some functionality is not working correctly")
        
        return overall_success, test_results


def main():
    """Main function to run the integration test"""
    test_runner = CVIntegrationTest()
    success, results = test_runner.run_integration_test()
    
    # Clean up test files (optional)
    cleanup = input("\n🗑️  Delete test files? (y/N): ").lower().strip() == 'y'
    if cleanup:
        test_files = list(project_root.glob("test_cv_*.pdf"))
        for file in test_files:
            try:
                file.unlink()
                print(f"  🗑️  Deleted {file.name}")
            except Exception as e:
                print(f"  ❌ Could not delete {file.name}: {e}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
