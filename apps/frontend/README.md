# 🎨 Job Hunter AI - Frontend

Interface moderna construída com **Next.js 14 (App Router)** e **React**.

## 🛠️ Stack

- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Components**: ShadcnUI
- **State**: React Query (TanStack Query) + Zustand
- **Icons**: Lucide React

## 🚀 Setup Local

### 1. Dependências

```bash
cd apps/frontend
npm install
```

### 2. Variáveis de Ambiente

Copie o `.env.example`:

```bash
cp .env.example .env.local
```

### 3. Rodar Desenvolvimento

```bash
npm run dev
```
Acesse: http://localhost:3000

## 📦 Build Produção

```bash
npm run build
npm start
```

## 🏗️ Estrutura

- `app/`: Páginas e Layouts (App Router)
- `components/`: Componentes reutilizáveis
- `lib/`: Utilitários e configurações
- `hooks/`: Custom React Hooks
- `public/`: Assets estáticos
