---
name: systematic-debugging
description: "4-phase root cause debugging: understand bugs before fixing."
version: 1.2.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, troubleshooting, problem-solving, root-cause, investigation]
    related_skills: [test-driven-development, writing-plans, subagent-driven-development]
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Someone wants it fixed NOW (systematic is faster than thrashing)

## The Four Phases

You MUST complete each phase before proceeding to the next.

---

## Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

### 1. Read Error Messages Carefully

- Don't skip past errors or warnings
- They often contain the exact solution
- Read stack traces completely
- Note line numbers, file paths, error codes

**Action:** Use `read_file` on the relevant source files. Use `search_files` to find the error string in the codebase.

### 2. Reproduce Consistently

- Can you trigger it reliably?
- What are the exact steps?
- Does it happen every time?
- If not reproducible → gather more data, don't guess

**Action:** Use the `terminal` tool to run the failing test or trigger the bug:

```bash
# Run specific failing test
pytest tests/test_module.py::test_name -v

# Run with verbose output
pytest tests/test_module.py -v --tb=long
```

### 3. Check Recent Changes

- What changed that could cause this?
- Git diff, recent commits
- New dependencies, config changes

**Action:**

```bash
# Recent commits
git log --oneline -10

# Uncommitted changes
git diff

# Changes in specific file
git log -p --follow src/problematic_file.py | head -100
```

### 4. Gather Evidence in Multi-Component Systems

**WHEN system has multiple components (API → service → database, CI → build → deploy):**

**BEFORE proposing fixes, add diagnostic instrumentation:**

For EACH component boundary:
- Log what data enters the component
- Log what data exits the component
- Verify environment/config propagation
- Check state at each layer

Run once to gather evidence showing WHERE it breaks.
THEN analyze evidence to identify the failing component.
THEN investigate that specific component.

### 5. Trace Data Flow

**WHEN error is deep in the call stack:**

- Where does the bad value originate?
- What called this function with the bad value?
- Keep tracing upstream until you find the source
- Fix at the source, not at the symptom

**Action:** Use `search_files` to trace references:

```python
# Find where the function is called
search_files("function_name(", path="src/", file_glob="*.py")

# Find where the variable is set
search_files("variable_name\\s*=", path="src/", file_glob="*.py")
```

### Phase 1 Completion Checklist

- [ ] Error messages fully read and understood
- [ ] Issue reproduced consistently
- [ ] Recent changes identified and reviewed
- [ ] Evidence gathered (logs, state, data flow)
- [ ] Problem isolated to specific component/code
- [ ] Root cause hypothesis formed

**STOP:** Do not proceed to Phase 2 until you understand WHY it's happening.

---

## Phase 2: Pattern Analysis

**Find the pattern before fixing:**

### 1. Find Working Examples

- Locate similar working code in the same codebase
- What works that's similar to what's broken?

**Action:** Use `search_files` to find comparable patterns:

```python
search_files("similar_pattern", path="src/", file_glob="*.py")
```

### 2. Compare Against References

- If implementing a pattern, read the reference implementation COMPLETELY
- Don't skim — read every line
- Understand the pattern fully before applying

### 3. Identify Differences

- What's different between working and broken?
- List every difference, however small
- Don't assume "that can't matter"

### 4. Understand Dependencies

- What other components does this need?
- What settings, config, environment?
- What assumptions does it make?

---

## Phase 3: Hypothesis and Testing

**Scientific method:**

### 1. Form a Single Hypothesis

- State clearly: "I think X is the root cause because Y"
- Write it down
- Be specific, not vague

### 2. Test Minimally

- Make the SMALLEST possible change to test the hypothesis
- One variable at a time
- Don't fix multiple things at once

### 3. Verify Before Continuing

- Did it work? → Phase 4
- Didn't work? → Form NEW hypothesis
- DON'T add more fixes on top

### 4. When You Don't Know

- Say "I don't understand X"
- Don't pretend to know
- Ask the user for help
- Research more

---

## Phase 4: Implementation

**Fix the root cause, not the symptom:**

### 1. Create Failing Test Case

- Simplest possible reproduction
- Automated test if possible
- MUST have before fixing
- Use the `test-driven-development` skill

### 2. Implement Single Fix

- Address the root cause identified
- ONE change at a time
- No "while I'm here" improvements
- No bundled refactoring

### 3. Verify Fix

```bash
# Run the specific regression test
pytest tests/test_module.py::test_regression -v

# Run full suite — no regressions
pytest tests/ -q
```

### 4. If Fix Doesn't Work — The Rule of Three

- **STOP.**
- Count: How many fixes have you tried?
- If < 3: Return to Phase 1, re-analyze with new information
- **If ≥ 3: STOP and question the architecture (step 5 below)**
- DON'T attempt Fix #4 without architectural discussion

### 5. If 3+ Fixes Failed: Question Architecture

**Pattern indicating an architectural problem:**
- Each fix reveals new shared state/coupling in a different place
- Fixes require "massive refactoring" to implement
- Each fix creates new symptoms elsewhere

