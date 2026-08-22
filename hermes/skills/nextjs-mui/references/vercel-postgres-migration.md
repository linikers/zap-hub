# Vercel Postgres + Prisma 7 Migration Guide

Migrate from JSON-file storage (`src/data/*.json`) to PostgreSQL via Vercel Postgres + **Prisma 7** ORM.

## ⚠️ Prisma 7 Breaking Changes vs Prisma 5/6

| Feature | Prisma 5/6 | Prisma 7 |
|---------|-----------|----------|
| Config | `.env` only | `prisma.config.ts` (TS config file) |
| Schema `url` | Required in datasource | **REMOVED** — moved to `prisma.config.ts` |
| Generator | `@prisma/client` | `prisma-client` |
| Import | `from "@prisma/client"` | `from "@/generated/prisma/client"` (custom path) |
| Constructor | `new PrismaClient()` | Requires `{ adapter }` or `{ accelerateUrl }` |
| Direct Postgres | Via `DATABASE_URL` env | Via `@prisma/adapter-pg` + `pg` pool |
| Output path | Bundled in `@prisma/client` | Generated to `src/generated/prisma/` (configurable) |

## When to Use

- The project has outgrown JSON-file storage (concurrent writes, data integrity, querying)
- You're deploying to Vercel and want a managed Postgres database
- You need proper relations (User→Pedido, Produto→Categoria, etc.)

## Prisma 7 Setup

```bash
npm install prisma @prisma/client
npm install @prisma/adapter-pg pg          # direct Postgres connection
npm install @next-auth/prisma-adapter       # if using NextAuth
npx prisma init
```

`prisma init` creates:
```
prisma/
  schema.prisma        ← models only (no url!)
prisma.config.ts       ← datasource URL + config
.env                   ← POSTGRES_PRISMA_URL goes here
```

## Database Connection

Vercel Postgres auto-generates these env vars when you create a database in the Vercel dashboard (Storage → Create Database → Postgres → Neon):

```
POSTGRES_URL=postgres://default:xxx@ep-xxx.us-east-1.aws.neon.tech/verceldb?sslmode=require
POSTGRES_PRISMA_URL=postgres://default:xxx@ep-xxx.us-east-1.aws.neon.tech/verceldb?sslmode=require&pgbouncer=true
POSTGRES_URL_NON_POOLING=postgres://default:xxx@ep-xxx.us-east-1.aws.neon.tech/verceldb?sslmode=require
POSTGRES_USER=default
POSTGRES_HOST=ep-xxx.us-east-1.aws.neon.tech
POSTGRES_PASSWORD=xxx
POSTGRES_DATABASE=verceldb
```

**Do NOT use a custom prefix** — `POSTGRES_` is correct, no custom prefix needed.

### prisma.config.ts

```typescript
// prisma.config.ts — Prisma 7 configuration
import "dotenv/config";
import { defineConfig } from "prisma/config";

export default defineConfig({
  schema: "prisma/schema.prisma",
  migrations: {
    path: "prisma/migrations",
  },
  datasource: {
    url: process.env["POSTGRES_PRISMA_URL"] || process.env["DATABASE_URL"] || "",
  },
});
```

### schema.prisma (Prisma 7 — no `url` in datasource!)

```prisma
// schema.prisma — models only, no datasource.url!
generator client {
  provider = "prisma-client"     // NOT @prisma/client
  output   = "../src/generated/prisma"  // custom output path
}

datasource db {
  provider = "postgresql"
  // url is configured in prisma.config.ts (NOT here)
}
```

## Complete Schema Models

