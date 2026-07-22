---
name: impeccable
description: "Use when the user wants to design, redesign, shape, critique, audit, polish, clarify, distill, harden, optimize, adapt, animate, colorize, extract, or otherwise improve a frontend interface. Covers websites, landing pages, dashboards, product UI, app shells, components, forms, settings, onboarding, and empty states. Handles UX review, visual hierarchy, information architecture, cognitive load, accessibility, performance, responsive behavior, theming, anti-patterns, typography, fonts, spacing, layout, alignment, color, motion, micro-interactions, UX copy, error states, edge cases, i18n, and reusable design systems or tokens. Also use for bland designs that need to become bolder or more delightful, loud designs that should become quieter, live browser iteration on UI elements, or ambitious visual effects that should feel technically extraordinary. Not for backend-only or non-UI tasks."
argument-hint: "[command] [target]"
user-invocable: true
license: Apache 2.0. Based on Anthropic's frontend-design skill. See NOTICE.md for attribution.
---

Designs and iterates production-grade frontend interfaces. Real working code, committed design choices, exceptional craft.

## Setup

Before any design work or file edits:

1. Load context (PRODUCT.md / DESIGN.md) via the loader script.
2. Identify the register and load the matching register reference (brand.md or product.md).
3. **If the user invoked a sub-command (e.g. `craft`, `shape`, `audit`), load its reference file too.** This is non-negotiable: `craft` without `craft.md` loaded means you'll skip the shape-and-confirm step the user expects.

Skipping these produces generic output that ignores the project.

### 1. Context gathering

Two files, case-insensitive. The loader looks at the project root by default and falls back to `.agents/context/` and `docs/` if the root is clean. Override with `IMPECCABLE_CONTEXT_DIR=path/to/dir` (absolute or relative to cwd).

- **PRODUCT.md**: required. Users, brand, tone, anti-references, strategic principles.
- **DESIGN.md**: optional, strongly recommended. Colors, typography, elevation, components.

Load both in one call:

```bash
node /root/.hermes/skills/impeccable/scripts/load-context.mjs
```

Consume the full JSON output. Never pipe through `head`, `tail`, `grep`, or `jq`. The output's `contextDir` field tells you where the files were resolved from.

If the output is already in this session's conversation history, don't re-run. Exceptions requiring a fresh load: you just ran `/impeccable teach` or `/impeccable document` (they rewrite the files), or the user manually edited one.

`/impeccable live` already warms context via `live.mjs`. If you've run `live.mjs`, don't also run `load-context.mjs` this session.

If PRODUCT.md is missing, empty, or placeholder (`[TODO]` markers, <200 chars): run `/impeccable teach`, then resume the user's original task with the fresh context. If the original task was `/impeccable craft`, resume into `/impeccable shape` before any implementation work.

If DESIGN.md is missing: nudge once per session (*"Run `/impeccable document` for more on-brand output"*), then proceed.

### 2. Register

Every design task is **brand** (marketing, landing, campaign, long-form content, portfolio: design IS the product) or **product** (app UI, admin, dashboard, tool: design SERVES the product).

Identify before designing. Priority: (1) cue in the task itself ("landing page" vs "dashboard"); (2) the surface in focus (the page, file, or route being worked on); (3) `register` field in PRODUCT.md. First match wins.

If PRODUCT.md lacks the `register` field (legacy), infer it once from its "Users" and "Product Purpose" sections, then cache the inferred value for the session. Suggest the user run `/impeccable teach` to add the field explicitly.

Load the matching reference: [reference/brand.md](reference/brand.md) or [reference/product.md](reference/product.md). The shared design laws below apply to both.

## Shared design laws

Apply to every design, both registers. Match implementation complexity to the aesthetic vision: maximalism needs elaborate code, minimalism needs precision. Interpret creatively. Vary across projects; never converge on the same choices. the model is capable of extraordinary work. Don't hold back.

### Color

