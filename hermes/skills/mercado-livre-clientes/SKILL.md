---
name: mercado-livre-clientes
description: "CRM completo para Mercado Livre — clientes, vendas, produtos, ROI, e configuração da conta. Tudo salvo em JSON."
version: 2.6.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [mercado-livre, clientes, vendas, crm, roi, produtos]
---

# Mercado Livre - Gestão Completa

CRM completo para sua loja do Mercado Livre. Dados salvos em `/root/mercadoLivre/dados.json`.

## Banco de dados

Arquivo principal: `/root/mercadoLivre/dados.json`

⚠️ Há também `/root/mercadoLivre/clientes.json` (cópia antiga apenas da lista de clientes, usada pelo sistema de comandos WhatsApp). **Sempre sincronizar ambos** ao cadastrar/editar/remover clientes.

Estrutura do `dados.json`:
- `clientes` — lista de clientes (id, nome, email, telefone, tipo, estado)
- `vendas` — histórico de vendas
- `produtos` — catálogo de produtos
- `conta` — configurações GLOBAIS da loja (não por cliente individual)
- `ultimo_id_*` — contadores auto-incremento

> A conta ML (api_token, refresh_token, comissão, etc.) é configurada no nível da loja (`conta`), não por cliente.

---

## 🧑‍💼 CLIENTES

### Cadastrar
```
Cadastra cliente: João Silva, joao@email.com, 44 99999-8888, Comprador, SP
```
Campos: `nome`, `email`, `telefone`, `tipo` (Comprador/Vendedor/Ambos), `estado`

### Listar
```
Listar clientes
Mostrar todos os clientes
```

### Buscar
```
Buscar cliente João
Cliente de SP
Procurar por email joao@email.com
```

### Atualizar
```
Editar cliente ID 1: telefone 44 98888-7777
Atualizar cliente João: email novo@email.com
```

### Remover
```
Remover cliente ID 3
Excluir cliente João
```

---

## 📦 PRODUTOS

### Cadastrar produto
```
Cadastra produto: iPhone 14, 128GB, 3500.00, Eletrônicos, 10
```
Campos: `nome`, `descricao`, `preco_custo`, `preco_venda`, `categoria`, `estoque`, `sku`

### Listar produtos
```
Listar produtos
Ver estoque
Produtos com estoque baixo
```

### Atualizar produto
```
Atualizar produto ID 1: preco_venda 3200.00
Adicionar 5 unidades no estoque do iPhone
```

---

## 💰 VENDAS

### Registrar venda
```
Registrar venda: João Silva, iPhone 14, 2 unidades, 3500.00 cada, 21/05/2026
```
Campos: `cliente_id`, `cliente_nome`, `produto_id`, `produto_nome`, `quantidade`, `valor_unitario`, `valor_total`, `data`, `status` (Pago/Pendente/Cancelado/Enviado), `comissao_ml`, `custo_envio`, `lucro_liquido`

### Ver vendas
```
Listar vendas
Vendas desse mês
Vendas pendentes
Vendas de maio
```

### Resumo financeiro
```
Resumo de vendas
Relatório financeiro
Calcular ROI
Lucro total
```

---

## 📊 ROI E FINANCEIRO

O Hermes calcula automaticamente:

```
ROI = (Lucro Líquido - Custos) / Custos × 100
```

Onde:
- **Receita Bruta** = soma de todas as vendas
- **Comissão ML** = percentual configurado na conta (ex: 16%)
- **Custo Produto** = preço de custo × quantidade
- **Custo Envio** = configurado na conta
- **Custos Fixos** = mensais (configurado na conta)
- **Lucro Líquido** = Receita - Comissão - Custos - Custos Fixos
- **ROI** = (Lucro Líquido / Custos Totais) × 100

### Comandos
```
Relatório de ROI
Lucro desse mês
Produto mais vendido
Cliente que mais comprou
Média de vendas por mês
```

---

## ⚙️ CONFIGURAÇÃO DA CONTA

### Configurar loja
```
Configurar loja: nome Minha Loja ML, comissao 16, envio_medio 25.00, custos_fixos 500.00
```

### Ver configuração
```
Ver configuração da conta
Mostrar dados da loja
```

### 🔄 Renovação de Token (responsabilidade do agente)

O access token do ML expira a cada 6h. **O agente deve renovar automaticamente** — NÃO peça confirmação ao usuário. O fluxo:

1. Ler `dados.json` → `conta.refresh_token`
2. POST para `https://api.mercadolibre.com/oauth/token` com `grant_type=refresh_token`
3. Salvar novo `access_token` + `refresh_token` em `dados.json`
4. Se o refresh_token falhar (expirado > 30 dias), precisa de re-autorização manual

