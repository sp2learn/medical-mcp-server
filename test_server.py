#!/usr/bin/env python3
"""
Test script for the Medical MCP Server
"""

import asyncio
import json
from dotenv import load_dotenv
from medical_client import MedicalClient

# Load environment variables
load_dotenv()

async def test_medical_client():
    """Test the medical client functionality."""
    print("Testing Medical MCP Server...")
    
    try:
        client = MedicalClient()
        print(f"✓ Client initialized with model: {client.model_type}")
        
        # Test medical query
        print("\n--- Testing Medical Query ---")
        question = "What are the common symptoms of diabetes?"
        response = await client.query_medical_question(question)
        print(f"Question: {question}")
        print(f"Response: {response[:200]}...")
        
        # Test symptom checker
        print("\n--- Testing Symptom Checker ---")
        symptoms = ["headache", "fever", "fatigue"]
        response = await client.analyze_symptoms(symptoms, age=30, gender="female")
        print(f"Symptoms: {symptoms}")
        print(f"Response: {response[:200]}...")
        
        print("\n✓ All tests completed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        print("Make sure you have:")
        print("1. Installed requirements: pip install -r requirements.txt")
        print("2. Created .env file with your API keys")
        print("3. Set MEDICAL_MODEL to 'gemini' or 'nova'")

if __name__ == "__main__":
    asyncio.run(test_medical_client())