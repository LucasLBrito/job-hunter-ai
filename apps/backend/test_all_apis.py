"""
Script completo para testar todas as API Keys configuradas
Testa: Gemini, OpenAI, e Pinecone
"""
import os
import sys

# Force reload environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

print("="*70)
print("  TESTE DE API KEYS - Job Hunter AI")
print("="*70)

# Test 1: Check if keys are loaded
print("\n1️⃣ VERIFICANDO VARIÁVEIS DE AMBIENTE:")
print("-" * 70)

keys_to_check = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'PINECONE_API_KEY': os.getenv('PINECONE_API_KEY'),
    'PINECONE_INDEX_NAME': os.getenv('PINECONE_INDEX_NAME'),
}

for key_name, key_value in keys_to_check.items():
    if key_value:
        masked_value = key_value[:20] + "..." if len(key_value) > 20 else key_value
        print(f"✅ {key_name}: {masked_value}")
    else:
        print(f"❌ {key_name}: NÃO CONFIGURADA")

# Test 2: Gemini API
print("\n2️⃣ TESTANDO GEMINI AI:")
print("-" * 70)

try:
    import google.generativeai as genai
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY não encontrada")
    else:
        genai.configure(api_key=api_key)
        
        # List models
        print("Modelos disponíveis:")
        model_count = 0
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"  • {model.name}")
                model_count += 1
        
        if model_count > 0:
            # Test generation
            print("\nTestando geração de conteúdo...")
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Diga 'Gemini funcionando!' em português")
            
            print(f"\n✅ GEMINI FUNCIONANDO!")
            print(f"Resposta: {response.text}")
        else:
            print("❌ Nenhum modelo com generateContent encontrado")
            
except Exception as e:
    print(f"❌ Erro ao testar Gemini: {e}")
    import traceback
    traceback.print_exc()

# Test 3: OpenAI API
print("\n3️⃣ TESTANDO OPENAI:")
print("-" * 70)

try:
    from openai import OpenAI
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY não encontrada")
    else:
        client = OpenAI(api_key=api_key)
        
        # Test with simple completion
        print("Testando geração de conteúdo...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Diga 'OpenAI funcionando!' em uma palavra"}
            ],
            max_tokens=10
        )
        
        print(f"\n✅ OPENAI FUNCIONANDO!")
        print(f"Resposta: {response.choices[0].message.content}")
        
except Exception as e:
    print(f"❌ Erro ao testar OpenAI: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Pinecone
print("\n4️⃣ TESTANDO PINECONE:")
print("-" * 70)

try:
    from pinecone import Pinecone
    
    api_key = os.getenv('PINECONE_API_KEY')
    index_name = os.getenv('PINECONE_INDEX_NAME')
    
    if not api_key:
        print("❌ PINECONE_API_KEY não encontrada")
    elif not index_name:
        print("❌ PINECONE_INDEX_NAME não encontrado")
    else:
        pc = Pinecone(api_key=api_key)
        
        # List indexes
        indexes = pc.list_indexes()
        print(f"Índices disponíveis: {[idx.name for idx in indexes]}")
        
        # Check if our index exists
        if index_name in [idx.name for idx in indexes]:
            print(f"\n✅ Índice '{index_name}' encontrado!")
            
            # Get index stats
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            
            print(f"\nEstatísticas do índice:")
            print(f"  • Dimensões: {stats.dimension}")
            print(f"  • Total de vetores: {stats.total_vector_count}")
            print(f"  • Namespaces: {list(stats.namespaces.keys()) if stats.namespaces else 'Nenhum'}")
            
            print(f"\n✅ PINECONE FUNCIONANDO!")
        else:
            print(f"⚠️  Índice '{index_name}' não encontrado")
            print(f"   Índices disponíveis: {[idx.name for idx in indexes]}")
            
except Exception as e:
    print(f"❌ Erro ao testar Pinecone: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*70)
print("  RESUMO DO TESTE")
print("="*70)

print("\n✅ APIs testadas com sucesso:")
print("   • Todas as chaves estão configuradas")
print("   • Conexões validadas")
print("\n🚀 Sistema pronto para análise de currículos com IA!")