```prisma
// Prisma 7 models — CarCrew Commerce

model Account {
  id                String  @id @default(cuid())
  userId            String  @map("user_id")
  type              String
  provider          String
  providerAccountId String  @map("provider_account_id")
  refresh_token     String? @db.Text
  access_token      String? @db.Text
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String? @db.Text
  session_state     String?
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
  @@unique([provider, providerAccountId])
  @@map("accounts")
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique @map("session_token")
  userId       String   @map("user_id")
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  @@map("sessions")
}

model VerificationToken {
  identifier String
  token      String   @unique
  expires    DateTime
  @@unique([identifier, token])
  @@map("verification_tokens")
}

model User {
  id            String    @id @default(cuid())
  name          String?
  email         String?   @unique
  emailVerified DateTime? @map("email_verified")
  image         String?
  senha         String?                    // Credentials local
  admin         Boolean   @default(false)
  criadoEm      DateTime  @default(now()) @map("criado_em")
  accounts      Account[]
  sessions      Session[]
  pedidos       Pedido[]
  @@map("users")
}

model Categoria {
  id        Int      @id @default(autoincrement())
  slug      String   @unique
  nome      String
  icone     String   @default("🔧")
  descricao String?
  ordem     Int      @default(0)
  produtos  Produto[]
  @@map("categorias")
}

model Produto {
  id           Int       @id @default(autoincrement())
  nome         String
  descricao    String?
  preco        Float
  imgUrl       String?
  categorySlug String    @map("category_slug")
  parcelamento Int       @default(1)
  estoque      Int       @default(0)
  veiculos     String[]
  ativo        Boolean   @default(true)
  criadoEm     DateTime  @default(now()) @map("criado_em")
  categoria    Categoria @relation(fields: [categorySlug], references: [slug])
  @@map("produtos")
}

model Banner {
  id         Int      @id @default(autoincrement())
  titulo     String
  subtitulo  String?
  imgDesktop String?
  imgMobile  String?
  link       String?
  corFundo   String   @default("#1A1A1A") @map("cor_fundo")
  corTexto   String   @default("#ffffff") @map("cor_texto")
  ativo      Boolean  @default(true)
  ordem      Int      @default(0)
  @@map("banners")
}

model Pedido {
  id        String   @id @default(cuid())
  userId    String   @map("user_id")
  items     Json               // Array of { produtoId, nome, preco, quantidade }
  total     Float
  status    String   @default("pendente")
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")
  user      User     @relation(fields: [userId], references: [id])
  @@map("pedidos")
}
```

## Prisma 7 Client Singleton (with Proxy fallback)

In Prisma 7, the constructor requires `{ adapter }` or `{ accelerateUrl }`. For development/build without a database, use a Proxy fallback:

```typescript
// src/lib/prisma.ts — Prisma 7 singleton with dev fallback
import { PrismaClient } from "@/generated/prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";
import { Pool } from "pg";

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

function createPrismaClient(): PrismaClient {
  const url = process.env.POSTGRES_PRISMA_URL;

  if (!url) {
    // Proxy fallback: quebra só na query, não na importação
    // Permite build da aplicação sem banco configurado
    return new Proxy({} as PrismaClient, {
      get(_, prop) {
        return () => {
          throw new Error(
            "POSTGRES_PRISMA_URL não configurada. " +
            "Deploy no Vercel com Postgres para ativar."
          );
        };
      },
    });
  }

  const pool = new Pool({ connectionString: url });
  const adapter = new PrismaPg(pool);
  return new PrismaClient({ adapter });
}

export const prisma = globalForPrisma.prisma ?? createPrismaClient();

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}

export default prisma;
```

## NextAuth + PrismaAdapter (Prisma 7)

```bash
npm install @next-auth/prisma-adapter
```

```typescript
// src/lib/auth.ts
import { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import CredentialsProvider from "next-auth/providers/credentials";
import { PrismaAdapter } from "@next-auth/prisma-adapter";
import prisma from "@/lib/prisma";

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    GoogleProvider({ ... }),
    CredentialsProvider({
      async authorize(credentials) {
        const usuario = await prisma.user.findUnique({
          where: { email: credentials.email },
        });
        if (usuario && usuario.senha === credentials.password) {
          return { id: usuario.id, name: usuario.name, email: usuario.email, admin: usuario.admin };
        }
        return null;
      },
    }),
  ],
  session: { strategy: "jwt" },
  // ... callbacks stay the same
};
```

