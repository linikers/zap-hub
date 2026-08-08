User: direto pt-BR, admite erro, prático, solução simples. Resumo tabular 🔴🟡🟢. Análise arquitetural antes de grandes mudanças. Build+teste local OBRIGATÓRIO antes de push. Branch→PR→aprova→merge. Oferecer treinamento/config completa depois de implementar. Quer estado real do projeto (oq funciona/mock/falta).
§
Chat individual por user (userId). ADMIN ve todos historicos, outros veem so os seus.
§
MarketingOS: v1.7.0. MANAGER=ADMIN sem usuarios/whatsapp/pricing. CI: lint+type-check+build. Deploy VPS via self-hosted runner. OpenCode Go provider, deepseek-v4-flash com fallback reasoning_content→content. OPENCODE_API_KEY no systemd.
§
Lint empty catch: precisa eslint-disable-next-line. ML: ACCESS_TOKEN no systemd + self-healing 401; endpoint /users/{id}/items/search.
§
MarketingOS Ads: Meta v21 OUTCOME_* + is_adset_budget_sharing_enabled=false; insights [] ok. Google API=v21; dev token TESTE. 413: nginx 10m + express 15mb. Places: tela /places, API key por user (tabela PlacesConfig), leads sem site = quente. Dashboard: npx next start.
§
AutoHedge cron: key no .env → run.py --trade direto. portfolio/index.json: chaves trades[]/analyses[] (não trade_history/ultima_analise).
§
Relatorio HBS (deltasge): azkaban manda grupoNotas 'Base Nacional Comum'/'Parte Diversificada' (padrão modelo1Fundamental, NÃO áreas). historicoEscolar.css compartilhado c/ modelo1 → só regras aditivas escopadas #modelo-187-*. Texto vertical: .vertical-text + span (span herda 8pt global). Usuário: análise antes de alterar, mudanças cirúrgicas (só hbs+css), testa em outra máquina.
§
Taiff: RabbitMQ EKS ok; rollback .rabbit-rollback.txt. Feitos: #130 BLE webhook, #131 owner_hash HMAC, #132 logs (dispositivo+IP), #133 Sticky MERGED+TESTADO (S3 taiff-produtos-midia; anexos até 3; BLE 0xa2/0xa3/0xa4/0xba; AWS no helm). Foto perfil = PVC local (não S3). Chat #134 agente Supabase (AGENT_API_KEY/AGENT_ID no GH). Pendente #96. Backend não fala BLE.
§
linikers.cloud (com 'ni', NÃO linkers). Verificação domínio (Google/FB) no _app.tsx (não _document.jsx). Meta app 1569613858007188 modo DEV bloqueia anúncio (1885183); BSide page 1244998568955101, business 1729045410508773.