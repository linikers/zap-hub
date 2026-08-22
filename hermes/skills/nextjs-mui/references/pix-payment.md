# PIX Payment Integration

Server-side PIX generation using `qrcode-pix` (payload) + `qrcode` (QR Code image).

## Dependencies

```bash
npm install qrcode qrcode-pix
npm install --save-dev @types/qrcode
```

## API Route (`src/app/api/pix/route.ts`)

### Opção 1: Chave hardcoded (simples)

```ts
const chavePix = "sua-chave-pix@email.com";
```

### Opção 2: Ler chave do config admin (recomendado)

Lê a chave PIX ativa de um arquivo de configuração salvo pelo admin:

```ts
import { readFileSync, existsSync } from "fs";
import path from "path";

interface PixKey {
  id: string;
  tipo: string;
  chave: string;
  titular: string;
  banco: string;
  ativo: boolean;
}

function getChavePixAtiva(): string | null {
  try {
    const configPath = path.join(process.cwd(), "src/data/pagamentos.json");
    if (!existsSync(configPath)) return null;
    const config = JSON.parse(readFileSync(configPath, "utf-8"));
    const chavesAtivas = config.pix?.chaves?.filter((k: PixKey) => k.ativo) || [];
    return chavesAtivas.length > 0 ? chavesAtivas[0].chave : null;
  } catch {
    return null;
  }
}

// Na rota:
const chavePix = getChavePixAtiva() || "fallback@email.com";
```

### Rota completa com fallback

```ts
import { NextRequest, NextResponse } from "next/server";
import { QrCodePix } from "qrcode-pix";
import QRCode from "qrcode";
import { readFileSync, existsSync } from "fs";
import path from "path";

function getChavePixAtiva(): string | null {
  try {
    const configPath = path.join(process.cwd(), "src/data/pagamentos.json");
    if (!existsSync(configPath)) return null;
    const config = JSON.parse(readFileSync(configPath, "utf-8"));
    const chaves = config.pix?.chaves?.filter((k: any) => k.ativo) || [];
    return chaves.length > 0 ? chaves[0].chave : null;
  } catch { return null; }
}

export async function POST(req: NextRequest) {
  try {
    const { amount, nome, cidade } = await req.json();
    if (!amount || isNaN(amount) || amount < 0.01) {
      return NextResponse.json({ error: "Valor inválido" }, { status: 400 });
    }

    const chavePix = getChavePixAtiva() || "fallback@email.com";

    const payload = QrCodePix({
      version: "01",
      key: chavePix,
      name: (nome || "Loja").substring(0, 25),
      city: (cidade || "SaoPaulo").substring(0, 15),
      value: Number(amount),
      message: "Pedido",
    }).payload();

    const qrCodeBase64 = await QRCode.toDataURL(payload, {
      width: 350,
      margin: 2,
      color: { dark: "#1A1A1A", light: "#ffffff" },
    });

    return NextResponse.json({
      qrCode: qrCodeBase64,
      payload: pixPayload,
      chave: chavePix,
      amount: Number(amount),
      expiration: "24 horas",
    });
  } catch (error) {
    return NextResponse.json({ error: "Erro ao gerar PIX" }, { status: 500 });
  }
}
```

### Config file (`src/data/pagamentos.json`)

```json
{
  "pix": {
    "habilitado": true,
    "chaves": [
      {
        "id": "1",
        "tipo": "cpf",
        "chave": "000.000.000-00",
        "titular": "Nome do Titular",
        "banco": "Nubank",
        "ativo": true,
        "ordem": 0
      }
    ]
  },
  "boleto": { "habilitado": false },
  "cartao": { "habilitado": false }
}
```

> ⚠️ **Vercel:** `readFileSync` funciona em API routes (Serverless Node.js), mas o filesystem é read-only. O arquivo `pagamentos.json` precisa existir no build time. Para configs dinâmicas, usar banco de dados ou Vercel KV.

## PixPayment Component

A modal dialog showing:
- Checkmark icon + "PIX Gerado!"
- Valor total em destaque (laranja)
- QR Code image (base64 data URL)
- Código copia-e-cola (monospace) with copy button
- Loading spinner while generating

### Key UI elements:
- `slotProps={{ paper: { sx: { borderRadius: 3 } } }}` (MUI v9 API)
- Button toggles between "Copiar código PIX" and "Copiado!" (green) on click
- Clipboard API + fallback for older browsers

## Checkout Integration

```tsx
// In checkout form submit handler:
const handlePixPayment = async () => {
  setPixLoading(true);
  setPixOpen(true);
  try {
    const res = await fetch("/api/pix", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount: total, nome: form.nome, cidade: form.cidade }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error);
    setPixData(data);
  } catch (err) {
    // handle error, close modal
  } finally {
    setPixLoading(false);
  }
};
```
