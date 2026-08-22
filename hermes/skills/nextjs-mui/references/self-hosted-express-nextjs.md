# Self-Hosted Express API + Next.js Dashboard

Pattern for deploying a Node.js Express API and a Next.js dashboard side-by-side on the same server (Docker, VPS, or bare metal). No Vercel, no cloud functions.

For production deployment including Nginx reverse proxy, DNS setup, and systemd persistence, see `monorepo-typescript-setup/references/vps-production-deployment.md`.

## Architecture

```
Server (single host)
├── Express API  (port 3002)
│   ├── REST endpoints (/contatos, /campanhas, /eventos, /whatsapp)
│   ├── JWT auth middleware
│   ├── Background worker (scheduler poller)
│   └── Healthcheck at /health
│
├── Next.js Dashboard (port 3001)
│   ├── App Router pages (login, dashboard, contatos, eventos, whatsapp, campanhas)
│   ├── MUI dark theme
│   └── Proxies API calls via /api/* rewrite
│
├── PostgreSQL (5432)
└── Redis (6379)
```

## Starting the system

```bash
cd /root/hermes-marketing-orchestrator
npm run build

# Start API
DATABASE_URL="postgresql://user:pass@localhost:5432/db" \
PORT=3002 node apps/api/dist/index.js

# Start Dashboard (separate terminal)
cd apps/dashboard
NEXT_PUBLIC_API_URL=http://localhost:3002 npx next start -p 3001
```

## API Proxy (Next.js rewrites)

```javascript
async rewrites() {
  return [
    { source: '/api/:path*', destination: 'http://localhost:3002/:path*' }
  ];
}
```

## JWT Auth

1. POST /auth/login -> JWT token
2. Stored in localStorage
3. Bearer token on all authenticated fetch() calls

## Pitfalls

- **Use terminal(background=true)**, not nohup/disown
- **tsup exports**: require -> .js, import -> .mjs (never .cjs)
- **EADDRINUSE**: fuser -k PORT/tcp before restarting
- **'use client' needed** for localStorage access
- **Worker needs SIGTERM/SIGINT handlers** for graceful shutdown
