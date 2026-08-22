# PagBank Checkout Integration (Brazil)

## Overview

PagBank (formerly PagSeguro) is a Brazilian payment processor. This reference covers the hosted checkout flow for selling digital products (course, ebook).

There are **two APIs** — the newer OAuth-based REST API and the legacy Checkout Transparente (XML). The strategy is **dual-try**: attempt OAuth first, fall back to XML.

## Authentication Strategy

PagBank credentials from the Developer Portal (`dev.pagbank.com.br`) are **OAuth 2.0** credentials (`client_id` + `client_secret`), NOT an email/password pair. Credentials from `minhaconta.pagbank.com.br` are Checkout Transparente tokens (email + legacy token).

## Dual-Try Approach

Always try OAuth first, then fall back to XML:

```
Tentativa 1: POST https://api.pagseguro.com/oauth2/token
             (Basic Auth with client_id:client_secret + JSON body)
  → access_token received? → POST /orders (Bearer token)
  → fail? → Tentativa 2

Tentativa 2: POST https://ws.pagseguro.uol.com.br/v2/checkout
             (email + token as query params + XML body)
  → <code> received? → redirect to payment page
  → fail? → show credential error
```

## OAuth 2.0 (API Nova) — Preferred

### Step 1: Get Access Token

```ts
const auth = Buffer.from(`${clientId}:${clientSecret}`).toString("base64");

const res = await fetch("https://api.pagseguro.com/oauth2/token", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Basic ${auth}`,
  },
  body: JSON.stringify({ grant_type: "client_credentials" }),
});

const { access_token } = await res.json();
```

**NOT** form-urlencoded — the endpoint expects `application/json`.
**NOT** credentials in the body — use Basic Auth header.

### Step 2: Create Order

```ts
const order = await fetch("https://api.pagseguro.com/orders", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${access_token}`,
  },
  body: JSON.stringify({
    reference_id: `curso_${Date.now()}`,
    customer: { name, email },
    items: [{
      reference_id: "curso-erc20",
      name: "Curso: Do Zero ao seu Token ERC20",
      quantity: 1,
      unit_amount: 1900,  // centavos: R$19,00
    }],
    notification_urls: [`${baseUrl}/api/webhook`],
  }),
});
```

### Step 3: Redirect

```ts
const charge = order.charges?.[0];
const checkoutUrl = charge?.payment_response?.redirect_url
  || `https://pagseguro.uol.com.br/checkout/v2/payment/redirect.html?code=${order.id}`;
```

## Checkout Transparente (XML Legacy) — Fallback

When OAuth fails, try the legacy XML API:

```ts
const url = `https://ws.pagseguro.uol.com.br/v2/checkout?email=${encodeURIComponent(clientId)}&token=${encodeURIComponent(clientSecret)}`;
const body = `<?xml version="1.0" encoding="UTF-8"?>
<checkout>
  <currency>BRL</currency>
  <items>
    <item>
      <id>curso-erc20</id>
      <description>Course name</description>
      <amount>19.00</amount>
      <quantity>1</quantity>
    </item>
  </items>
  <reference>curso_${Date.now()}</reference>
  <sender><email>${email}</email><name>${name}</name></sender>
  <redirectURL>${baseUrl}/course</redirectURL>
  <notificationURL>${baseUrl}/api/webhook</notificationURL>
</checkout>`;

const res = await fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/xml;charset=UTF-8" },
  body,
});

const text = await res.text();
const codeMatch = text.match(/<code>(.*?)<\/code>/);
// Redirect to: https://pagseguro.uol.com.br/v2/checkout/payment.html?code={CODE}
```

## Webhook

PagBank sends POST to `notification_urls` with JSON body containing order status.

```ts
const charge = body.charges?.[0];
if (charge?.status === "PAID" || charge?.status === "AUTHORIZED") {
  // Grant access via body.customer?.email
}
```

## Environment Variables

```env
# OAuth mode (dev.pagbank.com.br):
PAGBANK_EMAIL=app_xxxxx           # Client ID
PAGBANK_TOKEN=client_secret_here  # Client Secret

# Legacy mode (minhaconta.pagbank.com.br):
# Same vars, just use email + token pair
```

**Leave both empty** to use demo mode (auto-approved purchases).

## Debugging on Vercel

When API integrations fail in Vercel serverless functions, add **tagged console.log** statements:

```ts
console.log("[PagBank] OAuth status:", res.status);
console.log("[PagBank] OAuth response:", JSON.stringify(data, null, 2));
```

View logs in **Vercel Dashboard > Functions > Latest Logs**. Always wrap `response.json()` in try/catch since non-JSON responses crash:

```ts
let data;
try { data = await res.json(); } catch {
  const text = await res.text();
  console.log("[PagBank] Raw response:", text);
}
```

## Common Errors

| HTTP | Error | Likely Cause |
|------|-------|--------------|
| 415 | Unsupported Media Type | Wrong Content-Type. Send JSON, not form-urlencoded |
| 401/403 | Unauthorized | Invalid credentials. Wrong token or expired |
| 41001 | invalid_request (code) | Credentials sent in wrong format or wrong grant_type |

## Getting Credentials

1. **OAuth**: https://dev.pagbank.com.br > Apps > Create App
   - Copy `Client ID` and `Client Secret`
2. **Legacy**: https://minhaconta.pagbank.com.br > Integrations
   - Copy email + token pair

## Windows (PowerShell) Testing

PowerShell's `curl` is an alias for `Invoke-WebRequest`. Use `curl.exe` or `Invoke-RestMethod`:

```powershell
$auth = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("client_id:client_secret"))
Invoke-RestMethod -Uri "https://api.pagseguro.com/oauth2/token" -Method POST `
  -Headers @{ "Authorization" = "Basic $auth"; "Content-Type" = "application/json" } `
  -Body '{"grant_type":"client_credentials"}'
```

## Bipa (Bitcoin/Lightning) Alternative

Bipa accepts crypto payments and converts to BRL. API at `api.bipa.app/v1/invoices` using `X-API-Key` header.

```env
BIPA_API_KEY=your_key_here
```
