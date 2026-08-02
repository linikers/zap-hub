User: direto pt-BR, admite erro, prático, solução simples, sem over-engineering. Resumo tabular 🔴🟡🟢. Análise arquitetural antes de grandes mudanças. Build local + testar OBRIGATÓRIO antes de push. Branch→PR→aprova→merge.
§
Gosta que eu ofereça treinamento/configuracao completa depois de implementar. Quer entender o estado real do projeto (oq funciona, oq é mock, oq falta). Aprecia resumo tabular com prioridades (🔴🟡🟢).
§
Chat individual por user (userId). ADMIN ve todos historicos, outros veem so os seus.
§
MarketingOS: v1.7.0. Footer sidebar. MANAGER=ADMIN sem usuarios/whatsapp/pricing. CI: lint+type-check+build. Deploy VPS via self-hosted runner. Login admin@marketingos.com/admin123. OpenCode Go provider, deepseek-v4-flash com fallback reasoning_content→content. OPENCODE_API_KEY no systemd.
§
PUSH: lint+type-check+build+test LOCAL antes de push (build force nos pacotes). CI vermelho = falha minha. Lint empty catch: precisa eslint-disable-next-line (comentario nao resolve). ML token: MERCADO_LIVRE_REFRESH_TOKEN no systemd, não no ads-credentials.json. carregarConfig() merge JSON + env.
§
Taiff: catálogo S3/CloudFront; migration segura: hasColumn() antes de addColumn().
§
Marketing OS landing: public/*.html só com extensão; CSS inline >10KB quebra build Vercel → MUI sx.
§
MarketingOS Ads: Meta v21 usa OUTCOME_* (VENDAS→OUTCOME_SALES, LEADS→OUTCOME_LEADS, TRAFEGO→OUTCOME_TRAFFIC, ENGAJAMENTO→OUTCOME_ENGAGEMENT) + is_adset_budget_sharing_enabled=false obrigatório. Google API=v21 (v18-20 deprecadas), dev token só p/ contas de teste. 413: nginx 10m + express 15mb (servidor). Usuário abre PR sozinho quando decide que acabou.
§
AutoHedge cron: key real no .env (01/08/2026) → run.py --trade direto; se placeholder, scripts/cron_run_trade.py; runpy.run_path não seta sys.path[0].
§
Relatorio HBS (deltasge): azkaban manda grupoNotas 'Base Nacional Comum'/'Parte Diversificada' (padrão modelo1Fundamental, NÃO áreas). historicoEscolar.css compartilhado c/ modelo1 → só regras aditivas escopadas #modelo-187-*. Texto vertical: .vertical-text + span (span herda 8pt global). Usuário: análise antes de alterar, mudanças cirúrgicas (só hbs+css), testa em outra máquina.