---
name: nota-fiscal-brasileira
description: "Use quando o usuário precisar processar, validar, consultar ou gerar notas fiscais brasileiras (NF-e, NFS-e, NFC-e, CT-e, MDF-e). Inclui parsing de XML, validação de assinatura digital, consulta SEFAZ, DANFE, manifestação do destinatário e backup."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [nfe, nfse, nfc-e, ct-e, sefaz, notas-fiscais, xml, danfe, brasil]
    related_skills: [ocr-and-documents, nano-pdf, whatsapp-cloud-api-bridge]
---

# Nota Fiscal Brasileira — NF-e, NFS-e, NFC-e, CT-e, MDF-e

## Visão Geral

O ecossistema de notas fiscais eletrônicas brasileiras inclui diversos modelos de documento fiscal transmitidos via XML para as SEFAZ estaduais e municipais. Esta skill cobre as operações mais comuns: parsing, validação, consulta, geração de DANFE, manifestação do destinatário e backup organizado de XMLs.

**Modelos de documento:**

| Sigla | Modelo | Descrição | Órgão |
|-------|--------|-----------|-------|
| NF-e | 55 | Nota Fiscal Eletrônica (mercadorias) | SEFAZ Estadual |
| NFC-e | 65 | Nota Fiscal ao Consumidor Eletrônica | SEFAZ Estadual |
| CT-e | 57 | Conhecimento de Transporte Eletrônico | SEFAZ Estadual |
| MDF-e | 58 | Manifesto Eletrônico de Documentos Fiscais | SEFAZ Estadual |
| NFS-e | — | Nota Fiscal de Serviços Eletrônica | Prefeitura Municipal |
| NF3-e | — | Nota Fiscal de Energia Elétrica Eletrônica | SEFAZ |
| NFCom | — | Nota Fiscal de Comunicação Eletrônica | SEFAZ |

## Quando Usar

- Usuário pede para ler/extrair dados de um XML de NF-e
- Usuário precisa validar uma nota fiscal (assinatura, schema, autorização)
- Usuário quer gerar DANFE em PDF a partir de um XML
- Usuário precisa consultar status de uma nota na SEFAZ
- Usuário quer fazer manifestação do destinatário (confirmação, ciência, desconhecimento)
- Usuário precisa organizar/download de XMLs de notas fiscais
- Usuário menciona contingência, carta de correção, ou inutilização
- Usuário pergunta **quais dados são necessários para emitir uma NF-e**
- Usuário está montando um sistema de emissão e quer saber o que o contador vs cliente precisa fornecer

**Não usar para:** Criação de notas fiscais do zero sem supervisão contábil (a geração de NF-e envolve implicações fiscais reais — sempre validar com contador).

## Dados Necessários para Emissão de NF-e

Emitir uma NF-e exige dados de **três fontes distintas**. Abaixo a divisão clara do que cada um fornece.

### 🔵 Grupo 1 — Dados do Emitente (fornecido pelo CONTADOR / cadastro da empresa)

São dados fixos da empresa, cadastrados **uma vez**:

| Dado | Obrigatório? | Descrição |
|------|:---:|-----------|
| **CNPJ** | ✅ | 14 dígitos do emitente |
| **Razão Social** | ✅ | Nome jurídico completo |
| **Nome Fantasia** | ❌ | Opcional mas recomendado |
| **Inscrição Estadual (IE)** | ✅ | Cadastro na SEFAZ. "isento" se não tiver |
| **Inscrição Municipal (IM)** | * | Para NFS-e / regime misto |
| **CRT** (Cód. Regime Tributário) | ✅ | 1=Simples Nacional, 2=Simples c/ excesso, 3=Regime Normal |
| **CNAE** principal | ✅ | 7 dígitos (classificação da atividade) |
| **Endereço completo** | ✅ | CEP, logradouro, nº, bairro, município (IBGE), UF |
| **Telefone** | ❌ | Contato comercial |
| **Certificado Digital A1** (.pfx/.p12 + senha) | ✅ | Assinatura do XML |
| **Parâmetros tributários por produto** | ✅ | CST/CSOSN, CST PIS, CST COFINS, alíquotas ICMS/IPI/PIS/COFINS |

### 🟢 Grupo 2 — Dados do Destinatário (fornecido pelo CLIENTE / comprador)

Variam **a cada nota**:

| Dado | Obrigatório? | Obs |
|------|:---:|------|
| **CNPJ ou CPF** | ✅ | 14 dígitos (PJ) ou 11 (PF) |
| **Nome / Razão Social** | ✅ | |
| **Inscrição Estadual** | ❌ | Obrigatória se destinatário for contribuinte |
| **Endereço completo** | ✅ | Logradouro, nº, bairro, município, UF, CEP |
| **Telefone** | ❌ | Opcional |

### 🟡 Grupo 3 — Dados da Operação (fornecido pelo VENDEDOR / empresário)

Variam **a cada nota**:

| Dado | Obrigatório? | Exemplo |
|------|:---:|---------|
| **Natureza da operação** | ✅ | "Venda de mercadoria", "Remessa", "Prestação de serviço" |
| **CFOP** | ✅ | 5.102 (venda dentro do estado), 6.102 (interestadual) |
| **Data de emissão** | ✅ | Automático (hoje) |
| **Série** | ✅ | Definida na SEFAZ (ex: 1, 2) |
| **Produto/Serviço** | ✅ | Descrição, NCM, unidade, quantidade, valor unitário, valor total |
| **Informações complementares** | ❌ | "Pedido #123", "Contrato XYZ" |

### ⚙️ Infraestrutura Técnica para Emissão

A infra se divide em dois níveis:

**Nível 1 — Consulta/Validação (já funciona):**
```
PostgreSQL + Redis + MCP Server + WhatsApp Bot
→ consultar NF-e, validar chave, status SEFAZ, parse XML, DANFE
```

