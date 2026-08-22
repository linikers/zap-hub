# PWA Setup with Serwist + Next.js

Serwist é o sucessor moderno do `next-pwa` (que foi descontinuado). Funciona com Next.js App Router, SSR, e gera service worker com precaching automático.

## Instalação

```bash
npm install @serwist/next @serwist/sw serwist
```

## Configuração

### 1. next.config.ts — wrap com withSerwistInit

```ts
import type { NextConfig } from "next";
import withSerwistInit from "@serwist/next";

const nextConfig: NextConfig = {
  turbopack: {},  // ← OBRIGATÓRIO no Next.js 16! Ver abaixo
  // suas configs existentes (headers, images, etc.)
};

const serwistConfig = {
  swSrc: "src/sw.ts",          // source do service worker
  swDest: "public/sw.js",      // output (gerado no build)
  globPatterns: ["**/*.{js,css,html,json,ico,png,svg,jpg,jpeg,webp,avif}"],
  globIgnores: ["/admin/**", "/api/**", "/sw.js"],  // não cachear admin/API
};

export default withSerwistInit(serwistConfig)(nextConfig);
```

### ⚠️ Next.js 16 + Turbopack — pegadinha obrigatória

No Next.js 16, o **Turbopack** é o bundler padrão. O `withSerwistInit()` adiciona configuração webpack internamente, e o Next.js 16 **exige uma config explícita do Turbopack** quando detecta webpack config. Sem isso o build falha com:

```
ERROR: This build is using Turbopack, with a `webpack` config and no `turbopack` config.
Error: Call retries were exceeded
```

**Fix:** adicionar `turbopack: {}` no nextConfig (vazio — só pra satisfazer o checker):

```ts
const nextConfig: NextConfig = {
  turbopack: {},  // ← resolve o conflito webpack/Turbopack
  async headers() { ... },
};
```

**Se ainda falhar** (service worker não é gerado), forçar webpack no build:

```json
// package.json
"build": "prisma generate && next build --webpack"
```

### 2. src/sw.ts — Service worker

```ts
import { defaultCache } from "@serwist/next/worker";
import type { PrecacheEntry, SerwistGlobalConfig } from "serwist";
import { Serwist } from "serwist";

declare global {
  interface WorkerGlobalScope extends SerwistGlobalConfig {
    __SW_MANIFEST: Array<PrecacheEntry | string>;
  }
}

declare const self: WorkerGlobalScope & typeof globalThis;

const serwist = new Serwist({
  precacheEntries: self.__SW_MANIFEST,
  skipWaiting: true,
  clientsClaim: true,
  navigationPreload: true,
  runtimeCaching: defaultCache,
  fallbacks: {
    entries: [
      {
        url: "/~offline",
        matcher({ request }) {
          return request.destination === "document";
        },
      },
    ],
  },
});

serwist.addEventListeners();
```

### 3. Manifest.json — public/manifest.json

```json
{
  "name": "Nome do Site",
  "short_name": "NomeCurto",
  "description": "Descrição para SEO e PWA",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#E65100",
  "orientation": "portrait-primary",
  "categories": ["shopping", "automotive"],
  "lang": "pt-BR",
  "scope": "/",
  "icons": [
    { "src": "/icons/icon-192x192.svg", "sizes": "192x192", "type": "image/svg+xml", "purpose": "any maskable" },
    { "src": "/icons/icon-512x512.svg", "sizes": "512x512", "type": "image/svg+xml", "purpose": "any maskable" },
    { "src": "/icons/icon-192x192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable" },
    { "src": "/icons/icon-512x512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }
  ],
  "screenshots": [],
  "shortcuts": [
    {
      "name": "Ver Produtos",
      "short_name": "Produtos",
      "url": "/",
      "icons": [{ "src": "/icons/icon-192x192.png", "sizes": "192x192", "type": "image/png" }]
    }
  ]
}
```

> SVG icons são o formato moderno — Chrome, Firefox, Samsung Internet todos suportam. PNG continua necessário para iOS (Safari) e Android < 8.

