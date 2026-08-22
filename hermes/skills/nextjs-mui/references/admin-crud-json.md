# Admin CRUD with JSON Persistence

> Append-only pattern for small-project admin backends using Next.js API routes + flat JSON files.
> This user prefers JSON-file storage over databases (similar to their Mercado Livre client system).

## Data Layer

Store data as JSON arrays in `src/data/`:

```
src/data/
├── usuarios.json       ← users (with admin flag)
├── produtos.json       ← products
└── categorias.json     ← categories
```

Each file is a JSON array. A unique `id` field serves as primary key.

## Lib Helper Pattern

Create a dedicated lib file for each domain:

```ts
// src/lib/produtos-admin.ts
import { readFileSync, writeFileSync, existsSync } from "fs";
import path from "path";

const DATA_PATH = path.join(process.cwd(), "src/data/produtos.json");

export function lerTodos(): Item[] {
  if (!existsSync(DATA_PATH)) return [];
  return JSON.parse(readFileSync(DATA_PATH, "utf-8"));
}

export function salvarTodos(items: Item[]) {
  writeFileSync(DATA_PATH, JSON.stringify(items, null, 2));
}

export function proximoId(items: Item[]): number {
  if (items.length === 0) return 1;
  return Math.max(...items.map((i) => i.id)) + 1;
}
```

## API Route Pattern (CRUD)

### List + Create (`route.ts`)

```ts
// src/app/api/admin/produtos/route.ts
export async function GET() {
  return NextResponse.json(lerTodos());
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const items = lerTodos();
  const novo = { id: proximoId(items), ...body, criadoEm: new Date().toISOString() };
  salvarTodos([...items, novo]);
  return NextResponse.json(novo, { status: 201 });
}
```

### Single item Get + Update + Delete (`[id]/route.ts`)

```ts
// src/app/api/admin/produtos/[id]/route.ts
export async function GET(req, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const item = lerTodos().find((i) => i.id === Number(id));
  if (!item) return NextResponse.json({ error: "Não encontrado" }, { status: 404 });
  return NextResponse.json(item);
}

export async function PUT(req, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const body = await req.json();
  const items = lerTodos();
  const idx = items.findIndex((i) => i.id === Number(id));
  if (idx === -1) return NextResponse.json({ error: "Não encontrado" }, { status: 404 });
  items[idx] = { ...items[idx], ...body };
  salvarTodos(items);
  return NextResponse.json(items[idx]);
}

export async function DELETE(req, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let items = lerTodos();
  const idx = items.findIndex((i) => i.id === Number(id));
  if (idx === -1) return NextResponse.json({ error: "Não encontrado" }, { status: 404 });
  items.splice(idx, 1);
  salvarTodos(items);
  return NextResponse.json({ message: "Excluído" });
}
```

## Admin Page Pattern

### List page with table
```tsx
// Full-width table with search, action buttons, and status chips
// Each row: ID | Name | Price | Category | Stock | Status | Actions (View/Edit/Delete)
// Actions: Visibility icon (view on site), Edit icon (edit page), Delete icon (confirm modal)
// Delete modal: confirmation dialog, calls DELETE API, refreshes list
```

### Create page
```tsx
// Form with breadcrumb navigation
// POST to API on submit → success message → redirect to list
// Validation on required fields before submit
```

### Edit page
```tsx
// Same form as create, but pre-filled from `useEffect` fetch by ID
// PUT to API on submit → success message → redirect to list
// Include active/inactive toggle (Switch component) for soft-delete pattern
```

## Auth + Role Guard

Every admin page checks session on mount:

```tsx
const { data: session, status } = useSession();

if (status === "unauthenticated" || (status === "authenticated" && !session?.user?.admin)) {
  // Redirect to /admin/login
}
```

## Users JSON Structure

```json
[
  {
    "nome": "Admin",
    "email": "admin@carcrew.com.br",
    "senha": "admin1234",
    "admin": true,
    "criadoEm": "2026-05-25T00:00:00.000Z"
  }
]
```

First registered user is auto-admin. The CredentialsProvider in `auth.ts` reads from this JSON file to validate login.

## Pitfalls

- **File path resolution:** `process.cwd()` resolves to the project root, not `src/`. Always join `path.join(process.cwd(), "src/data/...")`.
- **Race conditions:** JSON file CRUD is NOT safe for concurrent writes. For single-user admin panels it's fine; for production multi-user, use SQLite.
- **No validation on writes:** The API routes don't validate types deeply. Server-side validation should be added for production use.
- **`params` is a Promise:** In Next.js 16 App Router, route handler params must be awaited: `const { id } = await params;`
