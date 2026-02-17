import sys
import os
import asyncio
from pathlib import Path

# Force utf-8
sys.stdout.reconfigure(encoding='utf-8')
import logging

# Configure logging to show info
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 1. Setup Environment
sys.path.append(os.getcwd())

def load_env(filename):
    path = os.path.join(os.getcwd(), filename)
    if not os.path.exists(path):
        print(f"{filename} not found at {path}")
        return

    print(f"Loading {filename}...")
    content = ""
    # Try encodings
    for encoding in ['utf-8', 'utf-16', 'latin-1']:
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except UnicodeError:
            continue
    
    if not content:
        print(f"Failed to read {filename} with any encoding")
        return

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'): continue
        if '=' in line:
            k, v = line.split('=', 1)
            val = v.strip().strip("'").strip('"')
            os.environ[k] = val

load_env('.env')
load_env('.env.local')

# 2. Imports with guards
try:
    try:
        import docx
    except ImportError:
        print("MISSING: python-docx not installed")
    
    from app.services.extraction.local import LocalTextExtractor
    from app.services.analysis.gemini_client import GeminiClient
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

# 3. Main Logic
async def main():
    print("--- Starting Reproduction Script ---")
    
    upload_dir = Path("uploads/resumes")
    if not upload_dir.exists():
        print(f"Directory not found: {upload_dir.absolute()}")
        return

    # Look for ALL supported types
    extensions = [".pdf", ".docx", ".md", ".txt"]
    files = []
    for ext in extensions:
        files.extend(list(upload_dir.rglob(f"*{ext}")))
    
    if not files:
        print("No resumes found (checked: .pdf, .docx, .md, .txt)")
        return
        
    # Sort by recent
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    target_file = files[0]
    print(f"Testing with most recent file ({target_file.suffix}): {target_file}")
    
    # Extract
    print("\n--- EXTRACTING TEXT ---")
    extractor = LocalTextExtractor()
    try:
        text = await extractor.extract_text(target_file)
        print(f"Extraction result length: {len(text)}")
        if len(text) < 100:
            print(f"WARNING: Text is very short: '{text}'")
        else:
            print(f"Text preview: {text[:200]}...")
    except Exception as e:
        print(f"EXTRACTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return

    # Analyze
    print("\n--- ANALYZING WITH GEMINI ---")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set!")
        return
    print(f"API Key found: {api_key[:5]}...")

    client = GeminiClient()
    try:
        result = await client.analyze_resume(text)
        print("\n--- ANALYSIS RESULT ---")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\nANALYSIS FAILED: {e}")
        import google.generativeai as genai
        try:
            print("Listing available models:")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f"- {m.name}")
        except Exception as list_err:
            print(f"Failed to list models: {list_err}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
