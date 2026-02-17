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

openai_key = os.environ.get("OPENAI_API_KEY")
gemini_key = os.environ.get("GEMINI_API_KEY")

print(f"OPENAI_API_KEY present: {bool(openai_key)}")
if openai_key:
    print(f"OPENAI_API_KEY prefix: {openai_key[:7]}...")

print(f"GEMINI_API_KEY present: {bool(gemini_key)}")

llm_provider = os.environ.get("LLM_PROVIDER")
print(f"LLM_PROVIDER: {llm_provider}")
