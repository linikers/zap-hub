## Hermes Adaptation — Cross-Cutting Notes

The Impeccable skill was originally designed for Claude Code / Cline. This reference documents how to adapt each command for Hermes Agent.

### Prerequisites

- Hermes has `browser_navigate`, `browser_snapshot`, `browser_vision` tools for visual inspection
- `delegate_task` replaces Claude's `spawn_agent` / `fork_context` for sub-agent work
- No `detect.mjs`, `live-server.mjs`, or `critique-storage.mjs` are available in Hermes environment
- Project context files (PRODUCT.md, DESIGN.md) go in the project root or `.agents/context/`

### Critique Command — Hermes Adaptation

The `critique` command relies on `detect.mjs` for Assessment B (automated scan). Since that script is unavailable:

**Assessment B (browser evidence) adaptation:**
1. Start the dev server in background: `terminal(command="npm run dev -- --port 3099", background=true)`
2. Navigate via: `browser_navigate(url="http://localhost:3099/")`
3. Use `browser_snapshot(full=true)` for DOM/snapshot inspection
4. Use `browser_vision(question="...")` for visual analysis (layout, colors, spacing, typography)
5. Use `browser_console(expression=...)` for programmatic DOM queries
6. Combine findings manually into the critique report

**Assessment A (design review) adaptation:**
- Same as original: read source files, read the snapshot, apply design heuristics
- No sub-agents needed — do it sequentially in the main session

**Report generation:**
- Same structure: heuristic scores, anti-patterns, priority issues, personas
- Skip the "Visual overlays" section (no detect.js injection available)
- Skip persistence/write to `.impeccable/critique/` (no critique-storage.mjs)

**Critique-only (source analysis) adaptation:**
When the dev server can't start (missing deps, blocked terminal, no browser) or the user just wants a quick assessment:

1. Read the project structure: `find . -maxdepth 3 -not -path './.git/*' -not -path './node_modules/*' | sort`
2. Read key files: `package.json`, `App.tsx`/theme config, layout components, page components, CSS files
3. Assess theme system (MUI createTheme, CSS variables, CSS files loaded)
4. Assess design system depth (custom UI wrappers, design tokens, consistent styling)
5. Identify anti-patterns (gradient text, glassmorphism defaults, boilerplate CSS, window.confirm)
6. Score each heuristic (identity, consistency, hierarchy, typography, responsiveness, accessibility, code org, UX)
7. Produce the full critique report with 🔴 P0 / 🟠 P1 / 🟡 P2 priority ratings

### Critique → Issues → PRs Workflow

After critique, convert findings into GitHub issues first, then fix in separate sequential PRs.

1. **Check existing labels** and create priority/labeling labels if needed:
   ```bash
   gh label list --repo owner/repo
   # Create missing labels:
   for label in "P0" "P1" "P2" "design"; do
     gh label create "$label" --repo owner/repo 2>/dev/null || true
   done
   ```

2. **Create one GitHub Issue per P0/P1 finding**, each with:
   - Clear title with priority prefix: `[P0] Tema padrão sem identidade`
   - Body with four sections:
     ```
     ## Problema
     <What's wrong, why it matters>

     ## Localização
     `file/path.tsx` — linha N

     ## Impacto
     <Who this affects, what breaks>

     ## Sugestão
     <How to fix, what to use instead>
     ```
   - Labels: priority (P0/P1) + category (design/bug/enhancement)

3. **Sequencing strategy** — fix in dependency order:
   - **Phase 1 — Infrastructure**: CSS conflicts, boilerplate removal, font loading. These unblock the rest.
   - **Phase 2 — Visual foundation**: Theme customization, color palette, DESIGN.md. Everything visual depends on this.
   - **Phase 3 — Component fixes**: Hero gradient, anti-pattern removal, confirm dialogs. Independent visual fixes.
   - **Phase 4 — Polish**: Transitions, micro-interactions, skeleton loading, CSS cleanup. Final pass.

4. **Fix in separate sequential PRs** (one issue at a time), **unless** changes are small and tightly scoped (1-5 lines each, same file/concern), in which case combine them into a single PR. When uncertain, ask the user: "sao alteracoes pequenas — um PR unico ou separados?"
   - Always start from updated master: `git checkout master && git pull origin master`
   - Create branch: `git checkout -b fix-<descriptive-name>`
   - Each branch named `fix-<descriptive-name>` (lowercase, hyphens)
   - Commit message format: `fix: descrição curta (Closes #N)` or `feat: descrição (Closes #N, #M)`
   - Each PR body references the issue: `Closes #N`
   - **Wait for user to merge** before starting the next PR, unless they explicitly batch-approve
   - Use `gh issue create` for issues, `gh pr create` for PRs

5. **PR body format:**
   ```markdown
   ## O que mudou

   **Problema:** <one-line summary>

   ### Mudanças
   - ✅ `<file>` — <change description>

   ## Arquivos alterados
   - `path/to/file` — <what changed>

   Closes #N
   ```

### Sub-agent Adaptation

