FROM node:20-alpine AS base

# Dependências para node-gyp e pacotes npm
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Dependências
FROM base AS deps
COPY package.json package-lock.json* ./
RUN npm ci

# Compilação
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Usaremos o `.env.production` no docker-compose e construiremos
RUN npm run build

# Execução em ambiente de produção
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Configura Next.js Standalone
# Importante: defina no next.config.ts `output: 'standalone'`
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