**Nível 2 — Emissão (precisa construir):**
```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│ Gerar XML    │────▶│ Assinar com  │────▶│ Transmitir   │
│ NFe 4.00     │     │ Cert. A1     │     │ SEFAZ        │
│ (lxml)       │     │ (signxml)    │     │ (zeep/SOAP)  │
└─────────────┘     └──────────────┘     └──────────────┘
                                                │
                                                ▼
                                         ┌──────────────┐
                                         │ Retorno:      │
                                         │ cStat=100     │
                                         │ + nProt       │
                                         └──────────────┘
```

Para emitir, além do stack acima, é necessário:
1. **Certificado Digital A1** (.pfx/.p12) na pasta `certificados/`
2. **Webservice SEFAZ** da UF do emitente (endpoint SOAP)
3. **Lote de emissão** (pode enviar 1 a 50 NF-e por lote)
4. **Tratar retorno**:
   - `cStat=100` → Autorizada (salvar XML com protocolo)
   - `cStat=2xx` → Rejeitada (corrigir e reenviar)
   - `cStat=3xx` → Denegada (problema fiscal do destinatário)

## Stack Técnico Recomendado

### MCP Server pronto (recomendado para automação)

Existe um servidor MCP publicado no PyPI com 43+ tools fiscais — incluindo
todas as operações NF-e (parse XML, validação, DANFE, assinatura, manifestação,
distribuição via mTLS). Zero API key. Veja `references/mcp-fiscal-brasil.md`
para configuração completa, lista de tools e limitações.

```bash
# Rápido
uvx mcp-fiscal-brasil

# No Hermes, adicionar em config.yaml:
# mcp_servers:
#   fiscal-brasil:
#     command: "uvx"
#     args: ["mcp-fiscal-brasil"]
```

### Bibliotecas Python (para código customizado)

```bash
# Essenciais
pip install lxml signxml cryptography requests zeep

# Opcionais (nível mais alto / frameworks)
pip install pynfe erpbrasil.edoc erpbrasil.transmissao erpbrasil.assinatura

# DANFE / PDF
pip install reportlab weasyprint jinja2

# OCR de DANFE escaneado (ver skill ocr-and-documents)
pip install pymupdf marker-pdf
```

### Ferramentas CLI

```bash
# Validação rápida de XML
xmllint --noout --schema padrao_nfe_v4.0.xsd nfe.xml
```

## Estrutura do XML de NF-e

O XML de NF-e segue o layout oficial do CONFAZ (versão 4.0 a partir de 2021):

```
<nfeProc>                          ← Raiz (após autorização)
├── <NFe>                          ← Dados da nota
│   ├── <infNFe>                   ← Informações (ID = chave de acesso)
│   │   ├── <ide>                  ← Identificação (modelo, série, nNF, dhEmi, tpNF, tpEmis, ...)
│   │   ├── <emit>                 ← Emitente (CNPJ, xNome, xFant, enderEmit, IE, ...)
│   │   ├── <dest>                 ← Destinatário (CNPJ/CPF, xNome, enderDest, IE, ...)
│   │   ├── <det>                  ← Itens (produto, NCM, CFOP, CST, qCom, vUnCom, ...)
│   │   ├── <total>                ← Totais (ICMS, IPI, PIS, COFINS, NF)
│   │   ├── <transp>              ← Transporte
│   │   ├── <cobr>                ← Cobrança (boleto, duplicatas)
│   │   ├── <pag>                 ← Pagamentos (cartão, pix, dinheiro)
│   │   ├── <infAdic>            ← Informações complementares
│   │   └── <infRespTec>         ← Responsável técnico (CSRT)
│   └── <Signature>               ← Assinatura digital do emitente
└── <protNFe>                     ← Protocolo de autorização da SEFAZ
    ├── <tpAmb>                   ← 1=Produção, 2=Homologação
    ├── <nProt>                   ← Número do protocolo
    └── <digVal>                  ← Digest value do protocolo
```

### Chave de Acesso (44 dígitos)

```
AAAA  MM  FFFF  PPPP  SSSSSSSSSS  OOOOOOOOOOO  NN  T
  ↑    ↑    ↑     ↑        ↑            ↑       ↑   ↑
Ano   Mês  CNPJ  Modelo   Série        Número   tpEmis Código
      emissão     (55)    (0-999)                 (1=Normal) Verificador
```

## Operações Comuns

### 1. Parse de XML de NF-e

```python
from lxml import etree

def parse_nfe(xml_path: str) -> dict:
    """Extrai os principais campos de um XML de NF-e."""
    tree = etree.parse(xml_path)
    root = tree.getroot()
    ns = {"ns": "http://www.portalfiscal.inf.br/nfe"}

    infNFe = root.find(".//ns:infNFe", ns)

    # Identificação
    ide = infNFe.find("ns:ide", ns)
    chave = infNFe.get("Id")  # "NFe352006...".replace("NFe", "")
    nNF = ide.findtext("ns:nNF", ns)
    serie = ide.findtext("ns:serie", ns)
    dh_emi = ide.findtext("ns:dhEmi", ns)
    tp_emis = ide.findtext("ns:tpEmis", ns)  # 1=Normal, 2=Contingência, ...
    modelo = ide.findtext("ns:mod", ns)

    # Emitente
    emit = infNFe.find("ns:emit", ns)
    cnpj_emit = emit.findtext("ns:emit/ns:CNPJ", ns) or emit.findtext("ns:CNPJ", ns)
    nome_emit = emit.findtext("ns:xNome", ns)

    # Destinatário
    dest = infNFe.find("ns:dest", ns)
    cnpj_dest = dest.findtext("ns:CNPJ", ns) if dest.find("ns:CNPJ", ns) is not None else None
    cpf_dest = dest.findtext("ns:CPF", ns) if dest.find("ns:CPF", ns) is not None else None
    nome_dest = dest.findtext("ns:xNome", ns)

    # Itens
    itens = []
    for det in infNFe.findall("ns:det", ns):
        prod = det.find("ns:prod", ns)
        item = {
            "n_item": det.get("nItem"),
            "cProd": prod.findtext("ns:cProd", ns),
            "xProd": prod.findtext("ns:xProd", ns),
            "NCM": prod.findtext("ns:NCM", ns),
            "CFOP": prod.findtext("ns:CFOP", ns),
            "uCom": prod.findtext("ns:uCom", ns),
            "qCom": prod.findtext("ns:qCom", ns),
            "vUnCom": prod.findtext("ns:vUnCom", ns),
        }
        itens.append(item)

    # Totais
    total = infNFe.find(".//ns:ICMSTot", ns)
    vNF = total.findtext("ns:vNF", ns) if total is not None else None

    return {
        "chave": chave.replace("NFe", ""),
        "nNF": nNF,
        "serie": serie,
        "modelo": modelo,
        "dhEmi": dh_emi,
        "tpEmis": tp_emis,
        "emitente": {"CNPJ": cnpj_emit, "nome": nome_emit},
        "destinatario": {"CNPJ": cnpj_dest or cpf_dest, "nome": nome_dest},
        "itens": itens,
        "vNF": vNF,
    }
```

