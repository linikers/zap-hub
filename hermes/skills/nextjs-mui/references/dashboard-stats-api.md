# Dashboard Stats API

## API: `GET /api/admin/stats`

Returns aggregated dashboard data by reading all `src/data/*.json` files.

### Response Shape

```json
{
  "produtos": 9,
  "usuarios": 2,
  "banners": 3,
  "estoque": 175,
  "ultimosProdutos": [
    { "id": 9, "nome": "Mangueira para Suspensão...", "preco": 89.90, "estoque": 25 }
  ],
  "vendasPorMes": [
    { "mes": "Jan", "valor": 12345, "pedidos": 14 },
    { "mes": "Fev", "valor": 9876, "pedidos": 11 }
  ]
}
```

### Implementation

```typescript
import { readFileSync, existsSync } from "fs";
import path from "path";

function lerJson(relativePath: string): any[] {
  try {
    const p = path.join(process.cwd(), "src/data", relativePath);
    if (!existsSync(p)) return [];
    return JSON.parse(readFileSync(p, "utf-8"));
  } catch { return []; }
}

export async function GET() {
  const produtos = lerJson("produtos.json");
  const usuarios = lerJson("usuarios.json");

  // Calculate stats
  const totalEstoque = produtos.reduce((sum, p) => sum + (p.estoque || 0), 0);

  // Latest 5 products sorted by criadoEm
  const ultimos = [...produtos]
    .sort((a, b) => new Date(b.criadoEm || 0).getTime() - new Date(a.criadoEm || 0).getTime())
    .slice(0, 5)
    .map(p => ({ id: p.id, nome: p.nome, preco: p.preco, estoque: p.estoque }));

  // Mock monthly sales (replace with real data when orders exist)
  const meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"];
  const vendasPorMes = meses.map((mes, i) => ({
    mes,
    valor: Math.floor(Math.random() * 15000) + 3000,
    pedidos: Math.floor(Math.random() * 20) + 5,
  }));

  return NextResponse.json({
    produtos: produtos.length,
    usuarios: usuarios.length,
    estoque: totalEstoque,
    ultimosProdutos: ultimos,
    vendasPorMes,
  });
}
```

### Frontend (recharts)

```tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";

<ResponsiveContainer width="100%" height={300}>
  <BarChart data={stats.vendasPorMes}>
    <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
    <XAxis dataKey="mes" stroke="#999" fontSize={13} />
    <YAxis stroke="#999" fontSize={13} />
    <Tooltip />
    <Legend />
    <Bar dataKey="valor" name="Vendas (R$)" fill="#E65100" radius={[4, 4, 0, 0]} />
    <Bar dataKey="pedidos" name="Pedidos" fill="#1A1A1A" radius={[4, 4, 0, 0]} />
  </BarChart>
</ResponsiveContainer>
```

### Pitfalls

- `process.cwd()` works in both dev and Vercel — path resolves from project root
- Random mock data for `vendasPorMes` means the chart changes on every page load. Replace with real data when orders are persisted.
- Stats run on every page load — no caching. Add `export const dynamic = 'force-dynamic'` or implement SWR if performance becomes an issue.