**STOP and question fundamentals:**
- Is this pattern fundamentally sound?
- Are we "sticking with it through sheer inertia"?
- Should we refactor the architecture vs. continue fixing symptoms?

**Discuss with the user before attempting more fixes.**

This is NOT a failed hypothesis — this is a wrong architecture.

---

## Pitfall: Tool Output Escaping Traps

When analyzing code for regex/string escaping bugs, `read_file` escapes backslashes in its output. A file containing `\\n` (2 backslashes + n) displays as `\\\\n` (4 backslashes in the output). This can lead to misdiagnosing a correct regex as broken.

**ALWAYS verify at the byte level before proposing escaping fixes:**

```bash
# See actual bytes in the file
sed -n 'LINEp' file.ts | xxd | head
# or
grep -n 'pattern' file.ts | cat -v
```

If the xxd shows `5c 5c 6e`, the file has `\\n` (2 backslashes + n) — which in a JS regex `/\\n/g` correctly matches literal `\n`. This is the standard pattern for converting `\n` escape sequences to real newlines. Do NOT "fix" this.

**The trap:** Interpreting display-layer escaping as file-layer content, proposing a fix for a non-existent bug, and wasting time on a no-op patch.

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals a new problem in a different place**
- **"analise/verifique" → jumped to implementing fixes** (WRONG: user asked to analyze, not fix)

**ALL of these mean: STOP. Return to Phase 1.**

### Analyze vs. Implement — The #1 Mistake

When the user says "analise", "verifique", "olhe", "checou", "check if", "investigate", or "debug" — they want a DIAGNOSIS, not a fix. Do NOT:
- Create branches
- Delete files
- Modify code
- Push commits

DO:
- Read the code
- Trace the data flow
- Produce a written report with root causes
- Wait for the user to say "implemente" / "crie a branch" / "remova"

The user will explicitly ask for implementation when ready. Jumping ahead wastes their time and trust.

**If 3+ fixes failed:** Question the architecture (Phase 4 step 5).

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern, don't fix again. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence, trace data flow | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare, identify differences | Know what's different |
| **3. Hypothesis** | Form theory, test minimally, one variable at a time | Confirmed or new hypothesis |
| **4. Implementation** | Create regression test, fix root cause, verify | Bug resolved, all tests pass |

## Hermes Agent Integration

### Investigation Tools

Use these Hermes tools during Phase 1:

- **`search_files`** — Find error strings, trace function calls, locate patterns
- **`read_file`** — Read source code with line numbers for precise analysis
- **`terminal`** — Run tests, check git history, reproduce bugs
- **`web_search`/`web_extract`** — Research error messages, library docs

### With delegate_task

For complex multi-component debugging, dispatch investigation subagents:

```python
delegate_task(
    goal="Investigate why [specific test/behavior] fails",
    context="""
    Follow systematic-debugging skill:
    1. Read the error message carefully
    2. Reproduce the issue
    3. Trace the data flow to find root cause
    4. Report findings — do NOT fix yet

    Error: [paste full error]
    File: [path to failing code]
    Test command: [exact command]
    """,
    toolsets=['terminal', 'file']
)
```

### Debugging API Integrations in Serverless (Vercel, AWS Lambda, etc.)

When an external API call fails in a serverless environment, use **tagged console.log at every boundary**:

```ts
console.log("[ServiceName] Payload:", JSON.stringify(payload));
console.log("[ServiceName] Status:", response.status);
let data;
try { data = await response.json(); } catch {
  const text = await response.text();
  console.log("[ServiceName] Raw:", text);
}
console.log("[ServiceName] Response:", JSON.stringify(data));
```

Key rules:
- **Wrap every `response.json()` in try/catch** — serverless APIs can return non-JSON error bodies (HTML, XML, empty).
- **Tag logs with `[ServiceName]`** — makes them findable in Vercel's log viewer (Dashboard > Functions > Latest Logs).
- **Dual-try strategy** when unsure which credentials the user has: try the newer API first, fall back to legacy. Log which path succeeded.
- **Never use `writeFileSync` (or any filesystem write) in serverless functions** — Vercel/AWS Lambda filesystems are **read-only** at runtime. Any `writeFile`, `writeFileSync`, or file-based persistence throws silently in production while working fine locally. Fix: (a) wrap file writes in try/catch so they don't crash the happy path, (b) use a database (Vercel KV, Supabase, Turso) for real persistence, or (c) design the flow so no file write is needed for the success path (e.g. Pix QR code generation doesn't need to persist before showing the QR).

### With test-driven-development

When fixing bugs:
1. Write a test that reproduces the bug (RED)
2. Debug systematically to find root cause
3. Fix the root cause (GREEN)
4. The test proves the fix and prevents regression

### Pre-Commit Code Review (absorbed from requesting-code-review)

Automated verification pipeline before code lands. Load via `skill_view(name="systematic-debugging", file_path="references/pre-commit-review.md")`.

