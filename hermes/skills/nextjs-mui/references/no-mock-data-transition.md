# Static → API-Driven Component Transition

Pattern for removing hardcoded/mocked data from client components and replacing with API fetches. Makes the app ready for real data entry after deployment, without seed data.

## When to Use

- You shipped with hardcoded arrays (e.g., `const produtos = [...]`) but now want real data from API
- The deploy needs to work **without seed data** — fresh database shows empty states
- You want the admin panel to be the sole data entry point after deploy

## The Problem

```tsx
// ❌ BEFORE: page imports hardcoded data directly
"use client";
import { produtos } from "@/lib/produtos";   // static array
import { categorias } from "@/lib/categorias"; // static array

export default function Home() {
  return produtos.map(p => <ProductCard produto={p} />);
}
```

Problems with this approach:
- Static data is baked into the bundle — never changes without a redeploy
- Admin CRUD writes to a different data source (JSON files → database)
- Cannot show a "no products yet" state to guide the user

## The Solution

### Step 1: Create Public API Routes

```typescript
// src/app/api/produtos/route.ts — public API
import { NextResponse } from "next/server";
import prisma from "@/lib/prisma";

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const where: any = { ativo: true };

    if (searchParams.get("id")) where.id = Number(searchParams.get("id"));
    if (searchParams.get("category")) where.categorySlug = searchParams.get("category");
    if (searchParams.get("search")) {
      where.OR = [
        { nome: { contains: searchParams.get("search"), mode: "insensitive" } },
        { descricao: { contains: searchParams.get("search"), mode: "insensitive" } },
      ];
    }

    const produtos = await prisma.produto.findMany({ where, orderBy: { criadoEm: "desc" } });

    return NextResponse.json(produtos.map(p => ({
      id: p.id, nome: p.nome, descricao: p.descricao,
      preco: p.preco, imgUrl: p.imgUrl || "/placeholder.svg",
      category: p.categorySlug, parcelamento: p.parcelamento, veiculos: p.veiculos,
    })));
  } catch {
    return NextResponse.json([]);  // no database → empty
  }
}
```

### Step 2: Update Components to Fetch

```tsx
// ✅ AFTER: fetch from API on mount
"use client";
import { useState, useEffect } from "react";
import { CircularProgress } from "@mui/material";

interface ProdutoData {
  id: number; nome: string; descricao: string;
  preco: number; imgUrl: string; category: string;
  parcelamento: number; veiculos?: string[];
}

export default function Home() {
  const [produtos, setProdutos] = useState<ProdutoData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/produtos")
      .then(r => r.json())
      .then(setProdutos)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress sx={{ color: "#E65100" }} />;

  if (produtos.length === 0) {
    return (
      <Box sx={{ textAlign: "center", py: 8, color: "#999" }}>
        <Typography variant="h6">Nenhum produto cadastrado</Typography>
        <Typography variant="body2">Acesse o painel admin para cadastrar</Typography>
      </Box>
    );
  }

  return produtos.map(p => <ProductCard produto={p as any} />);
}
```

### Step 3: Handle the Proxy Fallback

The API routes use try/catch returning `[]` when the database isn't configured. The Prisma client itself needs a proxy fallback to avoid crashing at import time (see `references/vercel-postgres-migration.md` for the full Prisma singleton implementation).

## Component Migration Checklist

| Component | Old Import | New Fetch | State |
|-----------|-----------|-----------|-------|
| Home page | `import { produtos } from "@/lib/produtos"` | `fetch("/api/produtos")` | loading + empty + data |
| Product detail | `import { produtos } from "@/lib/produtos"` | `fetch("/api/produtos?id=X")` | loading + notFound + data |
| Header nav | `import { categorias } from "@/lib/categorias"` | `fetch("/api/categorias")` | empty until fetched |
| Any category list | `import { categorias } from "@/lib/categorias"` | `fetch("/api/categorias")` | empty until fetched |

## Empty States

Every API-driven page needs these three states:

```tsx
if (loading) return <Spinner />;       // 1. Loading
if (empty) return <EmptyState />;       // 2. No data (fresh DB)
return <DataView />;                     // 3. Normal render
```

The empty state should guide the user: "Nenhum produto cadastrado — acesse o painel admin para cadastrar seus produtos."

## Pitfalls

- **`as any` cast**: The API returns `category: string` but your `Produto` type expects `category: CategoriaSlug`. Use `as any` when passing to ProductCard, or widen the type. A proper solution would unify the types.
- **Bundle size**: Removing static arrays from lib files slightly reduces JS bundle. The gain is marginal but real.
- **API route 404 without DB**: The try/catch returning `[]` means the API always returns 200 with `[]`, never 500. Keeps client-side error handling simple.
