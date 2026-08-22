# Jest + TypeScript Strict Mode Test Compilation Errors

## Class of Problem

Tests fail to compile (TS errors) instead of failing at runtime. The TS compiler (via `ts-jest`) rejects the test file before it can run. Common causes:

1. **Import path miscalculation** from deeply nested test directories
2. **`@types/jest` breaking changes** (v30 simplified `jest.fn()` generics)
3. **`strict: true` causing `never` inference** on mock return values
4. **Null/undefined mismatch** between TypeORM entities and service code

---

## Symptom 1: TS2307 — Cannot find module

**Error:**
```
tests/unit/services/auth/GetProfileService.spec.ts:2:39
error TS2307: Cannot find module '../../../src/services/auth/GetProfileService'
```

**Root cause:** Import path calculated incorrectly from deeply nested test directory.

**How to verify:** Resolve the path manually:

```bash
node -e "
const path = require('path');
console.log(path.resolve(path.dirname('tests/unit/services/auth/test.spec.ts'), '../../../src/services/auth/Service'));
"
```

**Pattern:**
- From `tests/unit/services/<domain>/` → need `../../../../src/...` (4 levels up = project root)
- From `tests/unit/schemas/` → need `../../../src/...` (3 levels up = project root)
- Common mistake: `../../../src` from `tests/unit/services/<domain>/` resolves to `tests/src/`, NOT `src/`

**Fix:** Compare with a **known-working test** at the same depth level. Count the `../` in working tests:

| Test location | Working import | Broken import |
|---|---|---|
| `tests/unit/services/products/*.spec.ts` | `../../../../src/services/...` | — |
| `tests/unit/services/auth/*.spec.ts` | `../../../../src/services/...` | `../../../src/services/...` |

---

## Symptom 2: TS2558 — Expected 0-1 type arguments, but got 2

**Error:**
```
error TS2558: Expected 0-1 type arguments, but got 2

  const mockRepo = { findOneBy: jest.fn<any, any>() };
```

**Root cause:** `@types/jest@30` changed `jest.fn()` from 2 type params (`jest.fn<T, Y>()`) to 1 type param (`jest.fn<T>()`).

**Fix:** Remove type args entirely:
```ts
// ❌ BROKEN (jest <29 compatibility)
jest.fn<any, any>()

// ✅ WORKS (jest 30+)
jest.fn()
```

Same applies to `jest.Mock` — `jest.Mock<any, any>` is also broken. Use `jest.Mock` (0 args) or `jest.Mock<any>` (1 arg).

---

## Symptom 3: TS2345 — Argument of type '...' not assignable to parameter of type 'never'

**Error:**
```
error TS2345: Argument of type '{ id: string; nome: string; }'
is not assignable to parameter of type 'never'.

  mockRepo.findOneBy.mockResolvedValue({ id: "1", nome: "João" });
```

**Root cause:** In `strict: true` mode with `@types/jest@30`, `jest.fn()` returns `jest.Mock<unknown>`. But when used inside an object literal:

```ts
const mockRepo = { findOneBy: jest.fn() };
```

TypeScript infers `mockRepo.findOneBy` as `jest.Mock<unknown>` → `mockResolvedValue` expects `unknown | Promise<unknown>`. However, **strict inference collapses the type to `never`** in some contexts (a known interaction with TypeScript 5.9+ structural typing).

**Fix — cast the mock return values with `as any`:**

```ts
// ✅ WORKS — cast each call site
(mockRepo.findOneBy as any).mockResolvedValue({ id: "1", nome: "João" });

// Alternatively, cast the mock itself at assignment (requires careful typing)
const mockRepo = { findOneBy: jest.fn() as any };
```

This is consistent with how other passing tests in the codebase handle it (they use `as any` in `mockReturnValueOnce` calls).

---

## Symptom 4: TS2322 — Type 'string | null' not assignable to 'string | undefined'

**Error:**
```
error TS2322: Type 'string | null' is not assignable to type 'string | undefined'.
  Type 'null' is not assignable to type 'string | undefined'.

  profile.cep = data.cep ?? null;
```

**Root cause:** TypeORM entity declares nullable column as `string?` (which is `string | undefined`), but service code assigns `null` (from Yup schema transform).

**Fix — use `string | null` with `!` in entities, not `?`:**

```ts
// ❌ BROKEN — nullable = true with ? means string | undefined
@Column({ type: "varchar", length: 9, nullable: true })
cep?: string;

// ✅ WORKS — nullable = true with ! means string | null (follows project pattern)
@Column({ type: "varchar", length: 9, nullable: true })
cep!: string | null;
```

**Project convention check:** Look at other entities in the codebase (e.g., `Product.ts`) for the established pattern. `!` (definite assignment assertion) with explicit `| null` is standard in TypeORM entities where the column allows DB nulls.

---

## Systematic debugging flow for test suite failures

```
1. Read the THREE groups of errors:
   - TS2307 (module not found) → check IMPORT PATHS
   - TS2558 (wrong type args) → check jest.fn() SIGNATURE
   - TS2345 (never inference) → check MOCK TYPES
   - TS2322 (null vs undefined) → check ENTITY NULLABLE CONVENTION

2. For import paths: compare with a WORKING test at same depth
3. For type args: remove generics from jest.fn(), use as any on values
4. For null/undefined: align entity convention with project standard
5. Run only the failed tests first, then full suite
```