- Use OKLCH. Reduce chroma as lightness approaches 0 or 100; high chroma at extremes looks garish.
- Never use `#000` or `#fff`. Tint every neutral toward the brand hue (chroma 0.005–0.01 is enough).
- Pick a **color strategy** before picking colors. Four steps on the commitment axis:
  - **Restrained**: tinted neutrals + one accent ≤10%. Product default; brand minimalism.
  - **Committed**: one saturated color carries 30–60% of the surface. Brand default for identity-driven pages.
  - **Full palette**: 3–4 named roles, each used deliberately. Brand campaigns; product data viz.
  - **Drenched**: the surface IS the color. Brand heroes, campaign pages.
- The "one accent ≤10%" rule is Restrained only. Committed / Full palette / Drenched exceed it on purpose. Don't collapse every design to Restrained by reflex.

### Theme

Dark vs. light is never a default. Not dark "because tools look cool dark." Not light "to be safe."

Before choosing, write one sentence of physical scene: who uses this, where, under what ambient light, in what mood. If the sentence doesn't force the answer, it's not concrete enough. Add detail until it does.

"Observability dashboard" does not force an answer. "SRE glancing at incident severity on a 27-inch monitor at 2am in a dim room" does. Run the sentence, not the category.

### Typography

- Cap body line length at 65–75ch.
- Hierarchy through scale + weight contrast (≥1.25 ratio between steps). Avoid flat scales.

### Layout

- Vary spacing for rhythm. Same padding everywhere is monotony.
- Cards are the lazy answer. Use them only when they're truly the best affordance. Nested cards are always wrong.
- Don't wrap everything in a container. Most things don't need one.

### Motion

- Don't animate CSS layout properties.
- Ease out with exponential curves (ease-out-quart / quint / expo). No bounce, no elastic.

### Absolute bans

Match-and-refuse. If you're about to write any of these, rewrite the element with different structure.

- **Side-stripe borders.** `border-left` or `border-right` greater than 1px as a colored accent on cards, list items, callouts, or alerts. Never intentional. Rewrite with full borders, background tints, leading numbers/icons, or nothing.
- **Gradient text.** `background-clip: text` combined with a gradient background. Decorative, never meaningful. Use a single solid color. Emphasis via weight or size.
- **Glassmorphism as default.** Blurs and glass cards used decoratively. Rare and purposeful, or nothing.
- **The hero-metric template.** Big number, small label, supporting stats, gradient accent. SaaS cliché.
- **Identical card grids.** Same-sized cards with icon + heading + text, repeated endlessly.
- **Modal as first thought.** Modals are usually laziness. Exhaust inline / progressive alternatives first.

### Copy

- Every word earns its place. No restated headings, no intros that repeat the title.
- **No em dashes.** Use commas, colons, semicolons, periods, or parentheses. Also not `--`.

### The AI slop test

If someone could look at this interface and say "AI made that" without doubt, it's failed. Cross-register failures are the absolute bans above. Register-specific failures live in each reference.

**Category-reflex check.** Run at two altitudes; the second one catches what the first one misses.

- **First-order:** if someone could guess the theme + palette from the category alone ("observability → dark blue", "healthcare → white + teal", "finance → navy + gold", "crypto → neon on black"), it's the first training-data reflex. Rework the scene sentence and color strategy until the answer isn't obvious from the domain.
- **Second-order:** if someone could guess the aesthetic family from category-plus-anti-references ("AI workflow tool that's not SaaS-cream → editorial-typographic", "fintech that's not navy-and-gold → terminal-native dark mode"), it's the trap one tier deeper. The first reflex was avoided; the second wasn't. Rework until both answers are not obvious. The brand register's [reflex-reject aesthetic lanes](reference/brand.md) list catches the currently-saturated families.

### Fixing Existing Components — Surgical Only

When fixing layout/CSS bugs in an existing component, the user expects MINIMAL
targeted changes. The #1 failure mode is breaking working behavior while fixing
the reported issue.

**Pitfall: Rewriting fixes nothing.** If you restructure the JSX to "clean it
up", you will break something that was working. The user WILL notice and will
lose trust. Every rewrite attempt that breaks working behavior is worse than
the original bug.

