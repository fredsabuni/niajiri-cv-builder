#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.openai_service import OpenAIService

def test_openai_service():
    print("=== Testing OpenAI Service ===")
    
    try:
        # Initialize the service
        service = OpenAIService()
        print(f"✅ OpenAI service initialized successfully")
        print(f"Model: {service.model}")
        print(f"Cost mode: {service.cost_mode}")
        
        # Test natural language parsing for experience
        print("\n=== Testing Natural Language Parsing ===")
        test_input = "I worked at Vodacom as a Sales Assistant from January 2021 until now, helping customers"
        section = "experience"
        
        parsed_data, error = service.parse_natural_language(test_input, section)
        
        if error:
            print(f"❌ Parsing failed: {error}")
        else:
            print(f"✅ Parsing successful: {parsed_data}")
            
        # Also test a simple enhancement
        print("\n=== Testing Summary Enhancement ===")
        test_summary = "I am a sales person"
        enhanced = service.enhance_summary(test_summary)
        print(f"Original: {test_summary}")
        print(f"Enhanced: {enhanced}")
        
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_openai_service()