### 2. Validar Assinatura Digital

```python
from lxml import etree
from signxml import XMLVerifier

def validar_assinatura(xml_path: str) -> bool:
    """Verifica a assinatura digital do emitente no XML."""
    tree = etree.parse(xml_path)
    root = tree.getroot()
    # O certificado do emitente está embutido no XML em <Signature>/<KeyInfo>/<X509Data>
    try:
        # O signxml procura automaticamente a tag <Signature> no XML
        verifier = XMLVerifier()
        verifier.verify(root, require_x509=True)
        return True
    except Exception as e:
        print(f"Falha na verificação da assinatura: {e}")
        return False
```

### 3. Validar Schema XSD

```python
from lxml import etree
import requests

def validar_schema(xml_path: str, schema_url: str = None) -> list:
    """Valida o XML contra o schema oficial da NF-e.
    Schema padrão: http://www.portalfiscal.inf.br/nfe/schema/nfe_v4.0.xsd
    """
    tree = etree.parse(xml_path)

    if schema_url is None:
        # Tenta descobrir a versão pelo XML
        root = tree.getroot()
        ns = root.nsmap.get(None, "")
        if "v4.0" in ns or "4.00" in ns:
            schema_url = "https://www.portalfiscal.inf.br/nfe/schema/nfe_v4.0.xsd"
        else:
            schema_url = "https://www.portalfiscal.inf.br/nfe/schema/nfe_v3.10.xsd"

    # Baixa o schema
    resp = requests.get(schema_url)
    schema_doc = etree.fromstring(resp.content)
    schema = etree.XMLSchema(schema_doc)

    erros = []
    if not schema.validate(tree):
        for err in schema.error_log:
            erros.append(f"Linha {err.line}: {err.message}")

    return erros
```

### 4. Consultar Status na SEFAZ

```python
from zeep import Client
from lxml import etree

def consultar_status_nfe(uf: str, ambiente: str = "2", cert_path: str = None, key_path: str = None) -> dict:
    """Consulta o status do serviço NF-e na SEFAZ de um estado (homologação=2, produção=1).
    Usa zeep + certificado A1.

    Webservices: https://hom1.sefaz.XX.gov.br/NfeStatusServico/NfeStatusServico2.asmx
    (substituir XX pela UF, ex: PR, SP, MG, RJ...)

    Documentação oficial dos endpoints:
    https://www.portalfiscal.inf.br/nfe/wsdl/NfeStatusServico2_v4.00.wsdl
    """
    # Mapa de UFs para SVRS (Serviço Virtual de Roteamento) quando o estado
    # não tem webservice próprio — SVRS roteia para o ambiente certo.
    svrs_urls = {
        "homologacao": "https://hom1.sefazvirtual.rs.gov.br/",
        "producao": "https://sefazvirtual.rs.gov.br/",
    }

    wsdl = f"https://www.portalfiscal.inf.br/nfe/wsdl/NfeStatusServico2_v4.00.wsdl"

    client = Client(wsdl, transport={
        "cert": cert_path,
        "key": key_path,
    } if cert_path else None)

    # Corpo da consulta
    body = f"""<consStatServ xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
        <tpAmb>{ambiente}</tpAmb>
        <cUF>{codigos_uf[uf]}</cUF>
        <xServ>STATUS</xServ>
    </consStatServ>"""

    body_etree = etree.fromstring(body.encode())
    response = client.service.nfeStatusServicoNF2(body_etree)

    return {
        "tpAmb": response.infProt.tpAmb,
        "cUF": response.infProt.cUF,
        "cStat": response.infProt.cStat,    # Código de status (100=normal, 200=Lento, ...)
        "xMotivo": response.infProt.xMotivo,
        "dhRecbto": response.infProt.dhRecbto,
        "tMed": response.infProt.tMed if hasattr(response.infProt, 'tMed') else None,
    }

codigos_uf = {
    "RO": 11, "AC": 12, "AM": 13, "RR": 14, "PA": 15, "AP": 16, "TO": 17,
    "MA": 21, "PI": 22, "CE": 23, "RN": 24, "PB": 25, "PE": 26, "AL": 27,
    "SE": 28, "BA": 29,
    "MG": 31, "ES": 32, "RJ": 33, "SP": 35,
    "PR": 41, "SC": 42, "RS": 43,
    "MS": 50, "MT": 51, "GO": 52, "DF": 53,
}
```

### 5. Manifestação do Destinatário

A manifestação permite ao destinatário declarar ciência, confirmação, desconhecimento ou não-realização da operação.

