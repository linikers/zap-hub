# React / MUI Polish Patterns

Concrete code patterns found across real React+MUI projects. Apply during the polish phase of a project overhaul.

## Theme Typos & Fixes

### Missing `#` in hex colors
```tsx
// WRONG — no `#` prefix
color: '63768D',
color: '#55971',  // also invalid (5 chars)

// RIGHT
color: '#63768D',
color: '#554971',
```

### Property name swapped
```tsx
// WRONG — transition value is actually a boxShadow
transition: '0px 3px 6px rgba(0, 0, 0, 0.1)',

// RIGHT
boxShadow: '0px 3px 6px rgba(0, 0, 0, 0.1)',
```

### Duplicate property (last wins, first is dead code)
```tsx
// WRONG — first boxShadow is silently overridden
boxShadow: '0px 3px 6px rgba(0, 0, 0, 0.1)',
boxShadow: '0px 5px 10px rgba(0, 0, 0, 0.2)',

// RIGHT
boxShadow: '0px 5px 10px rgba(0, 0, 0, 0.2)',
```

## Dark Theme Contrast

On dark backgrounds (#36213E, #1A1A2E), text needs sufficient contrast:

| Role | Wrong (too dim) | Right (readable) |
|------|-----------------|------------------|
| `text.primary` | `#63768D`, `#554971` | `#B8F3FF`, `#E0E0E0` |
| `text.secondary` | `#554971` | `#8AC6D0`, `#90CAF9` |

Rule of thumb: on a very dark bg, primary text should be ≥ #B0B0B0, secondary ≥ #808080. Test with WCAG contrast checkers.

## Skeleton Over "Carregando..."

Replace bare `<Typography>Carregando...</Typography>` with MUI `Skeleton`:

```tsx
import { Skeleton } from "@mui/material";

// Instead of:
{loading && <Typography>Carregando...</Typography>}

// Do:
{loading && (
  <Box sx={{ width: "80%", maxWidth: 600 }}>
    <Skeleton variant="text" width="60%" height={40}
      sx={{ bgcolor: "rgba(184,243,255,0.1)", mb: 2 }} />
    <Skeleton variant="rounded" height={120}
      sx={{ bgcolor: "rgba(184,243,255,0.1)", mb: 1 }} />
  </Box>
)}
```

For dark themes, tint Skeleton with `rgba(themeColor, 0.1)` instead of default gray.

## prefers-reduced-motion

Add to global CSS to respect accessibility preferences:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Transition Easing

Use `ease-out` for natural deceleration (feels smoother than default `ease`):

```tsx
// WRONG
transition: "transform 0.2s, box-shadow 0.2s",

// RIGHT
transition: "transform 0.2s ease-out, box-shadow 0.2s ease-out",
```

## Blinking/Flickering Animations → Float

Replace infinite opacity-blink animations with subtle float/translate:

