# Library Gotchas — Next.js + MUI + react-icons + framer-motion

Workarounds descobertos para problemas comuns de tipagem em projetos Next.js 13 com React 18 + TypeScript strict.

## react-icons v5 (^5.5.0) — JSX component typing error

```tsx
// ❌ ERRO: 'SiNextdotjs' cannot be used as a JSX component
// Type error: "return type 'ReactNode' is not a valid JSX element. Type 'undefined' is not assignable to type 'Element | null'."
import { SiNextdotjs } from "react-icons/si";
<SiNextdotjs size={22} />

// ✅ CORRETO: cast via `: any` (padrão do projeto)
const NextIcon: any = SiNextdotjs;
<NextIcon size={22} />
```

**Atinge:** `react-icons/si`, `react-icons/fa6`, `react-icons/md`, `react-icons/di`, `react-icons/tb` — todos os submódulos do react-icons v5.

**Por que acontece:** react-icons v5 usa tipos que geram `ReactNode` em vez de `ReactElement`, incompatível com `@types/react` 18 + `strict: true`.

**Solução no projeto:** Mesmo padrão usado em ferramentas.tsx — alocar via `const Icon: any = OriginalIcon`.

## framer-motion v11 — AnimatePresence quebra

```tsx
// ❌ ERRO: 'AnimatePresence' cannot be used as a JSX component
import { motion, AnimatePresence } from "framer-motion";
<AnimatePresence>...</AnimatePresence>

// ✅ CORRETO: proxy via `: any`
const AnimatePresenceProxy: any = AnimatePresence;
<AnimatePresenceProxy mode="wait">...</AnimatePresenceProxy>
```

**Alternativa mais simples:** Se o componente aparece uma vez (ex: landing page pós-boot), remova o `AnimatePresence` completamente e use apenas `motion.div` com `initial/animate` — não precisa de `AnimatePresence` pra animações de entrada única.

```tsx
// Simplificado — sem AnimatePresence:
const MotionBox = motion.create(Box);
return <MotionBox initial={{ opacity: 0 }} animate={{ opacity: 1 }}>...</MotionBox>;
```

## MUI `sx` tokens vs hex colors

Em vez de hex soltos, usar tokens do tema MUI:

| Hex antigo | Token MUI |
|-----------|-----------|
| `"#d4d0c4"`, `"gray"` | `"background.default"` |
| `"#f5f5f5"`, `"white"` | `"background.paper"` |
| `"#e2e8f0"` (borda) | `divider` (via `borderColor: "divider"` + `borderRight: 1`) |
| `"#3b5998"` | `"primary.main"` |
| `"#f8fafc"` | `"background.default"` |

**Importante:** `sx` aceita string com o nome do token (`bgcolor: "background.default"`), mas se quiser o valor real use `theme.palette.background.default`.