```python
import requests
from lxml import etree

def manifestar_destinatario(
    chave: str,
    tipo_evento: str,  # "210200"=Confirmação, "210210"=Ciência, "210220"=Desconhecimento, "210240"=Não Realização
    cnpj: str,
    cert_path: str,
    key_path: str,
    ambiente: str = "2",
) -> dict:
    """Envia manifestação do destinatário para a SEFAZ.

    endPoint:
    Homologação: https://hom1.sefazvirtual.rs.gov.br/Evento/Evento?wsdl
    Produção:    https://sefazvirtual.rs.gov.br/Evento/Evento?wsdl
    """

    url = "https://hom1.sefazvirtual.rs.gov.br/Evento/Evento?wsdl" if ambiente == "2" \
          else "https://sefazvirtual.rs.gov.br/Evento/Evento?wsdl"

    # Montagem do XML de evento
    # (omitido por brevidade — usar erpbrasil.edoc que abstrai isso)
    pass
```

> **⚠️ Importante:** A manifestação tem prazos legais. A ciência (210210) deve ser feita em até 15 dias. A confirmação (210200) pode ser feita a qualquer momento. Consulte um contador para prazos atualizados.

### 6. Gerar DANFE (PDF)

```python
from lxml import etree
import os

def gerar_danfe(xml_path: str, output_path: str = None) -> str:
    """Gera DANFE em PDF a partir do XML autorizado.

    Opção 1: Usar erpbrasil.edoc (recomendado)
    Opção 2: Usar weasyprint + template HTML (mais customizável)
    """

    # Opção 1: via erpbrasil
    # from erpbrasil.edoc.pdf import DANFE
    # from erpbrasil.edoc import NFe
    # nfe = NFe()
    # danfe = DANFE()
    # pdf = danfe.generate(nfe.load_xml(xml_path))
    # with open(output_path, "wb") as f:
    #     f.write(pdf)

    # Opção 2: via weasyprint + template
    from jinja2 import Template
    from weasyprint import HTML

    tree = etree.parse(xml_path)
    root = tree.getroot()
    ns = {"ns": "http://www.portalfiscal.inf.br/nfe"}

    infNFe = root.find(".//ns:infNFe", ns)

    dados = {
        "chave": infNFe.get("Id", "").replace("NFe", ""),
        "emitente": infNFe.findtext("ns:emit/ns:xNome", "", ns),
        "destinatario": infNFe.findtext("ns:dest/ns:xNome", "", ns),
        "vNF": infNFe.findtext(".//ns:vNF", "", ns),
        "dhEmi": infNFe.findtext("ns:ide/ns:dhEmi", "", ns),
    }

    html_template = """
    <html><body>
    <h1>DANFE</h1>
    <p><strong>Chave:</strong> {{ chave }}</p>
    <p><strong>Emitente:</strong> {{ emitente }}</p>
    <p><strong>Destinatário:</strong> {{ destinatario }}</p>
    <p><strong>Valor:</strong> R$ {{ vNF }}</p>
    <p><strong>Emissão:</strong> {{ dhEmi }}</p>
    </body></html>
    """

    html = Template(html_template).render(**dados)
    output_path = output_path or xml_path.replace(".xml", "_DANFE.pdf")
    HTML(string=html).write_pdf(output_path)

    return output_path
```

### 7. Extrair XMLs de Email (backup)

```python
import imaplib
import email
from email.header import decode_header
import os

def baixar_xmls_nfe_do_email(
    email_user: str,
    email_pass: str,
    imap_server: str = "imap.gmail.com",
    output_dir: str = "./xmls_nfe",
    dias_para_tras: int = 7,
):
    """Baixa XMLs de NF-e anexados em emails da caixa de entrada.
    Funciona com qualquer servidor IMAP (Gmail, Outlook, etc.)
    """
    os.makedirs(output_dir, exist_ok=True)

    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_user, email_pass)
    mail.select("INBOX")

    status, ids = mail.search(None, f'(SINCE {(datetime.now() - timedelta(dias=dias_para_tras)).strftime("%d-%b-%Y")} SUBJECT "NF-e")')
    # Pode refinar: SUBJECT "DANFE" OR SUBJECT "NF-e"

    contador = 0
    for msg_id in ids[0].split():
        status, data = mail.fetch(msg_id, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])

        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            filename = part.get_filename()
            if filename and filename.lower().endswith(".xml"):
                payload = part.get_payload(decode=True)
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(payload)
                contador += 1

    mail.close()
    mail.logout()
    return contador
```

### 8. Organizar XMLs em Pastas

```python
import os
import shutil
from lxml import etree
from datetime import datetime
import re

def organizar_xmls(pasta_origem: str, pasta_destino: str):
    """Organiza XMLs de NF-e em pastas por mês/ano."""
    ns = {"ns": "http://www.portalfiscal.inf.br/nfe"}

    for fname in os.listdir(pasta_origem):
        if not fname.endswith(".xml"):
            continue

        path = os.path.join(pasta_origem, fname)
        try:
            tree = etree.parse(path)
            root = tree.getroot()
            infNFe = root.find(".//ns:infNFe", ns)
            dh_emi = infNFe.findtext("ns:ide/ns:dhEmi", "", ns)
            # Formato: 2024-03-15T10:30:00-03:00
            dt = datetime.fromisoformat(dh_emi)
            mes_ano = dt.strftime("%Y-%m")

            # CNPJ do emitente como subpasta
            cnpj = infNFe.findtext("ns:emit/ns:CNPJ", "sem_cnpj", ns)
            destino = os.path.join(pasta_destino, mes_ano, cnpj)
            os.makedirs(destino, exist_ok=True)
            shutil.copy2(path, os.path.join(destino, fname))
        except Exception as e:
            print(f"Erro ao processar {fname}: {e}")
```

## Exemplos de Linha de Comando

### Extrair informações rápidas de um XML

```bash
python3 -c "
from lxml import etree
t = etree.parse('nfe.xml')
ns = {'ns': 'http://www.portalfiscal.inf.br/nfe'}
r = t.getroot()
i = r.find('.//ns:infNFe', ns)
print('Chave:', i.get('Id').replace('NFe',''))
print('Emitente:', i.findtext('ns:emit/ns:xNome','', ns))
print('Destinatário:', i.findtext('ns:dest/ns:xNome','', ns))
print('Valor R$:', i.findtext('.//ns:vNF','', ns))
print('Itens:')
for d in i.findall('ns:det', ns):
    p = d.find('ns:prod', ns)
    print(f'  [{d.get(\"nItem\")}] {p.findtext(\"ns:xProd\", \"\", ns)} qtd={p.findtext(\"ns:qCom\", \"\", ns)}')
"
```

