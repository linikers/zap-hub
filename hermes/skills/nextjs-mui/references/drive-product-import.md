# Google Drive → Produto — Import Workflow

## Visão Geral

Importar produtos com fotos e descrições a partir de pastas públicas do Google Drive. Usado para o catálogo CarCrew quando as fotos e descrições estão organizadas em pastas no Drive dos fornecedores.

## Pré-requisitos

- `gdown` CLI: `pip install gdown`
- Pasta do Drive configurada como **pública** (qualquer um com o link pode ver)
- Cada pasta de produto com arquivos de foto + opcionalmente um `.txt` com descrição

## Workflow

### 1. Listar conteúdo da pasta do Drive

```bash
gdown --folder "https://drive.google.com/drive/folders/PASTA_ID" --json
```

Retorna JSON array com:
```json
[
  { "url": "https://drive.google.com/uc?id=FILE_ID", "path": "Produto X/1.jpg" },
  { "url": "https://drive.google.com/uc?id=FILE_ID2", "path": "Produto X/444.txt" }
]
```

### 2. Identificar arquivos de descrição

As pastas geralmente têm:
- `444.txt` ou `Nome do Produto.txt` — descrição técnica
- `Novo Documento de Texto.txt` — descrição avulsa (Windows)
- `Descrição.txt` — nome explícito
- `G1 a G4.txt`, `polo fox.txt` — nome específico do produto

### 3. Ler descrição

```bash
curl -sL "https://drive.google.com/uc?id=FILE_ID_DO_TXT"
```

O conteúdo normalmente inclui: nome do produto, especificações técnicas, conteúdo da embalagem, garantia.

### 4. Fazer upload das fotos para Cloudinary

Via admin do Cloudinary ou via API, fazer upload de cada foto.
Convenção de path no Cloudinary: `carcrew/produtos/{categoria}/{nome-arquivo}`

### 5. Estruturar o produto em `produtos.json`

```json
{
  "id": 14,
  "nome": "Compressor HKI 444C Premium Cromado 200 PSI 12V",
  "descricao": "Parágrafos extraídos do .txt...",
  "preco": 0,
  "imgUrl": "https://res.cloudinary.com/.../compressors/444-cromado.webp",
  "category": "compressores",
  "parcelamento": 12,
  "veiculos": ["Universal"],
  "ativo": false
}
```

- `preco: 0` = "Sob consulta" (usar `sobConsulta` no frontend)
- `ativo: false` = produto oculto, não aparece no site até ativar

### 6. Convenção de nomes de pasta vs categoria

O Drive pode ter pastas com nomes diferentes dos slugs do sistema:

| Drive Folder | Category Slug | Status |
|---|---|---|
| `compressors/` | `compressores` | Folder name differs |
| `shocks/` | `amortecedores` | Folder name differs |
| `bolsas/` | `bolsas-de-ar` | Folder name differs |
| `bandejas/` | `bandejas` | ✅ Match |
| `componentes/` | `componentes` | ✅ Match |

Mapear manualmente ou criar script de normalização.

### 7. Pastas que não existem (precisa criar)

Para categorias sem pasta em `public/produtos/`, criar diretório e baixar as fotos do Drive:

```bash
mkdir -p public/produtos/calcos-antirruido
```

## Pitfalls

- **Drive URLs expiram?** URLs `https://drive.google.com/uc?id=...` parecem estáveis para pastas públicas.
- **Sem .txt** = sem descrição. Produtos como "Suporte Lixadeira" podem não ter descrição — pedir pro usuário fornecer.
### Múltiplas fotos

O sistema agora suporta galeria de imagens via campo `galeria: string[]`:

```json
{
  "imgUrl": "https://res.cloudinary.com/.../principal.webp",
  "galeria": [
    "https://res.cloudinary.com/.../foto-2.webp",
    "https://res.cloudinary.com/.../foto-3.webp"
  ]
}
```

- `imgUrl`: imagem principal (obrigatório, usada no card)
- `galeria[]`: imagens extras (opcional, exibidas na página de detalhe como miniaturas clicáveis)
- O ProductCard exibe badge `+N fotos` quando o produto tem galeria

**Workflow para adicionar múltiplas fotos:**

1. Identificar na pasta do Drive os arquivos de foto (`.jpg`, `.webp`, `.png`)
2. Fazer upload de cada uma para Cloudinary
3. Adicionar as URLs no array `galeria` em `produtos.json`
4. O frontend já renderiza a galeria com miniaturas automaticamente

**Upload de fotos no Cloudinary:**
```
Padrão de path: carcrew/produtos/{categoria}/{nome-arquivo}
Exemplo: carcrew/produtos/compressors/444-cromado-2.webp
```

### Upload via Node.js (unsigned, server-side)

Sem precisar de API Key/Secret — usa o upload preset configurado no Cloudinary Dashboard:

```python
import urllib.request, json, os

CLOUD_NAME = "drvnlgib2"
UPLOAD_PRESET = "carcrew"  # configurado no Cloudinary Dashboard como unsigned

def upload_to_cloudinary(file_path):
    boundary = "----" + os.urandom(8).hex()
    crlf = "\r\n"

    body = b""
    body += f"--{boundary}{crlf}".encode()
    body += f'Content-Disposition: form-data; name="upload_preset"{crlf}{crlf}'.encode()
    body += f"{UPLOAD_PRESET}{crlf}".encode()
    body += f"--{boundary}{crlf}".encode()
    body += f'Content-Disposition: form-data; name="folder"{crlf}{crlf}'.encode()
    body += f"carcrew/produtos{crlf}".encode()
    body += f"--{boundary}{crlf}".encode()

    filename = os.path.basename(file_path)
    body += f'Content-Disposition: form-data; name="file"; filename="{filename}"{crlf}'.encode()
    body += f"Content-Type: application/octet-stream{crlf}{crlf}".encode()
    with open(file_path, "rb") as f:
        body += f.read()
    body += f"{crlf}--{boundary}--{crlf}".encode()

    req = urllib.request.Request(
        f"https://api.cloudinary.com/v1_1/{CLOUD_NAME}/image/upload",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
        return result.get("secure_url", "")
```

Requisitos: upload preset `carcrew` deve estar configurado no Cloudinary Dashboard como **unsigned** (Settings → Upload → Upload presets → Enable unsigned).

### Máximo de 4 imagens por produto

Por decisão de negócio, limitar a **4 imagens no máximo** por produto (1 `imgUrl` + 3 `galeria`). Ao importar do Drive, selecionar apenas as 4 primeiras fotos, ignorando vídeos .mp4.

### Filtrar apenas imagens do Drive

Ao importar, ignorar arquivos que terminam em `.txt`, `.mp4`, `.csv`:

```python
matched = [
    f for f in drive_files
    if f["path"].startswith(prod_prefix)
    and not any(f["path"].endswith(ext) for ext in [".txt", ".mp4", ".csv"])
][:4]  # max 4
```

### Script de importação completo

Ver exemplo completo em `/root/carCrewCommerce/scripts/import-drive-products.py` (se existir). O workflow típico:

1. `gdown --folder "DRIVE_URL" --json > /tmp/drive_files.json`
2. Identificar produtos (pastas) e arquivos de imagem dentro
3. Para cada produto: baixar imagens do Drive, upload pro Cloudinary, criar entrada no produtos.json
4. Commitar e push

- **Vídeos .mp4**: não usar como `imgUrl` — são pra demonstração, não thumbnail.
- **Encoding Windows**: `.txt` podem vir com `\r\n` (CRLF). Converter ao processar.
