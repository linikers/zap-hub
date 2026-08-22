# Parallel Code Cleanup (absorbed from simplify-code skill)

Three narrow reviewers beat one broad reviewer. Each searches for a single class of problem, running concurrently via `delegate_task` batch mode.

## Phase 1 — Identify the diff
```bash
git diff                    # uncommitted working-tree changes
git diff HEAD               # include staged
git diff --staged           # staged only
git diff HEAD~1             # last commit
git diff main...HEAD        # this branch
```

## Phase 2 — Launch three reviewers in parallel

Give EVERY reviewer the **complete diff** plus absolute repo path. Each gets `terminal`, `file`, `search` toolsets.

### Reviewer 1 — Code Reuse
Search for code duplicating existing functionality. Flag: new functions duplicating existing ones, hand-rolled logic an existing utility does.

### Reviewer 2 — Code Quality
Look for: redundant state, parameter sprawl, copy-paste-with-variation, leaky abstractions, stringly-typed code.

### Reviewer 3 — Efficiency
Look for: unnecessary work, missed concurrency, hot-path bloat, TOCTOU anti-patterns, memory issues, overly broad reads.

## Phase 3 — Aggregate and apply
1. Merge findings, dedup overlapping
2. Discard false positives
3. Resolve conflicts: correctness > user focus > readability/reuse > micro-perf
4. Apply surviving fixes with `patch` / `write_file`
5. Verify: run targeted tests for touched files, re-run linter
6. Summarize changes

## Pitfalls
- Don't fan out wider than ~3 reviewers
- Give the WHOLE diff to each reviewer (cross-file issues hide in gaps)
- Require `file:line` evidence; drop findings without it
- Large diffs (>2000 lines) — scope down before delegating
