
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Carregar variáveis de ambiente
load_dotenv(encoding="utf-8")

api_key = os.getenv("GEMINI_API_KEY")

print("="*60)
print("🧪 TESTE DE CHAVE GEMINI")
print("="*60)

if not api_key:
    print("❌ GEMINI_API_KEY não encontrada no .env")
    exit(1)

print(f"🔑 Chave encontrada: {api_key[:10]}...{api_key[-5:]}")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    print("\n📨 Enviando prompt de teste...")
    response = model.generate_content("Olá, responda apenas com 'OK' se estiver funcionando.")
    
    print(f"\n✅ Resposta do Gemini: {response.text}")
    print("\n🎉 SUCESSO! A chave está funcionando corretamente.")

except Exception as e:
    print(f"\n❌ ERRO NA CHAMADA DA API:")
    print(f"{str(e)}")
