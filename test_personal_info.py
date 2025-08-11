#!/usr/bin/env python3
"""
Test script to verify personal info processing works correctly
"""

def test_safe_extraction():
    """Test the safe extraction logic"""
    
    # Test case 1: Normal case with all fields
    parsed_data_complete = {
        "name": "Fredy Sabuni",
        "email": "",  # Missing email
        "phone": "0714276333",
        "address": "Dar Tanzania"
    }
    
    # Test case 2: None values (simulating OpenAI response)
    parsed_data_with_none = {
        "name": "Fredy Sabuni",
        "email": None,  # None instead of empty string
        "phone": "0714276333",
        "address": "Dar Tanzania"
    }
    
    # Test case 3: Missing keys
    parsed_data_missing_keys = {
        "name": "Fredy Sabuni",
        "phone": "0714276333",
        "address": "Dar Tanzania"
        # email key is completely missing
    }
    
    def safe_extract(parsed_data):
        name = (parsed_data.get("name") or "").strip()
        email = (parsed_data.get("email") or "").strip()
        phone = (parsed_data.get("phone") or "").strip()
        address = (parsed_data.get("address") or "").strip()
        
        return name, email, phone, address
    
    print("Test 1 - Complete data with empty email:")
    name, email, phone, address = safe_extract(parsed_data_complete)
    print(f"Name: '{name}', Email: '{email}', Phone: '{phone}', Address: '{address}'")
    
    print("\nTest 2 - Data with None email:")
    name, email, phone, address = safe_extract(parsed_data_with_none)
    print(f"Name: '{name}', Email: '{email}', Phone: '{phone}', Address: '{address}'")
    
    print("\nTest 3 - Missing email key:")
    name, email, phone, address = safe_extract(parsed_data_missing_keys)
    print(f"Name: '{name}', Email: '{email}', Phone: '{phone}', Address: '{address}'")
    
    # Test missing items logic
    def check_missing_items(name, email, phone):
        missing_items = []
        if not name:
            missing_items.append("name")
        if not email and not phone:
            missing_items.append("contact method (email or phone)")
        return missing_items
    
    print("\nTest missing items logic:")
    for test_name, (n, e, p) in [
        ("Complete with phone", ("John", "", "123456")),
        ("Complete with email", ("John", "john@test.com", "")),
        ("Missing name", ("", "john@test.com", "123456")),
        ("Missing contact", ("John", "", "")),
        ("Missing everything", ("", "", ""))
    ]:
        missing = check_missing_items(n, e, p)
        print(f"{test_name}: Missing {missing if missing else 'nothing'}")

if __name__ == "__main__":
    test_safe_extraction()
