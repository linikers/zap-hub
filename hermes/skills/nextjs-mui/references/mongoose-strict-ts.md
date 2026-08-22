# Mongoose 8 + Next.js + strict TypeScript: fixing `connection.db` is possibly `undefined`

## Problem

With TypeScript's `strict: true` (which enables `strictNullChecks`), this code fails to compile:

```typescript
const db = (await dbConnect()).connection.db;
const user = await db.collection("users").findOne({ email });
//          ^^ Type error: 'db' is possibly 'undefined'
```

`mongoose.connection.db` has the type `Db | undefined` because Mongoose does not guarantee the underlying MongoDB driver connection is established at the type level. This is a real possibility — if `.connect()` hasn't resolved fully, `.db` can be `undefined`.

## Solution: `getDb()` helper

Create a helper in your MongoDB connection module that handles the null check and returns a definitely-typed `Db`:

```typescript
// src/lib/mongodb.ts
import mongoose from 'mongoose';
import type { Db } from 'mongodb';

// ... existing dbConnect() function ...

export async function getDb(): Promise<Db> {
  const conn = await dbConnect();
  const db = conn.connection.db;
  if (!db) {
    throw new Error('MongoDB connection not established');
  }
  return db;
}
```

Then in API routes that need the raw MongoDB driver:

```typescript
// Before (build error)
const db = (await dbConnect()).connection.db;

// After (clean)
const db = await getDb();
```

## Benefits

- **Type-safe**: returns `Promise<Db>`, never `Db | undefined`
- **Runtime safety**: throws an explicit error if `db` is undefined, rather than crashing later with a cryptic `.collection is not a function`
- **Dead-simple**: one helper function replaces the pattern across all API routes
- **No redundant calls**: also fixes the common anti-pattern of calling `await dbConnect()` twice (once to connect, once for `.connection.db`)

## Scope

This applies to any project using:
- Mongoose 8.x (any version with `Db | undefined` typing)
- TypeScript with `strict: true` (or `strictNullChecks: true`)
- Next.js Pages Router API routes (`/pages/api/*.ts`)

The same pattern applies to App Router routes (`/app/api/*/route.ts`) as well — the Mongoose type issue is independent of router version.
