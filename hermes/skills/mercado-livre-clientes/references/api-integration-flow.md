# ML API Integration Flow

## ⚠️ Portal Status (2026)

**O portal brasileiro (developers.mercadolivre.com.br) está frequentemente fora do ar**, retornando
"Hubo un error accediendo a esta pagina..." — tanto de navegador quanto de API.
Isso NÃO é só problema de DNS — o servidor SPA deles cai com frequência.

- **Sempre tentar pelo site internacional primeiro:** https://developers.mercadolibre.com/
- Selecione "Brasil" → se o portal BR estiver no ar, redireciona
- Se cair, tente de novo mais tarde ou use outro país (ex: Argentina) como referência de docs

## Developer Portal Access

- **Working entry point:** https://developers.mercadolibre.com/ (international)
- Select country "Brasil" → redirects to https://developers.mercadolivre.com.br/
- ⚠️ DNS note: `developers.mercadolivre.com.br` does NOT resolve via public DNS
  from all networks — the browser may load it (client-side SPA) but curl/wget from
  a server often fails with "Could not resolve host". Always enter via the
  international site and let the browser redirect.
- ⚠️ **Same DNS issue applies to the API:** `api.mercadolivre.com.br` also
  fails to resolve from many servers. Always use `api.mercadolibre.com`
  (without `.br`) for OAuth token exchange, refresh, and all API calls.
- The Brazil portal is a React SPA that sometimes shows "Hubo un error accediendo
  a esta pagina..." — retrying usually works. Se persistir, o portal pode estar
  realmente fora do ar (manutenção do ML — comum em fins de semana).

## Creating an Application — PORTAL NOVO (2025+)

⚠️ **IMPORTANTE: O portal do Mercado Livre foi redesenhado.** As instruções antigas
de aba "Scopes" ou "Permisos" NÃO EXISTEM mais no novo portal. O fluxo mudou.

### 🔄 Opção 1: Ativar Refresh Token em app EXISTENTE (recomendado)

Se você já criou um app e o token veio SEM `refresh_token`, **não precisa criar outro app**.

1. Acesse **https://developers.mercadolibre.com/** e faça login
2. Selecione **"Brasil"**
3. Vá em **"Minhas Aplicações"** → clique no seu app
4. Procure a aba **"Fluxo OAuth"** (OAuth Flow)
5. Lá você encontra as opções de fluxo:
   - ☐ **Refresh Token** ← **MARQUE ESTA OPÇÃO** 🚨
   - ☐ PKCE (não precisa marcar a menos que queira)
6. Clique em **Salvar** / **Save**
7. Gere um **novo code** de autorização (o anterior foi consumido)
8. Na URL de autorização, inclua `&scope=read+write+offline_access`
9. Troque o code por token — agora a resposta incluirá `refresh_token`

> ✅ **Testado com sucesso.** Essa opção existe no novo portal e funciona.
> O checkbox "Refresh Token" fica na aba "Fluxo OAuth", NÃO em "Scopes" (que
> nem existe mais como aba separada).

### 🔑 Opção 2: Criar app novo do zero

1. Acesse **https://developers.mercadolibre.com/** e faça login
2. Selecione **"Brasil"**
3. Vá em **"Minhas Aplicações"** (My Applications)
4. Clique em **"Criar nova aplicação"** (Create new application)
5. Preencha nome e descrição

6. **🔑 ESCOLHA O TIPO DE APP CORRETAMENTE — ESSE É O PONTO CRÍTICO:**
   - Selecione **"App Privada" (Private App)** — é ESSE tipo que permite `offline_access`
   - Apps do tipo "Público" ou "App Web" podem NÃO gerar refresh_token
   - ⚠️ Se você criar o app e DEPOIS não conseguir ativar offline_access, significa
     que o tipo de app não suporta — precisa criar um NOVO app como Privado

7. **Redirect URI:** escolhe uma das opções abaixo:
   - **`https://oauth.pstmn.io/v1/callback`** (recomendado — Postman OAuth, funciona)
   - **`https://www.example.com/callback`** (placeholder comum)
   - URL de um túnel ativo (Cloudflare/ngrok)
   - ⚠️ **`https://localhost` NÃO funciona** — ML rejeita como inválido

8. **Scopes/Permissões:** No NOVO portal, os scopes são definidos no momento da criação
   e podem variar conforme o tipo de app. Garanta que os scopes básicos estão lá:
   - `read` — ler dados da conta, vendas, perguntas
   - `write` — criar/atualizar anúncios
   - ⚠️ `offline_access` **NÃO aparece mais como uma checkbox visível** no novo portal.
     Ele é **concedido automaticamente** para apps do tipo "Privado".

9. Salve → copie **Client ID** e **Client Secret**

### 🚨 SOLUÇÃO DE PROBLEMAS — "Não encontro offline_access no portal"

Se o usuário disser que NÃO encontra a opção `offline_access` nas configurações do app:

**Contexto:** O Mercado Livre redesenhou o portal (2025+) e a aba "Scopes" não existe mais.
O `offline_access` agora é configurado de outra forma.

**✅ Solução correta (testada na prática):**

1. O `offline_access` não existe como um scope/toggle com esse nome
2. No novo portal, ele virou um checkbox chamado **"Refresh Token"** dentro da aba **"Fluxo OAuth"**
3. **Peça para o usuário:**
   - Entrar no app → aba **"Fluxo OAuth"**
   - Marcar **"Refresh Token"**
   - Salvar
4. Gerar um NOVO code de autorização com `scope=read+write+offline_access` na URL
5. Trocar o code por token — o `refresh_token` virá na resposta