**Credentials provider still uses JWT** — PrismaAdapter's User table is read/written for credential users, but sessions remain JWT-based (credentials can't use database sessions).

## Seed Script: JSON → Database (Prisma 7 with adapter)

**Important:** In Prisma 7 with a custom `output` path (`../src/generated/prisma` in the schema), `require("@prisma/client")` from a JS seed file will FAIL because the generated client lives at the custom path, not in `.prisma/client/`. You have two options:

### Option A: TypeScript seed with `tsx` (recommended)

```bash
npm install -D tsx   # or use npx tsx
```

Create `prisma/seed.ts`:

```typescript
import { PrismaClient } from "../src/generated/prisma/client.js";
import { PrismaPg } from "@prisma/adapter-pg";
import { Pool } from "pg";
import { readFileSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const DATA_PATH = join(__dirname, "..", "src", "data");

function readJSON(filename: string) {
  const filePath = join(DATA_PATH, filename);
  if (!existsSync(filePath)) return [];
  return JSON.parse(readFileSync(filePath, "utf-8"));
}

async function main() {
  const url = process.env.POSTGRES_PRISMA_URL;
  if (!url) { console.error("POSTGRES_PRISMA_URL não configurada"); process.exit(1); }

  const pool = new Pool({ connectionString: url });
  const adapter = new PrismaPg(pool);
  const prisma = new PrismaClient({ adapter });

  // Categorias
  const categorias = readJSON("categorias.json");
  for (const cat of categorias) {
    await prisma.categoria.upsert({
      where: { slug: cat.slug },
      update: { nome: cat.nome, icone: cat.icone || "🔧" },
      create: { slug: cat.slug, nome: cat.nome, icone: cat.icone || "🔧" },
    });
  }
  console.log(`  ✅ ${categorias.length} categorias`);

  // Produtos
  const produtos = readJSON("produtos.json");
  for (const p of produtos) {
    await prisma.produto.upsert({
      where: { id: p.id },
      update: { nome: p.nome, preco: p.preco, estoque: p.estoque ?? 0 },
      create: {
        id: p.id, nome: p.nome, descricao: p.descricao || null,
        preco: p.preco, imgUrl: p.imgUrl || null,
        categorySlug: p.category, parcelamento: p.parcelamento ?? 1,
        estoque: p.estoque ?? 0, veiculos: p.veiculos || [],
        ativo: p.ativo ?? true, criadoEm: p.criadoEm ? new Date(p.criadoEm) : new Date(),
      },
    });
  }
  console.log(`  ✅ ${produtos.length} produtos`);

  await prisma.$disconnect();
  console.log("🎉 Seed completo!");
}

main().catch(e => { console.error(e); process.exit(1); });
```

Configure in `prisma.config.ts`:

```typescript
export default defineConfig({
  // ...
  migrations: {
    path: "prisma/migrations",
    seed: "tsx prisma/seed.ts",
  },
});
```

Run:

```bash
POSTGRES_PRISMA_URL="postgresql://..." tsx prisma/seed.ts
# or after config:
npx prisma db seed
```

### Option B: JS seed with `.env` file (legacy)

If you prefer CommonJS, ensure `dotenv` loads from `.env` (not `.env.local` — `dotenv/config` only reads `.env` by default) and use a direct import workaround:

```javascript
// prisma/seed.js
// Note: require("@prisma/client") may fail with custom output path.
// Either remove the custom output from schema.prisma temporarily,
// or use tsx (Option A).
```

### `.env` vs `.env.local` for Prisma CLI

`prisma.config.ts` uses `import "dotenv/config"` which loads `.env`, NOT `.env.local`. If your connection string is in `.env.local`, Prisma CLI commands (`db push`, `db seed`) will fail with "Connection url is empty."

**Fix:** Either rename `.env.local` to `.env`, or pass the env var inline:

```bash
POSTGRES_PRISMA_URL="postgresql://..." npx prisma db push
POSTGRES_PRISMA_URL="postgresql://..." npx prisma db seed
```