### Verificar se XML está autorizado

```bash
# XML autorizado tem <protNFe> com nProt
grep -q '<nProt>' nfe.xml && echo "AUTORIZADO" || echo "SEM PROTOCOLO"
```

### Checar se é homologação ou produção

```bash
grep -oP '<tpAmb>\K[12]' nfe.xml  # 1=Produção, 2=Homologação
```

## Ambientes SEFAZ

A SEFAZ possui múltiplos ambientes de autorização:

| Sigla | Nome | Quando usar |
|-------|------|-------------|
| SVRS | Sefaz Virtual do Rio Grande do Sul | Routeamento padrão para consulta e eventos |
| SVAN | Sefaz Virtual do Ambiente Nacional | AN (Ambiente Nacional) — contingência |
| SVC | Sefaz Virtual de Contingência | RS, SP, AN — quando SVRS cai |
| SEFAZ própria | Alguns estados mantêm próprio (SP, MG, RJ) | Autorização direta |

### Endpoints principais (Homologação)

```
Autorização:     https://hom1.sefazvirtual.rs.gov.br/NfeAutorizacao/NfeAutorizacao.asmx?wsdl
Retorno Aut.:    https://hom1.sefazvirtual.rs.gov.br/NfeRetAutorizacao/NfeRetAutorizacao.asmx?wsdl
Consulta:        https://hom1.sefazvirtual.rs.gov.br/NfeConsulta/NfeConsulta2.asmx?wsdl
Status Serviço:  https://hom1.sefazvirtual.rs.gov.br/NfeStatusServico/NfeStatusServico2.asmx?wsdl
Evento:          https://hom1.sefazvirtual.rs.gov.br/Evento/Evento?wsdl
Inutilização:    https://hom1.sefazvirtual.rs.gov.br/NfeInutilizacao/NfeInutilizacao2.asmx?wsdl
```

Para produção, trocar `hom1.` por vazio e `homologacao`/`hom` por `producao`.

## Certificado Digital (A1 / A3)

A comunicação com a SEFAZ exige certificado digital ICP-Brasil.

| Tipo | Arquivo | Uso |
|------|---------|-----|
| **A1** | `.pfx` ou `.p12` + senha | Arquivo, válido 1 ano |
| **A3** | Token/ cartão | Hardware, mais seguro, conectado via driver |

**Converter A1 (PFX) para PEM:**

```bash
openssl pkcs12 -in certificado.pfx -out cert.pem -clcerts -nokeys
openssl pkcs12 -in certificado.pfx -out key.pem -nocerts -nodes
openssl pkcs12 -in certificado.pfx -out cacerts.pem -cacerts -nokeys
```

**Verificar validade:**

```bash
openssl x509 -in cert.pem -noout -dates
# Alerta se expiry < 30 dias
```

## Códigos de Retorno SEFAZ (cStat)

| Código | Significado | Ação |
|--------|-------------|------|
| 100 | Autorizado | Nota válida |
| 101 | Cancelado | Nota cancelada |
| 102 | Nota Homologada | Ambiente de teste |
| 104 | Denegado | Irregularidade fiscal do destinatário |
| 107 | Cancelado fora de prazo | Precisa de carta de correção |
| 110 | Uso Denegado | Irregularidade fiscal do emitente |
| 135 | Evento homologado | Manifestação / CC-e aceita |
| 150 | Autorizado fora de prazo | Precisa de carta de correção |
| 200 | Rejeição | Motivo no campo xMotivo |
| 301 | Uso Denegado (IE) | IE do destinatário inativa |
| 999 | Serviço em manutenção | Tentar novamente após 1 min |

## Contingência

**tpEmis (tipo de emissão):**

| Código | Modalidade |
|--------|------------|
| 1 | Normal |
| 2 | Contingência FS (Formulário de Segurança) |
| 3 | Contingência SCAN (Sistema de Contingência do Ambiente Nacional) |
| 4 | Contingência DPEC (Declaração Prévia de Emissão em Contingência) |
| 5 | Contingência FS-DA (Formulário de Segurança para Impressão do DANFE) |
| 6 | Contingência SVC-AN (Sefaz Virtual de Contingência - Ambiente Nacional) |
| 7 | Contingência SVC-RS (Sefaz Virtual de Contingência - Rio Grande do Sul) |
| 9 | Contingência EPEC (Evento Prévio de Emissão em Contingência) — OFF desde 2022 |

## Common Pitfalls

1. **Esquecer de tratar namespaces corretamente.** O namespace da NF-e muda com a versão (v3.10 vs v4.00). Sempre use `.//ns:tag` com nsmapeamento explícito. Não confie em `findall("tag")` sem namespace.

2. **Certificado expirado.** Certificados A1 duram 1 ano. O script não valida automaticamente. Verifique a data com `openssl x509 -in cert.pem -noout -dates` antes de qualquer transmissão.

3. **Confundir homologação com produção.** tpAmb=1 (produção) emite nota fiscal REAL. Sempre começar com tpAmb=2 (homologação) e verificar se o DANFE exibe "HOMOLOGAÇÃO SEM VALOR FISCAL".

4. **Timezone nas datas.** A SEFAZ usa UTC-3 (America/Sao_Paulo). O XML pode vir com qualquer offset (+00:00, -03:00, -02:00 com horário de verão). Normalize para Brasília antes de exibir.

5. **Chave de acesso com RFC incorreta.** O dígito verificador (44º dígito) é módulo 11. Implementar validação ou usar `erpbrasil.edoc` que já faz.

6. **Esquecer de registrar CNPJ + IE para consultar na SEFAZ.** Muitos webservices exigem autenticação por certificado com CNPJ autorizado. Mesmo consulta pública pode precisar de certificado.

