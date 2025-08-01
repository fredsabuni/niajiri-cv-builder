#!/usr/bin/env python3
"""
Test script for experience parsing
"""

import sys
import os
# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import validate_experience

def test_experience_validation():
    """Test the experience validation function"""
    
    test_cases = [
        # (company, role, start_date, end_date, description, expected_result)
        ("Vodacom", "Sales Assistant", "01/2021", "now", "Helped customers", True),
        ("Vodacom", "Sales Assistant", "01/2021", "present", "Helped customers", True),
        ("Vodacom", "Sales Assistant", "01/2021", "12/2023", "Helped customers", True),
        ("", "Sales Assistant", "01/2021", "now", "Helped customers", False),  # Missing company
        ("Vodacom", "", "01/2021", "now", "Helped customers", False),  # Missing role
        ("Vodacom", "Sales Assistant", "2021", "now", "Helped customers", False),  # Wrong date format
        ("Vodacom", "Sales Assistant", "01/2021", "", "Helped customers", False),  # Missing end date
        ("Vodacom", "Sales Assistant", "01/2021", "now", "", False),  # Missing description
    ]
    
    print("Testing experience validation:")
    print("=" * 50)
    
    for i, (company, role, start_date, end_date, description, expected) in enumerate(test_cases, 1):
        result, error = validate_experience(company, role, start_date, end_date, description)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        print(f"Test {i}: {status}")
        print(f"  Input: company='{company}', role='{role}', start='{start_date}', end='{end_date}', desc='{description}'")
        print(f"  Expected: {expected}, Got: {result}")
        if not result:
            print(f"  Error: {error}")
        print()

def test_parsing():
    """Test parsing the exact user input"""
    user_input = "Vodacom, Sales Assistant, 01/2021, now, Helped customers"
    parts = [part.strip() for part in user_input.split(",")]
    
    print("Testing user input parsing:")
    print("=" * 30)
    print(f"Input: '{user_input}'")
    print(f"Parts: {parts}")
    print(f"Number of parts: {len(parts)}")
    
    if len(parts) >= 5:
        company, role, start_date, end_date = parts[:4]
        description = ", ".join(parts[4:])
        
        print(f"Parsed:")
        print(f"  company: '{company}'")
        print(f"  role: '{role}'")
        print(f"  start_date: '{start_date}'")
        print(f"  end_date: '{end_date}'")
        print(f"  description: '{description}'")
        
        is_valid, error = validate_experience(company, role, start_date, end_date, description)
        print(f"Validation result: {is_valid}")
        if not is_valid:
            print(f"Error: {error}")
    else:
        print(f"Error: Need 5 parts, got {len(parts)}")

if __name__ == "__main__":
    test_experience_validation()
    print()
    test_parsing()
