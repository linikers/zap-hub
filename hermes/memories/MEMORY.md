User exige análise arquitetural (Prompt 0) antes de implementar mudanças grandes — revisar SOLID, escalabilidade, duplicações, dependências circulares e aguardar aprovação. Relatórios estruturados obrigatórios. Não tolera retrabalho. Tech debt deve ser documentado como GitHub Issues para rastreamento.
§
Gosta que eu ofereça treinamento/configuracao completa depois de implementar. Quer entender o estado real do projeto (oq funciona, oq é mock, oq falta). Aprecia resumo tabular com prioridades (🔴🟡🟢).
§
Marketing OS: monorepo Turbo+Next+Prisma+PG. API 3002, Dash 3001. Domínios: marketing.linikers.cloud (VPS 2.24.115.130, SSL). CI/CD self-hosted runner VPS. Backup pg 12h, health 5min.
§
Google Ads/Meta Ads: brand verification OK, API Graph v21 ativa. App 1569613858007188.
§
Provedor LLM: OpenCode Go (opencode.ai/zen/go/v1). Prefere pt-BR direto, testar imediatamente. Exige que eu admita erro na hora em vez de tentar justificar ou contornar.
§
Workflow: branch → PR → usuário aprova → merge. Build local (npm run build + prisma generate) OBRIGATORIO antes de push. CI: lint strict, type-check, build. Deploy via self-hosted runner no VPS (nao SSH). Backup pg 12h, health 5min, cleanup semanal. Login admin@marketingos.com/admin123.
§
Portfolio linikers.cloud: Next.js + MUI v6 + framer-motion. Deploy Vercel.
§
User gosta de resolver problemas passo a passo, tem senso de humor, mas corrige rápido quando eu erro — prefere que eu admita o erro na hora em vez de justificar.
§
Ads /ads: tabs Google/Meta, sync auto ao carregar.
§
Marketing OS CI/CD: self-hosted runner no VPS substituiu SSH deploy (mais confiavel, mais rapido). Deploy automatico apos CI passar.
§
Taiff Connect S3/CloudFront: Bucket `taiff-produtos-midia`, CloudFront `digsnzaapp4io.cloudfront.net`. 69 produtos, 206 mídias (64 imgs, 64 fichas, 63 manuais, 15 logos). Migration produto catálogo (PR#114) usa `hasColumn()` porque DevOps adiciona colunas direto no Postgres. PVC com `storageClassName: gp2`. SendGrid funciona mas email não chega (DMARC). RabbitMQ: user `api-taiff`, pass `taif@@`. 113 arquivos (logos+vídeos) pendentes. DevOps: "adria".