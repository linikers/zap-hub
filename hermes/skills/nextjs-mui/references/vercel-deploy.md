# Vercel Deployment — Next.js Monorepo & Subdirectory (absorbed from vercel-monorepo-deploy skill)

## When to use which approach

| Scenario | Best approach |
|----------|--------------|
| **Simple**: Next.js app in a subdirectory, no root package.json | Dashboard Root Directory |
| **Monorepo**: root has backend dependencies (Hardhat, etc.) | `vercel-build` script |
| **Code-as-config**: need rootDirectory tracked in Git | `vercel.json` (check plan support) |

## Solution: vercel-build Script (Recommended for monorepos)

```json
{
  "scripts": {
    "vercel-build": "cd frontend && npm install && npm run build"
  }
}
```

Vercel always runs `vercel-build` if present, regardless of framework detection.

## Solution: Dashboard Root Directory (Recommended for simple cases)

1. **Connect Git** first (Settings > Git > Connect Git Repository)
2. **Set Root Directory** (Settings > General > Build & Development Settings)
3. **Trigger a deployment** (Deployments tab > Redeploy)

## Build Dependencies

### Tailwind CSS v4
`@tailwindcss/postcss` and `tailwindcss` MUST be in **dependencies**, not devDependencies:
```json
{
  "dependencies": {
    "@tailwindcss/postcss": "^4",
    "tailwindcss": "^4"
  }
}
```

### TypeScript Types
Use `--include=dev` in build command:
```json
{
  "scripts": {
    "vercel-build": "cd frontend && npm install --include=dev && npm run build"
  }
}
```

## Troubleshooting

### Merge not triggering deploy
**Cause:** Vercel GitHub App integration silently disconnected.

**Fix (two-step — BOTH needed):**
1. Dashboard: Settings > Git > reconnect repo
2. GitHub: https://github.com/apps/vercel → Install/Configure → select repo

```bash
# Verify
gh api repos/OWNER/REPO/commits/HEAD/check-runs --jq '.check_runs[] | select(.app.name | contains("Vercel"))'
```

### "No Next.js version detected"
Almost always means Root Directory is wrong, NOT that Next.js is missing. Set Root Directory in Dashboard.

### Build succeeds but routes return 404
Check `next.config.ts` for `basePath` or `distDir` conflicts.

### Cannot find module '@tailwindcss/postcss'
Move from devDependencies to dependencies.

### Root Directory field not visible
**Order of operations:** connect Git repo first, THEN the field appears.

## Deploy Hooks (workaround when GitHub integration broken)

```bash
# User sets up hook in Vercel Dashboard > Settings > Git > Deploy Hooks
# Agent triggers:
curl -X POST "https://api.vercel.com/v1/integrations/deploy/prj_xxx/yyy"
```

## Environment Variables

| File | Prefix | Purpose |
|------|--------|---------|
| Root `.env` | None | Hardhat deployment |
| `frontend/.env.local` | `NEXT_PUBLIC_` | Next.js runtime |

## Case Sensitivity
Windows is case-insensitive; Vercel (Linux) is case-sensitive. Use exact file casing in imports.

## Vercel serverless = read-only filesystem
`writeFileSync` / `fs.writeFile` throws in serverless functions. Always wrap in try/catch.
