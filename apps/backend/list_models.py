import os
import sys

# Force utf-8 output
sys.stdout.reconfigure(encoding='utf-8')

def load_env(filename):
    if not os.path.exists(filename): return
    # Try encodings
    for encoding in ['utf-8', 'utf-16', 'latin-1']:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                content = f.read()
                # If BOM remains, strip it? utf-8-sig handles it.
                # But let's just parse
                for line in content.splitlines():
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    if '=' in line:
                        k, v = line.split('=', 1)
                        os.environ[k] = v.strip().strip("'").strip('"')
            print(f"Loaded {filename} with {encoding}")
            return
        except UnicodeError:
            continue
    print(f"Failed to load {filename}")

load_env('.env')
load_env('.env.local')

import google.generativeai as genai

key = os.environ.get("GEMINI_API_KEY")
if not key:
    print("❌ No GEMINI_API_KEY found")
    sys.exit(1)

print(f"🔑 Key found: {key[:5]}...")

try:
    genai.configure(api_key=key)
    print("\n📋 Listing available models:")
    found = False
    for m in genai.list_models():
        print(f"- {m.name}")
        if 'generateContent' in m.supported_generation_methods:
            print(f"  ✅ Supports generateContent")
            found = True
        else:
            print(f"  ❌ No generateContent support")
            
    if not found:
        print("\n⚠️ No models support generateContent!")
        
except Exception as e:
    print(f"\n❌ Error listing models: {e}")
