# Build do Vercel / CI morre por ERESOLVE no npm install

## Sintoma
- O Vercel "não fez build" — ou o GH Actions falha já no passo de instalação.
- Rodando `npm install` localmente (puro, sem flags) o comando FALHA com:
  `npm error ERESOLVE could not resolve ... While resolving: @mui/styles@5.16.6 ... Found: react@18.3.1`
- O build NUNCA chega a rodar porque a instalação morre antes. Vercel não expõe log útil quando o install falha — só "Build Failed". É o root cause nº1 de "Vercel não buildou" que não é conexão do repo.

## Causa raiz
Conflito de peer dependency. Ex. comum em MUI: `@mui/styles@5` + React 18.
No Vercel o install padrão é `npm install` (não usa `--legacy-peer-deps`), então qualquer peer-conflict mata o build.

## Fix (no repo — resolve local, Vercel E CI de uma vez)

### 1. `.npmrc` na raiz do projeto (fix principal)
```
legacy-peer-deps=true
```
Confirmado: com esse arquivo, `npm install` puro passa (exit 0). Local, Vercel e Actions leem o mesmo `.npmrc`, então basta isso.

### 2. `vercel.json` (defensivo, explicita a intenção)
```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "installCommand": "npm install --legacy-peer-deps",
  "outputDirectory": ".next"
}
```

### 3. GitHub Actions como GATE de build (não depender só do Vercel)
```yaml
name: CI
on:
  push:
    branches: [master]
  pull_request:
    branches: [master]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5      # v5, NÃO v4
      - uses: actions/setup-node@v5    # v4 roda Node 20 (deprecado nos runners)
        with:
          node-version: 20
          cache: npm
      - run: npm install
      - run: npm run lint
      - run: npx tsc --noEmit
      - run: npm run build
```
- O workflow dispara no PUSH DO PR — auto-valida a própria branch. Se o PR roda verde, o build do Vercel também vai (mesmo install/build).
- Verificar: `gh run list --workflow=ci.yml` e `gh run watch <RUN_ID> --exit-status`.

## Escopo e limites honestos
- Sem token/CLI do Vercel NÃO dá para mexer no painel (conectar projeto ao repo, redeploy manual). Se depois do fix o Vercel ainda não construir, o restante é CONEXÃO do projeto no painel (Vercel → Settings → GitHub) — dashboard, não código. Dizer isso ao usuário, não adivinhar.

## Pitfalls extra
- Actions `@v4` (`checkout`, `setup-node`) disparam aviso "Node 20 is deprecated ... forced to run on Node 24" nos runners. Irrelevante ao build mas polui todo run. Subir para `@v5`.
- Regenerar `package-lock.json` com npm novo → diff costuma ser só campos `deprecated` novos (sem troca de versões) — inócuo.
- Não commitar mudança não explicada em `yarn.lock` num repo que usa npm; restaurar com `git checkout origin/master -- yarn.lock`.
- `gh pr create` para branch nova cujo base é uma branch já mergeada pode falhar com "No commits between ... (createPullRequest)" se a branch foi criada de base antiga — rebasear/realinhar em `origin/master` atual antes.