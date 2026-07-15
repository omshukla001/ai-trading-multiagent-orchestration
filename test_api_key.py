"""
Simple test to verify Google Gemini API key
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

print("=" * 80)
print("Google Gemini API Key Test")
print("=" * 80)
print(f"\nAPI Key found: {bool(api_key)}")
if api_key:
    print(f"API Key (first 20 chars): {api_key[:20]}...")
    print(f"API Key length: {len(api_key)}")
    
print("\n" + "=" * 80)
print("Testing API connection...")
print("=" * 80)

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    # Try to initialize with the correct model name
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        google_api_key=api_key
    )
    
    print("\n✓ Model initialized successfully")
    
    # Try a simple test call
    print("\nSending test message...")
    response = llm.invoke("Say 'API key is working' if you can read this.")
    print(f"\n✓ Response received:")
    print(f"  {response.content}")
    
    print("\n" + "=" * 80)
    print("✅ SUCCESS! Gemini API key is valid and working")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print(f"\nError type: {type(e).__name__}")
    print("\n" + "=" * 80)
    print("API Key Validation Failed")
    print("=" * 80)
    print("\nPlease verify:")
    print("1. Your API key is correct")
    print("2. Get a new key from: https://makersuite.google.com/app/apikey")
    print("3. Or use: https://aistudio.google.com/apikey")
    print("=" * 80)