**Mandatory process:**
1. Read the ENTIRE component before changing anything
2. Identify the exact lines causing the reported issue
3. Change ONLY those lines — CSS values, breakpoints, padding
4. Never add new wrapper elements unless absolutely necessary
5. Never reorganize existing JSX structure
6. Build and verify before committing
7. If a change breaks something else, REVERT IT and find a less invasive fix

**What to change:** CSS breakpoints, padding/margin values, maxWidth, display
properties, flex values. These are safe, isolated, and reversible.

**What NOT to change:** JSX nesting, component hierarchy, flex container
structure, element ordering, removing elements to "simplify". These cascade.

**If the user provides a detailed spec:** Follow it EXACTLY. Do not improvise,
do not "improve" it, do not add your own ideas. The spec is the contract.

**Pitfall: `justifyContent:center` + `overflowX:auto` = clipped items.** When
a flex container uses both `justifyContent: "center"` and `overflowX: "auto"`,
content that overflows is centered, but the scrollable area starts at center
and only scrolls right. Left-side items get permanently clipped. This is the
#1 cause of "the menu cuts off the first items" bugs. Fix: remove overflow or
use `justifyContent: "flex-start"` when overflow is needed. Prefer wrapping to
scrolling when center alignment matters.

**Pitfall: `flex:1 spacer` breaks centering.** `<Box sx={{ flex: 1 }} />`
pushes everything left, leaving one item isolated on the right. For centered
categories with a right-aligned button, use a 2-zone layout:
`<Box flex:1 justifyContent:center>{items}</Box><Button>action</Button>`.

**Build before committing.** Every CSS/layout change MUST pass `npx next build`
before commit. If it builds, it ships. If the user reports a regression, revert
the specific change that broke it — do not layer more fixes on top.

### Hermes Adaptation

This skill was designed for Claude Code. For Hermes Agent, **always** load `references/hermes-adaptation.md` — it documents which commands work, how to adapt the critique workflow (browser tools instead of detect.mjs), and how to use delegate_task instead of spawn_agent.

### Project Overhaul Workflow

When the user wants to run critique and then fix everything end-to-end, consult `references/project-overhaul-workflow.md`. It documents the proven pattern: critique → GitHub issues → separate fix PRs per issue → final polish pass. Use it when a user says "let's fix this project up" rather than "fix this one thing."

### React/MUI Polish Reference

When polishing a React + MUI project, load `references/react-mui-polish-patterns.md`. It documents concrete code patterns found across real projects: theme typos, contrast fixes, skeleton loading, animation replacements, glassmorphism cleanup, and more. Use as a checklist during the final polish pass.

### CarCrew Commerce Reference

When working on the CarCrew Suspensões e-commerce project (`github.com/linikers/carCrewCommerce`), load `references/carcrew-commerce.md`. It documents the brand's specific design tokens, hexagonal logo component specs, header layout, MUI v9 quirks, the banner system (Prisma schema, API, how to add image banners), and navigation patterns (?cat=slug routing).

### Marketing OS Dashboard Reference

When working on the Marketing OS dashboard (`github.com/linikers/hermes-marketing-orchestrator`), load `references/marketing-os-dashboard.md`. It documents the product register, scene sentence, Indigo + zinc dark palette, Inter typography, sidebar layout, and component patterns specific to this ongoing project.

### Free Banner Generation Reference

When generating banners programmatically (for any project), load `references/free-banner-generation.md`. It documents the free toolchain: Pollinations.ai for backgrounds, rembg for subject extraction, and PIL for compositing — plus pitfalls, quality tiers, and deployment steps.

### Free Banner Generation Tools

When the user needs AI-generated banners for e-commerce and asks about tools (especially free ones), load `references/free-banner-tools.md`. It documents Pollinations.ai (zero-setup, no API key), Leonardo.ai (150 free credits/day), HuggingFace Serverless, and the two-step compositing pattern (generate background + overlay logo/CTA with Python PIL). Also confirms Ideogram API is paid-only.

