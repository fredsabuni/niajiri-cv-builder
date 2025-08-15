#!/usr/bin/env python3
"""
Comprehensive test script to verify personal info processing works correctly
"""

import json
from typing import Dict, Any, List, Tuple


def safe_extract(parsed_data: Dict[str, Any]) -> Tuple[str, str, str, str]:
    """
    Safely extract personal information from parsed data
    Handles None values, missing keys, and whitespace
    """
    name = (parsed_data.get("name") or "").strip()
    email = (parsed_data.get("email") or "").strip()
    phone = (parsed_data.get("phone") or "").strip()
    address = (parsed_data.get("address") or "").strip()
    
    return name, email, phone, address


def check_missing_items(name: str, email: str, phone: str) -> List[str]:
    """
    Check for missing required information
    Returns list of missing items
    """
    missing_items = []
    if not name:
        missing_items.append("name")
    if not email and not phone:
        missing_items.append("contact method (email or phone)")
    return missing_items


def validate_email(email: str) -> bool:
    """Basic email validation"""
    if not email:
        return False
    return "@" in email and "." in email.split("@")[-1]


def validate_phone(phone: str) -> bool:
    """Basic phone validation"""
    if not phone:
        return False
    # Remove common separators and check if remaining chars are mostly digits
    cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")
    return len(cleaned) >= 7 and cleaned.replace(" ", "").isdigit()


def test_basic_scenarios():
    """Test basic extraction scenarios"""
    print("=" * 60)
    print("BASIC EXTRACTION SCENARIOS")
    print("=" * 60)
    
    test_cases = [
        ("Complete data", {
            "name": "John Smith",
            "email": "john.smith@email.com",
            "phone": "555-123-4567",
            "address": "123 Main St, New York, NY"
        }),
        
        ("Missing email", {
            "name": "Jane Doe",
            "email": "",
            "phone": "555-987-6543",
            "address": "456 Oak Ave, Boston, MA"
        }),
        
        ("Missing phone", {
            "name": "Bob Wilson",
            "email": "bob.wilson@company.com",
            "phone": "",
            "address": "789 Pine St, Seattle, WA"
        }),
        
        ("None values", {
            "name": "Alice Johnson",
            "email": None,
            "phone": "555-555-5555",
            "address": None
        }),
        
        ("Missing keys", {
            "name": "Mike Brown",
            "phone": "555-111-2222"
            # email and address keys missing
        }),
        
        ("Empty dictionary", {}),
        
        ("Whitespace data", {
            "name": "  Sarah Connor  ",
            "email": "  sarah@resistance.com  ",
            "phone": "  555-TERM-NAT  ",
            "address": "  Los Angeles, CA  "
        })
    ]
    
    for test_name, test_data in test_cases:
        print(f"\n{test_name}:")
        name, email, phone, address = safe_extract(test_data)
        missing = check_missing_items(name, email, phone)
        
        print(f"  Input: {json.dumps(test_data, indent=4)}")
        print(f"  Results:")
        print(f"    Name: '{name}'")
        print(f"    Email: '{email}'")
        print(f"    Phone: '{phone}'")
        print(f"    Address: '{address}'")
        print(f"  Validation: {'✓ VALID' if not missing else f'✗ INVALID - Missing: {missing}'}")


def test_international_scenarios():
    """Test international format scenarios"""
    print("\n" + "=" * 60)
    print("INTERNATIONAL FORMAT SCENARIOS")
    print("=" * 60)
    
    test_cases = [
        ("UK Format", {
            "name": "Oliver Thompson",
            "email": "oliver.thompson@email.co.uk",
            "phone": "+44 20 7946 0958",
            "address": "10 Downing Street, London, UK"
        }),
        
        ("German Format", {
            "name": "Hans Müller",
            "email": "hans.mueller@email.de",
            "phone": "+49 30 12345678",
            "address": "Alexanderplatz 1, Berlin, Germany"
        }),
        
        ("Japanese Format", {
            "name": "田中太郎",
            "email": "tanaka@email.jp",
            "phone": "+81-90-1234-5678",
            "address": "東京都渋谷区, Japan"
        }),
        
        ("Kenyan Format", {
            "name": "Wanjiku Njeri",
            "email": "wanjiku@email.co.ke",
            "phone": "+254 701 234567",
            "address": "Nairobi, Kenya"
        }),
        
        ("Tanzanian Format", {
            "name": "Fredy Sabuni",
            "email": "fredy@email.co.tz",
            "phone": "0714276333",
            "address": "Dar es Salaam, Tanzania"
        })
    ]
    
    for test_name, test_data in test_cases:
        print(f"\n{test_name}:")
        name, email, phone, address = safe_extract(test_data)
        missing = check_missing_items(name, email, phone)
        
        print(f"  Name: '{name}'")
        print(f"  Email: '{email}' (Valid: {validate_email(email)})")
        print(f"  Phone: '{phone}' (Valid: {validate_phone(phone)})")
        print(f"  Address: '{address}'")
        print(f"  Status: {'✓ VALID' if not missing else f'✗ INVALID - Missing: {missing}'}")


