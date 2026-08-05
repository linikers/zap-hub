User: direto pt-BR, admite erro, prático, solução simples. Resumo tabular 🔴🟡🟢. Análise arquitetural antes de grandes mudanças. Build+teste local OBRIGATÓRIO antes de push. Branch→PR→aprova→merge. Oferecer treinamento/config completa depois de implementar. Quer estado real do projeto (oq funciona/mock/falta).
§
Chat individual por user (userId). ADMIN ve todos historicos, outros veem so os seus.
§
MarketingOS: v1.7.0. Footer sidebar. MANAGER=ADMIN sem usuarios/whatsapp/pricing. CI: lint+type-check+build. Deploy VPS via self-hosted runner. Login admin@marketingos.com/admin123. OpenCode Go provider, deepseek-v4-flash com fallback reasoning_content→content. OPENCODE_API_KEY no systemd.
§
Lint empty catch: precisa eslint-disable-next-line (comentario não resolve). ML token: MERCADO_LIVRE_REFRESH_TOKEN no systemd (não no ads-credentials.json). carregarConfig() merge JSON+env.
§
MarketingOS landing: CSS inline >10KB quebra build Vercel → MUI sx.
§
MarketingOS Ads: Meta v21 usa OUTCOME_* (VENDAS→OUTCOME_SALES, LEADS→OUTCOME_LEADS, TRAFEGO→OUTCOME_TRAFFIC, ENGAJAMENTO→OUTCOME_ENGAGEMENT) + is_adset_budget_sharing_enabled=false obrigatório. Google API=v21 (v18-20 deprecadas), dev token só p/ contas de teste. 413: nginx 10m + express 15mb (servidor).
§
AutoHedge cron: key real no .env → run.py --trade direto; senão scripts/cron_run_trade.py.
§
Relatorio HBS (deltasge): azkaban manda grupoNotas 'Base Nacional Comum'/'Parte Diversificada' (padrão modelo1Fundamental, NÃO áreas). historicoEscolar.css compartilhado c/ modelo1 → só regras aditivas escopadas #modelo-187-*. Texto vertical: .vertical-text + span (span herda 8pt global). Usuário: análise antes de alterar, mudanças cirúrgicas (só hbs+css), testa em outra máquina.
§
Taiff: RabbitMQ EKS ok; rollback .rabbit-rollback.txt. Migration: default de STRING com aspas ('ativo') senão 'cannot use column reference in DEFAULT expression'. Implementados: ManualDigital #123, Analytics #121, ModosInteligentes #122. Pendente: #39 chat (só falta OPENAI_API_KEY no helm), #96 perf; standby #71/#72/#127. Front admin nosso, app outra equipe. Backend NÃO fala BLE — app aplica, backend persiste presets.