**Caminho alternativo** (se o "Refresh Token" não estiver disponível no app existente):
- Criar um NOVO app do zero, selecionando **"App Privada"** (Private App) se a opção existir
- Usar o novo Client ID e Client Secret
- Passar `scope=read+write+offline_access` na URL de autorização

### ⚠️ client_credentials NÃO dá refresh_token

O grant type `client_credentials` retorna scope `offline_access` mas **nunca retorna
refresh_token**. Só o `authorization_code` grant retorna refresh_token.

```bash
# 🔴 ISSO NÃO dá refresh_token:
curl -X POST https://api.mercadolibre.com/oauth/token \
  -d 'grant_type=client_credentials&client_id=...&client_secret=...&scope=read+write+offline_access'
# Resposta tem access_token mas NÃO tem refresh_token

# ✅ ISSO dá refresh_token (com code do usuário):
curl -X POST https://api.mercadolibre.com/oauth/token \
  -d 'grant_type=authorization_code&client_id=...&client_secret=...&code=TG-...&redirect_uri=...'
# Resposta TEM access_token + refresh_token ✅
```

### ⚠️ Token output truncation

O terminal corta tokens longos com `...`. **Sempre salve a resposta num arquivo:**

```bash
curl -s -X POST https://api.mercadolibre.com/oauth/token \
  -d 'grant_type=authorization_code&...' \
  -o /tmp/ml_token_response.json \
  -w "%{http_code}"

# Depois leia separadamente:
python3 -c "import json; d=json.load(open('/tmp/ml_token_response.json')); print('TOKEN:', d['access_token']); print('REFRESH:', d['refresh_token'])"
```

### 🔬 Diagnóstico: como saber se o app tem offline_access

Depois de fazer a troca do code por token, **verifique a resposta COMPLETA**:

```json
{
  "access_token": "APP_USR-...",
  "token_type": "Bearer",
  "expires_in": 21600,
  "scope": "read ... write",
  "user_id": 50816240
}
```

Se NÃO aparecer o campo `refresh_token` na resposta, **o offline_access não está ativo**
para este app — mesmo que você tenha passado `scope=offline_access` na URL.

👉 A resposta SEM `refresh_token` é a confirmação definitiva de que o app não tem
offline_access habilitado.

## OAuth Token Exchange

After registering credentials with `Configurar API ML:`, Hermes should:

1. **Build the authorization URL — MUST include explicit `scope` parameter:**
   ```
   https://auth.mercadolivre.com.br/authorization?\
     response_type=code&\
     client_id={CLIENT_ID}&\
     redirect_uri={REDIRECT_URI}&\
     scope=read+write+offline_access
   ```
   > ⚠️ **Critical: `offline_access` must be configured in BOTH places:**
   > 1. In the App permissions (developer portal) — via App Type "Privado"
   > 2. In the authorization URL — passed as `&scope=read+write+offline_access`
   >
   > If either is missing, the token response will NOT include a `refresh_token`,
   > and the access_token expires in 6 hours with no way to renew.

2. User authorizes in browser → gets `code` query param on redirect

3. **Exchange code for tokens — use `api.mercadolibre.com` (not `.com.br`):**
   ```bash
   curl -s -X POST https://api.mercadolibre.com/oauth/token \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'grant_type=authorization_code&\
         client_id={CLIENT_ID}&\
         client_secret={CLIENT_SECRET}&\
         code={CODE}&\
         redirect_uri={REDIRECT_URI}'
   ```
   > ⚠️ **Pitfall — output truncation:** Long `access_token` values get
   > truncated when curl prints to terminal. **Always save to a file:**
   > ```bash
   > curl -s -X POST https://api.mercadolibre.com/oauth/token \
   >   -H 'Content-Type: application/x-www-form-urlencoded' \
   >   -d 'grant_type=authorization_code&...' \
   >   -o /tmp/ml_token_response.json \
   >   -w "%{http_code}"
   > ```
   > Then read the file with `read_file` or `python3 -m json.tool`.

4. **Authorization codes expire fast** (~10 minutes) and are single-use.
   Exchange immediately upon receipt. If you get `invalid_grant`, the user
   needs to authorize again — codes cannot be reused.

5. **Test the token immediately after exchange:**
   ```bash
   curl -s https://api.mercadolibre.com/users/me \
     -H "Authorization: Bearer {ACCESS_TOKEN}" | python3 -m json.tool
   ```

6. **Response:** `{ access_token, refresh_token (if offline_access), token_type, expires_in, ... }`
   - `expires_in: 21600` = 6 hours
   - Without `refresh_token`, the token is unrecoverable after expiry
   - With `refresh_token`, use the Token Refresh flow below

## Token Refresh

```bash
curl -X POST https://api.mercadolibre.com/oauth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=refresh_token&\
      client_id={CLIENT_ID}&\
      client_secret={CLIENT_SECRET}&\
      refresh_token={REFRESH_TOKEN}'
```

> Use `api.mercadolibre.com` — the `.com.br` variant has DNS resolution issues.

## Useful API Endpoints

> **All endpoints use `api.mercadolibre.com`** (not `.com.br` — DNS doesn't resolve).
> Always prepend `https://api.mercadolibre.com`.

| Endpoint | Description |
|----------|-------------|
| `GET /users/me` | Current user info |
| `GET /items/search?q={query}` | Search listings |
| `GET /users/{user_id}/items/search` | User's listings |
| `GET /orders/search` | Sales orders |
| `GET /questions/search` | Buyer questions |
