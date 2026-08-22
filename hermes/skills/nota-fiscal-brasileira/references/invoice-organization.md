# Invoice Organizer — Organização de Notas Fiscais

Baseado no padrão do awesome-claude-skills (Invoice Organizer). Esta referência
complementa a `nota-fiscal-brasileira` skill com padrões de organização de arquivos.

## Quando Usar

- Pasta cheia de XMLs de NF-e sem organização
- Receber notas por email e precisar arquivar
- Preparar documentação para contabilidade
- Organizar por mês/ano para declaração de impostos

## Padrão de Nomenclatura

Formato recomendado para renomear XMLs e PDFs:

```
YYYY-MM-DD Fornecedor - NF-e - NFE_NUMERO - VALOR.xml
YYYY-MM-DD Fornecedor - NF-e - DescricaoProduto.xml
```

Exemplos:
```
2025-06-15 Empresa XYZ - NF-e - 123456 - 1500.00.xml
2025-06-15 Empresa XYZ - NF-e - MaterialEscritorio.xml
```

## Estrutura de Pastas Recomendada

```
notas-fiscais/
├── 2025/
│   ├── 01-Janeiro/
│   │   ├── CNPJ_12345678000199/
│   │   │   ├── Empresa XYZ - NF-e - 123.xml
│   │   │   └── Empresa XYZ - NF-e - 124.xml
│   │   └── CNPJ_98765432000199/
│   │       └── Fornecedor ABC - NF-e - 567.xml
│   ├── 02-Fevereiro/
│   └── ...
├── 2026/
│   ├── 01-Janeiro/
│   └── ...
└── nao_autorizadas/
    └── (XMLs sem protocolo de autorização)
```

## Script de Organização Automática

```python
import os
import shutil
from lxml import etree
from datetime import datetime
import re

def organizar_nfes(pasta_origem: str, pasta_destino: str):
    """
    Organiza XMLs de NF-e em pastas por ano/mes/emitente.
    Mantem os originais, cria copias organizadas.
    """
    ns = {"ns": "http://www.portalfiscal.inf.br/nfe"}

    for fname in os.listdir(pasta_origem):
        if not fname.endswith(".xml"):
            continue

        path = os.path.join(pasta_origem, fname)
        try:
            tree = etree.parse(path)
            root = tree.getroot()
            infNFe = root.find(".//ns:infNFe", ns)
            if infNFe is None:
                continue

            # Extrai data
            dh_emi = infNFe.findtext("ns:ide/ns:dhEmi", "", ns)
            dt = datetime.fromisoformat(dh_emi) if dh_emi else datetime.now()

            # Extrai emitente
            cnpj = infNFe.findtext("ns:emit/ns:CNPJ", "sem_cnpj", ns)
            nome = infNFe.findtext("ns:emit/ns:xNome", "Desconhecido", ns)
            # Limpa nome para nome de pasta
            nome_pasta = re.sub(r'[<>:"/\\|?*]', '', nome)[:40]

            # Verifica se tem protocolo
            nProt = root.findtext("ns:protNFe/ns:nProt", "")
            pasta_status = "autorizadas" if nProt else "nao_autorizadas"

            # Monta destino: ano/mes/emitente/
            destino = os.path.join(
                pasta_destino,
                pasta_status,
                str(dt.year),
                f"{dt.month:02d}",
                f"{cnpj[:8]}_{nome_pasta}"
            )
            os.makedirs(destino, exist_ok=True)

            # Copia com nome padrao
            novo_nome = f"{dt.strftime('%Y-%m-%d')} {nome_pasta} - NF-e.xml"
            shutil.copy2(path, os.path.join(destino, novo_nome))
            print(f"OK: {fname} -> {destino}/")

        except Exception as e:
            print(f"Erro em {fname}: {e}")
```

## Extração de Dados para Planilha

Para gerar uma planilha com todas as NF-e extraídas:

```python
import csv, os
from lxml import etree

def nfes_para_csv(pasta: str, saida: str = "nfes.csv"):
    """Extrai dados de todos XMLs de uma pasta para CSV."""
    ns = {"ns": "http://www.portalfiscal.inf.br/nfe"}
    dados = []

    for root, dirs, files in os.walk(pasta):
        for f in files:
            if not f.endswith(".xml"):
                continue
            try:
                tree = etree.parse(os.path.join(root, f))
                r = tree.getroot()
                i = r.find(".//ns:infNFe", ns)
                if i is None:
                    continue
                dados.append({
                    "chave": i.get("Id", "").replace("NFe", ""),
                    "emissao": i.findtext("ns:ide/ns:dhEmi", ""),
                    "emitente": i.findtext("ns:emit/ns:xNome", ""),
                    "cnpj_emit": i.findtext("ns:emit/ns:CNPJ", ""),
                    "destinatario": i.findtext("ns:dest/ns:xNome", ""),
                    "valor": i.findtext(".//ns:vNF", ""),
                    "protocolo": r.findtext("ns:protNFe/ns:nProt", "SEM PROTOCOLO"),
                    "arquivo": f,
                })
            except:
                pass

    if dados:
        with open(saida, "w", newline="") as csvfile:
            w = csv.DictWriter(csvfile, fieldnames=dados[0].keys())
            w.writeheader()
            w.writerows(dados)
        print(f"{len(dados)} notas exportadas para {saida}")
    else:
        print("Nenhuma nota encontrada.")

    return dados
```

## Integracao com o Assistente NF-e

O cliente pode enviar XMLs pelo WhatsApp e o assistente:
1. Extrai os dados e mostra na conversa
2. Salva o XML na pasta organizada
3. Se tiver protocolo, considera autorizada

Ver `persona-assistente-nfe` para o tom de voz e respostas naturais.