When critique.md says "Delegate to sub-agents" (for independent A/B assessments):
- Use `delegate_task(goal="Assessment A: Design review of [target]", context="...", toolsets=["browser", "terminal", "file"])`
- Run A and B in parallel with separate `delegate_task` calls
- Wait for both results before synthesis

If delegate_task is unavailable, run sequentially and note: "Assessment independence: degraded (delegate_task unavailable)".

### General Notes

- All `{{scripts_path}}`, `{{command_prefix}}`, `{{model}}`, `{{command_hint}}` placeholders in reference files refer to Claude-specific harness — ignore them in Hermes
- `{{available_commands}}` → list the 23 commands from the SKILL.md table manually
- `{{ask_instruction}}` → use `clarify()` tool for user questions
- `live` command is not Hermes-compatible (requires Playwright browser injection)
- `pin`/`unpin` commands create standalone shortcuts — only works if Hermes loads them

### Polish Command — Hermes Adaptation (Source-Only Mode)

When the dev server cannot start (missing dependencies, blocked terminal, no browser available) or the codebase doesn't have a runnable frontend yet:

1. **Scan for polish items without a browser:**
   - Hardcoded hex colors in `sx`/`style` props
   - `console.error` / `console.log` calls that should be proper toast/error handlers
   - Commented-out code blocks
   - Unused CSS classes: check if classes defined in `.css` files are actually referenced in any `.tsx`
   - Pre-existing `eslint-disable` comments (signals technical debt)
   - Transitions without explicit easing (default `ease` instead of `ease-out`)
   - Missing `prefers-reduced-motion` media query

2. **Apply polish systematically:**
   - Always create a branch from updated master first
   - Fix each dimension (CSS cleanup, transitions, hardcoded colors, motion) in order
   - Test via git diff review (no build verification without node_modules)
   - Commit with prefix `polish:` and mention specific areas changed

### Commands That Work Well in Hermes

| Command | Hermes Compatible | Notes |
|---------|------------------|-------|
| critique | ✅ | With browser tool adaptation (see above) |
| audit | ✅ | Manual a11y/perf checks via browser + source |
| polish | ✅ | Manual fix pass |
| bolder | ✅ | Direct code changes |
| quieter | ✅ | Direct code changes |
| distill | ✅ | Direct code changes |
| harden | ✅ | Direct code changes |
| clarify | ✅ | Copy/UX improvements |
| adapt | ✅ | Responsive fixes |
| layout | ✅ | Spacing/hierarchy fixes |
| typeset | ✅ | Typography improvements |
| colorize | ✅ | Color improvements |
| craft | ✅ | Build from scratch |
| shape | ✅ | Plan before coding |
| teach | ✅ | Context setup |
| document | ✅ | Generate DESIGN.md from code |
| extract | ✅ | Pull tokens into design system |
| animate | ⚠️ | CSS/js only (no motion library) |
| delight | ✅ | Direct code changes |
| overdrive | ✅ | Direct code changes |
| optimize | ✅ | Manual perf analysis |
| onboard | ✅ | Empty/first-run states |
| live | ❌ | Requires Playwright browser injection |

---

## Heuristic Scoring Guide

Use this rubric when scoring designs in a critique report.

### Heuristics & What to Assess

| Heuristic | What to assess |
|-----------|---------------|
| **Identidade Visual** | Brand colors, logo, consistent personality. Not default MUI/Vite. |
| **Consistência** | Same color system, same component patterns. No conflicting CSS systems. |
| **Hierarquia Visual** | Clear heading scale, spacing rhythm, visual weight distribution. |
| **Tipografia** | Deliberate font choice (loaded, not just declared), scale, line length. |
| **Responsividade** | Works at mobile/tablet/desktop. MUI breakpoints used intentionally. |
| **Acessibilidade** | Color contrast, focus states, aria labels, touch targets ≥44px. |
| **Código/Organização** | Separation of concerns, componentization, file structure. |
| **UX/Flow** | User journeys intuitive, loading states, error handling, empty states. |

### Score Scale

| Score | Meaning |
|-------|---------|
| 1-3 | Critical issues. Needs fundamental rework. |
| 4-5 | Functional but generic. Lacks polish and identity. |
| 6-7 | Solid. Minor refinements needed. |
| 8-9 | Polished. Edge-case improvements only. |
| 10 | Exceptional. Reference-quality. |

### Anti-Pattern Checklist (banned by Impeccable)

- [ ] Gradient text (`background-clip: text` + gradient)
- [ ] Glassmorphism as default card style
- [ ] Side-stripe borders >1px
- [ ] Hero-metric template (big number + small label)
- [ ] Identical card grids (icon + heading + text repeated)
- [ ] Modal as first thought (exhaust inline alternatives)
- [ ] Em dashes (use commas/colons instead)
- [ ] Vite boilerplate CSS left in production

### Standard Issue Priority Labels

When creating issues from critique findings, create these labels if they don't exist:

```
P0 🔴 Critical — must fix (CSS conflicts, broken layouts)
P1 🟠 High priority — visual inconsistency, UX friction
P2 🟡 Medium — polish, nice-to-have improvements
design 🎨 Design system, UI visual identity
```
