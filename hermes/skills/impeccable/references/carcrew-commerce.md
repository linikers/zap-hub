# CarCrew Commerce — Brand Design Reference

## Brand DNA
- Suspensão automotiva — peças para carros rebaixados, air lift, off-road
- Público: mecânicos, entusiastas, donos de oficina
- Tom: direto, profissional, brasileiro, sem frescura
- Antirreferências: clean demais, minimalista, "loja genérica"

## Cores
| Token | Hex | Uso |
|-------|-----|-----|
| Primary (laranja) | `#E65100` | CTAs, links, headings, detalhes |
| Secondary (preto) | `#1A1A1A` | Texto principal, footer, nav |
| Tertiary | `#333333` | Subtítulos |
| Surface | `#ffffff` | Cards, header bg |
| Neutral | `#FAFAFA` | Fundo de página, search row |
| WhatsApp | `#25D366` | Botão WhatsApp |
| Logo orange | `#ff6a00` | Glow/texto do logo hexagonal |
| Logo white | `#fff` | Texto "CREW" no logo |

## Logo (CarCrewLogo — componente React)
- **Formato:** Hexágono via `clipPath: polygon(20% 0%, 80% 0%, 100% 50%, 80% 100%, 20% 100%, 0% 50%)`
- **Fonte:** Orbitron 900 (via `next/font/google`, variável `--font-orbitron`)
- **Estrutura:** Outer box preto + inner box (borda branca) + texto
- **Texto:** "CAR" (laranja #ff6a00), "CREW" (branco), "GARAGE" (laranja)
- **Glow/text-shadow:** Sutil — `0 0 2px, 0 0 4px` apenas
- **Padding/Border externo:** `{ xs: 2, md: 3.2 }`, borda preta `{ xs: "4px", md: "6px" }`
- **Padding/Border interno:** `{ xs: 2, md: 3.2 }`, borda branca `{ xs: "3px", md: "5px" }`
- **Font sizes (xs/md):** CAR `22/58`, CREW `29/72`, GARAGE `18/42`
- **Posição no header:** Centralizado (flexbox com flex:1 dos dois lados)
- **Link:** Envolto em `<Link href="/">`

## Header Layout (atualizado Jul/2026)
```
┌──────────────────────────────────────────────┐
│        [    LOGO HEXAGONAL    ]   👤  🛒   │  ← Row 1: 56-64px
│  ───────────────────────────────────────────  │
│     🔍  O que deseja procurar?              │  ← Row 2: search própria
│  ───────────────────────────────────────────  │
│  Cat1 | Cat2 | … | +Cats (centralizados)    │  ← Row 3: nav escura, lg+
└──────────────────────────────────────────────┘
                                          ┌────┐
                                          │ 💬 │  ← FAB WhatsApp fixo
                                          └────┘
```

### Row 3: Nav de categorias
- **Container**: `maxWidth="xl"` (1536px) para caber 11 categorias + "+ Categorias"
- **Breakpoint**: `display: { xs: "none", lg: "block" }` — nav só aparece ≥1200px; abaixo, hamburger + Drawer
- **Hamburger**: `display: { xs: "flex", lg: "none" }` — drawer lateral c/ categorias, conta, WhatsApp
- **Centering**: categorias em `<Box flex:1 justifyContent:"center">`, WhatsApp em `<Button flexShrink:0>`
- **WhatsApp removido da nav**: agora é FAB flutuante `position:fixed, bottom:24px, right:24px, zIndex:1300`
- **Padding responsivo**: `px: { lg: 1.25, xl: 2 }` nos botões de categoria
- **Sem overflowX no Box externo** — era a causa do menu "solto" no scroll
- **Sem minWidth:fit-content** — empurrava conteúdo e quebrava layout

## Design Principles (CarCrew-specific)
1. **OUSADO > contido.** Hexágono, neon glow, preto-e-laranja. Logo grande centralizado.
2. **Efeitos sutis, não exagerados.** Glow 2-4px, hexágono largo (20/80).
3. **Componentização.** Se o usuário fornecer código exato, implementar fielmente.
4. **MUI v9.** Usar `slotProps`, não `PaperProps`. `next/font/google` para fontes.
5. **Busca em linha própria**, abaixo do logo. Focus ring laranja.

## Sistema de Banners

### Schema Prisma
```prisma
model Banner {
  id         Int      @id @default(autoincrement())
  titulo     String
  subtitulo  String?
  imgDesktop String?   // URL relativa (ex: /banners/banner1-desktop.svg)
  imgMobile  String?   // URL relativa (ex: /banners/banner1-mobile.svg)
  link       String?
  corFundo   String   @default("#1A1A1A") @map("cor_fundo")
  corTexto   String   @default("#ffffff") @map("cor_texto")
  ativo      Boolean  @default(true)
  ordem      Int      @default(0)
}
```

### Como adicionar banner
1. Coloque a imagem em `public/banners/`
2. Insira no banco via API (`POST /api/admin/banners`) ou via script Prisma direto
3. O frontend lê banners ativos e renderiza carrossel automático com navegação e dots
4. Se `imgDesktop` estiver preenchido, usa a imagem; senão, usa `corFundo` como fallback

### API de banners
- `GET /api/admin/banners` — lista todos
- `POST /api/admin/banners` — criar novo (body: `{titulo, subtitulo?, imgDesktop?, imgMobile?, link?, corFundo?, corTexto?, ativo?, ordem?}`)
- `PUT /api/admin/banners/[id]` — atualizar
- `DELETE /api/admin/banners/[id]` — remover

### Admin UI
- Painel em `/admin/banners` com CRUD completo + **upload de imagem via Cloudinary**
- Campos: título, subtítulo, link, imgDesktop (upload Cloudinary + URL manual), imgMobile, cores, toggle ativo
- Preview em miniatura na tabela de listagem
- Cloudinary: cloud `drvnlgib2`, preset `carcrew` (componente `CloudinaryUpload` existente)

## Stack & Deploy

- Repo: `github.com/linikers/carCrewCommerce`
- Host: Vercel (Next.js 15 + MUI v9 + Prisma 7)
- Banco: PostgreSQL via Neon.tech (connection pooling)
- Imagens: Cloudinary (`drvnlgib2`, preset `carcrew`)
- WhatsApp: (44) 99813-3182

### Vercel serverless — armadilha de filesystem

**NUNCA usar `fs.writeFileSync` em API routes.** Vercel serverless tem filesystem **read-only**.
`writeFileSync` falha silenciosamente e retorna 500 genérico. O erro NÃO aparece nos logs do Vercel.

**Solução:** sempre usar Prisma/PostgreSQL para persistência. O banco Neon.tech já está configurado via `POSTGRES_PRISMA_URL`. Use `prisma.configuracao.upsert()` para key-value stores (ver `src/app/api/admin/pagamentos/route.ts` como exemplo).

Model de key-value genérico (já existe no schema):
```prisma
model Configuracao {
  chave String @id
  valor Json
  @@map("configuracoes")
}
```

## SEO Keywords (Local + Produto)

Prioridade para rankeamento Google — incluir em meta tags, headings, e texto visível:

| Categoria | Keywords |
|---|---|
| **Local** | oficina suspensão Maringá, peças suspensão Maringá, rebaixados Maringá |
| **Produto** | suspensão a ar, suspensão fixa, suspensão rosca, coilover, air lift, bolsa de ar |
| **Serviço** | veículos rebaixados, customização automotiva, rebaixamento, kit suspensão |
| **Marca** | Car Crew Garage, carcrew suspensões |
| **Peças** | amortecedores, molas, calço antirruído, ponta de eixo, bandejas, compressores |

A home page (`page.tsx`) é `"use client"` — conteúdo renderizado via JS. Googlebot executa JS, mas o texto inicial do HTML é mínimo. Para garantir indexação:
- Manter seção SEO com `<Typography>` abaixo do Footer
- Meta keywords no `layout.tsx` com todas as keywords acima
- Página `/sobre` tem conteúdo estático rico — manter atualizada
- Banco: Neon.tech (POSTGRES_PRISMA_URL em .env.local)

### Noindex em páginas sem valor SEO

Páginas que NÃO devem ser indexadas (adicionar `layout.tsx` com `robots: { index: false }`):
- `/conta` — página de conta do usuário
- `/login` — página de login
- `/register` — página de cadastro
- `/checkout` — página de checkout

Pattern: criar `src/app/<rota>/layout.tsx`:
```tsx
import type { Metadata } from "next";
export const metadata: Metadata = {
  robots: { index: false, follow: false },
};
export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
```

### Google Search Console — Diagnóstico de indexação

Ferramentas ativas no projeto:
- **Search Console**: carcrew.com.br cadastrado (acessar: `search.google.com/search-console`)
- **Google Business Profile**: Car Crew Garage, 5.0★ 121 avaliações, endereço em Maringá/PR
- **Google Analytics (GA4)**: ID `G-6YMBYX21SF`

Problema comum: páginas "Detectada, mas não indexada no momento" (50+ páginas).
Causas típicas:
1. Páginas funcionais (conta/login/checkout) descobertas via links internos → resolver com `noindex`
2. Páginas de produto com pouco conteúdo → melhorar descrições e conteúdo
3. URLs de filtro/busca com query params → usar `canonical` na home

Após aplicar correções no site, ir em Indexação → Páginas → "Validar correção" no Search Console.
