User: direto pt-BR, admite erro, prático, solução simples, sem over-engineering. Resumo tabular 🔴🟡🟢. Análise arquitetural antes de grandes mudanças. Build local + testar OBRIGATÓRIO antes de push. Branch→PR→aprova→merge.
§
Gosta que eu ofereça treinamento/configuracao completa depois de implementar. Quer entender o estado real do projeto (oq funciona, oq é mock, oq falta). Aprecia resumo tabular com prioridades (🔴🟡🟢).
§
Chat individual por user (userId). ADMIN ve todos historicos, outros veem so os seus.
§
Ads: Google token pendente. Meta App 1569613858007188 OK. ML configurado (refresh). /ads tabs Todas/Google/Meta/ML. Sync auto.
§
AutoHedge: 0.14 SOL + $0.33 USDC ($10.73, -13.5%). Cron MA Bounce (be08b8b0e6fd) deprecated, DeepSeek pipeline (3a77ffd34c4d) 80% HOLD. Nova estratégia Fear<25→Fear>28 pronta pra deploy.
§
MarketingOS: v1.7.0. Footer sidebar. MANAGER=ADMIN sem usuarios/whatsapp/pricing. CI: lint+type-check+build. Deploy VPS via self-hosted runner. Login admin@marketingos.com/admin123. OpenCode Go provider, deepseek-v4-flash com fallback reasoning_content→content. OPENCODE_API_KEY no systemd.
§
Trading: rejeita propostas genéricas — exige backtest com dados reais ("de onde vc tirou?"). AutoHedge $10.73 (-$1.67). Estratégia vencedora: Fear<25→BUY, Fear>28→SELL, TP+2%, SL-3% (+22.2%/90d, 16 trades). Breakeven ~63d. Scripts backtest em /root/autohedge-bot/. Skill: crypto-trading-backtest.
§
PUSH: lint+type-check+build+test LOCAL antes de push. CI vermelho = falha minha. ML token: MERCADO_LIVRE_REFRESH_TOKEN no systemd, não no ads-credentials.json. carregarConfig() merge JSON + env.
§
Workflow: branch → PR → CI verde → merge. NUNCA push direto pra main. SEMPRE verificar lint + type-check + build + testes ANTES de push. Build force (npm run build nos pacotes modificados) pra garantir sem cache. NUNCA reportar "pronto" com CI vermelho. Lint empty catch: comentario nao resolve no-empty, precisa de eslint-disable-next-line.