7. **XML assinado mas com schema inválido.** A assinatura digital pode passar mesmo se campos obrigatórios estiverem faltando. Sempre validar schema E assinatura.

8. **DANFE com leiaute desatualizado.** O DANFE é regulamentado pelo CONFAZ. Leiautes de 2018, 2021 e 2024 existem. Usar bibliotecas mantidas (erpbrasil.edoc, pynfe) em vez de templates próprios.

9. **Manifestação não pode ser desfeita.** Uma vez enviada, a manifestação (ciência, confirmação, desconhecimento) é irreversível. Confirmar com o usuário antes de enviar.

10. **Pular verificação do protocolo.** XML salvo antes da autorização não tem <protNFe>. Processar XML sem autorização como se fosse nota válida leva a erros contábeis. Sempre verificar existência de `<nProt>`.

## Integração WhatsApp

O NFe Assistant usa WhatsApp como canal de atendimento. Existem **três métodos de conexão**:

### Método 3: Evolution API (RECOMENDADO para VPS Docker)
**Evolution API** (evolution-foundation/evolution-api, 8.7k stars) é um servidor REST completo para WhatsApp.
Roda via Docker compose, inclui dashboard web, suporta Baileys e Cloud API.

| Característica | Cloud API | Baileys | Evolution API |
|---------------|-----------|---------|---------------|
| Setup | Meta Dashboard | Node.js manual | Docker compose |
| Dashboard | Meta Dashboard | Nenhum | Web UI inclusa |
| QR Code | N/A | WebSocket | REST + WebSocket |
| Multi-instância | Apps separados | Portas separadas | Built-in |
| Webhooks | Meta webhooks | Custom handler | Configurável |
| Database | Meta servers | Nenhum | PostgreSQL |
| Docker | N/A | Manual | Imagem oficial |

**Quando usar Evolution API:**
- VPS com Docker
- Múltiplos números WhatsApp
- Dashboard de monitoramento
- Sem conta Meta Developer
- Webhook-based message handling

**Docker compose completo (nfe-brasil):**

O monorepo `github.com/linikers/nfe-brasil` já inclui um docker-compose.yml completo
com 5 serviços: PostgreSQL, Redis, Evolution API, MCP Server e WhatsApp Bot.
Portas mapeadas (sem conflito com serviços existentes):
- 5433: PostgreSQL (evita conflito com 5432)
- 6380: Redis (evita conflito com 6379)
- 8085: Evolution API
- 8090: MCP Server (port 8000 interna)
- 3010: WhatsApp Bot

Para subir: `cd /opt/nfe-brasil && docker compose up -d`

**Criar instância WhatsApp no Evolution API:**

1. Dashboard web: `http://SEU_IP:8085/manager` (login com a API key)
2. Via API (curl):
   ```bash
   API_KEY="nfe-brasil-2026"  # ou a key configurada no docker-compose

   # Criar instância
   curl -X POST http://localhost:8085/instance/create/nfe-brasil \
     -H "apikey: $API_KEY" -H "Content-Type: application/json" \
     -d '{"integration": "WHATSAPP-BAILEYS"}'

   # Conectar (retorna QR code base64 PNG)
   curl -H "apikey: $API_KEY" \
     http://localhost:8085/instance/connect/nfe-brasil

   # Verificar status
   curl -H "apikey: $API_KEY" \
     http://localhost:8085/instance/connectionState/nfe-brasil

   # Listar instâncias
   curl -H "apikey: $API_KEY" \
     http://localhost:8085/instance/fetchInstances
   ```
3. Escanear QR code com WhatsApp do celular (WhatsApp → Dispositivos conectados → Conectar dispositivo)
4. Após scan, o webhook já está configurado (WEBHOOK_GLOBAL_URL aponta pro bot na porta 3010)

**Pitfall: instância criada ≠ conectada.** O endpoint `create` apenas registra a instância.
A conexão só acontece depois do QR scan. Verificar com `connectionState` — deve retornar
`open` (conectado) e não `close`.

**Pitfall: QR code expira rápido.** Assim como Baileys, o QR da Evolution API expira em
~20 segundos. Se usando dashboard, escaneie imediatamente. Se via API, reenvie o `connect`
se o scan falhar.

**Docker compose (mínimo):**
```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: evolution_db
      POSTGRES_USER: evolution
      POSTGRES_PASSWORD: sua-senha
    volumes:
      - pg_data:/var/lib/postgresql/data

  evolution-api:
    image: evoapicloud/evolution-api:latest
    ports:
      - "8080:8080"
    environment:
      - DATABASE_PROVIDER=postgresql
      - DATABASE_CONNECTION_URI=postgresql://evolution:sua-senha@postgres:5432/evolution_db
      - WEBHOOK_GLOBAL_ENABLED=true
      - WEBHOOK_GLOBAL_URL=http://bot:3001/webhook/evolution
      - AUTHENTICATION_API_KEY=sua-api-key
    depends_on:
      - postgres
```

**QR Code via REST:**
```bash
# Criar instância
curl -X POST http://localhost:8080/instance/create/nfe-brasil \
  -H "apikey: sua-api-key" -H "Content-Type: application/json" \
  -d '{"integration": "WHATSAPP-BAILEYS"}'

# Obter QR code (retorna base64 PNG)
curl -H "apikey: sua-api-key" \
  http://localhost:8080/instance/connect/nfe-brasil

# Verificar status
curl -H "apikey: sua-api-key" \
  http://localhost:8080/instance/connectionState/nfe-brasil
```

**Webhook payload:**
```json
{
  "event": "messages.upsert",
  "instance": "nfe-brasil",
  "data": {
    "key": { "remoteJid": "5544991528386@s.whatsapp.net", "fromMe": false },
    "message": { "conversation": "nota fiscal" }
  }
}
```

