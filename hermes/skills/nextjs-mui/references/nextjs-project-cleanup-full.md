---
name: nextjs-project-cleanup
description: Organização e limpeza de projetos Next.js — README, docs, código comentado, catch vazios, .env tracking, build/lint verification.
---

# Next.js Project Cleanup

Use quando o usuário pedir para "organizar", "deixar bonito", "limpar" um projeto Next.js.

## Checklist de Organização

### 1. READMEs
- Substituir README.md boilerplate do create-next-app por descrição real do projeto
- Se o projeto estiver em subpasta, criar README.md na raiz explicando a estrutura

### 2. Documentação (docs/)
- Verificar se `docs/` existe e se os arquivos estão preenchidos
- Sugerir: `context.md` (arquitetura), `plan.md` (futuro), `guidelines.md` (padrões)

### 3. Limpeza de Código
- Remover imports comentados (`// import ...`)
- Remover blocos de código comentados inteiros (funções mortas, estados comentados)
- Remover pastas de teste/dados que vazaram (`prompts/`, `test-data/`)
- Corrigir keyframes CSS inválidos (valores como `-50%`, duplicatas)
- **Detectar páginas duplicadas no Pages Router** — `pages/perfil.tsx` + `pages/perfil/perfil.tsx` criam duas URLs diferentes. Uma delas é lixo.
- **Detectar dados fictícios/hardcoded** em dashboards e painéis admin (`"421"`, `"408"`, `"802"` etc.) — números sem fonte real poluem mais do que placeholder honesto

> Consulte `references/library-gotchas.md` para workarounds de react-icons v5 e framer-motion v11

### 4. Analytics — Catch Blocks
- `try { logEvent(...) } catch (error) {}` → substituir por `console.warn(...)`
- Procurar padrão: `catch (error) {}` em todo o projeto

### 5. .env Tracking
- Verificar se `.env` está no `.gitignore` (adicionar se necessário)
- Se `.env` já está sendo trackeado: `git rm --cached .env` + adicionar ao `.gitignore`
- Criar `.env.example` com placeholders vazios

### 6. Package Manager
- Verificar se usa npm ou yarn (checar presença de `package-lock.json` vs `yarn.lock`)
- Remover o que não for usado: `yarn.lock`, `.yarnrc.yml`, `.yarn/`
- Atualizar `.gitignore` (remover entradas do manager não utilizado)

### 7. Build Verification
- Rodar `npm install` (ou `yarn`)
- Rodar `npm run build` — verificar 0 warnings, 0 erros
- Rodar `npm run lint` — verificar sem warnings/errors

### 8. PR Workflow (preferido pelo usuário)

1. **Criar branch a partir do commit anterior ao primeiro de mudança** — NÃO commitar direto na main
   ```bash
   git checkout -b feat/organizacao <commit-anterior>
   git cherry-pick <commit1> <commit2> ...  # aplicar commits um a um
   ```
2. **Push da branch e criar PR:**
   ```bash
   git push origin feat/organizacao
   gh pr create --base main --head feat/organizacao --title "..." --body "..."
   ```
3. **NÃO reverter a main.** ⚠️ REGRA ABSOLUTA: manter a main atualizada com as alterações. Reverter commits e ter que refazer depois causa retrabalho e frustração ("Não caralho, vamo implantar todas modificações mas eu faço merge"). Se os commits já estão na main:
   - Crie a branch a partir do commit anterior (pré-mudança)
   - Cherry-pick os commits
   - O PR vai mostrar diff corretamente
   - A main continua com as alterações deployadas
4. **Se por engano reverteu a main:** reverter o revert (git revert do commit de revert) ou fazer merge da branch de volta. Não force push na main.

### 9. Criar GitHub Issues para Pendências Encontradas

Quando a análise de código ou de features incompletas revelar itens acionáveis:

