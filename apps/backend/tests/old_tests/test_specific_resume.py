import sys
import os
import asyncio
import logging
from pathlib import Path

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

from app.services.extraction.local import LocalTextExtractor
from app.services.analysis.openai_client import OpenAIClient

async def main():
    if len(sys.argv) < 2:
        print("Usage: py test_specific_resume.py <path_to_pdf>")
        return

    file_path = Path(sys.argv[1])
    print(f"Testing file: {file_path}")
    
    if not file_path.exists():
        print("File not found!")
        return

    # 1. Extraction
    print("\n--- EXTRACTING TEXT ---")
    extractor = LocalTextExtractor()
    try:
        text = await extractor.extract_text(file_path)
        print(f"Extraction successful. Length: {len(text)} chars")
        print(f"Preview: {text[:200]}...")
    except Exception as e:
        print(f"EXTRACTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return

    # 2. Analysis
    print("\n--- ANALYZING WITH OPENAI ---")
    client = OpenAIClient()
    if not client.client:
        print("OpenAI Client failed to init")
        return

    try:
        result = await client.analyze_resume(text)
        import json
        print("\n--- RESULT ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("\nSUCCESS!")
    except Exception as e:
        print(f"\nANALYSIS FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
