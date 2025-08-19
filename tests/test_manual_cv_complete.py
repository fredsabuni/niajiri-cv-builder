#!/usr/bin/env python3
"""
Simple manual test to verify CV building functionality
Tests the core functionality without UI dependencies
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_manual_cv_creation():
    """Manual test of CV creation without dependencies"""
    print("🧪 Manual CV Creation Test")
    print("=" * 40)
    
    # Test data - all 5 required sections
    cv_data = {
        "personal_info": {
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "+1 (555) 123-4567",
            "location": "New York, NY, USA"
        },
        "summary": "Experienced Software Engineer with 5+ years in full-stack development. Proven track record of delivering scalable applications using modern technologies. Strong problem-solving skills and leadership experience.",
        "experience": [
            {
                "position": "Senior Software Engineer",
                "company": "Tech Solutions Inc.",
                "duration": "2021 - Present",
                "description": "Led development of microservices architecture serving 1M+ users. Implemented CI/CD pipelines reducing deployment time by 60%. Mentored junior developers and delivered high-quality software solutions."
            },
            {
                "position": "Software Developer", 
                "company": "StartupCorp",
                "duration": "2019 - 2021",
                "description": "Developed web applications using React and Node.js. Built RESTful APIs and integrated third-party services. Participated in agile development processes."
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
            "Python", "JavaScript", "React", "Node.js", "Docker", 
            "AWS", "PostgreSQL", "Git", "Agile/Scrum"
        ]
    }
    
    print("✅ Test data created")
    
    # Test 1: Validate data structure
    print("\n🔍 Testing data validation...")
    
    def has_data_check(cv_data, section_key):
        """Same validation logic as streamlit_app.py"""
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
    validation_results = {}
    
    for section in required_sections:
        is_valid = has_data_check(cv_data, section)
        validation_results[section] = is_valid
        status = "✅" if is_valid else "❌"
        print(f"  {status} {section}")
    
    all_valid = all(validation_results.values())
    print(f"\n📊 Validation: {'✅ PASSED' if all_valid else '❌ FAILED'}")
    
    # Test 2: Test PDF generation
    print("\n📄 Testing PDF generation...")
    
    try:
        from services.pdf_generator import CVPDFGenerator
        
        pdf_generator = CVPDFGenerator()
        templates = ["Modern", "Classic", "Minimal"]
        pdf_results = {}
        
        for template in templates:
            try:
                pdf_buffer = pdf_generator.generate_pdf(cv_data, template)
                
                if pdf_buffer and len(pdf_buffer.getvalue()) > 1000:
                    pdf_results[template] = True
                    print(f"  ✅ {template}: {len(pdf_buffer.getvalue()):,} bytes")
                    
                    # Save test PDF
                    test_file = project_root / f"manual_test_{template.lower()}.pdf"
                    with open(test_file, 'wb') as f:
                        f.write(pdf_buffer.getvalue())
                    print(f"    💾 Saved: {test_file.name}")
                else:
                    pdf_results[template] = False
                    print(f"  ❌ {template}: Failed or empty")
                    
            except Exception as e:
                pdf_results[template] = False
                print(f"  ❌ {template}: Error - {str(e)}")
        
        pdf_success = all(pdf_results.values())
        print(f"\n📊 PDF Generation: {'✅ PASSED' if pdf_success else '❌ FAILED'}")
        
    except Exception as e:
        print(f"  ❌ PDF Generation failed: {str(e)}")
        pdf_success = False
    
    # Test 3: Test session file creation
    print("\n💾 Testing session file creation...")
    
    try:
        # Create a test session file
        sessions_dir = project_root / "sessions"
        sessions_dir.mkdir(exist_ok=True)
        
        test_session_file = sessions_dir / "manual_test_session.json"
        
        with open(test_session_file, 'w') as f:
            json.dump(cv_data, f, indent=2)
        
        # Verify file was created and can be read
        with open(test_session_file, 'r') as f:
            loaded_data = json.load(f)
        
        if loaded_data == cv_data:
            print("  ✅ Session file created and verified")
            session_success = True
        else:
            print("  ❌ Session file data mismatch")
            session_success = False
            
    except Exception as e:
        print(f"  ❌ Session file error: {str(e)}")
        session_success = False
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 MANUAL TEST SUMMARY")
    print("=" * 40)
    
    tests = [
        ("Data validation", all_valid),
        ("PDF generation", pdf_success),
        ("Session persistence", session_success)
    ]
    
    for test_name, passed in tests:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<25} {status}")
    
    overall_success = all(result for _, result in tests)
    
    print("-" * 40)
    if overall_success:
        print("🎉 ALL MANUAL TESTS PASSED!")
        print("✅ CV data structure is valid")
        print("✅ PDF generation works for all templates")
        print("✅ Session persistence works")
        print("\n🎯 The CV building core functionality is working!")
    else:
        print("⚠️  SOME MANUAL TESTS FAILED!")
        print("❌ Check the specific failures above")
    
    return overall_success


def test_download_simulation():
    """Simulate the download button logic from streamlit_app.py"""
    print("\n🔽 Testing Download Button Logic")
    print("=" * 40)
    
    # Same test data
    cv_data = {
        "personal_info": {"name": "John Doe", "email": "john@email.com", "phone": "+1-555-123-4567"},
        "summary": "Experienced developer with strong technical skills",
        "experience": [{"position": "Developer", "company": "Tech Corp", "description": "Built software"}],
        "education": [{"degree": "BS Computer Science", "institution": "University"}],
        "skills": ["Python", "JavaScript", "React"]
    }
    
    # Test the exact logic from streamlit_app.py
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
    
    print(f"📊 Required sections completed: {completed_required}/5")
    for section in required_sections:
        has_data = has_data_check(cv_data, section)
        status = "✅" if has_data else "❌"
        print(f"  {status} {section}")
    
    print(f"\n🔽 Download available: {'✅ YES' if all_required_completed else '❌ NO'}")
    
    if all_required_completed:
        print("✅ User would see active download buttons")
        print("✅ User can download CV in all 3 templates")
    else:
        print("❌ User would see disabled download buttons")
        print("❌ User would see error message about missing sections")
    
    return all_required_completed


def main():
    """Run all manual tests"""
    print("🚀 Starting Manual CV Building Tests")
    print("=" * 50)
    
    # Test 1: Core functionality
    core_success = test_manual_cv_creation()
    
    # Test 2: Download logic
    download_success = test_download_simulation()
    
    print("\n" + "=" * 50)
    print("🎯 FINAL RESULTS")
    print("=" * 50)
    
    if core_success and download_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Core CV building functionality works")
        print("✅ Download logic works correctly")
        print("✅ Users can successfully fill all 5 sections and download CV")
        
        print("\n📋 Manual Test Summary:")
        print("• Personal info section ✅")
        print("• Professional summary ✅")
        print("• Work experience ✅")
        print("• Education ✅")
        print("• Skills ✅")
        print("• PDF generation (3 templates) ✅")
        print("• Download readiness check ✅")
        
    else:
        print("⚠️  SOME TESTS FAILED!")
        if not core_success:
            print("❌ Core functionality issues")
        if not download_success:
            print("❌ Download logic issues")
    
    # Cleanup option
    cleanup = input("\n🗑️  Delete test files? (y/N): ").lower().strip() == 'y'
    if cleanup:
        test_files = list(project_root.glob("manual_test_*.pdf"))
        session_files = list((project_root / "sessions").glob("manual_test_*.json"))
        
        for file in test_files + session_files:
            try:
                file.unlink()
                print(f"  🗑️  Deleted {file.name}")
            except Exception as e:
                print(f"  ❌ Could not delete {file.name}: {e}")
    
    return 0 if (core_success and download_success) else 1


if __name__ == "__main__":
    sys.exit(main())
