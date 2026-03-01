# 📝 Guia Completo de Variáveis de Ambiente

## 🎯 Onde Colocar?

As variáveis de ambiente já estão no arquivo:

**📂 Localização:**
```
job-hunter-ai\apps\backend\.env.local
```

Esse arquivo **JÁ EXISTE** e **JÁ ESTÁ CONFIGURADO** com valores padrão para teste!

## 🔑 Variáveis Essenciais (Já Configuradas)

### ✅ Para Teste Básico (Já Funcionam!)

Estas já estão no `.env.local` e permitem rodar o servidor:

```bash
# App Settings
APP_NAME=Job Hunter AI
VERSION=0.1.0
ENV=development
DEBUG=true

# Security (para teste - MUDAR em produção)
SECRET_KEY=dev-secret-key-CHANGE-THIS-IN-PRODUCTION-min-256-bits-long

# Database (SQLite local)
DATABASE_URL=sqlite+aiosqlite:///./data/database.db
```

### ⚠️ Para Funcionalidades Completas (Adicionar Depois)

Estas você precisa adicionar suas próprias chaves de API:

#### 1. **LLM (Análise de Vagas com IA)**

**Opção A - OpenAI:**
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```

**Opção B - Anthropic:**
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
```

#### 2. **Azure Document Intelligence (Análise de Currículo)**
```bash
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://seu-resource.cognitiveservices.azure.com
AZURE_DOCUMENT_INTELLIGENCE_KEY=sua-chave-azure
```

#### 3. **WhatsApp Business API (Notificações)**
```bash
WHATSAPP_API_TOKEN=seu-token-whatsapp
WHATSAPP_PHONE_NUMBER_ID=seu-phone-id
WHATSAPP_BUSINESS_ACCOUNT_ID=seu-account-id
```

## 📝 Como Editar as Variáveis

### Método 1: Editar no VS Code/Editor

1. Abrir o arquivo:
```
job-hunter-ai\apps\backend\.env.local
```

2. Encontrar a linha que quer mudar, exemplo:
```bash
OPENAI_API_KEY=your-openai-key-here
```

3. Substituir pelo valor real:
```bash
OPENAI_API_KEY=sk-proj-ABC123XYZ...
```

4. Salvar (Ctrl+S)

### Método 2: Via Terminal

```powershell
# Abrir o arquivo no notepad
notepad "c:\Users\LUCAS\OneDrive\Documentos\Meu Projetos\agents_test\job-hunter-ai\apps\backend\.env.local"
```

## 🚀 Para Testar AGORA (Sem API Keys)

**Você NÃO precisa configurar API keys para o teste básico!**

O servidor vai iniciar e funcionar com os endpoints básicos:
- ✅ `/` (root)
- ✅ `/health` (health check)
- ✅ `/test` (test endpoint)
- ✅ `/docs` (Swagger UI)

As funcionalidades de IA (análise de vagas, currículo) precisam das API keys, mas o servidor roda sem elas!

## 🔧 Como Executar o Teste (Comando Correto)

**IMPORTANTE**: Use aspas por causa dos espaços no caminho!

```powershell
# PowerShell - Use aspas
cd "c:\Users\LUCAS\OneDrive\Documentos\Meu Projetos\agents_test\job-hunter-ai\apps\backend"

# Executar o script de teste
.\RODAR_TESTE.bat
```

Ou execute diretamente clicando duplo em:
```
job-hunter-ai\apps\backend\RODAR_TESTE.bat
```

## 📋 Checklist Rápido

- [x] Arquivo `.env.local` já existe
- [x] Variáveis básicas já configuradas
- [ ] (Opcional) Adicionar API keys para IA
- [ ] Rodar `RODAR_TESTE.bat`
- [ ] Testar http://localhost:8000

## 🎯 Variáveis Mínimas para Cada Funcionalidade

| Funcionalidade | Variáveis Necessárias | Obrigatório? |
|----------------|----------------------|--------------|
| Servidor básico | SECRET_KEY | ✅ Sim (já tem) |
| Endpoints básicos | Nenhuma extra | ✅ Já funciona |
| Análise de vagas com IA | OPENAI_API_KEY ou ANTHROPIC_API_KEY | ❌ Opcional |
| Análise de currículo | AZURE_DOCUMENT_INTELLIGENCE_* | ❌ Opcional |
| Notificações WhatsApp | WHATSAPP_* | ❌ Opcional |

## 🆘 Perguntas Frequentes

**Q: Preciso de todas as variáveis para testar?**
A: Não! O servidor roda com as variáveis básicas que já estão configuradas.

**Q: Onde conseguir as API keys?**
A: 
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Azure: https://portal.azure.com/

**Q: O arquivo .env.local é seguro?**
A: Para desenvolvimento local, sim. NÃO faça commit dele no git (já está no `.gitignore`).

**Q: Como usar o comando cd com espaços?**
A: Use aspas: `cd "c:\Users\LUCAS\OneDrive\Documentos\Meu Projetos\..."`

---

**🎉 Para começar**: Apenas execute `RODAR_TESTE.bat` - as variáveis básicas já estão prontas!
