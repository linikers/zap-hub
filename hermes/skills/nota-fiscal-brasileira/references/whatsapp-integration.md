# WhatsApp NFe Assistant — Integração com WhatsApp Cloud API

## Visão Geral

O Assistente NFe para WhatsApp permite que clientes consultem, validem e solicitem
serviços de nota fiscal diretamente pelo WhatsApp do estabelecimento, sem precisar
de atendente humano.

## Arquitetura

```
WhatsApp Client (telefone do cliente)
    ↕ (Cloud API Webhook)
Meta Graph API
    ↕ (POST /webhook)
whatsapp-cloud-bridge.py (porta 3001)
    │
    ├── detectar_intencao_nfe() ── sim ──→ handle_nfe_message()
    │   (mensagem fiscal)                  │
    │                                      ├── menu principal
    │                                      ├── consulta por chave
    │                                      ├── validação de XML
    │                                      ├── status SEFAZ
    │                                      ├── solicitação DANFE
    │                                      └── falar com atendente
    │
    └── detectar_intencao_nfe() ── não ──→ call_hermes()
        (mensagem normal)                    (hermes chat -q)
```

## Componentes

### `~/.hermes/scripts/whatsapp_nfe.py`
Módulo Python com o assistente NFe. Contém:

| Função | Descrição |
|--------|-----------|
| `detectar_intencao_nfe(texto)` | Detecta se a mensagem tem intenção fiscal. Retorna (bool, acao, params) |
| `handle_nfe_message(texto, from_number, nome_cliente, send_func, attachment_path)` | Handler principal — processa e responde |
| `validar_chave_acesso(chave)` | Valida chave de 44 dígitos (módulo 11) |
| `extrair_info_xml(xml_path)` | Parseia XML de NF-e e extrai dados |
| `formatar_whatsapp_resposta(texto)` | Remove markdown para WhatsApp |
| `responder_*()` | Funções que montam cada resposta do menu |

### Intenções Detectadas

| Ação | Gatilho | Descrição |
|------|---------|-----------|
| `menu_principal` | "menu", "ajuda", "nfe", "nota fiscal" | Menu interativo com 8 opções |
| `chave_detectada` | 44 dígitos numéricos | Chave de acesso identificada |
| `consultar_chave` | "consultar" + chave | Exibe dados da chave |
| `validar_xml` | "validar", "xml" | Pede envio do arquivo XML |
| `danfe` / `danfe_chave` | "danfe", "2 via", "2ª via" | Solicita 2ª via do DANFE |
| `status_sefaz` | "status", "sefaz" + UF | Status do serviço SEFAZ por estado |
| `emitir` | "emitir", "gerar", "quero nota" | Orientação para emissão |
| `cancelar` | "cancelar", "cancelamento" | Procedimento de cancelamento |
| `carta_correcao` | "carta de correção", "cc-e" | Informações sobre CC-e |
| `manifestacao` | "manifestar", "manifestação" | Opções de manifestação |
| `falar_atendente` | "atendente", "falar com" | Transfere para humano |

### Palavras-chave de Detecção

Definidas em `PALAVRAS_NFE` no módulo: nota fiscal, nfe, nfce, cte, danfe, xml,
fiscal, sefaz, nfse, manifestação, status, situação.

Também detecta números de menu (1-8), e qualquer string de 44 dígitos como chave.

### Fluxo XML Anexado

Quando o cliente envia um arquivo XML como documento:
1. Bridge baixa o media da API Graph (`download_media()`)
2. Salva em `/tmp/` e passa o caminho para `handle_nfe_message()`
3. Handler chama `extrair_info_xml()` (usa lxml)
4. Retorna dados formatados: emitente, destinatário, itens, valor, protocolo
5. Arquivo temporário é deletado após processamento

## Configuração

1. Bridge Cloud API deve estar rodando (`bash ~/.hermes/scripts/run-whatsapp-cloud.sh start`)
2. NFe handler é importado automaticamente pelo bridge
3. Nenhuma configuração extra necessária

## Testes

```bash
# Modo CLI interativo
cd ~/.hermes/scripts
python3 whatsapp_nfe.py

# Testar detector de intenção
python3 -c "
from whatsapp_nfe import detectar_intencao_nfe
tem, acao, params = detectar_intencao_nfe('quero consultar nfe')
print(f'Ação: {acao}, Params: {params}')
"

# Simular webhook
curl -X POST http://localhost:3001/webhook \
  -H "Content-Type: application/json" \
  -d '{"object":"whatsapp_business_account","entry":[{"id":"1278406254494004","changes":[{"value":{"messaging_product":"whatsapp","metadata":{"display_phone_number":"NUMBER","phone_number_id":"1044220182118213"},"messages":[{"from":"5511999999999","id":"test_nfe","type":"text","text":{"body":"quero nota fiscal"}}]}}]}]}'
```

## Limitações Atuais

- Geração real de DANFE exige XML autorizado + weasyprint/erpbrasil — implementação
  futura deve chamar `gerar_danfe()` da skill e enviar PDF como mídia
- Consulta SEFAZ em tempo real exige certificado A1 configurado no servidor
- Histórico de conversa não é mantido entre mensagens (cada chamada é fresh)
- Sandbox do Cloud API limita a 5 números de destinatários

## Alternativa: nfe-brasil (Evolution API + MCP Server)

Existe um repo monorepo que combina MCP server + WhatsApp bot + Evolution API:
- **Repo:** github.com/linikers/nfe-brasil
- **Approach:** Evolution API (Baileys) ao invés de Cloud API
- **Vantagens:** Não precisa de conta Meta, dashboard inclusa, multi-instância
- **Portas:** PostgreSQL 5433, Redis 6380, Evolution 8085, MCP 8090, Bot 3010
- **Bot persona:** Linguagem natural, sem códigos técnicos, envia PDF + links SEFAZ
- **Fluxo:** Chave → consulta + link SEFAZ | XML → DANFE PDF | CNPJ → dados empresa
- **Emissão do zero:** Pendente (ver issue #1 no repo) — requer certificado A1 + planilha de clientes
