# 🐳 Job Hunter AI - Guias do Docker

Esta pasta contém os arquivos de orquestração do **Docker Compose**, usados para rodar todo o ecossistema do Job Hunter AI (Frontend + Backend + Banco de Dados) com apenas um comando.

## Ambientes Recomendados

Oferecemos dois setups dependendo da sua necessidade:

### 1. Ambiente de Desenvolvimento (`docker-compose.dev.yml`)
Recomendado para **rodar o sistema em sua máquina local** enquanto visualiza o frontend e faz requisições pro backend localmente.

Nesse modo:
- O código do backend reflete alterações locais quase em tempo real (hot-reload do Uvicorn).
- O backend não tenta rodar um PostgreSQL pesado; ele usará o SQLite local configurado no backend.

**Como rodar:**
```bash
# A partir da raiz do projeto:
docker-compose -f docker/docker-compose.dev.yml up -d --build
```
> Obs: Garanta que você configurou seus arquivos `.env` em `apps/backend` e `apps/frontend` antes.

### 2. Ambiente de Produção (`docker-compose.prod.yml`)
Recomendado para **implantação na nuvem** ou testes mais pesados.

Nesse modo:
- Não há hot-reload. O código é focado em performance.
- Geralmente acompanha a provisão de um banco de dados real (PostgreSQL).

**Como rodar:**
```bash
docker-compose -f docker/docker-compose.prod.yml up -d --build
```

---

## 🛑 Comandos Úteis

**Ver os logs em tempo real (Para saber se deu erro em alguma IA ou Backend):**
```bash
docker-compose -f docker/docker-compose.dev.yml logs -f
```

**Parar os containers (sem deletar os dados):**
```bash
docker-compose -f docker/docker-compose.dev.yml stop
```

**Derrubar tudo e iniciar do zero:**
```bash
docker-compose -f docker/docker-compose.dev.yml down -v
```
