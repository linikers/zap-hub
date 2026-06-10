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

## Header Layout
```
┌──────────────────────────────────────────────┐
│        [    LOGO HEXAGONAL    ]   👤  🛒   │  ← Row 1: 56-64px
│  ───────────────────────────────────────────  │
│     🔍  O que deseja procurar?              │  ← Row 2: search própria
│  ───────────────────────────────────────────  │
│  Cat1 | Cat2 | … | +Cats | [💬 WhatsApp]   │  ← Row 3: nav escura
└──────────────────────────────────────────────┘
```

## Design Principles (CarCrew-specific)
1. **OUSADO > contido.** Hexágono, neon glow, preto-e-laranja. Logo grande centralizado.
2. **Efeitos sutis, não exagerados.** Glow 2-4px, hexágono largo (20/80).
3. **Componentização.** Se o usuário fornecer código exato, implementar fielmente.
4. **MUI v9.** Usar `slotProps`, não `PaperProps`. `next/font/google` para fontes.
5. **Busca em linha própria**, abaixo do logo. Focus ring laranja.

## Projetos Relacionados
- Repo: `github.com/linikers/carCrewCommerce` — Vercel deploy, carcrew.com.br
- Stack: Next.js 15, MUI v9, Prisma 7, PostgreSQL (Neon)
- WhatsApp: (44) 99813-3182