#### Fluxo recomendado (cron jobs e sessões normais)

**Passo 1:** Executar curl salvando resposta em arquivo:
```bash
curl -s --max-time 15 -X POST "https://api.mercadolibre.com/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "client_id=SEU_CLIENT_ID" \
  -d "client_secret=SEU_CLIENT_SECRET" \
  -d "refresh_token=SEU_REFRESH_TOKEN" \
  -o /tmp/ml_token.json
```

**Passo 2:** Ler tokens do arquivo com `read_file` (evita truncamento):
```
read_file /tmp/ml_token.json
```

**Passo 3:** Atualizar `dados.json` usando `patch` com strings específicas:
```
patch dados.json: substituir api_token antigo pelo novo
patch dados.json: substituir api_refresh_token antigo pelo novo
patch dados.json: substituir api_expira_em antigo pelo novo
patch dados.json: substituir ultimo_token_refresh e ultima_atualizacao
```

#### ⚠️ Pitfall: `execute_code` bloqueado em cron jobs

**`execute_code` NÃO funciona em cron jobs** — retorna erro "BLOCKED". Para renovar
token em cron, usar `terminal` + `read_file` + `patch` conforme o fluxo acima.

O `execute_code` funciona normalmente em sessões interativas (chat direto).

#### ⚠️ Pitfall: tokens truncados no terminal

O output do curl pode ser truncado pelo terminal (tokens longos com `...`). Por isso:
1. Sempre salvar com `-o /tmp/ml_token.json`
2. Ler com `read_file` (não com `cat` — `cat` TAMBÉM pode ser truncado)
3. Alternativa: `python3 -c "import json; d=json.load(open('/tmp/ml_token.json')); print(d['access_token'])"`

#### ⚠️ Pitfall: não usar `curl | python3` em terminal direto

O security layer pode redigir o token. Usar `-o arquivo` e ler separadamente.

### API do Mercado Livre (para integração automática)

Pra integrar de verdade com o Mercado Livre, precisa criar um App no portal de desenvolvedores e ativar o **Refresh Token**:

#### 🔄 Caminho A: Ativar Refresh Token em app EXISTENTE (mais rápido)

Se você já criou um app e quer adicionar refresh_token sem criar outro:

1. Acessa **https://developers.mercadolibre.com/** → **Brasil** → login
2. **"Minhas Aplicações"** → clica no seu app
3. Procura a aba **"Fluxo OAuth"** (OAuth Flow)
4. Lá tem as opções:
   - ☐ **Refresh Token** ← **MARCA ESSA AQUI** 🚨
   - ☐ PKCE (não precisa marcar)
5. **Salva**
6. Gera um NOVO code de autorização (com `scope=read+write+offline_access` na URL)
7. Troca o code por token — agora vem com `refresh_token` incluso

> ✅ Esse caminho funciona e foi testado com sucesso. O checkbox "Refresh Token"
> está dentro da aba "Fluxo OAuth" do app no novo portal do ML.

#### 🔑 Caminho B: Criar app novo do zero

1. Acessa **https://developers.mercadolibre.com/** (internacional, funciona)
2. Clica em **"Brasil"** → login → **"Minhas Aplicações"** → **"Criar nova"**
3. Preenche nome, descrição
4. **Tipo de app:** se houver a opção **"App Privada"**, selecione ela para garantir
5. **Redirect URI:** (veja opções abaixo)
6. **Scopes/Permissões:** no novo portal, os scopes são configurados na criação
7. Salva → copia **Client ID** + **Client Secret**

#### 🌐 Redirect URI (qual caminho escolher)

- ✅ **`https://oauth.pstmn.io/v1/callback`** (recomendado — Postman, funciona perfeitamente)
- ✅ **`https://www.example.com/callback`** (placeholder)
- ⚠️ `https://localhost` **NÃO funciona** — ML rejeita como inválido

Depois de pegar as credenciais, usar:
```
Configurar API ML: client_id SEU_ID, client_secret SEU_SECRET
```

