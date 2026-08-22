# Consultando Pedidos Reais da API ML

O banco local (`dados.json`) pode estar vazio/desatualizado. Para dados reais,
consulte a API do Mercado Livre diretamente.

## 1. Token Refresh (se expirado)

Tokens expiram em 6 horas. O `refresh_token` salvo em `dados.json.conta` permite renovar:

```bash
curl -s --max-time 15 -X POST "https://api.mercadolibre.com/oauth/token" \
  -H "content-type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&refresh_token={REFRESH_TOKEN}" \
  -o /tmp/ml_token.json
```

> ⚠️ **Cron jobs:** `execute_code` é bloqueado em cron jobs sem aprovação.
> Para workflows em cron, usar `terminal` com chamadas curl individuais e
> `python3 -c "..."` para parsing, em vez de scripts Python grandes via execute_code.

⚠️ **Token truncado no terminal** — sempre extrair com Python:
```python
import json, subprocess
r = subprocess.run(['curl', '-s', '--max-time', '15',
  '-X', 'POST', 'https://api.mercadolibre.com/oauth/token',
  '-H', 'content-type: application/x-www-form-urlencoded',
  '-d', f'grant_type=refresh_token&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&refresh_token={REFRESH_TOKEN}'],
  capture_output=True, text=True)
d = json.loads(r.stdout)
token = d['access_token']
```

## 2. Consultar Vendas por Data

Busca pedidos pagos do seller em um período:

```python
import json, subprocess
r = subprocess.run(['curl', '-s', '--max-time', '15',
  '-H', f'Authorization: Bearer {token}',
  'https://api.mercadolibre.com/orders/search?seller={SELLER_ID}&order.date_created.from=2026-05-25T00:00:00-03:00&order.date_created.to=2026-05-26T23:59:59-03:00'],
  capture_output=True, text=True)
orders = json.loads(r.stdout)
```

## 3. Estrutura da Resposta

Cada pedido (`results[]`) contém:

| Campo | Descrição |
|-------|-----------|
| `id` | ID do pedido |
| `date_created` | Data de criação (UTC-4) |
| `status` | paid / cancelled / pending |
| `payments[].total_paid_amount` | Valor pago REAL (inclui frete pago pelo comprador) — **usar para receita** |
| `payments[].status` | approved / in_mediation / refunded |
| `order_items[].item.title` | Nome do produto |
| `order_items[].item.seller_sku` | SKU do vendedor |
| `order_items[].quantity` | Quantidade |
| `order_items[].unit_price` | Preço unitário |
| `order_items[].sale_fee` | Taxa do ML por unidade |
| `payments[].payment_method_id` | Forma de pagamento (pix, etc.) |
| `buyer.nickname` | Nickname do comprador |
| `shipping.id` | ID do envio |
| `tags` | Tags do pedido (paid, pack_order, etc.) |

## 4. Paginação Exemplo (quando paging.total > 50)

Sempre verificar `paging.total` — se > 50, é necessário paginar:

```python
import json, subprocess, time

token = "seu_access_token"
seller_id = 50816240
from_date = "2026-05-29T00:00:00-03:00"
to_date = "2026-06-05T23:59:59-03:00"

all_results = []
offset = 0
limit = 50

while True:
    url = (f"https://api.mercadolibre.com/orders/search?seller={seller_id}"
           f"&order.date_created.from={from_date}&order.date_created.to={to_date}"
           f"&limit={limit}&offset={offset}")
    r = subprocess.run(['curl', '-s', '--max-time', '15',
        '-H', f'Authorization: Bearer {token}', url],
        capture_output=True, text=True)
    d = json.loads(r.stdout)
    results = d.get('results', [])
    all_results.extend(results)
    total = d.get('paging', {}).get('total', 0)
    offset += limit
    if offset >= total:
        break
    time.sleep(0.5)  # rate limit safety

# Now process all_results (filter paid, aggregate, etc.)
paid_orders = [o for o in all_results if o.get('status') == 'paid']
```

Exemplo real: consulta de 7 dias para seller 50816240 retornou 115 resultados,
exigindo 3 páginas (offset=0, 50, 100).

## 5. ⚠️ Pitfalls

- **Fuso horário:** A API retorna em UTC-4. BRT = UTC-3. Para datas "de hoje" em BRT,
  subtrair 1 hora no filtro. Ex: buscar de `T00:00:00-03:00` pega pedidos da
  01:00 UTC-4 em diante.
- **Token expirado:** Se a resposta for `401`, o token expirou. Renovar com o `refresh_token` salvo em `dados.json.conta.refresh_token`.
- **Rate limit:** ML tem rate limiting. Para muitas consultas, espaçar com
  `time.sleep(1)` entre chamadas.
- **Paginação é obrigatória:** Para muitas vendas, a API paginifica (`offset`/`limit` params).
  O default é 50 resultados por página. Calcular páginas: `ceil(total / 50)`.
  Se não paginar, você só vê os primeiros 50 pedidos.
- **seller_id:** Está no final do `api_token` (`...-50816240`). Extrair com:
  `python3 -c "print('APP_USR-...-50816240'.split('-')[-1])"`
- **paid_amount via payments array:** O campo `order.paid_amount` pode não existir. A receita real está em `payments[].total_paid_amount` onde `payments[].status == 'approved'`. Esse valor já inclui frete pago pelo comprador.
- **sale_fee é a comissão exata:** O campo `order_items[].sale_fee` já vem com o valor da comissão do ML por unidade. Mais preciso que aplicar percentual fixo. **Multiplique por `quantity`** — o fee é POR UNIDADE, não por pedido.
