#!/usr/bin/env python3
"""Quick test script to check Gemini API key and available models"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found!")

try:
    genai.configure(api_key=api_key)
    print("\n✅ API key configured successfully\n")
    
    print("Available models that support generateContent:")
    print("-" * 60)
    
    models = genai.list_models()
    generate_models = []
    
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            model_name = m.name.split('/')[-1]
            generate_models.append(model_name)
            print(f"  • {model_name}")
    
    if not generate_models:
        print("  ⚠️ No models found!")
    
    print()
    
except Exception as e:
   print(f"\n❌ Error: {type(e).__name__}: {e}\n")
