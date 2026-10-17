# DANFE NFC-e (modelo 65) — cupom de 80 mm

Quando usar: gerar o PDF de uma **NFC-e autorizada** para entregar ao cliente
(WhatsApp, impressão, e-mail).

## O documento é outro

O DANFE de NFC-e **não** é o DANFE A4 da NF-e: é um **cupom de 80 mm** (largura da
bobina térmica), com QR Code, chave de acesso e protocolo. Bibliotecas que geram
DANFE de NF-e **não** geram o de NFC-e:

- `brazilfiscalreport` 1.0.0 (usada pelo `danfe.py` de NF-e) não tem classe para NFC-e —
não force o modelo 65 por esse caminho, ele levanta erro por design.
- Gere o cupom você mesmo com **fpdf2** (PDF) + **segno** (QR). Ambos leves e sem
dependência de browser.

## Estrutura do cupom (na ordem em que sai impresso)

1. Emitente: razão social, `CNPJ: 00.000.000/0000-00  IE: ...`, endereço, `Município/UF CEP: ...`, fone.
2. Título: `DANFE NFC-e - DOCUMENTO AUXILIAR DA NOTA FISCAL DE CONSUMIDOR ELETRONICA`
   + `Nao permite aproveitamento de credito de ICMS`.
3. **Faixa de homologação** `SEM VALOR FISCAL - AMBIENTE DE HOMOLOGACAO` **somente quando `tpAmb=2`**.
4. Identificação: nota nº, série, modelo, emissão, natureza da operação.
5. Itens: `nItem. descrição`, `qCom uCom x vUnCom`, total do item.
6. `TOTAL R$ ...` + pagamentos (`tPag` → DINHEIRO/PIX/CARTÃO) + desconto se houver.
7. Consumidor: nome/doc do `<dest>` ou **`CONSUMIDOR NAO IDENTIFICADO`** quando o XML não tem `<dest>` (caso normal da NFC-e de balcão).
8. Chave de acesso em **blocos de 4 dígitos** (11 blocos), protocolo de autorização e URL de consulta.
9. **QR Code como imagem** — leia o conteúdo do próprio XML (`<infNFeSupl><qrCode>`).

**Nunca remonte a URL do QR Code à mão**: versão e presença de CSC mudam por UF
(a v3 online dispensa CSC — ver a seção de NFC-e no SKILL.md). O XML autorizado é a
fonte da verdade.

## Duas passadas: medir, depois desenhar

fpdf2 não reflui nem recorta depois do `output()`, e a altura do cupom depende do
conteúdo (descrição longa quebra em mais linhas). Faça:

1. Monte uma lista de linhas (texto, tamanho, negrito, alinhamento, separador).
2. Quebre cada texto com `pdf.get_string_width(...)` usando **a mesma fonte e o mesmo
tamanho** que o PDF final vai usar.
3. Some as alturas e só então crie o documento: `FPDF(unit="mm", format=(80, altura))`.

Registrar a fonte só depois de `add_page()` muda a métrica e a quebra não bate com o
render — instale fonte e tamanho antes de medir.

## Acentuação

As fontes core do fpdf2 (Helvetica) são latin-1 e estragam `Ç/Ã/Õ/É`. Registre um TTF:
`/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` e `DejaVuSans-Bold.ttf` com
`add_font("DejaVu", "", caminho)` / `add_font("DejaVu", "B", caminho)`.

## Consequência da regra 373 no cupom que o cliente vê

Em homologação a SEFAZ obriga a descrição do **item 1** a ser o texto padronizado
`NOTA FISCAL EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL`. O cupom sai com
esse texto no lugar do produto — o produto real vai em informações complementares.
Avise o usuário: não é defeito do gerador, é o ambiente de teste.

## Conferir o PDF sem olhar para ele

```bash
pdftotext -layout nota.pdf -   # lê o conteúdo (acompanha o layout)
pdfimages -list nota.pdf       # confirma que o QR entrou como imagem (aparece 1 image)
```

Em teste automatizado (pypdf), verifique: começa com `%PDF`, largura da página
**80 mm = 226,77 pt**, os textos-chave (emitente, `SEM VALOR FISCAL`, total em vírgula,
`CONSUMIDOR NAO IDENTIFICADO`, protocolo) e a existência de um XObject `/Image`
nos recursos da página — é o QR.

## Instalar as dependências num venv feito com uv

Venv criado por `uv venv` **não tem o módulo `pip`** (`No module named pip`) — não é
falta de pacote, é o formato do venv. Instale apontando para o Python do venv:

```bash
uv pip install --python .venv/bin/python fpdf2 segno pypdf
```

Um `pip install` executado de fora do venv instala no Python do sistema/Hermes:
parece que instalou, mas o `import` dentro do script continua falhando — confira com
`.venv/bin/python -c "import segno"`.
