# Next.js SEO — Full Guide (absorbed from nextjs-seo skill)

## Metadata API

Always in `layout.tsx` root (or per-page via `generateMetadata`):

```ts
import type { Metadata } from "next";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "https://seudominio.com.br"),
  title: {
    default: "Nome da Loja — Descrição Curta",
    template: `%s | Nome da Loja`,
  },
  description: "Descrição com 150-160 caracteres para SEO.",
  keywords: ["palavra1", "palavra2"],
  authors: [{ name: "Nome da Empresa" }],
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};
```

**`metadataBase` é obrigatório** para resolução correta de URLs canônicas e OG image.

## Open Graph & Twitter Cards

```ts
openGraph: {
  type: "website",
  locale: "pt_BR",
  siteName: "Nome da Loja",
  title: "Título para Compartilhamento",
  description: "Descrição do compartilhamento",
  url: siteUrl,
  images: [{
    url: "/og-image.jpg",   // 1200x630px obrigatório
    width: 1200,
    height: 630,
    alt: "Nome da Loja",
  }],
},
twitter: {
  card: "summary_large_image",
  title: "Título no Twitter",
  description: "Descrição no Twitter",
  images: ["/og-image.jpg"],
},
```

**Imagem OG**: 1200x630px, proporção 1.91:1. Sem redimensionamento automático pelo Next.js.

## Favicon — Next.js Metadata API

```ts
export const metadata: Metadata = {
  icons: {
    icon: [
      { url: "/favicon/favicon.ico", sizes: "any" },
      { url: "/favicon/favicon-16x16.png", sizes: "16x16", type: "image/png" },
      { url: "/favicon/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon/favicon.svg", type: "image/svg+xml" },
    ],
    apple: [
      { url: "/favicon/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
    ],
  },
};
```

Cache headers (next.config.ts):
```ts
async headers() {
  return [{
    source: "/favicon/:path*",
    headers: [
      { key: "Cache-Control", value: "public, max-age=31536000, immutable" },
    ],
  }];
}
```

## Google Search Console

### DNS (recomendado)
No Search Console, escolher "DNS TXT record". Vantagem: funciona independente do site.

### Meta Tag
```ts
verification: {
  google: process.env.NEXT_PUBLIC_GOOGLE_VERIFICATION || "",
},
```

## Google Analytics / Google Ads (gtag.js)

```tsx
import Script from "next/script";

<Script
  src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"
  strategy="afterInteractive"
/>
<Script id="google-analytics" strategy="afterInteractive">
  {`
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-XXXXXXXXXX');
  `}
</Script>
```

## JSON-LD Structured Data

### Store (home/loja)
```tsx
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{
    __html: JSON.stringify({
      "@context": "https://schema.org",
      "@type": "Store",
      name: "Nome da Loja",
      image: `${siteUrl}/og-image.jpg`,
      url: siteUrl,
      telephone: "(44) 99999-9999",
      address: {
        "@type": "PostalAddress",
        streetAddress: "Rua, número - Bairro",
        addressLocality: "Cidade",
        addressRegion: "UF",
        postalCode: "CEP",
        addressCountry: "BR",
      },
      sameAs: ["https://www.instagram.com/...", "https://www.facebook.com/..."],
    }),
  }}
/>
```

### Product (página de produto)
```tsx
const sobConsulta = !produto.preco || produto.preco <= 0;

<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{
    __html: JSON.stringify({
      "@context": "https://schema.org",
      "@type": "Product",
      name: produto.nome,
      description: produto.descricao,
      image: produto.imgUrl ? [produto.imgUrl] : [`${siteUrl}/og-image.jpg`],
      category: categoria?.nome || produto.category,
      sku: String(produto.id),
      brand: { "@type": "Brand", name: "Nome da Marca" },
      url: `${siteUrl}/produto/${produto.id}`,
      offers: {
        "@type": "Offer",
        price: sobConsulta ? "0" : produto.preco.toFixed(2),
        priceCurrency: "BRL",
        availability: sobConsulta
          ? "https://schema.org/InStoreOnly"
          : "https://schema.org/InStock",
        url: `${siteUrl}/produto/${produto.id}`,
        priceValidUntil: new Date(
          new Date().setFullYear(new Date().getFullYear() + 1)
        ).toISOString().split("T")[0],
        seller: { "@type": "Organization", name: "Nome da Loja" },
      },
    }),
  }}
/>
```

### BreadcrumbList
```tsx
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{
    __html: JSON.stringify({
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      itemListElement: [
        { "@type": "ListItem", position: 1, name: "Home", item: siteUrl },
        ...(categoria ? [
          { "@type": "ListItem", position: 2, name: categoria.nome },
        ] : []),
        { "@type": "ListItem", position: categoria ? 3 : 2, name: produto.nome },
      ],
    }),
  }}
/>
```

## Server Component × Client Component split

Pages need dynamic metadata (OG, title) + interactive UI (cart, gallery). `generateMetadata` only works in **Server Components**.

**Pattern:** Server Component wrapper + Client Component child

- Server Component: `generateMetadata()` + JSON-LD + data loading + passes as props
- Client Component: `"use client"` + interactive UI (no fetch — receives props)