**Enviar PDF via Evolution API:**
```python
import base64, httpx

async def enviar_pdf(numero, caminho_pdf, instance="nfe-brasil"):
    with open(caminho_pdf, "rb") as f:
        pdf_b64 = base64.b64encode(f.read()).decode()
    
    await httpx.AsyncClient().post(
        f"{EVOLUTION_URL}/message/sendFile/{instance}",
        json={
            "number": numero,
            "mimetype": "application/pdf",
            "fileName": "DANFE.pdf",
            "file": f"data:application/pdf;base64,{pdf_b64}",
        },
        headers={"apikey": API_KEY},
    )
```

**Portas típicas (sem conflito):**
- 5433: PostgreSQL (evita conflito com PostgreSQL existente na 5432)
- 6380: Redis
- 8085: Evolution API
- 8090: MCP Server
- 3010: WhatsApp Bot

**Bot webhook handler pattern (Python/FastAPI):**
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/webhook/evolution")
async def webhook(request: Request):
    body = await request.json()

    if body.get("event") not in ("messages.upsert", "messages.set"):
        return JSONResponse({"status": "ok"})

    raw_data = body.get("data", {})
    instance = body.get("instance", "nfe-brasil")

    # v2.3+ sends data as list; older versions send dict
    items = raw_data if isinstance(raw_data, list) else [raw_data]
    for data in items:
        if not isinstance(data, dict):
            continue
        if data.get("key", {}).get("fromMe", False):
            continue
        if data.get("key", {}).get("remoteJid", "").endswith("@g.us"):
            continue

        texto = data.get("message", {}).get("conversation", "")
        if not texto:
            texto = data.get("message", {}).get("extendedTextMessage", {}).get("text", "")
        if not texto:
            continue

        numero = data["key"]["remoteJid"].replace("@s.whatsapp.net", "")

        if detectar_intencao_nfe(texto):
            resposta = await processar_nfe(texto)
            await enviar_whatsapp(numero, resposta, instance)

    return JSONResponse({"status": "ok"})
```

**⚠️ Evolution API v2.3+ breaking change:** `data` field is now a list, not dict.
Also requires Redis config: `CACHE_REDIS_ENABLED=true` + `CACHE_REDIS_URI=redis://host:6379`.

**QR code dinâmico no portfolio (Next.js):**
Usar REST API da Evolution API pra buscar QR a cada 30 segundos.
Não usar imagem fixa — QR expira em ~20 segundos.
Ver `references/evolution-api-setup.md` pra detalhes.

**Repos relevantes:**
- github.com/linikers/nfe-brasil — Monorepo MCP server + Evolution API + bot
- github.com/linikers/zap-hub — Configs Cloud API / Baileys

### Método 1: Cloud API (Meta Business)
Usa a Meta WhatsApp Cloud API via webhook HTTP. Ativação rápida (testado com ML Atendente e número pessoal). Basta token + Phone Number ID + webhook público.

### Método 2: Baileys QR (PLANO B — mais complexo)
Usa bridge Node.js que conecta via QR Code escaneado no celular. Exige: QR scan, sessão persistente, daemon 24/7, reconexão manual se perder sessão. Usado no NF-e quando Cloud API não estava disponível.

### Driver Cloud API (RECOMENDADO — mais simples)
Usa a Meta WhatsApp Cloud API via webhook HTTP. Ativação rápida (testado com ML Atendente e número pessoal). Basta token + Phone Number ID + webhook público.

### Driver Baileys QR (PLANO B — mais complexo)
Usa bridge Node.js que conecta via QR Code escaneado no celular. Exige: QR scan, sessão persistente, daemon 24/7, reconexão manual se perder sessão. Usado no NF-e quando Cloud API não estava disponível.

### Repositório Centralizado

A configuração completa (scripts, drivers, bots, tunnel, setup) vive no **zap-hub**:
**https://github.com/linikers/zap-hub**

```
zap-hub/
├── drivers/
│   ├── cloud-api/         ← RECOMENDADO
│   │   ├── bridge.py       - Webhook HTTP (porta 3001)
│   │   └── .env.example
│   └── baileys/           ← PLANO B
│       ├── bridge.js        - QR Code Node.js
│       ├── daemon.py        - Poller + processamento
│       └── .env.example
├── bots/
│   ├── nfe/               ← NF-e (Baileys QR, +55 44 991670539)
│   ├── ml-atendente/      ← Cloud API
│   └── pessoal/           ← Cloud API
└── scripts/
    ├── setup.sh           - Scaffold de nova instância
    ├── tunnel.sh           - Webhook público (localtunnel)
    └── tunnel-watchdog.sh  - Com autoreconexão
```

**Arquivos do NFe Assistant no zap-hub:**
- `bots/nfe/bot.py` — Módulo do assistente (originalmente `whatsapp_nfe.py`)
- `drivers/baileys/daemon.py` — Daemon de polling (originalmente `whatsapp-nfe-daemon.py`)
- `bots/nfe/run.sh` — Script de gerenciamento (start/stop/logs/qr)

### Arquitetura

```
WhatsApp Cliente → Meta Graph API → whatsapp-cloud-bridge.py (porta 3001)
                                        │
                                   detectar_intencao_nfe()
                                        │
                           ┌────────────┴────────────┐
                           ▼                         ▼
                    handle_nfe_message()       call_hermes()
                    (fiscal)                   (geral)
                           │
                    ├─ Menu principal
                    ├─ Consulta por chave
                    ├─ Validação de XML anexado
                    ├─ Status SEFAZ por UF
                    ├─ Solicitação de DANFE
                    └─ Falar com atendente
```

### Como Funciona

1. Bridge do WhatsApp Cloud API recebe a mensagem do cliente
2. Antes de chamar o Hermes, executa `detectar_intencao_nfe(texto)`
3. Se for intenção fiscal → `handle_nfe_message()` processa e responde direto pela API
4. Se não for → Mensagem vai pro Hermes normalmente (atendimento geral) ou, **em modo restrito**, recebe uma recusa educada ("Infelizmente não posso ajudar com isso. Meu foco é nota fiscal...")

### Modo Restrito (WHATSAPP_RESTRICTED_MODE)