8-step process: get diff → static security scan → baseline tests/lint → self-review checklist → independent reviewer subagent → evaluate → auto-fix loop (max 2 cycles) → commit with `[verified]` prefix.

Core principle: No agent should verify its own work. Fresh context finds what you miss.

## Parallel Code Cleanup (absorbed from simplify-code)

Three focused reviewers running in parallel, aggregate findings, apply fixes. Load via `skill_view(name="systematic-debugging", file_path="references/parallel-cleanup.md")`.

Three reviewers: Code Reuse (find duplications), Code Quality (redundant state, copy-paste, leaky abstractions), Efficiency (unnecessary work, missed concurrency, memory issues). Run via `delegate_task` batch mode.

## References

- [`react-infinite-render-loop.md`](references/react-infinite-render-loop.md) — Diagnosing and fixing React `useEffect` dependency loops that cause repeated API calls and browser slowdown. Covers the inline-function-as-dep anti-pattern, How to Verify steps, and the stable-context-reference fix pattern.
- [`ethers-bad-data-contract-mismatch.md`](references/ethers-bad-data-contract-mismatch.md) — Diagnosing ethers.js `BAD_DATA` errors when calling contract functions the deployed bytecode doesn't have. Covers root causes (old deployment, wrong address, ABI drift), graceful handling with try/catch, complete local Hardhat dev workflow, MetaMask v13 configuration, and prevention.
- [`pagbank-checkout-br.md`](references/pagbank-checkout-br.md) — Brazilian payment integration with PagBank (formerly PagSeguro). Covers Basic Auth (email:token), order creation, webhook handling, redirect URL, Windows PowerShell testing, and Bipa crypto alternative.
- [`jest-typescript-strict-test-errors.md`](references/jest-typescript-strict-test-errors.md) — Jest + TypeScript strict mode test compilation failures. Covers import path miscalculation from deeply nested test dirs, `@types/jest@30` breaking changes (`jest.fn()` 0-1 type args), `strict: true` causing `never` inference on mock return values, and TypeORM entity nullable conventions (`string | null` vs `string?`).
- [`nextjs-production-error-defense.md`](references/nextjs-production-error-defense.md) — Next.js production error patterns: "e is not a function" root causes (IIFEs in JSX, stale CDN chunks, unchecked API response shapes), multi-layer error defense (ErrorBoundary → error.tsx → global-error.tsx → loading.tsx), API call hardening with AbortController timeout, and Vercel cache-busting strategy.
- [`rabbitmq-connectivity-diagnostics.md`](references/rabbitmq-connectivity-diagnostics.md) — Step-by-step RabbitMQ connectivity diagnostics for Kubernetes deployments. Covers the 4-layer model (URI Parse → DNS → TCP → AMQP Handshake), implementation code for Express health endpoints and Node.js CLI diagnostic scripts, and a K8s debugging checklist. Designed for debugging message queue connectivity issues.
- [`nodejs-url-query-string-mismatch.md`](references/nodejs-url-query-string-mismatch.md) — Node.js HTTP server returns wrong content type because `req.url === "/path"` fails when browser appends `?t=cacheBuster`. Covers debugging path (curl works, browser doesn't), raw byte inspection, fix pattern, and prevention.
- [`express5-typescript-pitfalls.md`](references/express5-typescript-pitfalls.md) — Express 5 breaking type changes in `@types/express@5.x`. Covers `req.params` typed as `string | string[]` instead of `string`, fix patterns, and prevention.
- [`cicd-config-propagation-debug.md`](references/cicd-config-propagation-debug.md) — Debugging when production services use fallback config values because CI/CD pipelines fail to inject environment variables. Step-by-step trace from application behavior → pod env vars → Helm values → pipeline YAML → source of truth.
- [`helm-eks-deployment-debug.md`](references/helm-eks-deployment-debug.md) — Debugging Helm "UPGRADE FAILED: context deadline exceeded" on EKS. Covers pod state diagnosis, anti-affinity/readiness-probe/RabbitMQ connectivity patterns, and CI/CD pipeline debugging workflow.
- [`vercel-readonly-filesystem.md`](references/vercel-readonly-filesystem.md) — Debugging crashes in Vercel serverless functions caused by writeFileSync/filesystem writes. Covers the read-only FS limitation, three fix options (try/catch, database, Vercel Blob), and a real-world Pix QR code example.
- [`taiff-connect-auth-flow-debug.md`](references/taiff-connect-auth-flow-debug.md) — Taiff Connect backend auth flow: provider fallback pattern (Twilio→Console), Firebase social login pitfalls, forgot-password TODO email, Helm env injection debugging.

## Real-World Impact

From debugging sessions:
- Systematic approach: 15-30 minutes to fix
- Random fixes approach: 2-3 hours of thrashing
- First-time fix rate: 95% vs 40%
- New bugs introduced: Near zero vs common

**No shortcuts. No guessing. Systematic always wins.**
