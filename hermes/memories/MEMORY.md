User: direto pt-BR, admite erro, prático, solução simples. Resumo tabular 🔴🟡🟢. Análise arquitetural antes de grandes mudanças. Build+teste local OBRIGATÓRIO antes de push. Branch→PR→aprova→merge. Oferecer treinamento/config completa depois de implementar. Quer estado real do projeto (oq funciona/mock/falta).
§
catalogo: 5.581 prods (3.040 importados). Compra SO pelo preco real Shopee: lucro = mercado x 0,80 - custo; mercado <= custo = NAO COMPRAR. Lista diversificada (max 2 por tipo).
§
ML: ACCESS_TOKEN no systemd + self-healing 401.
§
HBS (deltasge): plano/analise ANTES de alterar; testa em outra maquina.
§
Taiff stick: owner_hash=token assinado (não id); access/revoke/unlink/transfer/lock prontos; ble lock 0xA0-0xA5; expira 24h.
§
watchdog a71d019b5232 avisa WhatsApp). Conversao: acao 'Contato' (page-load) mede linikers.cloud/ir/whatsapp.
§
Dogama: ~2.1k prods sem API, coleta via preview, cron 6h; creds config/.
§
CJ Dropshipping: token config/cj-credentials.json; cron 15d.
§
gh CLI: `gh pr edit` falha sem scope read:org → usar REST `gh api -X PATCH repos/O/R/pulls/N`.
§
Taiff admin: ADMIN só via create-admin.ts (register cria EXTERNAL); dbPassword RDS prod só via secrets do deploy.
§
Taiff: deploy roda migration sozinho (helm pre-upgrade) → merge na main aplica em prod. Swagger prod = runtime src/http/**. PG local taiff-pg-tmp:5434.
§
Fiverr: br.fiverr.com/linikers; copy/capas em /root/fiverr/.
§
Comunicacao: sem jargao; mostrar ONDE esta a falha antes do fix; veredito pedido ('sim ou nao') = responder a palavra primeiro; abrir site/QR no pane pra ele logar.
§
Entregar arquivo = MEDIA:/caminho em MAIÚSCULO ("Media:" não vira card); ele baixa pelo chat, não busca em /root.
§
Desligados 18/09/26 (RAM): NF-e (/opt/nfe-brasil; religar: compose start) e Rocketstar.
§
Trabalha em lotes com pausa; codigo novo vai no PR ja aberto (nao abrir PR novo).
§
Nunca usar 'hermes' em nomes em contas externas dele (tokens, projetos, apps).
§
PR de UI: quer analise visual ANTES de aprovar (capturas nos 2 temas + leitura critica do resultado); nao aprova sem ver a tela.
§
Terminal redige segredo na saida: nao julgar chave por ela (conferir no diff antes de mexer em prod).