# Fechar uma área admin aberta (Next.js App Router + NextAuth v4)

Sintoma típico: o painel "pede login" na tela, mas a API responde sem cookie. O cliente
protege a interface; a rota não protege nada.

## 1. Medir antes de mexer

```bash
grep -rn "getServerSession" src | wc -l        # 0 = nenhuma rota valida sessão
ls src/middleware.ts 2>/dev/null               # ausente = nenhuma barreira antes do handler
```

Em produção, só GET e só o status — a resposta pode ter dado pessoal:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://SITE/api/admin/produtos
```

`200` sem cookie confirma. Não rode DELETE/PUT em produção: a prova de escrita é o build local.

## 2. Guard por handler (primeira camada)

`src/lib/api-auth.ts`:

```ts
import { getServerSession } from "next-auth";
import { NextResponse } from "next/server";
import { authOptions } from "@/lib/auth";

export async function requireAdmin(): Promise<NextResponse | null> {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Não autorizado" }, { status: 401 });
  if (!(session.user as { admin?: boolean }).admin)
    return NextResponse.json({ error: "Acesso restrito" }, { status: 403 });
  return null;
}
```

Em cada handler, como **primeira** instrução:

```ts
export async function GET() {
  const denied = await requireAdmin();
  if (denied) return denied;
  // ...
}
```

Inserir em massa num repo com muitos handlers (regex sobre a assinatura, preservando os args):

```python
import re, glob
GUARD = '\n  const denied = await requireAdmin();\n  if (denied) return denied;\n'
pat = re.compile(r'(export async function (GET|POST|PUT|PATCH|DELETE)\s*\([^)]*\)\s*\{)')
for f in glob.glob("src/app/api/admin/**/route.ts", recursive=True):
    if "callback" in f:   # redirect OAuth do provedor: sem sessão, fora do guard
        continue
    s = open(f).read()
    s = pat.sub(lambda m: m.group(1) + GUARD, s)
    if 'from "@/lib/api-auth"' not in s:
        s = 'import { requireAdmin } from "@/lib/api-auth";\n' + s
    open(f, "w").write(s)
```

## 3. Middleware (segunda camada)

```ts
// src/middleware.ts
export default withAuth(
  (req) => {
    if (req.nextauth.token?.admin) return NextResponse.next();
    if (req.nextUrl.pathname.startsWith("/api/admin"))
      return NextResponse.json({ error: "Não autorizado" }, { status: 401 });
    return NextResponse.redirect(new URL("/login", req.url));
  },
  { callbacks: { authorized: () => true }, pages: { signIn: "/login" } }
);
export const config = { matcher: ["/admin/:path*", "/api/admin/:path*"] };
```

`authorized` **precisa** devolver `true`. Devolvendo `Boolean(token)`, o `withAuth`
redireciona antes do seu código e a API responde 307 (HTML de login) em vez de 401 JSON.

## 4. Senha e sessão

- `bcryptjs` (puro JS, roda serverless) cost 10–12. Nunca comparar `senha === password`.
- Conta legada em texto puro: continua entrando e é migrada no primeiro login.

```ts
if (!usuario?.senha) return null;
const emHash = usuario.senha.startsWith("$2");
const confere = emHash
  ? await compare(credentials.password, usuario.senha)
  : usuario.senha === credentials.password;
if (!confere) return null;
if (!emHash) {
  await prisma.user.update({
    where: { id: usuario.id },
    data: { senha: await hash(credentials.password, 12) },
  });
}
return { id: usuario.id, name: usuario.name, email: usuario.email, admin: usuario.admin };
```

- `secret: process.env.NEXTAUTH_SECRET || "qualquer-string"` é forjável: quem lê o repo assina
  JWT com `admin: true`. Remova o fallback — mas **confirme a env ANTES do merge, não depois**:

  ```bash
  npx vercel link --yes --scope <time> --project <projeto>
  npx vercel env ls production | grep NEXTAUTH_SECRET   # vazio = o site cai no merge
  ```

  O fallback mascarava a ausência da variável; sem ele o NextAuth recusa assinar e **o painel
  inteiro sai do ar no instante do deploy**. Se a env não existir, crie antes:

  ```bash
  openssl rand -base64 48 | tr -d '\n' | npx vercel env add NEXTAUTH_SECRET production
  openssl rand -base64 48 | tr -d '\n' | npx vercel env add NEXTAUTH_SECRET preview
  ```

  Env nova só vale em deploy novo: republique. Trocar o segredo **invalida as sessões
  existentes** — avise que o dono vai precisar logar de novo, junto com o fix, em vez de
  deixá-lo descobrir sozinho.

  Diagnóstico do sintoma (não é banco, não é CORS, não é o middleware):

  ```bash
  curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' https://SITE/admin
  # 307 https://SITE/api/auth/error?error=Configuration
  curl -s -o /dev/null -w '%{http_code}\n' https://SITE/api/auth/providers   # 500
  ```

  `error=Configuration` + `500` em `/api/auth/*` com o site público em `200` = segredo de sessão
  ausente. Não investigue Prisma nem middleware antes de checar isso.
- Cadastro **nunca** deriva `admin` de "é o primeiro usuário": em banco vazio o primeiro visitante
  que se cadastra vira dono do painel.

## 5. CORS

`Access-Control-Allow-Origin: *` em `/api/:path*` inclui o admin. Webhook server-to-server não usa
CORS; restrinja a uma allowlist por env (`CORS_ALLOWED_ORIGINS`) em vez do curinga.

## 6. Provar que fechou (build de produção local)

```bash
ss -lptn 'sport = :3055' && kill <pid>      # mate pela porta, não por nome
npx next build
NEXTAUTH_SECRET=teste npx next start -p 3055 &
for r in produtos pedidos stats pagamentos categorias banners; do
  printf "%-12s %s\n" "$r" "$(curl -s -o /dev/null -w '%{http_code}' localhost:3055/api/admin/$r)"
done
curl -s -o /dev/null -w '%{http_code}\n' -X DELETE localhost:3055/api/admin/produtos/1
curl -s -o /dev/null -w '%{http_code} -> %{redirect_url}\n' localhost:3055/admin/produtos
curl -s -o /dev/null -w '%{http_code}\n' localhost:3055/            # público segue 200
```

Esperado: `401` em todas as rotas de API (inclusive DELETE/POST), `307 -> /login?callbackUrl=…`
na página, `200` no site público. Se vier `307` na API, o `authorized` do `withAuth` está barrando
antes do seu código. Se vier `401` no site público, o matcher está largo demais.

Preview da Vercel protegido por SSO não serve para esse teste — use o build local.
