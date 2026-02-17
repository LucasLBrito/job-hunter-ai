"""
Teste direto das API Keys (sem .env)
"""
import os

# Load keys from .env.local or environment
from dotenv import load_dotenv
load_dotenv('.env.local')
load_dotenv('.env')

assert os.getenv('GEMINI_API_KEY'), 'GEMINI_API_KEY not set in .env.local'
assert os.getenv('OPENAI_API_KEY'), 'OPENAI_API_KEY not set in .env.local (optional)'
os.environ.setdefault('PINECONE_INDEX_NAME', 'job-hunter')

print("="*70)
print("  TESTE DE API KEYS")
print("="*70)

# Test Gemini
print("\n🧪 TESTANDO GEMINI AI...")
try:
    import google.generativeai as genai
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    
    # Use the correct model name
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'Gemini working!' in Portuguese")
    
    print(f"✅ GEMINI FUNCIONANDO!")
    print(f"   Resposta: {response.text}")
except Exception as e:
    print(f"❌ Gemini falhou: {e}")

# Test OpenAI
print("\n🧪 TESTANDO OPENAI...")
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content":"Say 'OpenAI working!' in Portuguese"}],
        max_tokens=20
    )
    
    print(f"✅ OPENAI FUNCIONANDO!")
    print(f"   Resposta: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ OpenAI falhou: {e}")

# Test Pinecone
print("\n🧪 TESTANDO PINECONE...")
try:
    from pinecone import Pinecone
    pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
    
    indexes = pc.list_indexes()
    print(f"✅ PINECONE FUNCIONANDO!")
    print(f"   Índices: {[idx.name for idx in indexes]}")
    
    if os.environ['PINECONE_INDEX_NAME'] in [idx.name for idx in indexes]:
        index = pc.Index(os.environ['PINECONE_INDEX_NAME'])
        stats = index.describe_index_stats()
        print(f"   Vetores no índice: {stats.total_vector_count}")
except Exception as e:
    print(f"❌ Pinecone falhou: {e}")

print("\n" + "="*70)
print("✅ TESTE COMPLETO!")
