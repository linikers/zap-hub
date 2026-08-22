# Next.js ML Dashboard Integration

Pattern for displaying ML campaign/product data in a Next.js portfolio dashboard.

## Architecture

```
ML API (api.mercadolibre.com)
    ↓ fetch via curl/Python
/root/mercadoLivre/dados.json (cache local)
    ↓ read from filesystem
Next.js API Route (/api/ml/campanhas)
    ↓ transform & respond
Next.js Page (/admin/ml)
```

## Step 1: Import Products from ML API

ML limits `?ids=` parameter to **20 items per request**. Fetch in batches:

```python
import json, urllib.request

# 1. Get all item IDs for the seller
url = 'https://api.mercadolibre.com/users/{SELLER_ID}/items/search?search_type=scan&limit=50'
# Response: { "results": ["MLB...", "MLB...", ...], "paging": { "total": N } }

# 2. Fetch details in batches of 20
all_ids = response['results']
all_products = []

for i in range(0, len(all_ids), 20):
    batch = all_ids[i:i+20]
    ids_str = ','.join(batch)
    url = f'https://api.mercadolibre.com/items?ids={ids_str}'
    # Response: [{ "body": { "id", "title", "price", "sold_quantity", ... } }, ...]
    
    for item in data:
        body = item.get('body', {})
        if body.get('id'):
            all_products.append({
                'id': body['id'],
                'title': body.get('title', ''),
                'price': body.get('price', 0),
                'sold_quantity': body.get('sold_quantity', 0),
                'available_quantity': body.get('available_quantity', 0),
                'thumbnail': body.get('thumbnail', ''),
                'permalink': body.get('permalink', ''),
            })

# 3. Save to dados.json
ml_data = json.load(open('/root/mercadoLivre/dados.json'))
ml_data['produtos'] = all_products
json.dump(ml_data, open('/root/mercadoLivre/dados.json', 'w'), indent=2)
```

## Step 2: Next.js API Route

Create at `src/pages/api/ml/campanhas.ts`:

```typescript
import type { NextApiRequest, NextApiResponse } from "next";
import fs from "fs";

export default async function handler(req, res) {
  const dadosPath = "/root/mercadoLivre/dados.json";
  const raw = fs.readFileSync(dadosPath, "utf-8");
  const dados = JSON.parse(raw);
  
  const produtos = dados.produtos || [];
  const conta = dados.conta || {};

  const campanhas = produtos.map((p) => ({
    id: p.id,
    content: p.title,
    platform: "mercadolivre",
    budget: p.price,
    revenue: p.price * p.sold_quantity,
    sold: p.sold_quantity,
    stock: p.available_quantity,
    roi: calcROI(p.price, p.sold_quantity, conta.comissao_percentual || 16),
    thumbnail: p.thumbnail,
    link: p.permalink,
    status: p.sold_quantity > 0 ? "published" : "paused",
  }));

  res.json({
    loja: conta.nome_loja,
    totalProdutos: campanhas.length,
    totalRevenue: campanhas.reduce((s, c) => s + c.revenue, 0),
    totalSold: campanhas.reduce((s, c) => s + c.sold, 0),
    campanhas,
  });
}
```

## Step 3: React Page

Create at `src/pages/admin/ml/index.tsx` — consumes the API and renders a MUI dashboard with:

- **Summary cards**: total products, total sold, gross revenue, avg ticket
- **Table**: product name, price, sold, stock, revenue, estimated commission, ROI
- **Chips**: color-coded status indicators

## Key ML API Endpoints

| Endpoint | Purpose | Notes |
|----------|---------|-------|
| `GET /users/{id}/items/search?search_type=scan&limit=N` | List all item IDs | Paginated; max ~50 per request |
| `GET /items?ids=ID1,ID2,...` | Get item details | Max **20** IDs per request |
| `GET /orders/search?seller={id}&order.date_created.from=...` | Sales orders | See `querying-real-orders.md` |

## Important Notes

- **Always use `api.mercadolibre.com`** (without `.br`) — DNS issues with Brazilian domain
- **Token expires in 6 hours** — use `refresh_token` or fetch fresh data each time
- **dados.json as cache** — products don't change frequently, so batch-importing once is fine for a dashboard
- **ROI estimation** — commission percentage stored in `dados.json.conta.comissao_percentual` (default 16%)
- **Thumbnails** — ML returns `http://` URLs; convert to `https://` for Next.js Image/Avatar components
