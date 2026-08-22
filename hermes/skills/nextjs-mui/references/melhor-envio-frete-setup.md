# Melhor Envio — Integração de Frete

## Visão Geral

Integração com a API do Melhor Envio para cálculo de frete no checkout, geração de etiquetas e rastreio. Usa OAuth 2.0 para autenticação.

## Fluxo de Configuração

1. **Cadastro como parceiro** no [Melhor Envio para parceiros](https://melhorenvio.com.br/parceiros)
2. **Criar Aplicativo** no painel — gera Client ID + Client Secret
3. **Redirect URI** configurada: `https://seudominio.com/api/admin/frete/callback`
4. **Usuário coloca Client ID/Secret** na tela `/admin/frete` → clica "Conectar"
5. **OAuth flow**: redirect → Melhor Envio autoriza → callback salva access_token

## Estrutura de Arquivos

```
src/
  app/
    admin/frete/page.tsx          # Tela de configuração (admin)
    api/admin/frete/
      config/route.ts             # GET (ler) / PATCH (salvar) config
      auth/route.ts               # GET — inicia OAuth redirect
      callback/route.ts           # GET — recebe code, troca por token
  data/
    frete.json                    # Config persistida em JSON
```

## API Routes

### Config — GET /api/admin/frete/config
Retorna config sem secrets:
```json
{
  "originCep": "87000-000",
  "packageWeight": 0.5,
  "packageHeight": 2,
  "packageWidth": 16,
  "packageLength": 18,
  "markupPercent": 0,
  "sandbox": true,
  "hasClientId": true,
  "hasClientSecret": true,
  "hasToken": true,
  "tokenExpiresAt": "2026-06-10T..."
}
```

### Config — PATCH /api/admin/frete/config
Atualiza campos específicos (clientId, clientSecret, originCep, dimensões, etc.).

### Auth — GET /api/admin/frete/auth
Redireciona para o Melhor Envio OAuth. Gera URL com base no sandbox/produção.

### Callback — GET /api/admin/frete/callback?code=...
Recebe o code, troca por access_token via POST /oauth/token, salva no frete.json.

## OAuth Token Exchange

```typescript
const tokenUrl = sandbox
  ? "https://sandbox.melhorenvio.com.br/oauth/token"
  : "https://melhorenvio.com.br/oauth/token";

const res = await fetch(tokenUrl, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    grant_type: "authorization_code",
    client_id: config.clientId,
    client_secret: config.clientSecret,
    redirect_uri: `${BASE_URL}/api/admin/frete/callback`,
    code,
  }),
});

const tokenData = await res.json();
// tokenData.access_token, tokenData.refresh_token, tokenData.expires_in
```

## Scopes Solicitados

```
frete:calcular frete:comprar etiquetas:gerar etiquetas:imprimir
loja:ler envio:ler envio:gerar usuarios:ler
```

## Ambientes

| Ambiente | Auth URL | Token URL |
|----------|----------|-----------|
| Sandbox (testes) | `https://sandbox.melhorenvio.com.br/oauth/authorize` | `https://sandbox.melhorenvio.com.br/oauth/token` |
| Produção | `https://melhorenvio.com.br/oauth/authorize` | `https://melhorenvio.com.br/oauth/token` |

## Próximos Passos

Após configurado, implementar o endpoint de cálculo no checkout:
- `POST https://api.melhorenvio.com.br/v1/frete/calcular` com CEP destino + peso/dimensões
- Aplicar markupPercent sobre o valor retornado
- Exibir opções de frete no checkout
