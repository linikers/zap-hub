# NextAuth Setup on Next.js 16+ (App Router)

NextAuth v4 with Google OAuth + Credentials provider, JWT sessions, no database required.

## Dependencies

```bash
npm install next-auth@4
```
Note: `next-auth@5` does NOT exist as of 2026. Use v4 with Next.js 16.

## File Structure

```
src/
├── lib/
│   ├── auth.ts              ← NextAuth config (providers, callbacks)
│   └── AuthProvider.tsx      ← Client component wrapping SessionProvider
├── app/
│   ├── layout.tsx            ← Wrap children with AuthProvider
│   ├── login/page.tsx        ← Custom login page
│   ├── register/page.tsx     ← Registration page
│   ├── conta/page.tsx        ← Protected account page
│   └── api/auth/[...nextauth]/route.ts  ← NextAuth API handler
└── types/
    └── next-auth.d.ts        ← Type augmentation for session.user.id
```

## Auth Config (`src/lib/auth.ts`)

```ts
import { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import CredentialsProvider from "next-auth/providers/credentials";

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Senha", type: "password" },
      },
      async authorize(credentials) {
        // Mock: replace with DB query in production
        if (credentials?.email?.includes("@") && credentials?.password === "123456") {
          return { id: "1", name: credentials.email.split("@")[0], email: credentials.email };
        }
        return null;
      },
    }),
  ],
  secret: process.env.NEXTAUTH_SECRET || "dev-fallback-secret",
  session: { strategy: "jwt" },
  pages: { signIn: "/login" },
  callbacks: {
    async session({ session, token }) {
      if (token && session.user) {
        (session.user as any).id = token.sub as string;
      }
      return session;
    },
  },
};
```

## Type Augmentation (`src/types/next-auth.d.ts`)

```ts
import "next-auth";

declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
    };
  }
}
```

## API Route

```ts
// src/app/api/auth/[...nextauth]/route.ts
import NextAuth from "next-auth";
import { authOptions } from "@/lib/auth";

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
```

## Client Provider

```tsx
"use client";
import { SessionProvider } from "next-auth/react";
import { ReactNode } from "react";

export default function AuthProvider({ children }: { children: ReactNode }) {
  return <SessionProvider>{children}</SessionProvider>;
}
```

## Layout Integration Order

```tsx
<AuthProvider>
  <MuiProvider>
    <CartProvider>{children}</CartProvider>
  </MuiProvider>
</AuthProvider>
```

## Sign In / Sign Out

```tsx
import { signIn, signOut, useSession } from "next-auth/react";

signIn("google", { callbackUrl: "/" });
signIn("credentials", { email, password, redirect: false });
signOut({ callbackUrl: "/" });

const { data: session, status } = useSession();
// status: "loading" | "authenticated" | "unauthenticated"
```

## File-Based Auth (JSON Storage)

For prototyping without a database, store users in a JSON file:

```ts
// src/lib/auth.ts — Credentials provider with JSON validation
import { readFileSync, existsSync } from "fs";
import path from "path";

const DATA_PATH = path.join(process.cwd(), "src/data/usuarios.json");

interface Usuario {
  nome: string;
  email: string;
  senha: string;
  admin: boolean;
  criadoEm: string;
}

function lerUsuarios(): Usuario[] {
  if (!existsSync(DATA_PATH)) return [];
  return JSON.parse(readFileSync(DATA_PATH, "utf-8"));
}

// In authorize():
async authorize(credentials) {
  const usuarios = lerUsuarios();
  const usuario = usuarios.find(
    (u) => u.email === credentials?.email && u.senha === credentials?.password
  );
  if (usuario) {
    return { id: usuario.email, name: usuario.nome, email: usuario.email, admin: usuario.admin };
  }
  return null;
}
```

### Register API route
```ts
// src/app/api/auth/register/route.ts
// Validates: required fields, email format, password >= 6 chars, no duplicate email
// First registered user becomes admin automatically
// Writes to src/data/usuarios.json
```

## Login Redirect for Admin Users

After credentials login, check the session for admin status and redirect accordingly:

```tsx
const handleEmailLogin = async (e: React.FormEvent) => {
  e.preventDefault();
  const result = await signIn("credentials", { email, password, redirect: false });

  if (result?.error) {
    setError("Credenciais inválidas");
    return;
  }

  // Retry session fetch to avoid race condition (NextAuth may not have set JWT yet)
  let session: any = null;
  for (let i = 0; i < 5; i++) {
    try {
      const res = await fetch("/api/auth/session");
      if (res.ok) {
        session = await res.json();
        if (session?.user) break;
      }
    } catch {}
    await new Promise((r) => setTimeout(r, 200));
  }

  if (session?.user?.admin) {
    router.push("/admin");
  } else {
    router.push("/");
  }
};
```

The retry loop prevents `POST /api/auth/_log 404` errors caused by a race condition where the session JWT isn't ready immediately after `signIn` returns.

### Admin Role in Session
```ts
// In JWT callback — persist admin flag
async jwt({ token, user }) {
  if (user) token.admin = (user as any).admin || false;
  return token;
}

// In session callback — expose admin flag
async session({ session, token }) {
  (session.user as any).admin = token.admin || false;
  return session;
}

// Type augmentation (next-auth.d.ts)
interface Session { user: { admin: boolean } }
interface User { admin?: boolean }
```

## ENV Variables

```
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
NEXTAUTH_SECRET=your-random-secret
NEXTAUTH_URL=http://localhost:3000
```

## Pitfalls

- next-auth@5 does not exist. v4 is current.
- Google OAuth callback URL pattern: `[origin]/api/auth/callback/google`
- session.user.id requires next-auth.d.ts type augmentation
- AuthProvider must be `"use client"` (SessionProvider uses React context)
- Credentials + JWT is prototyping-only. Add a real DB for production.
- Set pages.signIn in authOptions to use a custom login page instead of NextAuth's default.
