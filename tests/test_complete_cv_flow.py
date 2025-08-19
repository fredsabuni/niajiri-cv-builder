#!/usr/bin/env python3
"""
Comprehensive test script to fill all 5 required CV sections and test download functionality
Tests the complete flow from data entry to PDF generation
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.cv_agent import CVAgent
from agents.conversation_manager import ConversationManager
from utils.session_manager import SessionManager
from services.pdf_generator import CVPDFGenerator
from models.cv_data import CVData


class TestCompleteCVFlow:
    """Test class for complete CV building flow"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        # Use the sessions directory from the project
        sessions_dir = str(project_root / "sessions")
        self.conversation_manager = ConversationManager(sessions_dir)
        self.agent = CVAgent(self.conversation_manager)
        self.test_session_id = "test_complete_flow_session"
        
    def create_complete_test_data(self):
        """Create comprehensive test data for all 5 required sections"""
        return {
            "personal_info": {
                "name": "John Doe",
                "email": "john.doe@email.com",
                "phone": "+1 (555) 123-4567",
                "location": "New York, NY, USA"
            },
            "summary": "Results-driven Software Engineer with 5+ years of experience in full-stack development. Proven track record of delivering scalable web applications using modern technologies. Expertise in Python, JavaScript, and cloud platforms. Strong problem-solving skills and passion for clean, efficient code.",
            "experience": [
                {
                    "position": "Senior Software Engineer",
                    "company": "Tech Solutions Inc.",
                    "duration": "2021 - Present",
                    "description": "Led development of microservices architecture serving 1M+ users. Implemented CI/CD pipelines reducing deployment time by 60%. Mentored junior developers and collaborated with cross-functional teams to deliver high-quality software solutions."
                },
                {
                    "position": "Software Developer",
                    "company": "StartupCorp",
                    "duration": "2019 - 2021",
                    "description": "Developed and maintained web applications using React and Node.js. Built RESTful APIs and integrated third-party services. Participated in agile development processes and code reviews."
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University of Technology",
                    "year": "2019",
                    "grade": "3.8 GPA"
                }
            ],
            "skills": [
                "Python",
                "JavaScript",
                "React",
                "Node.js",
                "Docker",
                "AWS",
                "PostgreSQL",
                "Git",
                "Agile/Scrum"
            ],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "description": "Built a full-stack e-commerce platform with payment integration and real-time inventory management",
                    "technologies": "Python, Django, React, PostgreSQL, Stripe API"
                }
            ],
            "certifications": [
                {
                    "name": "AWS Solutions Architect Associate",
                    "issuer": "Amazon Web Services",
                    "date": "2022"
                }
            ]
        }
    
    def test_section_validation(self, cv_data):
        """Test that all required sections are properly validated"""
        print("🔍 Testing section validation...")
        
        required_sections = ["personal_info", "summary", "experience", "education", "skills"]
        results = {}
        
        for section in required_sections:
            has_data = self.has_data_check(cv_data, section)
            results[section] = has_data
            status = "✅" if has_data else "❌"
            print(f"  {status} {section}: {'Valid' if has_data else 'Missing/Invalid'}")
        
        all_complete = all(results.values())
        print(f"\n📊 Overall validation: {'✅ PASSED' if all_complete else '❌ FAILED'}")
        return all_complete, results
    
    def has_data_check(self, cv_data, section_key):
        """Helper function to check if a section has data (mirrors streamlit_app.py logic)"""
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
    
    def test_pdf_generation(self, cv_data):
        """Test PDF generation for all templates"""
        print("\n📄 Testing PDF generation...")
        
        pdf_generator = CVPDFGenerator()
        templates = ["Modern", "Classic", "Minimal"]
        results = {}
        
        for template in templates:
            try:
                print(f"  🎨 Generating {template} template...")
                pdf_buffer = pdf_generator.generate_pdf(cv_data, template)
                
                # Check if PDF was generated successfully
                pdf_size = len(pdf_buffer.getvalue())
                if pdf_size > 1000:  # Reasonable PDF should be > 1KB
                    results[template] = {"success": True, "size": pdf_size}
                    print(f"    ✅ {template}: Generated successfully ({pdf_size:,} bytes)")
                else:
                    results[template] = {"success": False, "error": "PDF too small"}
                    print(f"    ❌ {template}: PDF too small ({pdf_size} bytes)")
                    
            except Exception as e:
                results[template] = {"success": False, "error": str(e)}
                print(f"    ❌ {template}: Error - {str(e)}")
        
        successful_templates = sum(1 for r in results.values() if r["success"])
        print(f"\n📊 PDF Generation: {successful_templates}/{len(templates)} templates successful")
        return results
    
    def test_session_persistence(self, cv_data):
        """Test that CV data can be saved and loaded correctly"""
        print("\n💾 Testing session persistence...")
        
        try:
            # Save data
            self.session_manager.session_id = self.test_session_id
            self.session_manager.update_cv_data(cv_data)
            print("  ✅ Data saved successfully")
            
            # Load data
            loaded_data = self.session_manager.get_cv_data()
            
            # Compare data
            if loaded_data == cv_data:
                print("  ✅ Data loaded and matches original")
                return True
            else:
                print("  ❌ Loaded data doesn't match original")
                return False
                
        except Exception as e:
            print(f"  ❌ Session persistence error: {str(e)}")
            return False
    
    def test_agent_interaction(self):
        """Test basic agent functionality"""
        print("\n🤖 Testing agent interaction...")
        
        try:
            # Test session start
            response = self.agent.start_session(self.test_session_id)
            if response and len(response) > 10:
                print("  ✅ Agent session started successfully")
            else:
                print("  ❌ Agent session start failed")
                return False
            
            # Test message processing
            test_message = "Hello, I want to build my CV"
            response = self.agent.process_message(test_message)
            
            if response and len(response) > 10:
                print("  ✅ Agent message processing works")
                return True
            else:
                print("  ❌ Agent message processing failed")
                return False
                
        except Exception as e:
            print(f"  ❌ Agent interaction error: {str(e)}")
            return False
    
    def test_data_completeness(self, cv_data):
        """Test that all data fields are properly populated"""
        print("\n📋 Testing data completeness...")
        
        checks = []
        
        # Personal info completeness
        personal = cv_data.get("personal_info", {})
        required_personal = ["name", "email"]
        personal_complete = all(personal.get(field) for field in required_personal)
        checks.append(("Personal info required fields", personal_complete))
        
        # Summary length check
        summary = cv_data.get("summary", "")
        summary_adequate = len(summary) >= 50
        checks.append(("Summary length (≥50 chars)", summary_adequate))
        
        # Experience details
        experience = cv_data.get("experience", [])
        exp_complete = len(experience) > 0 and all(
            exp.get("position") and exp.get("company") and exp.get("description")
            for exp in experience
        )
        checks.append(("Experience completeness", exp_complete))
        
        # Education details
        education = cv_data.get("education", [])
        edu_complete = len(education) > 0 and all(
            edu.get("degree") and edu.get("institution")
            for edu in education
        )
        checks.append(("Education completeness", edu_complete))
        
        # Skills count
        skills = cv_data.get("skills", [])
        skills_adequate = len(skills) >= 3 if isinstance(skills, list) else len(skills.split(",")) >= 3
        checks.append(("Skills count (≥3)", skills_adequate))
        
        # Print results
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
        
        overall_complete = all(check[1] for check in checks)
        print(f"\n📊 Data completeness: {'✅ PASSED' if overall_complete else '❌ FAILED'}")
        return overall_complete
    
    def run_complete_test(self):
        """Run the complete test suite"""
        print("🚀 Starting Complete CV Flow Test")
        print("=" * 50)
        
        # Create test data
        print("📝 Creating comprehensive test data...")
        cv_data = self.create_complete_test_data()
        print("  ✅ Test data created")
        
        # Run all tests
        test_results = {}
        
        # Test 1: Section validation
        validation_passed, validation_results = self.test_section_validation(cv_data)
        test_results["section_validation"] = validation_passed
        
        # Test 2: Data completeness
        completeness_passed = self.test_data_completeness(cv_data)
        test_results["data_completeness"] = completeness_passed
        
        # Test 3: Session persistence
        persistence_passed = self.test_session_persistence(cv_data)
        test_results["session_persistence"] = persistence_passed
        
        # Test 4: PDF generation
        pdf_results = self.test_pdf_generation(cv_data)
        pdf_passed = all(result["success"] for result in pdf_results.values())
        test_results["pdf_generation"] = pdf_passed
        
        # Test 5: Agent interaction
        agent_passed = self.test_agent_interaction()
        test_results["agent_interaction"] = agent_passed
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        for test_name, passed in test_results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name:.<25} {status}")
        
        overall_passed = all(test_results.values())
        overall_status = "✅ ALL TESTS PASSED" if overall_passed else "❌ SOME TESTS FAILED"
        
        print("-" * 50)
        print(f"OVERALL RESULT: {overall_status}")
        
        if overall_passed:
            print("\n🎉 Complete CV flow is working correctly!")
            print("✅ All 5 required sections can be filled")
            print("✅ PDF download functionality works")
            print("✅ Data persistence works")
            print("✅ Agent interaction works")
        else:
            print("\n⚠️  Some components need attention before production use.")
        
        return overall_passed, test_results


def main():
    """Main function to run the test"""
    test_runner = TestCompleteCVFlow()
    success, results = test_runner.run_complete_test()
    
    # Save test results
    results_file = Path(project_root) / "test_results_complete_flow.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": str(Path(__file__).stat().st_mtime),
            "overall_success": success,
            "test_results": results
        }, f, indent=2)
    
    print(f"\n📁 Test results saved to: {results_file}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
