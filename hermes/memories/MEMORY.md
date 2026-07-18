User exige análise arquitetural (Prompt 0) antes de implementar mudanças grandes — revisar SOLID, escalabilidade, duplicações, dependências circulares e aguardar aprovação. Relatórios estruturados obrigatórios. Não tolera retrabalho. Tech debt deve ser documentado como GitHub Issues para rastreamento.
§
Gosta que eu ofereça treinamento/configuracao completa depois de implementar. Quer entender o estado real do projeto (oq funciona, oq é mock, oq falta). Aprecia resumo tabular com prioridades (🔴🟡🟢).
§
Marketing OS: monorepo Turbo+Next+Prisma+PG. API 3002, Dash 3001, Nginx proxy /api/→3002 /→3001. Domínios: linikers.cloud (portfolio), marketing.linikers.cloud (Marketing OS, VPS 2.24.115.130, SSL Let's Encrypt).
§
Google Ads: developerToken OEQDuF9ocvRef_5BoOKRSw, customerId 535-952-9291, refreshToken salvo. GAQL real client implementado. Redirect URI: https://marketing.linikers.cloud/api/ads/oauth/callback. SSL nginx. Default branch=main. Systemd API.
§
User é liniker — dono do Marketing OS (linikers.cloud / marketing.linikers.cloud). Email liniker.kurumin@gmail.com. Conta Google Ads 535-952-9291. NÃO tolera alucinação: se inventei dado, PR, projeto ou contexto (ex: Taiff Connect), ele corrige na hora e espera ação imediata, não justificativa. Prefere prints/evidência a texto descritivo. Exige acurácia total, respostas diretas e resultado concreto.
§
Provedor LLM: OpenCode Go (opencode.ai/zen/go/v1). Prefere pt-BR direto, testar imediatamente. Exige que eu admita erro na hora em vez de tentar justificar ou contornar.
§
CI Marketing OS: lint usa @typescript-eslint/no-explicit-any e no-unused-vars estritos. Type-check via root tsconfig com paths. Pacotes novos precisam ser adicionados ao root tsconfig paths. Arquivos pré-existentes com erro aceitam eslint-disable no topo.
§
Workflow: criar branch e PR em vez de commit direto na main para mudanças. Usuário aprova PR.
§
Google Ads developer token OEQDuF9ocvRef_5BoOKRSw em modo TESTE — pendente solicitar acesso básico no API Center pra conta real funcionar.