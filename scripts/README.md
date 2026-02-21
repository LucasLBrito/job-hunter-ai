# ⚙️ Job Hunter AI - Scripts de Automação

Esta pasta contém scripts criados para facilitar a sua vida no dia a dia. Eles instalam coisas e rodam os servidores sem que você precise digitar comandos imensos toda hora.

## O que tem aqui?

### `setup/`
Scripts projetados para a **primeira vez** que você for abrir o projeto no computador. Eles verificam Python, instalam pacotes, criam ambientes virtuais, etc.

### `start/`
Scripts para **iniciar os servidores rapidamente**. Use isso se você não quiser rodar via Docker.
- `start-backend-local.bat`: Abre o servidor FastAPI do Backend (Windows).
- `start-frontend-local.bat`: Abre o frontend Next.js (Windows).
*(Versões `.sh` disponíveis para Mac/Linux).*

### `verification/`
Ferramentas de teste rápido.
- Scripts Python para testar se o banco local foi criado, se uma integração específica está funcionando, etc. 

### `windows/`
Recursos legados que estavam soltos na raiz. Movidos pra cá para manter o repositório limpo.

---

> **Dica Pro**: Se você estiver no Linux ou Mac, sempre lembre de dar permissão de execução aos arquivos `.sh` rodando `chmod +x nomedoscript.sh`.
