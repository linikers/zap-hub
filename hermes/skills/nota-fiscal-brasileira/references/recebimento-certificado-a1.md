# Receber o certificado A1 (ou qualquer binário) do usuário

O `.pfx` é binário. Qualquer etapa que trate o arquivo como texto o destrói — e o
resultado continua tendo nome de certificado, extensão de certificado e um começo de DER
aparentemente válido. **Não confie em "baixou" nem em "é o mesmo arquivo": confira os bytes.**

## Procedimento

1. **Peça base64, nunca o binário.** É ASCII puro: nenhum transcode no caminho tem como alterar.
   - Windows: `certutil -encode "PAINEIRAS LTDA.pfx" cert.txt` (gera `cert.txt` já em base64)
   - Linux/macOS: `base64 -w0 certificado.pfx > cert.txt`
   - Alternativa aceitável: zipar o `.pfx` e mandar o `.zip` (anexo binário passa por canais que engasgam com `.pfx`).
2. **Peça que rode o comando no arquivo original** — o que a AC/portal entregou. Peça explícita: não no arquivo que ele já renomeou ou re-salvou antes.
3. **Decodifique e confira a integridade antes de qualquer outra coisa** (snippet abaixo).
4. Só então teste a senha.

## Conferência de integridade — rode isto primeiro

```python
b = open("cert.pfx", "rb").read()
print("tamanho:", len(b))
print("bytes NUL (0x00):", b.count(0))          # DER válido tem CENTENAS
print("U+FFFD (EF BF BD):", b.count(b"\xef\xbf\xbd"))
print("valores de byte ausentes:", [hex(v) for v in range(256) if v not in set(b)])
```

**Leitura do resultado:**

| Sinal | Significa |
|---|---|
| `0x00`, `0x07`, `0x0A` ausentes, `0x20` em abundância | canal trocou caracteres de controle por **espaço** (NUL/BEL/LF → 0x20) |
| muitos `EF BF BD` (U+FFFD) | canal decodificou como UTF-8 e substituiu bytes inválidos |
| zero bytes NUL | arquivo **inutilizável**, qualquer que seja a causa |

Ambos os manglings são **irreversíveis**: não dá para saber quais `0x20` eram originalmente `0x00`. Não tente reconstruir.

## Diagnóstico por `openssl` quando o parse falha

```bash
openssl asn1parse -in cert.pfx -inform DER | head    # onde o DER para de fazer sentido
openssl asn1parse -in cert.pfx -inform DER | tail    # normalmente quebra no MAC
```

Erros típicos de texto-mangling: `ASN1_get_object: too long`, `bad object header`,
`Field=mac, Type=PKCS12` e, no caso do NUL→espaço, um `AlgorithmIdentifier` terminando em
`05 20` (NULL com tamanho 0x20) em vez de `05 00`, ou um OID deslocado (`1.2.840.113549.1.32.1`
no lugar de `...1.7.1`).

**Mesmo quebrado, o arquivo ainda entrega metadados úteis**: o `asn1parse` caminha até falhar e
os textos sobrevivem ao mangling de bytes — dá para confirmar titular (CN com CNPJ/CPF), AC
emissora e datas de validade e já checar se o perfil do certificado serve (e-CNPJ esperado com
`clientAuth` + `emailProtection` no ExtendedKeyUsage e `digitalSignature` no KeyUsage).
Útil para separar "certificado errado" de "transporte ruim" sem pedir nada de novo ao usuário.

## Transferência P2P (JustBeamit e afins) por navegador

Links de transferência P2P (JustBeamit, WeTransfer-like) não respondem a um GET simples: o
arquivo sai do navegador do remetente por WebRTC. Para receber, dirija um navegador de verdade
e aponte o download para uma pasta que você controla:

1. `Browser.setDownloadBehavior` com `behavior='allow'` e `downloadPath=<pasta sua>`.
2. Abrir a página do link e esperar carregar.
3. Clicar no elemento de download (procure por `#dl-button`/texto "Download"; prefira clique
   físico por coordenada a `.click()`, que às vezes é ignorado por JS da própria página).
4. Fazer *polling* da pasta até o arquivo aparecer.

**A transferência é byte-exata — o download não introduz texto.** Mas se o arquivo já estava
danificado antes do upload, você recebe a danificação intacta. Portanto: **sempre rode a
conferência de integridade depois de baixar**; "veio por P2P" não é prova de que veio bom.

O remetente precisa manter a página dele aberta durante a transferência — se as zonas de
status da página estiverem vazias, o par não está conectado e o clique não faz nada.

## Enquanto o arquivo não chega

Quando a tarefa está bloqueada no artefato que o usuário tem que entregar, responda com **a
próxima ação única** e a verificação que você vai rodar — não reemita a análise toda. Se a
mesma mensagem chegar repetida, confira primeiro se um anexo novo entrou; depois responda em
duas linhas. Repetir o relatório inteiro a cada tentativa é ruído.
