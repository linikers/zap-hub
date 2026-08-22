# Product Data Fallback Chain (DB → JSON → Mock)

Pattern for serving real product data through API routes when the database isn't configured yet, using a tri-stage fallback chain.

## When to Use

- You shipped with `src/data/produtos.json` as the primary data file but want Prisma as the eventual source of truth
- The app must work on a fresh deploy without a database (no seed data)
- You want admin panel CRUD to write to DB while the public API falls back to JSON until DB is populated
- You're migrating from mock/hardcoded data to a JSON catalog of 30+ real products

## The Fallback Architecture

```
Public API (/api/produtos)
  │
  ├── Stage 1: Prisma DB (try/catch)
  │     └── If DB available → return DB data
  │
  ├── Stage 2: JSON file (fs.readFileSync)
  │     └── If DB empty/fails → read src/data/produtos.json
  │
  └── Stage 3: Mock array (lib/produtos.ts)
        └── If JSON file missing → return minimal fallback
```

## Full Implementation

```typescript
// src/app/api/produtos/route.ts
import { NextResponse } from "next/server";
import prisma from "@/lib/prisma";
import { readFileSync, existsSync } from "fs";
import path from "path";

interface ProdutoJson {
  id: number;
  nome: string;
  descricao: string;
  preco: number;
  imgUrl: string;
  category: string;
  parcelamento: number;
  veiculos?: string[];
}

function carregarProdutosJson(): ProdutoJson[] {
  try {
    const filePath = path.join(process.cwd(), "src/data/produtos.json");
    if (!existsSync(filePath)) return [];
    const todos: ProdutoJson[] = JSON.parse(readFileSync(filePath, "utf-8"));
    // Filtra só os publicados (ativo não é false) para a API pública
    return todos.filter((p) => p.ativo !== false);
  } catch {
    return [];
  }
}

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const id = searchParams.get("id");
  const category = searchParams.get("category");
  const veiculo = searchParams.get("veiculo");
  const search = searchParams.get("search");

  try {
    // Stage 1: Try Prisma
    const where: any = { ativo: true };
    if (id) where.id = Number(id);
    if (category) where.categorySlug = category;
    if (veiculo) where.veiculos = { has: veiculo };
    if (search) {
      where.OR = [
        { nome: { contains: search, mode: "insensitive" } },
        { descricao: { contains: search, mode: "insensitive" } },
      ];
    }

    const dbProdutos = await prisma.produto.findMany({ where, orderBy: { criadoEm: "desc" } });
    const dbData = dbProdutos.map(p => ({
      id: p.id, nome: p.nome, descricao: p.descricao || "",
      preco: p.preco, imgUrl: p.imgUrl || "/placeholder.svg",
      category: p.categorySlug, parcelamento: p.parcelamento, veiculos: p.veiculos,
    }));

    // Stage 2: Load JSON fallback
    const jsonProdutos = carregarProdutosJson();
    let jsonFiltered = [...jsonProdutos];
    if (category) jsonFiltered = jsonFiltered.filter(p => p.category === category);
    if (veiculo) jsonFiltered = jsonFiltered.filter(p => p.veiculos?.includes(veiculo));
    if (search) {
      const s = search.toLowerCase();
      jsonFiltered = jsonFiltered.filter(p =>
        p.nome.toLowerCase().includes(s) || p.descricao.toLowerCase().includes(s)
      );
    }

    // Specific ID lookup
    if (id) {
      if (dbData.length > 0) return NextResponse.json(dbData);
      const found = jsonFiltered.filter(p => p.id === Number(id));
      if (found.length > 0) return NextResponse.json(found);
      return NextResponse.json([]);
    }

    // Merge: DB first, then JSON (no ID duplicates)
    const dbIds = new Set(dbData.map(p => p.id));
    const combined = [...dbData, ...jsonFiltered.filter(p => !dbIds.has(p.id))];
    return NextResponse.json(combined);
  } catch {
    // Stage 3: Prisma not available — return raw JSON
    return NextResponse.json(carregarProdutosJson());
  }
}
```

## Category Expansion During Migration

When replacing mock products with real ones, the categories will likely need to grow:

1. **Update types** (`src/types/index.ts`) — add new `CategoriaSlug` variants
2. **Update data** (`src/data/categorias.json`) — add category records
3. **Update fallback** (`src/lib/categorias.ts`) — keep in sync with data file
4. **Update admin forms** — both `src/app/admin/produtos/novo/page.tsx` and `src/app/admin/produtos/[id]/edit/page.tsx`
5. **Update API default** (`src/app/api/admin/produtos/route.ts`) — change the default category from old to new
6. **Update Prisma schema** — if using Prisma, ensure `categorySlug` enum covers new slugs

Checklist command:
```bash
grep -rn "acessorio-instalacao\|mola-suspensao\|calco-antirruido\|ponta-de-eixo\|bolsa-de-ar" src/ --include="*.ts" --include="*.tsx"
```

## "Sob Consulta" Pricing Display

When product prices are not yet defined (migration in progress), use `preco: 0` in the data source and handle it in the UI:

```tsx
// In ProductCard.tsx or product detail page
const sobConsulta = produto.preco <= 0;

// Display
{sobConsulta ? "Sob Consulta" : `R$ ${produto.preco.toFixed(2)}`}

// Hide parcelamento when not priced
{!sobConsulta && (
  <Typography>ou {parcelas}x de R$ {valorParcela.toFixed(2)} sem juros</Typography>
)}

// WhatsApp link — omit price if "Sob Consulta"
href={`https://wa.me/5544991528386?text=Olá! Tenho interesse em: ${nome}${sobConsulta ? "" : ` (R$ ${preco.toFixed(2)})`}`}
```

## Missing Image Fallback Strategy

When importing product data from an external source (Google Drive, CSV, etc.), some products may lack images. Use a layered approach:

1. **Real images** → download from source, organize in `public/produtos/<category>/`
2. **Placeholder SVGs** → existing SVGs in `public/produtos/` as fallback
3. **Per-category defaults** → map categories to default images

```typescript
const defaultImages: Record<string, string> = {
  compressores: "/produtos/compressors/default.jpg",
  amortecedores: "/produtos/amortecedor1.svg",
  bolsas-de-ar: "/produtos/bolsa-ar1.svg",
  calcos-antirruido: "/produtos/calco1.svg",
  pontas-de-eixo: "/produtos/ponta-eixo1.svg",
  // ...
};

const imgUrl = produto.imgUrl || defaultImages[produto.category] || "/produtos/placeholder.svg";
```

## Pitfalls

- **`fs.readFileSync` only works in server components/API routes** — never in client components. Keep JSON reads in API routes only.
- **Bundle size**: `src/data/produtos.json` with 40+ products is ~15KB. This is bundled in the server, not the client. Acceptable.
- **Race condition**: If admin writes to DB while public API reads JSON, the data diverges. The JSON file is the "bootstrap" source — once DB is populated, delete the JSON fallback.
- **Filter consistency**: Ensure the JSON fallback filtering logic mirrors the Prisma query logic exactly. If they drift, search/filter will behave differently depending on which stage serves the data.
- **Command palette search**: Prisma's `contains` filter uses the DB's case-insensitive collation. JavaScript `.includes()` is case-sensitive by default — use `.toLowerCase()` on both sides in the fallback.