### 3b. Favicon.ico + Favicon.svg + Apple-touch-icon

Além do manifest, incluir no `<head>` via Next.js metadata `icons:`:

```ts
// src/app/layout.tsx
export const metadata: Metadata = {
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/favicon.svg", type: "image/svg+xml" },
    ],
    apple: [
      { url: "/icons/icon-192x192.png", sizes: "192x192", type: "image/png" },
    ],
  },
};
```

#### Gerando favicon.ico programaticamente (sem sharp/canvas)

O formato ICO é um container de imagens PNG/BMP. Script Node.js puro:

```js
// gen-favicon.js — usa zlib (stdlib) para gerar ICO multi-tamanho
const { writeFileSync } = require("fs");
const zlib = require("zlib");

function createPNG(size, hexR, hexG, hexB, radius) {
  // Cria PNG RGBA com círculo central
  const raw = Buffer.alloc(size * size * 4);
  const cx = size / 2, cy = size / 2;
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const idx = (y * size + x) * 4;
      const dist = Math.sqrt((x - cx) ** 2 + (y - cy) ** 2);
      const r = size * radius;
      if (dist <= r + 2) {
        raw[idx] = hexR; raw[idx+1] = hexG; raw[idx+2] = hexB; raw[idx+3] = 255;
      } else {
        raw[idx] = 0; raw[idx+1] = 0; raw[idx+2] = 0; raw[idx+3] = 0;
      }
    }
  }
  // ... PNG chunks (IHDR, IDAT with zlib, IEND)
  // ver implementação completa no histórico: favicon.ico (Python) ou gen-icons.cjs
}

function createICO(sizes) {
  // Container ICO: header + DIR entries + PNG data
  // ICO header: reserved(2) + type(2=ico) + count(2)
  // DIR entry: w, h, colors, reserved, planes, bpp, size, offset
}

// Gerar para 16, 32, 48, 64px
for (const size of [16, 32, 48, 64]) {
  const png = createPNG(size, 26, 26, 26, 0.42);
  sizes.push({ size, data: png });
}
writeFileSync("public/favicon.ico", createICO(sizes));
```

Para `favicon.svg`, criar SVG simples:

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="6" fill="#1A1A1A"/>
  <text x="16" y="18" font-family="Arial, sans-serif" font-weight="900" font-size="16"
        fill="#E65100" text-anchor="middle" dominant-baseline="central">CC</text>
</svg>
```

### Cache headers no next.config

```ts
async headers() {
  return [
    {
      source: "/icons/:path*",
      headers: [{ key: "Cache-Control", value: "public, max-age=31536000, immutable" }],
    },
    {
      source: "/banners/:path*",
      headers: [{ key: "Cache-Control", value: "public, max-age=86400" }],
    },
    {
      source: "/:all(favicon)\\.(ico|svg)",
      headers: [{ key: "Cache-Control", value: "public, max-age=31536000, immutable" }],
    },
    {
      source: "/manifest.json",
      headers: [{ key: "Cache-Control", value: "public, max-age=86400" }],
    },
  ];
}

### 4. Layout — referenciar o manifest

O layout já deve linkar o manifest. Em Next.js App Router, usar `metadata.manifest`:

```ts
// src/app/layout.tsx
export const metadata: Metadata = {
  manifest: "/manifest.json",
  // ...
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#E65100",
};
```

## Verificação

Após o deploy, testar:

1. **Lighthouse** — DevTools > Lighthouse > PWA — deve passar todos os checks
2. **Install prompt** — Chrome mobile > deve aparecer "Adicionar à tela inicial"
3. **Offline** — DevTools > Network > Offline — recarregar, deve mostrar conteúdo em cache
4. **Manifest** — DevTools > Application > Manifest — ícones, shortcuts, cores

## Debug

Se o service worker não registrar:
- Verificar se `public/sw.js` foi gerado no build (`next build` gera automaticamente)
- Verificar se o `swSrc` path está correto
- No DevTools > Application > Service Workers, ver se está "activated"
