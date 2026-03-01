# 🔧 Setup Python - Guia Rápido Windows

## ⚠️ Problema Detectado

O comando `python` não está configurado no PATH do Windows.

## 🔍 Soluções

### Opção 1: Usar `py` (Python Launcher - Recomendado)

O Windows geralmente tem o Python Launcher instalado. Teste:

```bash
py --version
```

Se funcionar, use `py` ao invés de `python` em todos os comandos:

```bash
# Criar venv
py -m venv venv

# Ativar venv
venv\Scripts\activate

# Instalar dependências
py -m pip install -r requirements.txt

# Executar app
py -m uvicorn app.main:app --reload
```

### Opção 2: Instalar Python 3.11+

1. **Baixar Python**: https://www.python.org/downloads/
2. **IMPORTANTE**: Marcar "Add Python to PATH" durante instalação
3. **Reiniciar terminal** após instalação

### Opção 3: Adicionar Python ao PATH Manualmente

1. Encontrar onde Python está instalado:
   - Geralmente: `C:\Users\LUCAS\AppData\Local\Programs\Python\Python311`
   - Ou: `C:\Python311`

2. Adicionar ao PATH:
   - Abrir "Editar variáveis de ambiente do sistema"
   - Clicar em "Variáveis de Ambiente"
   - Em "Variáveis do Sistema", selecionar "Path"
   - Clicar "Editar" → "Novo"
   - Adicionar o caminho do Python
   - Adicionar também: `C:\...\Python311\Scripts`
   - Clicar OK
   - **Reiniciar terminal**

### Opção 4: Usar Docker (Mais Simples!)

Se preferir evitar configuração do Python, use Docker:

```bash
# No diretório raiz do projeto
cd c:\Users\LUCAS\OneDrive\Documentos\Meu Projetos\agents_test\job-hunter-ai

# Verificar se Docker está instalado
docker --version

# Iniciar ambiente de desenvolvimento
docker-compose -f docker/docker-compose.dev.yml up -d

# Ver logs
docker-compose -f docker/docker-compose.dev.yml logs -f backend
```

Ou use o Makefile:

```bash
make dev
make logs-backend
```

O backend estará em: http://localhost:8000

## ✅ Próximos Passos (Depois de Configurar Python)

```bash
# 1. Navegar para backend
cd apps\backend

# 2. Criar venv (use 'py' se 'python' não funcionar)
py -m venv venv

# 3. Ativar venv
venv\Scripts\activate

# 4. Atualizar pip
python -m pip install --upgrade pip

# 5. Instalar dependências
pip install -r requirements.txt

# 6. Criar diretório de dados (caso não exista)
cd ..\..
mkdir data

# 7. Voltar para backend
cd apps\backend

# 8. Iniciar servidor
uvicorn app.main:app --reload
```

## 🎯 Teste Rápido

Após iniciar, teste no navegador:
- http://localhost:8000 (root)
- http://localhost:8000/health (health check)
- http://localhost:8000/docs (Swagger UI)

## 🐛 Resolução de Problemas

### "No module named 'fastapi'"

```bash
# Certifique-se que venv está ativado
venv\Scripts\activate

# Reinstale dependências
pip install -r requirements.txt
```

### "Database error"

```bash
# Crie o diretório data manualmente (na raiz do projeto)
mkdir c:\Users\LUCAS\OneDrive\Documentos\Meu Projetos\agents_test\job-hunter-ai\data
```

### "Port 8000 already in use"

```bash
# Use outra porta
uvicorn app.main:app --reload --port 8001
```

---

**💡 Dica**: Para desenvolvimento rápido, recomendo usar Docker! É mais simples e funciona imediatamente sem configurar Python.
