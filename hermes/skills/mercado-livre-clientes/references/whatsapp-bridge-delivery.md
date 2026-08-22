# WhatsApp Bridge — Entrega de Mensagens para Usuários Específicos

O WhatsApp bridge do Hermes roda em `localhost:3000` e aceita envio direto
de mensagens via HTTP, independente do `send_message` tool (que depende de
home channel configurado).

## Endpoint de Envio

```bash
curl -s --max-time 30 -X POST http://localhost:3000/send \
  -H "Content-Type: application/json" \
  -d '{"chatId":"554498133182@s.whatsapp.net","message":"Texto da mensagem"}'
```

Resposta: `{"success":true,"messageId":"3EB0..."}`

## Formato do chatId

O chatId segue o padrão `NUMERO@s.whatsapp.net`:
- Link (dono): `5544991528386@s.whatsapp.net`
- Alcides (CarCrew): `554498133182@s.whatsapp.net`

> O número do Alcides difere do que está na memória (`5544998133182`).
> O correto (confirmado pelo mapping LID) é `554498133182`.

## Como descobrir o chatId de um usuário

Os mappings LID-phone ficam em `~/.hermes/whatsapp/session/lid-mapping-*_reverse.json`:

```bash
for f in ~/.hermes/whatsapp/session/lid-mapping-*_reverse.json; do
  val=$(cat "$f" | tr -d '{}\n"\n ')
  if echo "$val" | grep -q "8133182"; then
    echo "$(basename $f) -> $val"
  fi
done
```

O nome do arquivo (sem `_reverse.json`) é o LID; o conteúdo é o número de telefone.
Formato do chatId: `NUMERO@s.whatsapp.net`.

## Health Check

```bash
curl -s --max-time 5 http://localhost:3000/health
# {"status":"connected","queueLength":0,"uptime":269640.65}
```

## 🚫 REGRA DE OURO: NUNCA misturar bridges

**Cada bridge é um número de WhatsApp DIFERENTE.** Enviar conteúdo ML
pelo bridge NF-e faz a mensagem chegar do número errado, confundindo
clientes e violando isolamento.

### Roteamento obrigatório (routing.json)

| Conteúdo | Bridge | Número |
|----------|--------|--------|
| ML, vendas, relatórios, ecommerce | 3000 (principal) | 5544991528386 |
| NF-e, contabilidade, SEFAZ | 3003 (NF-e) | 554491277833 |

### Envio validado (USE ESTE SCRIPT)

```bash
# Enviar relatório ML (SEMPRE via bridge 3000)
python3 /root/whatsapp-send/send-validated.py \
  --bridge 3000 --to "554498133182" \
  --content-type "relatorio_ml" --message "texto"

# Ou via wrapper shell
/root/whatsapp-send/send.sh 3000 554498133182 relatorio_ml "texto"
```

### Se o bridge 3000 estiver down

**NÃO tente enviar via 3003.** Em vez disso:
1. O script vai bloquear o envio automaticamente
2. Verificar: `python3 /root/whatsapp-send/send-validated.py --check-bridge 3000`
3. Reportar ao usuário: "Bridge principal (3000) está down. Reautenticar necessária."
4. NUNCA usar o bridge NF-e como fallback para conteúdo de outro contexto

### Diagnóstico rápido

```bash
# Verificar saúde dos bridges
python3 /root/whatsapp-send/send-validated.py --check-bridge 3000
python3 /root/whatsapp-send/send-validated.py --check-bridge 3003

# Ver audit log
python3 /root/whatsapp-send/send-validated.py --audit --last 20

# Ver estatísticas
python3 /root/whatsapp-send/send-validated.py --stats
```

> **Cron jobs:** `execute_code` é bloqueado em cron jobs. Use `terminal` com
> chamadas curl individuais em vez de scripts Python complexos.

## Pattern: Relatório Diário de Vendas

Usado para enviar resumo de vendas do ML para um usuário específico:

1. Refresh token da API ML (se expirado) — ver `references/querying-real-orders.md`
2. Buscar pedidos do período desejado (`order.date_created.from` / `.to`)
3. Formatar resumo com:
   - Vendas do dia anterior (ontem)
   - Vendas do dia atual (hoje)
   - Totais e quantidades
4. Enviar via `curl POST http://localhost:3000/send`

⚠️ **Mensagens longas:** O bridge tem chunking automático (4096 chars por chunk),
mas para envios muito grandes, prefira Python com a biblioteca `requests`.

⚠️ **Timeout:** O bridge tem SEND_TIMEOUT_MS=60000 (1 min). Use `--max-time 30` no
curl para não travar.
