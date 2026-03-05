"""
Script para criar um teste direto da análise do Gemini
"""
import os
from pathlib import Path

# Load key from .env.local
from dotenv import load_dotenv
load_dotenv('.env.local')
load_dotenv('.env')
assert os.getenv('GEMINI_API_KEY'), 'GEMINI_API_KEY not set in .env.local'

print("Testing Gemini API directly...")
print(f"GEMINI_API_KEY set: {os.environ.get('GEMINI_API_KEY')[:20]}...")

try:
    import google.generativeai as genai
    
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    
    # List available models
    print("\nAvailable models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
    
    # Test with a simple prompt
    print("\nTesting Gemini with simple prompt...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    response = model.generate_content("Say 'Hello, AI is working!' in Portuguese")
    print(f"\n✅ Gemini Response: {response.text}")
    
    print("\n🎉 GEMINI API ESTÁ FUNCIONANDO!")
    
except Exception as e:
    print(f"\n❌ Erro ao testar Gemini: {e}")
    import traceback
    traceback.print_exc()
