# mcp-fiscal-brasil — MCP Server para NF-e

## O que é

Servidor MCP publicado no PyPI (`mcp-fiscal-brasil`, v0.4.0) com 43+ tools
fiscais brasileiras. Zero API key obrigatória. Criado por Nikolas de Hor
(DeHor-Labs), licença MIT.

**Repo:** https://github.com/DeHor-Labs/mcp-fiscal-brasil

## Instalação e execução

```bash
# Rápido (uvx, sem instalar)
uvx mcp-fiscal-brasil

# Desenvolvimento (editável)
git clone https://github.com/DeHor-Labs/mcp-fiscal-brasil.git
cd mcp-fiscal-brasil
python3 -m venv .venv && source .venv/bin/activate
pip install -e "."

# Modo HTTP (para testes/debug)
python -m mcp_fiscal_brasil.server --transport http --port 8321

# Modo stdio (para Claude Desktop / Hermes)
python -m mcp_fiscal_brasil.server --transport stdio
```

## Configuração no Hermes

Adicionar em `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  fiscal-brasil:
    command: "uvx"
    args: ["mcp-fiscal-brasil"]
```

Ou para versão local editável:

```yaml
mcp_servers:
  fiscal-brasil:
    command: "/caminho/para/mcp-fiscal-brasil/.venv/bin/python"
    args: ["-m", "mcp_fiscal_brasil.server"]
```

## Tools NF-e disponíveis (43 no total)

### Core NF-e
| Tool | Descrição |
|------|-----------|
| `consultar_nfe` | Consulta NF-e pela chave de 44 dígitos (via API pública) |
| `validar_chave_nfe` | Valida dígito verificador (mód 11, offline) |
| `parse_nfe_xml` | Parse XML completo → dados estruturados |
| `gerar_danfe` | Gera DANFE PDF do XML (modelo 55, via brazilfiscalreport) |
| `validar_assinatura_nfe` | Valida XMLDSig + extrai dados do certificado |
| `consultar_status_sefaz` | Status do webservice SEFAZ por UF |
| `baixar_nfe_distribuicao` | NFeDistribuicaoDFe via mTLS (requer cert A1) |
| `manifestar_nfe` | Manifestação do destinatário (210200-210240) |
| `validate_nfe_full` | Validação consolidada (XML + chave + CNPJ) |

### NFSe / Simples / MEI
| Tool | Descrição |
|------|-----------|
| `consultar_nfse` | Orientação por município (50+ portais mapeados) |
| `consultar_simples_nacional` | Situação Simples Nacional/MEI |
| `consultar_status_mei` | Status MEI |

### CNPJ / CPF / Empresa
| Tool | Descrição |
|------|-----------|
| `consultar_cnpj` | Dados cadastrais via BrasilAPI/ReceitaWS |
| `consultar_empresa_completa` | Dados consolidados + Simples + CNAE |
| `validar_cpf` | Validação offline (mód 11) |
| `consultar_empresas_lote` | Até 50 CNPJs em paralelo |

### SPED / eSocial
| Tool | Descrição |
|------|-----------|
| `analisar_sped` | Análise EFD-ICMS/IPI, EFD-Contribuições, ECD, ECF |
| `listar_registros_sped` | Busca registros específicos no SPED |
| `summarize_sped` | Resumo executivo do arquivo SPED |
| `listar_eventos_esocial` | Lista eventos S- (tabelas, não periódicos, etc.) |
| `validar_evento_esocial` | Validação básica de XML eSocial |

### Tabelas / Referência (offline, SQLite embutido)
| Tool | Descrição |
|------|-----------|
| `consultar_ncm` | Tabela NCM |
| `consultar_cfop` | Tabela CFOP |
| `consultar_cnae` | Tabela CNAE |
| `consultar_cst` | Tabela CST |
| `consultar_cest` | Tabela CEST |
| `consultar_aliquota_icms` | Alíquotas ICMS por UF |
| `buscar_cnae` | Busca textual por atividade |

### Agentic (alto nível)
| Tool | Descrição |
|------|-----------|
| `analyze_cnpj_compliance` | Score 0-100 + risco + achados |
| `compare_tax_regimes` | Compara MEI/Simples/LP/LR |
| `risk_score_supplier` | Due diligence de fornecedor |
| `simular_transicao_reforma_tributaria` | Projeção IBS/CBS 2026-2033 |

### Outros
| Tool | Descrição |
|------|-----------|
| `consultar_cep` | Endereço por CEP |
| `consultar_certidao_federal` | URLs CND (RFB/PGFN) |
| `consultar_certidao_fgts` | URLs CRF (Caixa) |
| `taxa_selic`, `ipca_periodo`, `ptax_data` | Indexadores BCB |

## Limitações conhecidas

- **NFSe**: cada município é um mundo — a tool retorna orientação/portal,
  não consulta direta (não há API nacional padronizada)
- **SEFAZ sem certificado**: tools de distribuição/manifestação retornam
  "indisponível" (esperado — requer A1)
- **CNAE**: pode falhar se a API pública retornar formato inesperado
- **NFC-e (modelo 65)**: DANFE não suportado (só modelo 55)
- **CT-e / MDF-e**: não implementados
- **eSocial**: só listagem, sem validação XSD completa

## Dependências principais

```
fastmcp>=3.2.0      # servidor MCP
httpx>=0.27.0        # HTTP async
pydantic>=2.0        # schemas
lxml>=6.1.0          # parse XML
signxml>=4.5.1       # assinatura XMLDSig
cryptography>=48.0   # certificados A1 (PKCS12)
brazilfiscalreport   # DANFE PDF
```

## Uso como SDK Python

```python
from mcp_fiscal_brasil import FiscalBrasil

# Ou diretamente dos módulos
from mcp_fiscal_brasil.shared.validators import validate_cnpj, validate_chave_nfe
from mcp_fiscal_brasil.nfe.tools import consultar_nfe, validar_chave_nfe
from mcp_fiscal_brasil.nfe.danfe import gerar_danfe
from mcp_fiscal_brasil.nfe.assinatura import validar_assinatura_nfe
```

## Fork para personalização (MIT)

O repositório é MIT. Pode forkar, renomear e adicionar implementações
próprias. Única obrigação: manter LICENSE + crédito ao autor original.

Estrutura monorepo recomendada (Opção C):

```
nfe-brasil/
├── mcp-server/          ← fork do DeHor-Labs (adaptado)
├── whatsapp-bot/        ← bridge + bot NF-e
├── shared/              ← docs, templates, scripts
├── docker-compose.yml   ← roda os 2 processos
└── README.md
```
