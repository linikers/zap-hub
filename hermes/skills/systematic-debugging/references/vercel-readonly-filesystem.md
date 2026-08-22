# Vercel Serverless — Read-Only Filesystem

## Context

Vercel serverless functions (AWS Lambda) have a **read-only filesystem** at runtime. Any attempt to write to disk with `writeFileSync`, `writeFile`, or file-based persistence throws an `EROFS` or `ENOENT` error silently in production while working perfectly fine locally.

## Symptom

- API endpoint returns `500 Internal Server Error` in production
- Works fine in `npm run dev` locally
- Generic `"Erro interno"` or `"Internal Server Error"` in the response
- The process.env or next.config shows no path issues

## Root Cause

Filesystem writes in serverless environments fail because the execution environment is ephemeral and read-only. Code that uses `writeFileSync` for persistence (e.g., saving purchases to a JSON file) works on local dev but crashes in production.

## The Fix

### Option 1: Try/Catch (Quick Fix)

Wrap file writes in a try/catch so they don't crash the happy path:

```typescript
try {
  const purchases = existsSync(PURCHASES_PATH)
    ? JSON.parse(readFileSync(PURCHASES_PATH, "utf-8"))
    : [];
  purchases.push({ /* ... */ });
  writeFileSync(PURCHASES_PATH, JSON.stringify(purchases, null, 2));
} catch (e) {
  console.warn("[Pix] Nao foi possivel salvar purchase localmente (Vercel?):", e);
}
```

This is appropriate when:
- The file write is **non-essential** to the current operation (e.g., logging, caching)
- You can still return a successful response without the file write
- The data will be persisted later via webhook or manual confirmation

### Option 2: Use a Proper Database (Production Fix)

For real persistence, use one of:
- **Vercel KV** (Redis) — best if already in the Vercel account
- **Supabase** — PostgreSQL with free tier
- **Turso** — edge SQLite
- **Firebase/Firestore** — if already in the stack
- **MongoDB Atlas** — if using MERN stack

### Option 3: Vercel Blob

For file storage specifically, use Vercel Blob:
```typescript
import { put } from '@vercel/blob';
const { url } = await put('filename.json', JSON.stringify(data), { access: 'public' });
```

## When Each Option Fits

| Scenario | Option | Why |
|----------|--------|-----|
| Manual-confirmation flow (Pix) | 1 (try/catch) | User confirms payment manually anyway |
| Critical data that must persist | 2 (database) | File writes are unreliable in serverless |
| User uploads/images | 3 (Vercel Blob) | Purpose-built for file storage |

## Real-World Example: Pix Payment in erc20TokenLab

The course checkout was saving Pix purchases to `src/data/purchases.json`. On Vercel, `writeFileSync` crashed and the error was caught by a generic `catch` block that returned `"Erro interno"` — so the user saw an error instead of the Pix QR code.

**Fix:** Wrapped the file write in try/catch. The Pix QR code + payload are generated before the file write attempt, so even if the save fails, the user still gets the QR code and can pay. The purchase is saved when they send the receipt manually.
