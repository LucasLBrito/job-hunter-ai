# Guia de Contribuição e Versionamento

## 🌳 Ramos (Branches)

- `main`: Código estável e produção.
- `develop`: Integração de novas funcionalidades.
- `feature/*`: Novas funcionalidades (ex: `feature/auth-endpoints`).
- `fix/*`: Correções de bugs (ex: `fix/login-error`).

## 📝 Padrão de Commits

Usamos o padrão **Conventional Commits**:

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação, ponto e vírgula faltando, etc (sem mudança de código)
- `refactor:` Refatoração de código
- `test:` Adição ou correção de testes
- `chore:` Atualização de build tasks, configs, etc

**Exemplos:**
- `feat(backend): add login endpoint`
- `fix(auth): resolve jwt expiration issue`
- `docs: update setup guide`

## 🚀 Como Enviar Código

1. Crie uma branch: `git checkout -b feature/minha-feature`
2. Faça mudanças e commits.
3. Push para o repositório: `git push origin feature/minha-feature`
4. Abra um Pull Request (PR).

## 🧪 Testes

Antes de enviar, execute os testes:

```bash
cd apps/backend
.\EXECUTAR_TESTES.bat
```