def test_edge_cases():
    """Test edge cases and error conditions"""
    print("\n" + "=" * 60)
    print("EDGE CASES AND ERROR CONDITIONS")
    print("=" * 60)
    
    edge_cases = [
        ("Very long name", {
            "name": "Dr. Elizabeth Margaret Williamson-Thompson III, PhD, MD, Esq.",
            "email": "elizabeth@verylongdomainname.university.edu",
            "phone": "+1-555-123-4567",
            "address": "123 Very Long Street Name, Building Complex, Suite 456, City, State, Country, 12345"
        }),
        
        ("Special characters", {
            "name": "José María O'Connor-Smith",
            "email": "jose.maria@español.com",
            "phone": "+34-91-123-45-67",
            "address": "Calle Principal, Madrid, España"
        }),
        
        ("Numeric values", {
            "name": 12345,
            "email": "test@email.com",
            "phone": 5551234567,
            "address": "123 Main St"
        }),
        
        ("Boolean values", {
            "name": True,
            "email": False,
            "phone": None,
            "address": ""
        }),
        
        ("List values", {
            "name": ["John", "Doe"],
            "email": ["john@email.com"],
            "phone": [],
            "address": ["123 Main St", "Apt 4"]
        }),
        
        ("Mixed types", {
            "name": "Valid Name",
            "email": {"domain": "email.com"},
            "phone": ["555", "1234"],
            "address": 12345
        })
    ]
    
    for test_name, test_data in edge_cases:
        print(f"\n{test_name}:")
        try:
            name, email, phone, address = safe_extract(test_data)
            missing = check_missing_items(name, email, phone)
            
            print(f"  Name: '{name}' (type: {type(name).__name__})")
            print(f"  Email: '{email}' (type: {type(email).__name__})")
            print(f"  Phone: '{phone}' (type: {type(phone).__name__})")
            print(f"  Address: '{address}' (type: {type(address).__name__})")
            print(f"  Status: {'✓ HANDLED' if isinstance(name, str) else '✗ TYPE ERROR'}")
            
            if isinstance(name, str) and isinstance(email, str) and isinstance(phone, str):
                print(f"  Validation: {'✓ VALID' if not missing else f'✗ INVALID - Missing: {missing}'}")
        except Exception as e:
            print(f"  ✗ ERROR: {e}")


def test_validation_logic():
    """Test the validation logic thoroughly"""
    print("\n" + "=" * 60)
    print("VALIDATION LOGIC TESTS")
    print("=" * 60)
    
    validation_cases = [
        # (name, email, phone, expected_missing)
        ("John Doe", "john@email.com", "555-1234", []),
        ("Jane Smith", "jane@email.com", "", []),
        ("Bob Wilson", "", "555-9876", []),
        ("", "contact@email.com", "555-5555", ["name"]),
        ("Alice Cooper", "", "", ["contact method (email or phone)"]),
        ("", "", "", ["name", "contact method (email or phone)"]),
        ("   ", "email@test.com", "123456", ["name"]),  # whitespace name
        ("Valid Name", "   ", "   ", ["contact method (email or phone)"]),  # whitespace contacts
        ("María José", "", "123-456-7890", []),
        ("张三", "chinese@email.com", "", [])
    ]
    
    for name, email, phone, expected_missing in validation_cases:
        missing = check_missing_items(name, email, phone)
        status = "✓ PASS" if missing == expected_missing else "✗ FAIL"
        
        print(f"Name: '{name}', Email: '{email}', Phone: '{phone}'")
        print(f"  Expected: {expected_missing}")
        print(f"  Got: {missing}")
        print(f"  Result: {status}\n")


def test_real_world_scenarios():
    """Test real-world CV scenarios"""
    print("=" * 60)
    print("REAL-WORLD CV SCENARIOS")
    print("=" * 60)
    
    scenarios = [
        ("Fresh Graduate", {
            "name": "Emily Chen",
            "email": "emily.chen2024@university.edu",
            "phone": "+1-555-123-4567",
            "address": "Student Housing, University Campus, State"
        }),
        
        ("Senior Professional", {
            "name": "Dr. Robert Anderson, PhD",
            "email": "robert.anderson@corporation.com",
            "phone": "+1-555-987-6543",
            "address": "Executive District, Metropolitan City"
        }),
        
        ("Freelancer", {
            "name": "Alex Rivera",
            "email": "alex@freelancedesign.com",
            "phone": "",
            "address": "Remote Worker, Various Locations"
        }),
        
        ("International Applicant", {
            "name": "Priya Sharma",
            "email": "priya.sharma@techcompany.in",
            "phone": "+91-98765-43210",
            "address": "Bangalore, Karnataka, India"
        }),
        
        ("Career Changer", {
            "name": "Mark Thompson",
            "email": "",
            "phone": "555-NEW-CAREER",
            "address": "Transitioning Professional, Open to Relocation"
        })
    ]
    
    for scenario_name, data in scenarios:
        print(f"\n{scenario_name}:")
        name, email, phone, address = safe_extract(data)
        missing = check_missing_items(name, email, phone)
        
        print(f"  Personal Info Extracted:")
        print(f"    Name: {name}")
        print(f"    Email: {email}")
        print(f"    Phone: {phone}")
        print(f"    Address: {address}")
        
        if missing:
            print(f"  ⚠️  Warning: Missing {', '.join(missing)}")
        else:
            print("  ✓ All required information present")


def run_all_tests():
    """Run all test scenarios"""
    print("🚀 Starting Personal Info Processing Tests\n")
    
    test_basic_scenarios()
    test_international_scenarios()
    test_edge_cases()
    test_validation_logic()
    test_real_world_scenarios()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