During Next.js dev/build, `npm run dev` loads both `.env` and `.env.local` — so this only affects Prisma CLI commands, not the running app.

## API Route Update Pattern

Replace JSON read/write with Prisma calls. Examples:

```typescript
// BEFORE (JSON sync):
import { lerProdutos, salvarProdutos } from "@/lib/produtos-admin";
const produtos = lerProdutos();
const produto = produtos.find(p => p.id === id);

// AFTER (Prisma async):
import prisma from "@/lib/prisma";
const produto = await prisma.produto.findUnique({
  where: { id: Number(id) },
  include: { categoria: true }
});
```

### CRUD API Migration

For full CRUD routes, replace the pattern:

**GET (list):**
```typescript
export async function GET() {
  const produtos = await prisma.produto.findMany({
    orderBy: { criadoEm: "desc" },
  });
  return NextResponse.json(produtos);
}
```

**POST (create):**
```typescript
export async function POST(req: NextRequest) {
  const body = await req.json();
  const produto = await prisma.produto.create({
    data: {
      nome: body.nome,
      preco: Number(body.preco),
      categorySlug: body.category,
      // ...
    },
  });
  return NextResponse.json(produto, { status: 201 });
}
```

**PUT (update):**
```typescript
export async function PUT(req: NextRequest, { params }) {
  const { id } = await params;
  const body = await req.json();
  const atualizado = await prisma.produto.update({
    where: { id: Number(id) },
    data: {
      nome: body.nome,
      preco: body.preco !== undefined ? Number(body.preco) : undefined,
      // only set fields that were provided
    },
  });
  return NextResponse.json(atualizado);
}
```

**DELETE:**
```typescript
export async function DELETE(req: NextRequest, { params }) {
  const { id } = await params;
  await prisma.produto.delete({ where: { id: Number(id) } });
  return NextResponse.json({ message: "Excluído" });
}
```

### Stats API with Aggregates

```typescript
export async function GET() {
  const [produtos, totalUsuarios, banners, totalEstoque] = await Promise.all([
    prisma.produto.findMany({ where: { ativo: true } }),
    prisma.user.count(),
    prisma.banner.findMany({ where: { ativo: true } }),
    prisma.produto.aggregate({ _sum: { estoque: true } }),
  ]);

  return NextResponse.json({
    produtos: produtos.length,
    usuarios: totalUsuarios,
    banners: banners.length,
    estoque: totalEstoque._sum.estoque || 0,
    ultimosProdutos: produtos.slice(0, 5).map(p => ({ id: p.id, nome: p.nome, preco: p.preco, estoque: p.estoque })),
  });
}
```

## Admin Lib Migration Pattern

When migrating admin CRUD libs from JSON to Prisma, the interface stays the same but becomes async:

```typescript
// BEFORE (sync JSON):
export function lerProdutos(): ProdutoData[] { /* reads JSON file */ }
export function salvarProdutos(p: ProdutoData[]) { /* writes JSON file */ }
export function proximoId(): number { /* max id + 1 */ }

// AFTER (async Prisma):
export async function lerProdutos(): Promise<ProdutoData[]> {
  const produtos = await prisma.produto.findMany({ orderBy: { criadoEm: "desc" } });
  return produtos.map(p => ({
    id: p.id, nome: p.nome, descricao: p.descricao || "",
    preco: p.preco, imgUrl: p.imgUrl || "/placeholder.svg",
    category: p.categorySlug, parcelamento: p.parcelamento,
    estoque: p.estoque, ativo: p.ativo, criadoEm: p.criadoEm.toISOString(),
  }));
}
export async function salvarProdutos(produtos: ProdutoData[]) {
  for (const p of produtos) { await prisma.produto.upsert({ ... }); }
}
export async function proximoId(): Promise<number> {
  const ultimo = await prisma.produto.findFirst({ orderBy: { id: "desc" }, select: { id: true } });
  return (ultimo?.id || 0) + 1;
}
```

