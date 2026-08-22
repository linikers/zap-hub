# Weekly Sales Report via Cron Job (WhatsApp Delivery)

## Pattern
A cron job that queries REAL orders from the Mercado Livre API, generates a weekly sales summary, and delivers it to a WhatsApp contact via the local bridge.

## Full Step-by-Step Workflow

### 1. Refresh the API Token

Tokens expire every 6 hours and ML rotates the `refresh_token` on every refresh. Always refresh before querying:

```bash
curl -s --max-time 15 -X POST "https://api.mercadolibre.com/oauth/token" \
  -H "content-type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&refresh_token={REFRESH_TOKEN}" \
  -o /tmp/ml_token.json

# Extract both tokens (curl output may be truncated — always use Python)
python3 -c "import json; d=json.load(open('/tmp/ml_token.json')); print('ACCESS:', d['access_token']); print('REFRESH:', d['refresh_token'])"
```

Save **both** tokens back to `dados.json` after refresh:
- `conta.api_token` → new `access_token`
- `conta.refresh_token` → new `refresh_token` (ML rotates it on every refresh)

> ⚠️ **Shell variable gotcha:** When running `curl` inside Hermes `terminal()`, `$` signs in Python f-strings or shell variables are interpreted by the shell. To avoid truncation or "bad substitution" errors, write the curl call inside a `.py` file using Python's `subprocess` module (see step 2 for the pattern) rather than inline shell commands.

### 2. Query Orders with Pagination

The API returns max 50 results per page. Use `offset` to paginate:

```bash
# Page 1 (offset=0)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.mercadolibre.com/orders/search?seller={SELLER_ID}&order.date_created.from={FROM}T00:00:00-03:00&order.date_created.to={TO}T23:59:59-03:00&limit=50" \
  -o /tmp/page1.json

# Page 2 (offset=50)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.mercadolibre.com/orders/search?seller={SELLER_ID}&order.date_created.from={FROM}T00:00:00-03:00&order.date_created.to={TO}T23:59:59-03:00&limit=50&offset=50" \
  -o /tmp/page2.json

# Page N+1 as needed — check paging.total to know how many pages
```

### 3. Calculate Financial Stats

Use Python to process all pages, filter `paid` orders, and compute:

```python
import json
from collections import Counter

all_results = []
for f in ['/tmp/page1.json', '/tmp/page2.json', ...]:
    d = json.load(open(f))
    all_results.extend(d.get('results', []))

# Filter paid orders (status='paid')
paid_orders = [o for o in all_results if o.get('status') == 'paid']

# Helper for Brazilian locale (R$ 1.234,56)
def fmt_brl(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

total_receita = 0.0
total_comissao = 0.0
total_itens = 0
produtos = Counter()  # title -> qty

for order in paid_orders:
    # Revenue from APPROVED payments only (ignore in_mediation/refunded)
    for payment in order.get('payments', []):
        if payment.get('status') == 'approved':
            total_receita += float(payment.get('total_paid_amount', 0) or 0)

    for item in order.get('order_items', []):
        title = item.get('item', {}).get('title', 'Unknown')
        qty = item.get('quantity', 1) or 1
        total_itens += qty
        produtos[title] += qty
        # sale_fee is the exact ML commission per item (more accurate than flat %)
        total_comissao += float(item.get('sale_fee', 0) or 0) * qty

lucro_liquido = total_receita - total_comissao

top3 = produtos.most_common(3)
```

> ⚠️ **Revenue field:** The API returns revenue inside `payments[].total_paid_amount`, NOT at `order.paid_amount` (that field may not exist). Always iterate `payments` and filter by `status == 'approved'`.
>
> ⚠️ **`in_mediation` payments:** Orders with `status='paid'` may have some payments `in_mediation` (buyer dispute). Those payments are NOT counted in revenue but the order IS counted as a paid order. This gives a conservative revenue estimate.
>
> ⚠️ **Paginação com Python vs shell:** Shell commands with `$TOKEN` inline can fail due to variable expansion. Preferred pattern: write the curl in a `.py` file using `subprocess.run()` to avoid shell interpolation issues entirely.
```

### 4. Format WhatsApp Message

Short, direct format proven with real users:

```
📊 RELATÓRIO SEMANAL - CarCrew
Período: DD/MM a DD/MM

💰 Vendas pagas: X
📦 Itens vendidos: X
💵 Receita: R$ X.XXX,XX
💸 Comissão ML: -R$ X.XXX,XX
📈 Líquido: R$ X.XXX,XX

🔥 Top 3 produtos:
1. Produto X (X vendas)
2. Produto Y (X vendas)
3. Produto Z (X vendas)

Bom fim de semana! 🚀
```

If no paid orders: `"📊 Sem vendas essa semana. Bora correr atrás! 💪"`

### 5. Deliver via WhatsApp Bridge

The Hermes WhatsApp bridge runs at `localhost:3000`:

```bash
curl -s --max-time 30 -X POST http://localhost:3000/send \
  -H "Content-Type: application/json" \
  -d '{"chatId":"554498133182@s.whatsapp.net","message":"MENSAGEM AQUI"}'
```

Response: `{"success":true,"messageId":"..."}`

### 6. Save Updated Tokens

After refreshing the token, update `dados.json.conta`:
- `api_token` → new access_token
- `api_refresh_token` → new refresh_token (ML rotates it on every refresh)

## Known Contacts
- Alcides (CarCrew): `554498133182@s.whatsapp.net`
- Link (dono): `5544991528386@s.whatsapp.net`

## Pitfalls
- **Paginação é obrigatória**: se `paging.total > 50`, você precisa de múltiplas páginas
- **Revenue via payments array**: use `payments[].total_paid_amount` com filtro `status == 'approved'`, NÃO `order.paid_amount` (que pode não existir)
- **commission via sale_fee**: o campo `order_items[].sale_fee` tem a comissão exata por item. Não aplique percentual fixo — o ML cobra valores diferentes por categoria/plano. Multiplique por `quantity` (sale_fee é por unidade)
- **Token output truncado**: o terminal corta tokens longos com `...`. Sempre salve num arquivo e leia com Python
- **Token refresca refresh_token**: o ML rotaciona o refresh_token a cada renovação — sempre salve o novo
- **Shell $ expansion**: Não use `$TOKEN` inline em comandos `terminal()` se o token contiver caracteres especiais. Prefira Python com `subprocess.run(["curl", ...])` num arquivo `.py`
- **PolicyAgent 403 em paginação**: Se a segunda página retornar `{"blocked_by":"PolicyAgent"}`, o token pode estar truncado ou inválido. Verifique o token antes de paginar
- **in_mediation**: Orders `paid` podem ter pagamentos `in_mediation` (disputa). Revenue só de pagamentos `approved`

## Schedule Configuration
- Server runs in UTC. Brazil is UTC-3.
- To run at 17:30 BRT (Friday): schedule for `30 20 * * 5` (20:30 UTC)