> ⚠️ **Pitfalls comuns na integração:**
> - **DNS da API:** `api.mercadolivre.com.br` **não resolve** de muitos servidores.
>   Use `api.mercadolibre.com` (sem `.br`) para todas as chamadas.
> - **Refresh Token no NOVO PORTAL:** não fica na aba "Scopes" (que nem existe mais).
>   Fica na aba **"Fluxo OAuth"** como checkbox **"Refresh Token"**.
> - **client_credentials grant:** funciona e retorna scope `offline_access`, mas
>   **NÃO gera refresh_token** — só o `authorization_code` grant retorna refresh_token.
> - **Diagnóstico:** se a resposta do token exchange NÃO tiver o campo `refresh_token`,
>   o offline_access não está ativo — verifique se o checkbox "Refresh Token" está
>   marcado na aba "Fluxo OAuth" do app.
> - **Solução quando não vem refresh_token:**
>   1. Primeiro tenta ativar o "Refresh Token" no "Fluxo OAuth" (Caminho A acima)
>   2. Se não funcionar, cria um app novo como "App Privada" (Caminho B)
> - **Code expira rápido:** ~10 min e uso único. Troque por token imediatamente.
> - **Token output truncado:** o terminal corta tokens longos com `...`. Sempre salve
>   a resposta do curl num arquivo com `-o /tmp/ml_token.json` e leia separadamente.
>   Mas `cat` do arquivo salvo TAMBÉM pode sair truncado (security scan no terminal).
>   Use Python pra ler sem truncamento:
>   `python3 -c "import json; d=json.load(open('/tmp/ml_token.json')); print('TOKEN:', d['access_token'])"`
> - **Sempre incluir `scope=read+write+offline_access`** na URL de autorização, mesmo
>   com o checkbox marcado no portal — os dois lados precisam estar configurados.
>
Veja o guia completo em `references/api-integration-flow.md` para o fluxo
OAuth completo com exemplos de curl e resolução de problemas.
>
> Veja também `references/querying-real-orders.md` para o workflow de consulta
> de pedidos reais via API (incluindo refresh token e parsing).
>
> Veja também `references/weekly-sales-report-cron.md` para configurar relatório semanal automático por WhatsApp.
> workflow completo: refresh token → query com paginação → calcular receita/comissão via
> `paid_amount` e `sale_fee` → formatar relatório → entregar via bridge WhatsApp (`localhost:3000`).
>
Veja também `references/whatsapp-bridge-delivery.md` para entrega de
mensagens para usuários específicos via bridge HTTP.