1. **Usar `gh issue create --repo <owner>/<repo>`** para cada pendência distinta
2. **Boas práticas:**
   - Uma issue por tema (ex: #28 Configurar X profissional, #29 PagSeguro erc20, #30 Pendências técnicas)
   - Título descritivo em português
   - Body com contexto + o que fazer + referência a arquivos relevantes
   - Se aplicável, incluir comando ou código de exemplo
3. **Agrupar pendências pequenas** numa única issue guarda-chuva (#30) em vez de criar 15 issues individuais
4. **Sempre verificar antes:** `gh issue list --repo <owner>/<repo>` para evitar duplicatas

### 10. Verificar Deploy (Vercel)

Após fazer push, verificar se o deploy está ativo:

1. **Descobrir a URL:** perguntar ao usuário ou tentar padrões comuns:
   - `<project-name>.vercel.app`
   - `<project-name>-git-main-<user>.vercel.app`
   - `<user>-<project>.vercel.app`
3. **Se der 404:** provavelmente o repositório não está conectado ao Vercel
   - Verificar se existe pasta `.vercel` ou arquivo `vercel.json` — se não, não tem config automático
   - Orientar o usuário a conectar o repo no dashboard do Vercel (Settings > Git > Connect Git Repository)
   - **Root Directory:** se o Next.js estiver em subpasta (`linikers/`), configurar como root directory no Vercel
   - **Se o login no Vercel falhar** (2FA, erro 404 em `/settings/tokens`):
     - O caminho correto para criar token é `https://vercel.com/settings/tokens` (conta GLOBAL, não de um projeto específico)
     - Se der 404 mesmo assim, o usuário pode estar logado numa conta sem permissão ou a URL pode ter mudado — redirecionar para `https://vercel.com/account/tokens`
     - Alternativa sem token: conectar o repositório direto pelo dashboard Vercel em vez de CLI

4. **Fallback: GitHub Actions auto-deploy** (quando usuário não consegue acessar Vercel):
   - Template disponível em `templates/vercel-deploy.yml`
   - Requer secrets no GitHub: `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`
   - VERCEL_ORG_ID e VERCEL_PROJECT_ID: rodar `vercel pull` localmente uma vez e copiar do `.vercel/project.json`
   - O working-directory deve apontar pra subpasta se o Next.js não estiver na raiz
3. **Se o deploy existir mas mostrar conteúdo vazio:** pode ser CSS/JS que não carregou — fazer hard refresh ou verificar console do navegador
4. **Após conectar o repo:** o Vercel faz deploy automático em cada push na branch principal

### 11. Unfinished Features Analysis (opcional — quando o usuário perguntar "oq não terminei"/"oq falta")

Após o cleanup básico, analise o projeto em busca de features começadas mas não terminadas:

- **Módulos com placeholder** — números hardcoded, "Em breve", dados fictícios em dashboards
- **IA integrada mas não conectada** — provider de IA existe (Groq/Gemini) mas o form não chama a API
- **Checkout sem pagamento real** — modal de compra existe mas sem gateway integrado (só demo/placeholders)
- **CRUD sem execução** — posts/agendamentos salvos no banco mas nenhum cron job publica (Twitter, LinkedIn etc.)
- **Rotas duplicadas** — `pages/perfil.tsx` + `pages/perfil/perfil.tsx` (Next.js Pages Router)
- **Componente de transição sem destino** — tela de boot/animação que nunca revela conteúdo principal

Apresente num formato tipo "O que eu vi que não terminou" — lista numerada, cada item com diagnóstico breve e recomendação de próximo passo.

## ⚠️ REGRA CRÍTICA: Escopo definido, sem extras

**Quando o usuário pedir para "organizar", "limpar", "arrumar", NÃO faça:**

- ❌ Criar blog posts, personas, conteúdo novo — a não ser que ele peça explicitamente
- ❌ Implementar features novas (pagamento, postagem automática, etc.)
- ❌ Sugerir planos estratégicos longos não solicitados

**Faça APENAS:**
- ✅ O que ele pediu, na ordem que ele pediu
- ✅ Se ele perguntar "oq faltou", aí sim liste como diagnóstico — mas não execute sem autorização
- ✅ Se ele disser "faz do seu jeito", aí você pode usar seu julgamento, mas mantenha no escopo

**Sinal de alerta:** se você perceber que está escrevendo conteúdo editorial (post de blog, artigo, thread) e o usuário não pediu explicitamente, pare — pode ser que ele queira escrever pessoalmente e você só dar contexto.

## 10. MUI Theme Standardization (quando o projeto usa MUI)

Se o projeto usa MUI e o layout tem hex colors soltos em vez de tokens do tema:

1. **Identificar o padrão do usuário** — verificar qual versão do MUI está no `package.json` e qual provider usam nos projetos paralelos (CarCrew usa MUI v9 com slotProps)
2. **Criar `src/config/theme.ts`** com `createTheme()`:
   - Extrair as cores mais usadas do projeto (escaneie hex codes nas páginas)
   - Usar `mode: "dark"` se a home e loja já forem dark
   - Definir `background.default`, `background.paper`, `divider`, `primary.main`, `text.primary`, `text.secondary`
3. **Atualizar `_app.jsx`** — adicionar `ThemeProvider` + `CssBaseline`
4. **Substituir hex soltos por tokens do tema**:
   - `backgroundColor: "#d4d0c4"` → `bgcolor: "background.default"`
   - `backgroundColor: "#f5f5f5"` → `bgcolor: "action.hover"`
   - `backgroundColor: "gray"` → `bgcolor: "background.default"`
   - `backgroundColor: "white"` → `bgcolor: "background.paper"`
   - `borderRight: "1px solid #e2e8f0"` → `borderRight: 1, borderColor: "divider"`
5. **Verificar build** — o CssBaseline pode afetar estilos herdados

## Pitfalls Comuns (Next.js + MUI + TypeScript)

### react-icons v5 — JSX component typing error
```tsx
// ERRO: 'SiNextdotjs' cannot be used as a JSX component
import { SiNextdotjs } from "react-icons/si";
<SiNextdotjs size={22} />  // ❌ TypeScript strict: "return type 'ReactNode' is not a valid JSX element"

// CORRETO: cast via `: any`
const NextIcon: any = SiNextdotjs;
<NextIcon size={22} />     // ✅
```
react-icons v5 (^5.5.0) tem tipos que não casam com React 18 + TypeScript strict. O padrão do projeto é usar `: any` — siga ele. Isso vale pra `react-icons/si`, `react-icons/fa6`, `react-icons/md`, `react-icons/di` etc.

### framer-motion v11 — AnimatePresence quebra
```tsx
import { motion, AnimatePresence } from "framer-motion";

// ERRO: 'AnimatePresence' cannot be used as a JSX component
<AnimatePresence>...</AnimatePresence>  // ❌

// CORRETO: proxy via `: any`
const AnimatePresenceProxy: any = AnimatePresence;
<AnimatePresenceProxy mode="wait">...</AnimatePresenceProxy>  // ✅
```
Framer Motion v11 tem breaking changes na API. Se não precisar de `AnimatePresence` (ex: landing que aparece uma vez), remova o wrapper — simplifica.

### Boot sequence → conteúdo principal
Quando um componente exibe animação de boot (splash/terminal loading) e depois revela conteúdo:
1. O componente de animação deve expor um callback `onBootComplete?: () => void`
2. O componente pai gerencia o estado: `const [booted, setBooted] = useState(false)`
3. Enquanto `!booted`: mostra animação. Quando `booted`: mostra conteúdo
4. NÃO usar `router.push()` para sair da animação — isso é redirect, não transição
5. Se houver `router.push()` no componente de animação, substitua por callback

### Páginas duplicadas no Pages Router
Next.js Pages Router cria uma URL pra cada arquivo `.tsx` dentro de `pages/`:
- `pages/perfil.tsx` → `/perfil`
- `pages/perfil/perfil.tsx` → `/perfil/perfil`

Sempre verificar se há subpastas com arquivo de mesmo nome — é um padrão de erro comum.

## Comandos Úteis

```bash
# Verificar .env tracking
git ls-files .env

# Remover do tracking sem deletar local
git rm --cached .env

# Verificar código comentado
grep -r "// import\|// const\|// function" src/ --include="*.tsx" --include="*.ts"

# Verificar catch vazios
grep -rn "catch (error) {}" src/

# Detectar páginas duplicadas (Next.js Pages Router)
find src/pages -name '*.tsx' -o -name '*.jsx' | sed 's|.*/||' | sort | uniq -c | sort -rn | head -20

# Detectar números hardcoded suspeitos em dashboards
grep -rn '[0-9]\{3\}' src/pages/admin/ --include="*.tsx" | grep -v "import\|href\|width\|height\|fontSize\|margin\|padding\|zIndex\|maxWidth\|borderRadius"
```
