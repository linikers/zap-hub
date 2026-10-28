# Exportar o catálogo completo do ML (e alimentar uma loja própria)

Receita para puxar **todos** os anúncios do vendedor com o que a API entrega de verdade, e para saber o que ela **não** entrega antes de prometer cadastro fiscal completo.

## 1. Prova de vida do token

`/root/mercadoLivre/dados.json` → `conta.api_token`. Antes de qualquer lote:

```python
GET https://api.mercadolibre.com/users/me      # 200 + id == 50816240
GET https://api.mercadolibre.com/users/50816240/items/search?limit=1
# paging.total = tamanho do catálogo
```

`api_expira_em` no JSON pode estar no futuro e o token ainda estar morto (foi renovado à mão depois). O único teste válido é a chamada.

## 2. IDs e detalhes (duas chamadas, não uma)

```python
# todos os IDs, 100 por página
/users/<seller>/items/search?limit=100&offset=N   -> results[], paging.total

# detalhes em lote de 20 (limite da API) — sempre include_attributes=all
/items?ids=MLB1,MLB2,...&include_attributes=all
# resposta: [{code:200, body:{...}}, ...] — confira o code de cada item
```

**A descrição NÃO vem no multiget.** Uma chamada por item:

```python
/items/{id}/description  -> plain_text (ou text)
```

Com 200 itens, ~0,12 s de sleep entre chamadas segura o rate limit (rodou em ~37 s). Salve o JSON inteiro em disco antes de transformar — o pull é a parte cara.

## 3. O que existe e o que não existe (medido em 212 anúncios)

| Campo | Onde | Cobertura típica |
|---|---|---|
| `SELLER_SKU` | atributo | 212/212 |
| `BRAND` | atributo | 211/212 |
| `PART_NUMBER` | atributo | 207/212 |
| `PACKAGE_WEIGHT/HEIGHT/WIDTH/LENGTH` | atributo | ~87% |
| `GTIN` | atributo | **15/212** (2 por SKU único) |
| `SALE_FORMAT`, `UNITS_PER_PACK` | atributo | 12/212 |
| `EMPTY_GTIN_REASON` | atributo | 106/212 |
| **NCM, CEST, CFOP, CST/ICMS, origem** | — | **não existem na API de anúncio** |

Consequência prática: catálogo completo do ML é ótimo para nome, preço, estoque, fotos, descrição, medidas e identificação (SKU/marca/part number). Ele **não** resolve cadastro fiscal. Não escreva "exportei com dados fiscais" — o que dá para fazer é pré-preencher NCM por família e marcar como **sugestão para revisão**; CEST, CST e origem dependem do regime e ficam em branco de propósito.

## 4. Deduplicar antes de importar

O mesmo produto aparece em vários anúncios: 212 listagens viraram **128 SKUs únicos** (71 SKUs repetidos, 155 anúncios envolvidos). Só 1 grupo diferia por cor — o resto é anúncio duplicado de verdade.

Regra que funcionou:

1. agrupar por `SELLER_SKU`;
2. escolher o representante por `status='active'` primeiro, depois maior `available_quantity`;
3. **somar fotos de todas as listagens** do grupo (a segunda listagem costuma ter ângulos que a primeira não tem), cortando em 10;
4. usar descrição e medidas do representante;
5. sinalizar grupos com preço divergente — 58 dos 71 tinham preços diferentes, e isso é decisão comercial, não bug.

Status → `ativo`: `active` sim; `paused` e `under_review` entram como inativos (não descarte: o dono religa no ML e espera o produto existir na loja).

## 5. Medidas: use o ID do atributo, não o nome em português

O nome exibido varia com o idioma e com o catálogo (`Altura da embalagem` vs `Altura da embalagem do vendor`). Os ids são estáveis:

```python
def attr(item, key):
    for a in item.get('attributes', []):
        if a['id'] == key:
            return a.get('value_name') or (a.get('values') or [{}])[0].get('name')
PACKAGE_HEIGHT / PACKAGE_WIDTH / PACKAGE_LENGTH  # cm
PACKAGE_WEIGHT                                    # g
```

Extraia o número com regex (`"2.2 cm"` → `2.2`); vem string com unidade.

## 6. Entregar para uma loja própria (CarCrew)

O SKU do site **não é** o SKU do ML: o site usa `CC-0001…CC-0048` (backfill interno) e o ML usa `AMO-007`, `BOL-012`. Não existe chave de junção — casar por nome deu **12 acertos confiáveis em 48** (similaridade ≥ 0,72); o resto tem nome comercial diferente e o casamento vira palpite.

Antes de escrever em produção:

1. gerar CSV/JSON com o catálogo montado e as contagens (ativos, sem preço, sem foto, sem medida);
2. mostrar os números e as **duas decisões** ao dono: (a) atualizar só os casados e inserir o resto, ou substituir pelos 128 do ML; (b) revisar o CSV antes ou importar direto;
3. conferir que a coluna nova existe no banco antes de importar imagem/medida (`imagens String[]` no CarCrew exige o `ALTER TABLE` da migration — o build da Vercel não roda `migrate deploy`);
4. importar com `upsert` por SKU, `preco` e `precoBase` iguais ao preço do ML (a política de canal é aplicada depois, no servidor).
5. **Padronizar pelo SKU do ML, mantendo id e nome curado (decisão ratificada).** Renomear o SKU dos produtos existentes (`UPDATE produtos SET sku='<sku do ML>' … WHERE sku='CC-xxxx'`) preserva link, histórico e o nome comercial que o site já tinha; inserir o item do ML ao lado criaria produto duplicado. Item que o site vende e o ML não anuncia mantém o SKU interno — e fica sem preço até o dono decidir.
6. Sequência do banco e fotos externas: os dois tombos estão em `carcrew-dev`, seção de catálogo de marketplace — `produtos_id_seq` dessincronizada derruba o primeiro INSERT em massa, e foto de `http2.mlstatic.com` exige `remotePatterns` no `next.config.ts` (senão `_next/image` devolve 400 e o card fica branco).

Nunca grave o catálogo inteiro na loja sem esse retorno: 128 linhas em produção é mudança de negócio, não tarefa técnica.

## 7. Categorias

`GET /categories/{id}` devolve `name` e `path_from_root` — use o path para mapear para a categoria da loja (ex.: `… > Suspensão e Direção > Suspensão a Ar`). O SKU costuma ser mais confiável que a categoria do ML para decidir a prateleira: `BOL-*` é bolsa de ar mesmo quando o anúncio está em "Peças Nivelamento Automático".
