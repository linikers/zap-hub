# Banner Admin + Homepage Carousel

## Overview

Dynamic banners managed via admin panel and displayed as a carousel on the homepage.

## Data Layer

```json
// src/data/banners.json
[
  {
    "id": 1,
    "titulo": "Banner Title",
    "subtitulo": "Subtitle text",
    "imgDesktop": "/banners/banner1-desktop.svg",
    "imgMobile": "/banners/banner1-mobile.svg",
    "link": "/produto/1",
    "corFundo": "#1A1A1A",
    "corTexto": "#ffffff",
    "ativo": true,
    "ordem": 1
  }
]
```

### Lib Helpers
Create `src/lib/banners-admin.ts` with: `lerBanners()`, `salvarBanners()`, `proximoId()` — same pattern as other JSON-file CRUDs.

## API Routes

```
GET    /api/admin/banners          → list all
POST   /api/admin/banners          → create (requires titulo)
PUT    /api/admin/banners/[id]     → update
DELETE /api/admin/banners/[id]     → delete
```

## Admin Page (`/admin/banners`)

Tabela com colunas: Ordem, Título, Cor de fundo (chip colorido), Link, Ativo (chip), Ações (editar/excluir).

Modal único para criar/editar: título, subtítulo, link, cor fundo, cor texto, ativo.

## Homepage Carousel

Fetch banners from API, filter ativos, display as carousel:

```tsx
const [banners, setBanners] = useState([]);
const [bannerIndex, setBannerIndex] = useState(0);
const theme = useTheme();
const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

useEffect(() => {
  fetch("/api/admin/banners")
    .then(r => r.json())
    .then(data => setBanners(data.filter(b => b.ativo)))
    .catch(() => {});
}, []);

// Navigation
const anterior = () => setBannerIndex(i => i === 0 ? banners.length - 1 : i - 1);
const proximo = () => setBannerIndex(i => i === banners.length - 1 ? 0 : i + 1);

// Auto-play (5s)
useEffect(() => {
  if (banners.length <= 1) return;
  const timer = setInterval(proximo, 5000);
  return () => clearInterval(timer);
}, [banners.length, bannerIndex]);
```

### Carousel UI

- Background color matches `banners[bannerIndex].corFundo`
- Shows `imgMobile` on mobile (`isMobile` via `useMediaQuery`), `imgDesktop` on desktop
- Image fills entire banner area via `position: absolute; object-fit: cover; inset: 0`
- Navigation arrows (left/right) in semi-transparent circles
- Indicators: row of dots at bottom, active dot wider (24px), inactive 10px
- Smooth transition on background-color change

### SVG Banner Images

Create `public/banners/` directory with desktop (1200x400) and mobile (400x350) SVGs.
Naming convention: `banner{N}-desktop.svg` and `banner{N}-mobile.svg`.
