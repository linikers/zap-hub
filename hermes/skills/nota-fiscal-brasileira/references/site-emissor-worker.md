# Loja (e-commerce) → emissor próprio `nfe-brasil`: o contrato

Arquitetura validada no CarCrew e reutilizável em qualquer loja que use o `linikers/nfe-brasil` como emissor. **A loja não emite**: ela mantém a fila, monta o payload e recebe o resultado; o worker no servidor assina e transmite.

## Por que worker e não a aplicação

Emissão precisa de **certificado A1 em disco**, SOAP persistente e retry — não cabe em serverless (Vercel/Lambda) nem em request de usuário. O worker roda como processo no servidor (systemd/cron), com backoff: SEFAZ fora do ar é rotina.

```
loja (fila + pacote) --GET /api/fiscal/pendentes (Bearer cc_...)-> worker
worker --montar_pacote() assina / emitir() transmite-> SEFAZ
worker --POST /api/fiscal/retorno-> loja (autorizada | rejeitada + motivo)
```

## Contrato do pull

- Autenticação por **chave de API** (`Authorization: Bearer cc_...`) criada no painel da loja; é a única credencial do worker e não vai para o front.
- Parâmetros `de`/`ate` (ISO). Fila vazia responde **200** com lista vazia, nunca 404.
- O handler que devolve o pacote **marca as notas como exportadas na mesma transação** — senão o worker emite a mesma venda duas vezes.
- Payload já resolvido pela loja: `codigoMunicipio` (IBGE), `tipoDocumento`, `destinoOperacao`, `indicadorPresenca`, `modalidadeFrete`, `pagamento`.

## Helpers do emissor (`nfe/emissao/helpers.py`)

| Função | Regra |
|---|---|
| `destino_operacao(uf_dest, uf_emit)` | `2` interestadual, `1` interna; sem UF assume interna |
| `indicador_presenca(canal)` | `1` para `manual`/`pdv`/`balcao`, `2` (internet) no resto |
| `modalidade_frete(valor)` | `9` (sem frete) quando 0 — Full/marketplace; `0` quando há frete |
| `tipo_documento(doc)` | `('cpf', 11 dígitos)` / `('cnpj', 14)` / `(None, resto)` |
| `resolver_ibge(cep)` | Brasil API; devolve `None` quando não resolve |

**Não dependa de `resolver_ibge` no servidor**: ele pode não ter saída para a Brasil API (medido: `None` num host com o resto da internet liberado). O desenho correto é **a loja resolver o IBGE** e mandar pronto; o helper é só fallback. Falhar aqui é melhor que emitir com município errado.

## Worker (`mcp-server/scripts/worker_carcrew.py`)

Dois modos, e a diferença é a única coisa que importa operacionalmente:

```bash
python worker_carcrew.py                # F1: assina e salva XML (não transmite)
python worker_carcrew.py --transmitir   # F2: transmite para a SEFAZ
```

- Env: `CARCREW_SITE`, `CARCREW_CHAVE`, `CARCREW_PFX`, `CARCREW_PFX_SENHA`, `CARCREW_UF`, `CARCREW_RESP_CNPJ` (+ contato/e-mail/fone) para o `infRespTec`.
- Numeração em `numeracao.json` (série + próximo). **Rejeitada não consome número**; em produção o modelo 55 precisa de série própria.
- `cStat 103` (lote recebido) exige `consultar_recibo()` antes de concluir; só `100` devolve `autorizada` à loja.
- Erro numa nota **não derruba o lote**: captura por nota, devolve `rejeitada` com o motivo e segue.

## Pitfalls que custaram tempo

- **Clone velho do repositório produz diagnóstico errado.** `/opt/nfe-brasil` é o deploy (código bom, com o módulo `emissao/`); `/root/nfe-brasil` é um clone que pode estar commits atrás. Antes de responder "o emissor não faz X", `git fetch` e compare com `origin/main`, e olhe o deploy — o sintoma de clone velho é afirmar que falta capacidade que já está em produção.
- **`git reset --hard origin/main` num clone com trabalho não commitado apaga esse trabalho**, e arquivo nunca commitado não volta pelo reflog. `git status` antes; se houver alteração local, `git stash` ou commit. Recuperação possível: copiar do deploy (`/opt/<projeto>`) quando ele tem a mesma versão — e dizer ao dono o que foi perdido.
- **Descrição do item 1 em homologação** é padronizada ("NOTA FISCAL EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL"): sem isso, rejeição 373.
- **Nota de marketplace não tem frete do emitente** (Full): `modFrete=9` e `tPag=99` (outros) evitam rejeição de forma de pagamento que a loja não recebeu.