Rules:
- `generateMetadata` returns ONLY the name (template in layout adds store name)
- Cloudinary URLs go direct in OG (don't concat with siteUrl)

## Sitemap

### Approach A — API HTTP
```ts
import type { MetadataRoute } from "next";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://seudominio.com.br";
  const staticRoutes = [ /* ... */ ];
  let productRoutes: MetadataRoute.Sitemap = [];
  try {
    const res = await fetch(`${siteUrl}/api/produtos`);
    if (res.ok) {
      const produtos = await res.json();
      productRoutes = produtos.map((p: any) => ({
        url: `${siteUrl}/produto/${p.id}`,
        lastModified: new Date(),
        changeFrequency: "weekly" as const,
        priority: 0.8,
      }));
    }
  } catch { /* API not available during build */ }
  return [...staticRoutes, ...productRoutes];
}
```

### Approach B — readFileSync (works offline)
```ts
export default function sitemap(): MetadataRoute.Sitemap {
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://seudominio.com.br";
  const staticRoutes: MetadataRoute.Sitemap = [
    { url: siteUrl, lastModified: new Date(), changeFrequency: "weekly", priority: 1.0 },
  ];
  const productRoutes: MetadataRoute.Sitemap = [];
  try {
    const filePath = path.join(process.cwd(), "src/data/produtos.json");
    if (existsSync(filePath)) {
      const produtos = JSON.parse(readFileSync(filePath, "utf-8"));
      for (const p of produtos) {
        if (p.ativo !== false) {
          productRoutes.push({
            url: `${siteUrl}/produto/${p.id}`,
            lastModified: new Date(),
            changeFrequency: "weekly",
            priority: 0.8,
          });
        }
      }
    }
  } catch { /* fallback */ }
  return [...staticRoutes, ...productRoutes];
}
```

## robots.txt

```ts
import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: "/admin/",
    },
    sitemap: `${process.env.NEXT_PUBLIC_SITE_URL || "https://seudominio.com.br"}/sitemap.xml`,
  };
}
```

## PWA / Service Worker (Serwist + Turbopack)

```ts
// next.config.ts
import withSerwistInit from "@serwist/next";

const nextConfig: NextConfig = {
  turbopack: {},  // ← NEEDED for Next.js 16 + Serwist
};

const serwistConfig = {
  swSrc: "src/sw.ts",
  swDest: "public/sw.js",
  globPatterns: ["**/*.{js,css,html,json,ico,png,svg,jpg,jpeg,webp,avif}"],
  globIgnores: ["/admin/**", "/api/**", "/sw.js"],
};

export default withSerwistInit(serwistConfig)(nextConfig);
```

Service Worker (src/sw.ts):
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
});

serwist.addEventListeners();
```

## OG Image Generation (Python/Pillow)

```python
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
img = Image.new("RGB", (W, H), "#E65100")
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
except:
    font = ImageDraw.ImageFont.load_default()
    font_sub = font

text = "Nome da Loja"
bbox = draw.textbbox((0, 0), text, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx = (W - tw) // 2
ty = (H - th) // 2 - 20
draw.text((tx, ty), text, font=font, fill=(255, 255, 255))
```

### Split layout (wide banner → OG)
```python
banner = Image.open("public/meu-banner.jpg")
bw, bh = banner.size
og = Image.new("RGB", (1200, 630), "#ffffff")
draw = ImageDraw.Draw(og)
scale = 1200 / bw
new_h = int(bh * scale)
banner_resized = banner.resize((1200, new_h), Image.LANCZOS)
og.paste(banner_resized, (0, 0))
draw.rectangle([(0, new_h), (1200, 630)], fill="#1a1a1a")
```

## E-commerce SEO Audit (13 steps)

1. Check live meta tags (home + product page)
2. Check sitemap (products included?)
3. Check robots.txt
4. Check JSON-LD (Store + Product)
5. Check Google Search Console DNS verification
6. Check prices (R$0 products don't generate rich results)
7. Check Client Component barrier
8. Check canonical tags
9. Check image alt text
10. Check performance (PageSpeed Insights)
11. Check image optimization (see nextjs-mui Image Optimization section)
12. Check title template duplication
13. Check sitemap approach (fetch vs readFileSync)

### Severity classification
- **P0 Critical**: blocks indexing, sitemap, or metadata
- **P1 High**: affects rich results, social sharing, canonical
- **P2 Medium**: improves overall quality
- **P3 Low**: strategic/long-term

## Pitfalls

- `metadataBase` forgotten → OG URLs break in production
- OG image wrong format → 1200×630 ALWAYS, 1.91:1
- GA with `<script>` → use `<Script>` with `strategy="afterInteractive"`
- `useSearchParams()` without Suspense boundary (Next.js 16+) → build fails
- `title.template` + generateMetadata with site name → "Produto | Loja | Loja"
- `readFileSync` in Server Component with Turbopack → warning (works, safe to ignore)
- OG images with absolute URL + siteUrl → double URL concatenation
- Sitemap with fetch that depends on DB → fails silently during build