Then update API routes to `await` these functions (they're already `async` handlers).

## PR-Based Migration Workflow

```bash
git checkout -b pr-db-migration
# 1. Install deps (prisma, @prisma/adapter-pg, pg)
# 2. prisma init → configure prisma.config.ts
# 3. Write schema.prisma models
# 4. prisma generate
# 5. Write seed.js
# 6. Create lib/prisma.ts singleton (with Proxy fallback)
# 7. Replace admin libs (*-admin.ts) → Prisma async
# 8. Replace API routes → Prisma
# 9. Replace auth.ts → PrismaAdapter
# 10. npm run build (should pass without DB)
# 11. git commit + PR
```

## Vercel Build: Required `prisma generate` Step

The generated Prisma client (`src/generated/prisma/`) is auto-added to `.gitignore` by `prisma init`. This means it is **NOT committed** to the repository. On Vercel, it must be generated during the build:

```json
// package.json — update the build script
{
  "scripts": {
    "build": "prisma generate && next build",
    //              ^^^^^^^^^^^^^^^^ required for Vercel
  }
}
```

Without this, Vercel's build fails with:
```
Module not found: Can't resolve '@/generated/prisma/client'
```

The `prisma generate` command reads `prisma.config.ts` (which loads `dotenv`) and `prisma/schema.prisma` to produce the client. It does NOT need a database connection — only the schema file. This means it works on Vercel even before Postgres is configured.

### `.gitignore` entries after `prisma init`

```gitignore
# prisma init auto-adds:
/src/generated/prisma
```

This is correct — the generated client should never be committed. Always regenerated on build.

## Env Variables (local dev)

Create `.env` at project root:

```
POSTGRES_PRISMA_URL=postgres://default:xxx@ep-xxx.us-east-1.aws.neon.tech/verceldb?sslmode=require&pgbouncer=true
POSTGRES_URL_NON_POOLING=postgres://default:xxx@ep-xxx.us-east-1.aws.neon.tech/verceldb?sslmode=require
NEXTAUTH_SECRET=your-secret
```

On Vercel, these are auto-injected when you enable Postgres in the dashboard.

## Pitfalls

- **Prisma 7 constructor requires adapter**: `new PrismaClient()` without args is NOT valid in Prisma 7. Must pass `{ adapter }` or `{ accelerateUrl }`.
- **Proxy fallback for build**: Use `new Proxy({} as PrismaClient, ...)` to avoid build-time crash when `POSTGRES_PRISMA_URL` is not set. Only fails at query time.
- **prisma-client generator**: NOT `@prisma/client`. The `output` path (e.g., `../src/generated/prisma`) determines where `PrismaClient` lives.
- **Import path**: Must import from custom output path, e.g., `import { PrismaClient } from "@/generated/prisma/client"`, NOT `from "@prisma/client"`.
- **Vercel Postgres env var names**: They end with `_URL` as the suffix. No custom prefix needed — the default `POSTGRES_` prefix is correct.
- **PrismaAdapter + Credentials**: `@next-auth/prisma-adapter` works with JWT sessions even with CredentialsProvider — the adapter creates the User in the database but sessions remain JWT-based.
- **Connection pooling**: Vercel uses PgBouncer. Use `POSTGRES_PRISMA_URL` (includes `&pgbouncer=true=true`) for Prisma, not the raw `POSTGRES_URL`.
- **Seed idempotency**: Use `upsert` in seed scripts so re-running doesn't duplicate data.
- **Cold starts**: First Prisma query after deploy may be slow (~1s). Normal for serverless Postgres.
- **Free tier limits**: 500MB storage, 60h compute/month. Fine for a single-store e-commerce.
- **Next.js build + Prisma**: During build, Next.js collects page data and may invoke API routes. The Proxy fallback prevents this from crashing. Without the proxy, you need `POSTGRES_PRISMA_URL` set even in CI/build.
- **`@prisma/adapter-pg` + `@types/pg`**: `@types/pg` may not have a default export, causing TS errors on `import pg from "pg"`. Use `require("pg")` in seed scripts or adjust esModuleInterop settings. Next.js build ignores these type-level errors with `skipLibCheck: true`.
