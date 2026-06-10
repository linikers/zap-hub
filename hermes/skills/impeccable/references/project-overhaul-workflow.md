# Project Overhaul Workflow: Critique → Issues → PRs → Polish

A proven pattern for taking a frontend project from first look to fully polished, running end-to-end in a single session.

## When to Use This

When a user says "run critique on this project" or "let's fix this project up" — not for one-off feature work or bug fixes.

## The Pattern

### Phase 1: Critique (Discover)
1. Run critique on target — or manual equivalent: read source files, inspect components, analyze theme/style system
2. Score each heuristic (identity, consistency, typography, layout, UX, code quality)
3. List issues by priority (P0=critical, P1=high, P2=medium)
4. Present to user as a formatted report

### Phase 2: Issue Creation (Plan)
1. Create GitHub issues for each P0/P1 item at minimum
2. Create custom labels if needed: `P0`, `P1`, `P2`, `design`, `bug`, `enhancement`
3. Each issue gets: clear title, context, location (file + line), before/after
4. Reference related issues in bodies

### Phase 3: Fix PRs (Execute)
One PR per issue — never bundle unrelated fixes. Order matters — fix foundational issues first:

1. **CSS conflicts / boilerplate cleanup** — removes noise
2. **Theme / brand identity** — establishes the design system
3. **Component-level fixes** (gradients, glassmorphism, hero) — applies the theme
4. **UX/pattern fixes** (confirm dialogs, loading states) — polishes interactions
5. **Mobile/responsive fixes** — adapts to all screens
6. **Polish pass** — final refinement
### Phase 4: Polish (Finish)

After all fixes are merged, run one final polish pass using `references/react-mui-polish-patterns.md` as a checklist:

- Theme typos (missing `#`, swapped property names, duplicates)
- Dark theme contrast (text must be readable)
- "Carregando..." → MUI Skeleton
- `prefers-reduced-motion` media query added
- Transitions use `ease-out` instead of default `ease`
- Infinite blink/flicker animations → subtle float
- Glassmorphism → clean solid (unless purposeful)
- Dead code: remove commented JSX, unused CSS, console.log
- Consistency: verify all pages follow the DESIGN.md
- Responsive nav buttons: `fullWidth={true}` on mobile

## User Communication Flow

```
1. Critique report → user reviews
2. "Criar issues no GitHub?"
3. "Quer que eu comece pelos PRs?" → um PR de cada vez
4. After each merge: "Próximo? #N ou #M?"
5. After all PRs: status final — "Todas resolvidas!"
```

## Pitfalls

- Don't start fixing before the critique is accepted — user may disagree with priorities
- Don't create issues for items already resolved by other issues (duplicates confuse)
- Don't skip DESIGN.md creation — it anchors the whole overhaul
- Don't polish before functionally complete
- Don't let PRs grow beyond one issue — scope creep is the biggest risk
- Don't skip the final polish pass — it makes the work feel finished, not just fixed
- When bundling 2 issues (user asks), differentiate fixes in PR body so closing keywords still work

## User Preferences (embedded)

- User is Brazilian: reply in informal Portuguese ("bora", "chefia", "meu consagrado")
- User reviews before merge: show code, wait for approval before committing/pushing. See `github-pr-workflow` skill's **User Review Gate Pattern** section.
- User likes visual progress: status table with checkmarks
- **Batch decisions**: When changes are small (1-5 lines) and in the same concern, ask "sao alteracoes pequenas, pode fazer um pr so?". If user agrees, batch them into one PR with `Closes #A, #B, #C` in the body. Otherwise, keep them separate — always offer the choice, never assume.
