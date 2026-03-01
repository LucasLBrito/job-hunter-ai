
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
try:
    load_dotenv(encoding="utf-8")
except UnicodeDecodeError:
    # Try with utf-16 if utf-8 fails, common on Windows powershell redirects
    load_dotenv(encoding="utf-16")
except Exception as e:
    print(f"Warning: could not load .env: {e}")

from app.services.analysis.gemini_client import GeminiClient
from app.services.analysis.openai_client import OpenAIClient

async def test_ai_services():
    print("="*60)
    print("🧪 TESTE DE SERVIÇOS DE IA (GEMINI & OPENAI)")
    print("="*60)
    
    test_text = """
    Lucas Silva
    Engenheiro de Software Sênior
    Experiência:
    - 5 anos com Python, Django e FastAPI
    - 3 anos com React e TypeScript
    - Especialista em Arquitetura de Microsserviços
    """
    
    # 1. Test Gemini
    print("\n1️⃣ Testando Gemini Client...")
    gemini = GeminiClient()
    if gemini.model:
        try:
            print(f"   Modelo Gemini ativo: {gemini.model_name}")
            print("   Enviando teste...")
            result = await gemini.analyze_resume(test_text)
            print("   ✅ Sucesso no Gemini!")
            print(f"   Dados extraídos: {result.keys()}")
        except Exception as e:
            print(f"   ❌ Erro no Gemini: {e}")
    else:
        print("   ⚠️ Gemini não configurado ou falhou na inicialização.")

    # 2. Test OpenAI
    print("\n2️⃣ Testando OpenAI Client...")
    openai = OpenAIClient()
    if openai.client:
        try:
            print(f"   Modelo OpenAI ativo: {openai.model_name}")
            print("   Enviando teste...")
            result = await openai.analyze_resume(test_text)
            print("   ✅ Sucesso no OpenAI!")
            print(f"   Dados extraídos: {result.keys()}")
        except Exception as e:
            print(f"   ❌ Erro no OpenAI: {e}")
    else:
        print("   ⚠️ OpenAI não configurado.")

if __name__ == "__main__":
    try:
        asyncio.run(test_ai_services())
    except KeyboardInterrupt:
        print("\nTeste interrompido.")