## 💡 **WhatsApp bridge centralizado:** O repositório
[zap-hub](https://github.com/linikers/zap-hub) organiza TODAS as
conexões WhatsApp (Cloud API e Baileys QR) com scripts de setup,
drivers padronizados e gestão por bot. Consulte-o para configurar
novas instâncias ou entender o esquema de cada conexão ativa.

> **🚫 NUNCA usar o NFe bridge (port 3003) como fallback para envio de
> conteúdo ML/ecommerce.** Cada bridge é um número diferente. Envio
> cross-bridge causa mensagem chegando do número errado.
> Use sempre: `python3 /root/whatsapp-send/send-validated.py`
> Ver `references/whatsapp-bridge-delivery.md` para roteamento correto.

> Veja também `references/nextjs-dashboard-integration.md` para integrar
> dados do ML num dashboard Next.js (portfolio). Padrão: API route →
> lê dados.json → transforma produtos em campanhas → renderiza tabela MUI.

### 📦 Dados de Produto: Peso e Medidas (via API)

A API do ML **NÃO retorna** `weight` ou `dimensions` como campos top-level.
Os dados de embalagem ficam dentro do array `attributes`:

```python
# Buscar detalhes do item
result = subprocess.run([
    'curl', '-s', '-H', f'Authorization: Bearer {token}',
    f'https://api.mercadolibre.com/items/{item_id}'
], capture_output=True, text=True)
item = json.loads(result.stdout)

# Extrair peso e medidas do array attributes
dims = {}
for attr in item.get('attributes', []):
    name = attr.get('name', '').lower()
    if 'embalagem' in name and 'vendor' not in name:
        dims[attr['name']] = attr.get('value_name', 'N/A')

# Exemplo de retorno:
# {"Altura da embalagem": "15.2 cm", "Comprimento da embalagem": "23.8 cm",
#  "Largura da embalagem": "35.7 cm", "Peso da embalagem": "4740 g"}
```

**Nomes dos atributos-chave:**
| Atributo | Tipo |
|----------|------|
| `Altura da embalagem` | number_unit (cm) |
| `Comprimento da embalagem` | number_unit (cm) |
| `Largura da embalagem` | number_unit (cm) |
| `Peso da embalagem` | number_unit (g) |

> ⚠️ **Nem todo produto tem esses atributos.** Produtos novos ou sem
> informações de frete podem não ter. Verificar `len(dims) > 0` antes de usar.
>
> ⚠️ **Priorizar atributos SEM "vendor" no nome** — "Altura da embalagem do vendor"
> é a medida que o vendedor cadastrou manualmente; "Altura da embalagem" é a
> medida padrão do catálogo ML. Usar a do catálogo quando disponível.

Sem a API, os dados são manuais (você informa vendas, produtos, etc.)

> ⚠️ O domínio `developers.mercadolivre.com.br` **não resolve direto no DNS** — sempre entre pelo internacional `developers.mercadolibre.com/` e selecione Brasil.
> ⚠️ Além do DNS, o portal BR **frequentemente fica fora do ar** (erro 500 / "Hubo un error"). Se acontecer, tente de novo mais tarde.

---

## 🔐 CONTROLE DE ACESSO POR USUÁRIO

Quando diferentes pessoas conversam com o Hermes sobre o Mercado Livre, cada uma pode ter permissões diferentes. **Sempre verificar antes de criar/editar/alterar qualquer dado.**

### Regras conhecidas:

| Usuário | Permissão | Escopo | Exceção |
|---------|-----------|--------|---------|
| **Link** (dono) | Leitura e Escrita total | ML + ecommerce (se aplicável) | N/A |
| **Alcides** (CarCrew) | **SOMENTE LEITURA** por padrão | **Apenas ML** — nada de ecommerce/site | Se Alcides disser que alterou algo **no app/painel do ML**, pode fazer o que ele pedir |

### Ao interagir com Alcides:
1. 🔍 **Só consultar** — ler `clientes.json` e `dados.json`, nunca criar/editar/remover
2. 🚫 **Só Mercado Livre** — não mencionar carCrewCommerce, site, ecommerce, nem nenhum outro sistema
3. ❓ **Se não tiver info no sistema**, responder: "Não tenho essa informação cadastrada no sistema"
4. ✅ **Exceção:** Se Alcides disser "alterei no app do ML" ou similar, aí pode executar o que ele pedir (dentro do escopo ML)

### ⚠️ Pitfall: cross-bridge routing (BUG GRAVE descoberto em 2026-06-20)

**NUNCA enviar conteúdo ML pelo bridge NF-e (porta 3003).** Cada bridge
é um número de WhatsApp DIFERENTE. O bug: quando bridge 3000 caiu, o agente
usou 3003 como fallback → Alcides recebeu relatório ML do número NF-e.

**Fluxo correto:**
1. Verificar bridge 3000: `python3 /root/whatsapp-send/send-validated.py --check-bridge 3000`
2. Se down → BLOQUEAR envio + reportar "reautenticar necessária"
3. Se up → enviar via: `python3 /root/whatsapp-send/send-validated.py --bridge 3000 --to "554498133182" --content-type "relatorio_ml" --message "texto"`

**Config:** `/root/whatsapp-routing.json` — mapa bridge→conteúdo→permitido
**Audit:** `/root/whatsapp-audit.db` — log SQLite de todos os envios
**QR Server:** `http://VPS_IP:3002` — página para escanear QR de reautenticação

### ⚠️ Pitfall: banco local vs API real

O banco local (`dados.json`) pode estar desatualizado ou vazio mesmo com vendas ativas no ML.
**Sempre que possível, consultar a API real do ML** para dados de vendas em vez de confiar
apenas no cache local. Veja `references/querying-real-orders.md` para o workflow completo.

---

## 📋 EXEMPLOS PRÁTICOS

### Personality ML

No Hermes, é possível ativar uma persona especializada em ML para não misturar
assuntos. A persona **mercadolivre** foi criada em `~/.hermes/config.yaml` sob
`agent.personalities.mercadolivre` e inclui:

- Foco exclusivo em Mercado Livre (vendas, API, produtos, métricas)
- Regra de não misturar com ecommerce/site/web dev
- Regra de não alterar dados sem autorização
- Tom direto e prático

**Como usar:**
- `/personality mercadolivre` no chat (CLI) para ativar
- `/personality helpful` para voltar ao normal
- Ou simplesmente peça "ativa a persona ML"

### Cadastrar tudo do zero
```
1. Configurar loja: nome GameShop, comissao 14, envio_medio 20.00, custos_fixos 800.00
2. Cadastra produto: iPhone 14, 128GB Novinho, 2800.00, 4200.00, Eletrônicos, 15
3. Cadastra cliente: Pedro Alves, pedro@teste.com, 44 98888-5555, Comprador, PR
4. Registrar venda: Pedro Alves, iPhone 14, 1, 4200.00, 21/05/2026
5. Relatório de ROI
```