```tsx
// WRONG — magenta blink
const blinkAndChangeColor = keyframes`
  0% { opacity: 1; color: #ff00ff; }
  50% { opacity: 0.5; color: #ff00ff; }
  100% { opacity: 1; color: #ff00ff; }
`;

// RIGHT — subtle float
const float = keyframes`
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-6px); }
`;
```

## Glassmorphism → Clean Solid

Replace default glass/blur cards with solid backgrounds + subtle shadows:

```css
/* WRONG — glass as default */
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
}

/* RIGHT — clean solid */
.glass-card {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.2s ease-out;
}
.glass-card:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}
```

### When glassmorphism IS the right choice

Glassmorphism becomes purposeful, not default, when:
- The surface is a **hero/destaque** section (not a list of 20 identical items)
- The background behind the card has movement or depth (gradient, particles, canvas)
- The blur creates a **depth-of-field** effect that enhances the visual hierarchy

Example for a "hero" card with purposeful glassmorphism:

```tsx
<Card sx={{
  background: "rgba(255,255,255,0.02)",
  backdropFilter: "blur(8px)",
  border: "1px solid",
  borderColor: "divider",
  borderRadius: 3,
  transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
  "&:hover": {
    borderColor: "primary.main",
    transform: "translateY(-4px)",
    boxShadow: "0 8px 30px rgba(0,0,0,0.3), 0 0 20px rgba(34,211,238,0.08)",
  },
}}>
```

Key differences from anti-pattern glassmorphism:
- `blur(8px)` not `blur(12px)` — subtle, not heavy
- Glow on hover only — not constantly lit
- Paired with a dark background that has depth (gradient, particles, etc.)
- Used on 2-6 hero cards, never on a list of 20

## "AI Vibe" Banner: Canvas Neural Network Particles

When the user wants an "AI aesthetic" (not retro terminal, not SaaS cream), a subtle canvas particle network in the navbar/banner strikes the right balance: tech-forward without being gimmicky.

```tsx
// Navbar with neural network particle banner
<AppBar position="sticky" sx={{ background: "transparent", backdropFilter: "blur(12px)" }}>
  {/* Neural network particle strip */}
  <Box sx={{ height: 48, overflow: "hidden", position: "relative",
    background: "linear-gradient(90deg, rgba(34,211,238,0.05), rgba(168,85,247,0.05))" }}>
    <canvas ref={canvasRef} width={1280} height={48}
      style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }} />
    <Typography sx={{ fontFamily: "monospace", fontSize: "0.65rem", opacity: 0.6,
      position: "absolute", inset: 0, display: "flex", alignItems: "center",
      justifyContent: "center", pointerEvents: "none" }}>
      ▸ neural.network.active
    </Typography>
  </Box>
  {/* Nav links below */}
  <Toolbar>...</Toolbar>
</AppBar>
```

Canvas animation: 30 particles drifting horizontally, connected by thin lines when within 100px radius. Uses `requestAnimationFrame`. Keep the animation subtle — low alpha (0.2-0.5), thin lines (0.5px), slow drift (0.15-0.3 px/frame).

This pattern coexists well with retro terminal themes because:
- The particles use the theme's primary/accent color
- Monospace typography grounds it in terminal aesthetic
- The canvas is contained in a thin banner strip, not full-page
- It signals "AI/tech" without overwhelming the retro identity

Give buttons smooth hover transitions — the theme `MuiButton` overrides are the right place:

```tsx
components: {
  MuiButton: {
    styleOverrides: {
      root: {
        transition: 'transform 0.2s ease-out, box-shadow 0.2s ease-out',
        '&:hover': {
          transform: 'translateY(-2px)',
          // Remove duplicate boxShadow here — inherited from root
        },
      },
    },
  },
}
```

## Responsive Nav Buttons

On mobile, navigation buttons should be full-width for better touch targets:

```tsx
<Button fullWidth={true} sx={{ /* ... */ }}>
```

## Snackbar sobre alert()

Substitua `alert()` nativos por um sistema de snackbar global com Context API:

```tsx
// contexts/SnackbarContext.tsx
import { createContext, useContext, useState, useCallback, ReactNode } from "react";
import { Snackbar, Alert, AlertColor } from "@mui/material";

interface SnackbarContextType {
  showSnackbar: (message: string, severity?: AlertColor) => void;
}

const SnackbarContext = createContext<SnackbarContextType>({ showSnackbar: () => {} });

export function SnackbarProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [severity, setSeverity] = useState<AlertColor>("info");

  const showSnackbar = useCallback((msg: string, sev: AlertColor = "info") => {
    setMessage(msg);
    setSeverity(sev);
    setOpen(true);
  }, []);

  return (
    <SnackbarContext.Provider value={{ showSnackbar }}>
      {children}
      <Snackbar open={open} autoHideDuration={3000} onClose={() => setOpen(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}>
        <Alert onClose={() => setOpen(false)} severity={severity} variant="filled">
          {message}
        </Alert>
      </Snackbar>
    </SnackbarContext.Provider>
  );
}

export function useSnackbar() {
  return useContext(SnackbarContext);
}
```

Wrap no `_app.tsx`:

```tsx
<ThemeProvider theme={theme}>
  <CssBaseline />
  <SnackbarProvider>
    <Component {...pageProps} />
  </SnackbarProvider>
</ThemeProvider>
```

Uso em qualquer componente:

```tsx
// ANTES
alert("Erro ao salvar");
alert("Sucesso!");

// DEPOIS
const { showSnackbar } = useSnackbar();
showSnackbar("Erro ao salvar", "error");
showSnackbar("Sucesso!", "success");
```

Disponivel em QUALQUER componente dentro da arvore do _app — sem prop drilling.

## Dialog em temas escuros

Em temas dark com fundo gradiente, dialogs ficam dificeis de ler. Use fundo **solido** em vez de gradiente:

```tsx
// RUIM — gradiente cria ruido visual, texto dificil de ler
<Dialog PaperProps={{
  sx: { background: "linear-gradient(135deg, #36213E 0%, #554971 100%)" }
}}>

// BOM — fundo solido escuro, muito mais legivel
<Dialog PaperProps={{
  sx: { background: "#2D1B36" }  // tom unico, sem gradiente
}}>
```

Regra: dialogs = solidos. Gradientes reservados para backgrounds de pagina.

## Multi-submissao em dialogs

Quando o usuario precisa cadastrar varios itens do mesmo tipo (ex: varios trabalhos do mesmo artista), o dialog deve:

1. **Nao fechar** apos submit bem-sucedido
2. **Manter** o campo do "pai" (ex: nome do artista) preenchido
3. **Resetar** so os campos do item atual (trabalho, categoria)
4. Mostrar **snackbar** de confirmacao em vez de alert

```tsx
// ANTES — fecha tudo, usuario recomeca do zero
if (res.ok) {
  setForm({ name: "", work: "", category: "" });
  closeDialog();
  alert("Cadastrado!");
}

// DEPOIS — mantem nome, limpa so o necessario, nao fecha
if (res.ok) {
  setForm(prev => ({ ...prev, work: "", category: "" }));
  showSnackbar("Cadastrado!", "success");
  // Dialog continua aberto
}
```

Isso permite cadastro rapido em serie sem retrabalho.

## MUI Select em temas escuros

Em temas dark, o dropdown do MUI Select (Menu/Popover) herda o background padrao do tema, que pode ser um gradient ou cor clara — resultando em texto ilegivel. **Sempre defina MenuProps explicitamente**:

```tsx
// RUIM — dropdown herda tema, pode ficar ilegivel
<Select value={value} onChange={handleChange} sx={{ color: "#B8F3FF" }}>
  <MenuItem value="1">Opcao 1</MenuItem>
</Select>

// BOM — MenuProps forcado com fundo solido escuro e texto claro
<Select
  value={value}
  onChange={handleChange}
  MenuProps={{
    PaperProps: {
      sx: {
        bgcolor: "#2D1B36",
        border: "1px solid rgba(184, 243, 255, 0.2)",
        "& .MuiMenuItem-root": {
          color: "#B8F3FF",
          "&:hover": { bgcolor: "rgba(184, 243, 255, 0.1)" },
          "&.Mui-selected": {
            bgcolor: "rgba(184, 243, 255, 0.15)",
            color: "#B8F3FF",
          },
        },
      },
    },
  }}
  sx={{ color: "#B8F3FF" }}
>
  <MenuItem value="1">Opcao 1</MenuItem>
</Select>
```

**Importante**: Nao use `SelectProps={{ native: true }}` em temas escuros — o dropdown nativo do navegador ignora o tema MUI e pode ficar ilegivel. Prefira MUI Select padrao com MenuProps customizado.

## Estado Independente por Card (Shared State Anti-Pattern)

Quando renderiza uma **lista de cards com sliders/forms/checkboxes**, cada card deve ter seu proprio estado. NUNCA compartilhe um unico estado entre todos os cards:

```tsx
// 🚫 RUIM — estado unico compartilhado, todos os cards afetados
function VotePage() {
  const [voteValues, setVoteValues] = useState({ anatomy: 5, creativity: 5 });
  // Mudar slider no card A altera o card B tambem!

  return users.map(user => (
    <CompetitorCard
      voteValues={voteValues}        // ← MESMO objeto pra todo mundo
      onSliderChange={handleSliderChange}  // ← MESMO handler
    />
  ));
}

// ✅ BOM — cada card gerencia seu proprio estado internamente
function CompetitorCard({ user }) {
  const [sliders, setSliders] = useState({ anatomy: 5, creativity: 5 });
  // Mexer neste card nao afeta nenhum outro card

  return (
    <VotingCriteria
      value={sliders.anatomy}
      onChange={(_, val) => setSliders(prev => ({ ...prev, anatomy: val }))}
    />
  );
}
```

**Sinais de alerta**:
- Voce tem um estado no pai que e passado como prop para varios filhos do mesmo tipo
- Mudar um controle em um filho afeta os outros
- Voce esta usando `index` como key em vez de um ID estavel (o React pode misturar estado)

**Regra**: se cada card precisa de valores INDEPENDENTES, o estado pertence ao card, nao ao pai. O pai so fornece dados de leitura (via props) e um callback opcional (`onVoteComplete`, `onSave`) para notificar resultados.

## useEffect com funcoes — Cuidado com Loop Infinito

Nunca coloque **funcoes definidas no corpo do componente** como dependencia do `useEffect` sem `useCallback`:

```tsx
// 🚫 RUIM — toda render cria uma nova funcao, useEffect dispara infinito
function VotePage() {
  function notify(msg) { /* ... */ }
  useEffect(() => { fetchData(); }, [notify]); // ← notify muda sempre → LOOP
}

// ✅ BOM — useCallback estabiliza a referencia
function VotePage({ onNotify }) {
  const notify = useCallback((msg) => {
    if (onNotify) onNotify(msg);
  }, [onNotify]);
  useEffect(() => { fetchData(); }, [notify]); // ← estavel, executa uma vez
}

// ✅ AINDA MELHOR — use o SnackbarContext em vez de prop drilling
function VotePage() {
  const { showSnackbar } = useSnackbar(); // ← showSnackbar e estavel (useCallback interno)
  useEffect(() => { fetchData(); }, [showSnackbar]); // ← seguro, sem loop
}
```

**Padrao**: prefira hooks de contexto (`useSnackbar()`) ou refs estaveis em vez de funcoes recriadas como dependencias de useEffect. Se precisar de uma funcao prop, use `useCallback`.

## Identity: Remove Commented Code

During polish, remove commented-out JSX blocks and dead imports. These are common leftovers:

```tsx
{/* <OldComponent prop="value" /> */}  // ← DELETE
// const [oldState, setOldState] = useState(false); // ← DELETE (commented code)
```

## MUI v9: slotProps em vez de PaperProps / slotProps

**MUI v6–v9 removeu `PaperProps`, `InputProps`, `MenuProps`, etc. em favor de `slotProps`.** Se o projeto usa MUI v6+ (verifique com `cat node_modules/@mui/material/package.json | grep version`), essas props vão dar erro de TS.

### Drawer

```tsx
// 🚫 MUI v5 — PaperProps
<Drawer PaperProps={{ sx: { width: 280 } }}>

// ✅ MUI v6+ — slotProps
<Drawer slotProps={{ paper: { sx: { width: 280 } } }}>
```

### Dialog

```tsx
// 🚫 MUI v5
<Dialog PaperProps={{ sx: { background: "#2D1B36" } }}>

// ✅ MUI v6+
<Dialog slotProps={{ paper: { sx: { background: "#2D1B36" } } }}>
```

### Menu

```tsx
// 🚫 MUI v5
<Menu
  anchorEl={anchorEl}
  PaperProps={{ sx: { borderRadius: 2 } }}
>

// ✅ MUI v6+
<Menu
  anchorEl={anchorEl}
  slotProps={{ paper: { sx: { borderRadius: 2 } } }}
>
```

### Select (MenuProps → slotProps)

O `Select` é mais aninhado — o dropdown é um Menu, então em MUI v6+ use `slotProps`:

```tsx
// 🚫 MUI v5
<Select
  MenuProps={{
    PaperProps: {
      sx: { bgcolor: "#2D1B36" },
    },
  }}
>

// ✅ MUI v6+ — duplo slotProps: Menu.slotProps → paper
<Select
  slotProps={{
    paper: { sx: { bgcolor: "#2D1B36" } },
  }}
>
```

> **Atenção:** Em MUI v9, `MenuProps` também some. Use `slotProps` diretamente no Select. Consulte a documentação da versão exata se houver ambiguidade — a árvore de slots pode variar entre v6, v7, v8 e v9.

### Regra geral

Se o LSP acusar `Property 'X' does not exist on type`, o nome antigo provavelmente virou `slotProps`:

| Antes (MUI v5) | Depois (MUI v6+) |
|----------------|-------------------|
| `PaperProps` | `slotProps={{ paper: { ... } }}` |
| `InputProps` | `slotProps={{ input: { ... } }}` |
| `MenuProps` | Inline no slot do componente pai |
| `PopperProps` | `slotProps={{ popper: { ... } }}` |

## MUI v9: Grid API — `item` / `xs` / `sm` removidos

**MUI v9 removeu as props `item`, `xs`, `sm`, `md`, `lg`, `xl` do Grid.** Agora Grid usa CSS Grid puro (não Flexbox). Para layouts de 2 colunas, substitua por `Box` com `flexWrap`:

```tsx
// 🚫 MUI v5 — props removidas no v9
<Grid container spacing={2}>
  <Grid item xs={12} sm={6}>...</Grid>
  <Grid item xs={12} sm={6}>...</Grid>
</Grid>

// ✅ MUI v9 — Box com flexWrap
<Box sx={{ display: "flex", flexWrap: "wrap", gap: 3 }}>
  <Box sx={{ flex: "1 1 200px" }}>...</Box>
  <Box sx={{ flex: "1 1 200px" }}>...</Box>
</Box>
```

Quando precisar de grid mais complexo (múltiplas colunas com breakpoints), use `display: "grid"` + `gridTemplateColumns`:

```tsx
<Box sx={{
  display: "grid",
  gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr", md: "1fr 1fr 1fr" },
  gap: 2,
}}>
  {items.map(item => <Box key={item.id}>{item.nome}</Box>)}
</Box>
```

## Next.js 15+: `params` e `searchParams` são `Promise`

A partir do Next.js 15, `params` e `searchParams` em rotas dinâmicas (App Router) são **Promises**. O mesmo vale para `useParams()`.

**Em Server Components (Route Handlers):**

```tsx
// 🚫 Next.js 14
export async function GET(_req: Request, { params }: { params: { id: string } }) {
  const { id } = params;
}

// ✅ Next.js 15+
export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
}
```

**Em Client Components (useParams):**

```tsx
// ✅ Next.js 15+
const params = useParams();
const id = params.id as string;  // useParams() retorna um objeto, não Promise
```

> Atenção: `useParams()` no cliente retorna objeto síncrono (não Promise). Já o `params` recebido em Server Components / Route Handlers é Promise e precisa de `await`.

## Checklist Quick Reference

Before final commit, run through:

- [ ] All `#` prefixes on hex colors present and valid (6 chars)
- [ ] No duplicate CSS properties
- [ ] No `transition` values that should be `boxShadow` (or vice versa)
- [ ] Text contrast OK on dark backgrounds (≥ #B0B0B0 for primary)
- [ ] "Carregando..." replaced with Skeleton
- [ ] `prefers-reduced-motion` added
- [ ] All transitions use `ease-out`
- [ ] No infinite blink/flicker animations — use float instead
- [ ] Glassmorphism only where purposeful, not default. When used: blur ≤8px, glow on hover only, max 6 hero cards.
- [ ] No commented-out JSX or dead code
- [ ] Buttons have smooth hover transitions
- [ ] Nav buttons `fullWidth={true}` on mobile (wrap + gap)
- [ ] No `alert()` calls — replaced with SnackbarProvider + useSnackbar
- [ ] Dialog backgrounds are solid (not gradient) on dark themes
- [ ] Multi-submit dialogs keep open & preserve parent fields
- [ ] External widget embeds (Pinterest, YouTube, Spotify) wrapped in white background box on dark themes

## External Widget Embeds in Dark Themes

Third-party embed widgets (Pinterest boards, YouTube players, Spotify, Twitter cards) ship their own CSS with light backgrounds. On a dark-themed MUI site, the widget's white/light background creates a harsh contrast break and often makes embedded UI controls invisible.

### Pattern: White Background Wrapper

Wrap the embed in a `<Box>` with explicit white background:

```tsx
<Paper elevation={0} sx={{ border: "1px solid", borderColor: "divider" }}>
  <Typography sx={{ fontFamily: "monospace", color: "primary.main", mb: 2 }}>
    ▸ Inspiration Board
  </Typography>
  <Box sx={{ bgcolor: "#ffffff", borderRadius: 2, p: 2, minHeight: 400 }}>
    {/* Pinterest / YouTube / Spotify embed goes here */}
  </Box>
</Paper>
```

Key rules:
- Outer card uses the site's theme (glassmorphism, dark border)
- Inner `<Box>` forces `bgcolor: "#ffffff"` — the widget's natural habitat
- `borderRadius` and `padding` create breathing room between embed and wrapper
- `minHeight` prevents layout shift while third-party script loads

### Pinterest embed

Load `pinit.js` via `useEffect` to avoid SSR hydration mismatch:
```tsx
useEffect(() => {
  const script = document.createElement("script");
  script.type = "text/javascript";
  script.async = true;
  script.src = "https://assets.pinterest.com/js/pinit.js";
  document.body.appendChild(script);
  return () => { document.body.removeChild(script); };
}, []);
```

The embed markup is a simple `<a>` tag the script hydrates:
```html
<a data-pin-do="embedBoard"
   data-pin-board-width="800"
   data-pin-scale-height="400"
   data-pin-scale-width="80"
   href="https://www.pinterest.com/username/board-name/" />
```

This pattern generalizes: the wrapper provides the correct background, the embed lives inside without CSS conflicts.
- [ ] External widget embeds (Pinterest, YouTube, Spotify) wrapped in white background box on dark themes to prevent text/UI readability issues from the embed's light-theme content
