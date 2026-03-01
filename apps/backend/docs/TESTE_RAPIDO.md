# 🚀 TESTE RÁPIDO - 3 Passos Simples

## 📋 Passo 1: Instalar Dependências Mínimas

```bash
cd c:\Users\LUCAS\OneDrive\Documentos\Meu Projetos\agents_test\job-hunter-ai\apps\backend

# Ativar venv (se já criou)
venv\Scripts\activate

# Instalar versão mínima (compatível com Python 3.14)
pip install -r requirements-minimal.txt
```

## 🚀 Passo 2: Iniciar Servidor

```bash
# Opção 1: Executar diretamente
py main_simple.py

# Opção 2: Via uvicorn
uvicorn main_simple:app --reload
```

## ✅ Passo 3: Testar no Navegador

Aguarde a mensagem:
```
🚀 Starting up Job Hunter AI...
✅ Server initialized successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Então teste:

**1. Endpoint Root**
```
http://localhost:8000
```
Deve retornar:
```json
{
  "message": "🎯 Job Hunter AI API",
  "version": "0.1.0",
  "status": "running",
  "docs": "/docs"
}
```

**2. Health Check**
```
http://localhost:8000/health
```

**3. Test Endpoint**
```
http://localhost:8000/test
```

**4. Swagger UI (Documentação Interativa)**
```
http://localhost:8000/docs
```

## 🎯 O Que Estamos Testando?

✅ FastAPI instalado corretamente  
✅ Servidor inicia sem erros  
✅ Endpoints respondem JSON  
✅ Swagger UI funciona  
✅ Python 3.14 compatível (versão básica)

## 🐛 Se Der Erro

### "ModuleNotFoundError: No module named 'fastapi'"

```bash
# Certifique-se que venv está ativado
venv\Scripts\activate

# Reinstale
pip install -r requirements-minimal.txt
```

### "Address already in use" (Porta 8000 ocupada)

```bash
# Use outra porta
uvicorn main_simple:app --reload --port 8001
```

Então acesse: http://localhost:8001

## ⏭️ Próximo Passo

Depois que confirmar que o servidor básico funciona:
1. Instalar Python 3.11 para versão completa
2. Ou configurar Docker
3. Desenvolver endpoints de autenticação, jobs, etc.

---

**🎉 Objetivo**: Validar que FastAPI funciona no seu ambiente antes de adicionar complexidade!
