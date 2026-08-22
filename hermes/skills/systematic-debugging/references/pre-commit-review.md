# Pre-Commit Code Review (absorbed from requesting-code-review skill)

## Step 1 — Get the diff
```bash
git diff --cached
```
If empty, try `git diff` then `git diff HEAD~1 HEAD`.

## Step 2 — Static security scan
```bash
# Hardcoded secrets
git diff --cached | grep "^+" | grep -iE "(api_key|secret|password|token|passwd)\s*=\s*['\"][^'\"]{6,}['\"]"

# Shell injection
git diff --cached | grep "^+" | grep -E "os\.system\(|subprocess.*shell=True"

# Dangerous eval/exec
git diff --cached | grep "^+" | grep -E "\beval\(|\bexec\("

# Unsafe deserialization
git diff --cached | grep "^+" | grep -E "pickle\.loads?\("

# SQL injection
git diff --cached | grep "^+" | grep -E "execute\(f\"|\.format\(.*SELECT|\.format\(.*INSERT"
```

## Step 3 — Baseline tests and linting
Detect project language, run tests. Capture baseline_failures BEFORE changes (stash, run, pop). Only NEW failures block the commit.

```bash
# Python
python -m pytest --tb=no -q 2>&1 | tail -5
which ruff && ruff check . 2>&1 | tail -10

# Node
npm test -- --passWithNoTests 2>&1 | tail -10
which npx && npx eslint . 2>&1 | tail -10
```

## Step 4 — Self-review checklist
- No hardcoded secrets/credentials
- Input validation on user data
- SQL uses parameterized statements
- File ops validate paths
- External calls have error handling
- No debug print/console.log left
- No commented-out code
- New code has tests

## Step 5 — Independent reviewer subagent
```python
delegate_task(
    goal="""You are an independent code reviewer. Review the git diff and return ONLY valid JSON.

FAIL-CLOSED RULES:
- security_concerns non-empty -> passed must be false
- logic_errors non-empty -> passed must be false
- Cannot parse diff -> passed must be false

<code_changes>
[INSERT GIT DIFF]
</code_changes>

Return ONLY this JSON:
{
  "passed": true or false,
  "security_concerns": [],
  "logic_errors": [],
  "suggestions": [],
  "summary": "one sentence verdict"
}""",
    context="Independent code review.",
    toolsets=["terminal"]
)
```

## Step 6 — Evaluate
All passed → Step 8 (commit). Any failures → Step 7 (auto-fix).

## Step 7 — Auto-fix loop
Maximum 2 fix-and-reverify cycles. Spawn a THIRD agent context to fix ONLY reported issues. Re-run Steps 1-6 after fix.

## Step 8 — Commit
```bash
git add -A && git commit -m "[verified] <description>"
```
