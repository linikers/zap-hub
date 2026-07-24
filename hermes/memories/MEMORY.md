User: direto pt-BR, admite erro, prático, solução simples, sem over-engineering. Resumo tabular 🔴🟡🟢. Análise arquitetural antes de grandes mudanças. Build local + testar OBRIGATÓRIO antes de push. Branch→PR→aprova→merge.
§
Gosta que eu ofereça treinamento/configuracao completa depois de implementar. Quer entender o estado real do projeto (oq funciona, oq é mock, oq falta). Aprecia resumo tabular com prioridades (🔴🟡🟢).
§
Marketing OS: monorepo Turbo+Next+Prisma+PG. API 3002, Dash 3001. marketing.linikers.cloud. Self-hosted runner deploy. Roles: ADMIN>MANAGER>VIEWER. Alcides=MANAGER (alcides@linikers.cloud). Chat compartilhado, precisa individual. Builder local obrigatório.
§
Ads: Google token pendente. Meta App 1569613858007188 OK. ML configurado (refresh). /ads tabs Todas/Google/Meta/ML. Sync auto.
§
Provedor LLM: OpenCode Go (opencode.ai/zen/go/v1). Prefere pt-BR direto, testar imediatamente. Exige que eu admita erro na hora em vez de tentar justificar ou contornar.
§
Workflow: branch → PR → usuário aprova → merge. Build local (npm run build + prisma generate) OBRIGATORIO antes de push. CI: lint strict, type-check, build. Deploy via self-hosted runner no VPS (nao SSH). Backup pg 12h, health 5min, cleanup semanal. Login admin@marketingos.com/admin123.
§
Taiff Connect S3/CloudFront: Bucket `taiff-produtos-midia`, CloudFront `digsnzaapp4io.cloudfront.net`. 69 produtos, 206 mídias (64 imgs, 64 fichas, 63 manuais, 15 logos). Migration produto catálogo (PR#114) usa `hasColumn()` porque DevOps adiciona colunas direto no Postgres. PVC com `storageClassName: gp2`. SendGrid funciona mas email não chega (DMARC). RabbitMQ: user `api-taiff`, pass `taif@@`. 113 arquivos (logos+vídeos) pendentes. DevOps: "adria".
§
Versão 1.6.1→1.6.3999→1.7.0. Footer sidebar. CHANGELOG+git tags. 403 amigável. Taiff CloudFront: 113 arquivos pendentes (logos+vídeos).