## Commands

| Command | Category | Description | Reference |
|---|---|---|---|
| `craft [feature]` | Build | Shape, then build a feature end-to-end | [reference/craft.md](reference/craft.md) |
| `shape [feature]` | Build | Plan UX/UI before writing code | [reference/shape.md](reference/shape.md) |
| `teach` | Build | Set up PRODUCT.md and DESIGN.md context | [reference/teach.md](reference/teach.md) |
| `document` | Build | Generate DESIGN.md from existing project code | [reference/document.md](reference/document.md) |
| `extract [target]` | Build | Pull reusable tokens and components into design system | [reference/extract.md](reference/extract.md) |
| `critique [target]` | Evaluate | UX design review with heuristic scoring | [reference/critique.md](reference/critique.md) |
| `audit [target]` | Evaluate | Technical quality checks (a11y, perf, responsive) | [reference/audit.md](reference/audit.md) |
| `polish [target]` | Refine | Final quality pass before shipping | [reference/polish.md](reference/polish.md) |
| `bolder [target]` | Refine | Amplify safe or bland designs | [reference/bolder.md](reference/bolder.md) |
| `quieter [target]` | Refine | Tone down aggressive or overstimulating designs | [reference/quieter.md](reference/quieter.md) |
| `distill [target]` | Refine | Strip to essence, remove complexity | [reference/distill.md](reference/distill.md) |
| `harden [target]` | Refine | Production-ready: errors, i18n, edge cases | [reference/harden.md](reference/harden.md) |
| `onboard [target]` | Refine | Design first-run flows, empty states, activation | [reference/onboard.md](reference/onboard.md) |
| `animate [target]` | Enhance | Add purposeful animations and motion | [reference/animate.md](reference/animate.md) |
| `colorize [target]` | Enhance | Add strategic color to monochromatic UIs | [reference/colorize.md](reference/colorize.md) |
| `typeset [target]` | Enhance | Improve typography hierarchy and fonts | [reference/typeset.md](reference/typeset.md) |
| `layout [target]` | Enhance | Fix spacing, rhythm, and visual hierarchy | [reference/layout.md](reference/layout.md) |
| `delight [target]` | Enhance | Add personality and memorable touches | [reference/delight.md](reference/delight.md) |
| `overdrive [target]` | Enhance | Push past conventional limits | [reference/overdrive.md](reference/overdrive.md) |
| `clarify [target]` | Fix | Improve UX copy, labels, and error messages | [reference/clarify.md](reference/clarify.md) |
| `adapt [target]` | Fix | Adapt for different devices and screen sizes | [reference/adapt.md](reference/adapt.md) |
| `optimize [target]` | Fix | Diagnose and fix UI performance | [reference/optimize.md](reference/optimize.md) |
| `live` | Iterate | Visual variant mode: pick elements in the browser, generate alternatives | [reference/live.md](reference/live.md) |

Plus two management commands: `pin <command>` and `unpin <command>`, detailed below.

### Routing rules

1. **No argument**: render the table above as the user-facing command menu, grouped by category. Ask what they'd like to do.
2. **First word matches a command**: load its reference file and follow its instructions. Everything after the command name is the target.
3. **First word doesn't match**: general design invocation. Apply the setup steps, shared design laws, and the loaded register reference, using the full argument as context.

Setup (context gathering, register) is already loaded by then; sub-commands don't re-invoke `/impeccable`.

If the first word is `craft`, setup still runs first, but [reference/craft.md](reference/craft.md) owns the rest of the flow. If setup invokes `teach` as a blocker, finish teach, refresh context, then resume the original command and target.

## Pin / Unpin

**Pin** creates a standalone shortcut so `/impeccable <command>` invokes `/impeccable <command>` directly. **Unpin** removes it. The script writes to every harness directory present in the project.

```bash
node /root/.hermes/skills/impeccable/scripts/pin.mjs <pin|unpin> <command>
```

Valid `<command>` is any command from the table above. Report the script's result concisely. Confirm the new shortcut on success, relay stderr verbatim on error.
