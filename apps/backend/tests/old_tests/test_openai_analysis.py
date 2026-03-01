import sys
import os
import asyncio
import logging

# Force utf-8
sys.stdout.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load env robustly
def load_env(filename):
    if not os.path.exists(filename): return
    for encoding in ['utf-8', 'utf-16', 'latin-1']:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                content = f.read()
                for line in content.splitlines():
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    if '=' in line:
                        k, v = line.split('=', 1)
                        os.environ[k] = v.strip().strip("'").strip('"')
            print(f"Loaded {filename}")
            return
        except UnicodeError:
            continue

load_env('.env')
load_env('.env.local')

sys.path.append(os.getcwd())

from app.services.analysis.openai_client import OpenAIClient

async def main():
    print("Testing OpenAI Client...")
    client = OpenAIClient()
    
    if not client.client:
        print("Failed to init OpenAI Client - Key missing?")
        return

    text = "John Doe. Software Engineer. Python, JavaScript. Experience: 5 years at Tech Corp."
    print(f"Analyzing text: {text}")
    
    try:
        result = await client.analyze_resume(text)
        import json
        print("\n--- RESULT ---")
        print(json.dumps(result, indent=2))
        print("\nSUCCESS!")
    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
