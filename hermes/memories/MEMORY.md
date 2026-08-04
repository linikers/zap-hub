User: direto pt-BR, admite erro, prático, solução simples. Resumo tabular 🔴🟡🟢. Análise arquitetural antes de grandes mudanças. Build+teste local OBRIGATÓRIO antes de push. Branch→PR→aprova→merge. Oferecer treinamento/config completa depois de implementar. Quer estado real do projeto (oq funciona/mock/falta).
§
Chat individual por user (userId). ADMIN ve todos historicos, outros veem so os seus.
§
MarketingOS: v1.7.0. Footer sidebar. MANAGER=ADMIN sem usuarios/whatsapp/pricing. CI: lint+type-check+build. Deploy VPS via self-hosted runner. Login admin@marketingos.com/admin123. OpenCode Go provider, deepseek-v4-flash com fallback reasoning_content→content. OPENCODE_API_KEY no systemd.
§
PUSH: lint+type-check+build+test LOCAL antes de push (build force nos pacotes). CI vermelho = falha minha. Lint empty catch: precisa eslint-disable-next-line (comentario nao resolve). ML token: MERCADO_LIVRE_REFRESH_TOKEN no systemd, não no ads-credentials.json. carregarConfig() merge JSON + env.
§
Taiff: catálogo S3/CloudFront; migration: hasColumn() antes de addColumn(); migrations rodam no deploy (job helm). RabbitMQ #18 OK (03/08): broker VPS porta 5673 vhost taiff, RABBIT_URI secret GH; senha .env RABBIT_URI_PROD. #57 backend pronto: GET /devices/mine + PATCH /devices/:id. Migração EKS precisa kubeconfig.
§
Marketing OS landing: public/*.html só com extensão; CSS inline >10KB quebra build Vercel → MUI sx.
§
MarketingOS Ads: Meta v21 usa OUTCOME_* (VENDAS→OUTCOME_SALES, LEADS→OUTCOME_LEADS, TRAFEGO→OUTCOME_TRAFFIC, ENGAJAMENTO→OUTCOME_ENGAGEMENT) + is_adset_budget_sharing_enabled=false obrigatório. Google API=v21 (v18-20 deprecadas), dev token só p/ contas de teste. 413: nginx 10m + express 15mb (servidor).
§
AutoHedge cron: key real no .env → run.py --trade direto; senão scripts/cron_run_trade.py.
§
Relatorio HBS (deltasge): azkaban manda grupoNotas 'Base Nacional Comum'/'Parte Diversificada' (padrão modelo1Fundamental, NÃO áreas). historicoEscolar.css compartilhado c/ modelo1 → só regras aditivas escopadas #modelo-187-*. Texto vertical: .vertical-text + span (span herda 8pt global). Usuário: análise antes de alterar, mudanças cirúrgicas (só hbs+css), testa em outra máquina.