Quando `WHATSAPP_RESTRICTED_MODE=true`, a bridge **não chama o Hermes** para mensagens não-fiscais. Em vez disso, responde com `responder_fora_do_escopo()` — uma recusa educada e objetiva. Ideal para números de WhatsApp dedicados exclusivamente a NF-e.

Recursos adicionais no modo restrito:
- **Horário comercial**: configurável via `NFE_BUSINESS_HOUR_START`, `NFE_BUSINESS_HOUR_END`, `NFE_BUSINESS_DAYS`. Fora do horário, responde com "No momento estou offline."
- **Tom natural humano**: as respostas em `whatsapp_nfe.py` foram reescritas para soar como uma pessoa real, sem códigos técnicos.
  - **Regra de ouro**: NUNCA mostrar dados brutos de validação, códigos de erro, extração de dados da chave, ou cabeçalhos como "Hermes" ou "Assistente". Toda resposta deve parecer de um atendente humano.
  - **Exemplo de O QUE NÃO FAZER**: "Chave válida. Os dados que extraí dela: Mês/ano: 06/26, CNPJ: XX.XXX.XXX/XXXX-XX, Modelo: NF-e"
  - **Exemplo de COMO FAZER**: "Recebi sua chave! Com ela posso consultar o status da nota na SEFAZ, gerar o DANFE ou validar o XML. O que você prefere?"
  - **Respostas de XML**: não liste campos técnicos (nProt, tpAmb, dhEmi). Responda como: "Recebi o XML! É uma nota emitida por [NOME] no valor de R$ [VALOR], destinada a [NOME]. A nota está autorizada pela SEFAZ."
  - **Validação de chave**: se inválida: "Essa chave não parece válida. Pode verificar e tentar de novo?" — sem mostrar dígito verificador ou regra de validação.
  - **Fora do horário**: "nosso horário de atendimento é das 8 as 18h, aguarde retorno"
  - **Fora de escopo**: "desculpe não consigo atender sua solicitação no momento, atualmente só atendo notas fiscais"
  - **Menus**: usar linguagem natural, não menus numerados (1️⃣ 2️⃣ 3️⃣).
- **Modo 24/7 para testes**: editar `dentro_do_horario()` em `whatsapp_nfe.py` para `return True` durante homologação. Reverter antes de produção.
- **Recusa de assunto fora do escopo**: perguntas sobre vendas, cursos, suporte técnico ou qualquer coisa não-fiscal recebem uma recusa educada.

Para alterar o tom das respostas, edite as funções `responder_*()` em `whatsapp_nfe.py`.

### Arquivos

- `~/.hermes/scripts/whatsapp_nfe.py` — Módulo do assistente NFe (ou no repositório `zap-hub/bots/nfe/bot.py`)
- `~/.hermes/scripts/whatsapp-cloud-bridge.py` — Bridge patched (importa o módulo)
- `~/.hermes/scripts/whatsapp-nfe-daemon.py` — Daemon de polling (ou `zap-hub/drivers/baileys/daemon.py`)

### Quando Usar

- Cliente envia mensagem com "nota fiscal", "nfe", "danfe", chave de 44 dígitos
- Cliente envia XML anexado para validação
- Cliente pergunta sobre status SEFAZ, manifestação, cancelamento
- Cliente digita opções do menu (1-8)

## Verification Checklist

- [ ] XML começa com `<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">` (autorizado) ou `<NFe>` (não autorizado)
- [ ] Chave de acesso de 44 dígitos — dígito verificador confere (módulo 11)
- [ ] `<tpAmb>` indica ambiente correto (1=Produção, 2=Homologação)
- [ ] `<Signature>` presente e assinatura digital válida
- [ ] `<nProt>` presente (nota autorizada) ou lida adequadamente com nota em processamento
- [ ] Se DANFE gerado: exibe "HOMOLOGAÇÃO SEM VALOR FISCAL" quando tpAmb=2
- [ ] Se importando XMLs: origem confiável (não rejeitados pela SEFAZ)
- [ ] Schema XSD validado contra a versão correta
- [ ] Certificado A1 com validade > 30 dias
- [ ] Dados de itens, totais e destinatário extraídos corretamente

## Organização de Arquivos

Para organizar XMLs de NF-e em pastas por data/emitente, incluindo scripts
de renomeação automática e geração de planilhas, veja `references/invoice-organization.md`.

## MCP Server + WhatsApp Bot

Para criar um projeto NF-e completo com MCP server + WhatsApp bot,
veja `references/mcp-server-monorepo.md` — estrutura monorepo, fork
de packages Python, docker-compose e checklist de novos módulos.

## One-Shot Recipes

### Verificar nota rapidamente

```python
from lxml import etree
import sys
t = etree.parse(sys.argv[1]); ns={"ns":"http://www.portalfiscal.inf.br/nfe"}
r = t.getroot(); i = r.find(".//ns:infNFe", ns)
chave = i.get("Id","").replace("NFe","")
nProt = r.findtext("ns:protNFe/ns:nProt", "SEM PROTOCOLO", ns)
tpAmb = i.findtext("ns:ide/ns:tpAmb", "", ns)
print(f"Chave: {chave}")
print(f"nProt: {nProt}")
print(f"Amb: {'HOMOLOGAÇÃO' if tpAmb=='2' else 'PRODUÇÃO'}")
print(f"Emit: {i.findtext('ns:emit/ns:xNome','', ns)}")
print(f"Dest: {i.findtext('ns:dest/ns:xNome','', ns)}")
print(f"Valor: R$ {i.findtext('.//ns:vNF','', ns)}")
```

### Validar lote de XMLs

```bash
for xml in xmls/*.xml; do
    chave=$(grep -oP 'Id="NFe\K\d{44}' "$xml")
    prot=$(grep -oP '<nProt>\K\d+' "$xml")
    echo "$chave $([ -n "$prot" ] && echo AUTORIZADO || echo SEM_PROTOCOLO)"
done | column -t
```
