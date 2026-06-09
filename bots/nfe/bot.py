#!/usr/bin/env python3
"""
WhatsApp NFe Assistant — atendente de nota fiscal para WhatsApp Cloud API.

Tom natural e humano. Atendimento restrito a NF-e e contabilidade.
"""

import os
import sys
import json
import re
import logging
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

log = logging.getLogger("whatsapp-nfe")

# ── Horário de Atendimento ────────────────────────────────────────────────
# Formato: 24h. Ex: (8, 18) = 08:00 às 18:00
BUSINESS_HOUR_START = int(os.environ.get("NFE_BUSINESS_HOUR_START", "8"))
BUSINESS_HOUR_END = int(os.environ.get("NFE_BUSINESS_HOUR_END", "18"))
BUSINESS_DAYS = os.environ.get("NFE_BUSINESS_DAYS", "1,2,3,4,5")  # 1=seg, 7=dom
BUSINESS_TZ = os.environ.get("NFE_BUSINESS_TZ", "America/Sao_Paulo")


def dentro_do_horario() -> bool:
    """Verifica se está dentro do horário de atendimento."""
    import time as time_module
    try:
        import tzlocal
        from datetime import timezone
        # Tenta usar timezone local
        now = datetime.now()
    except ImportError:
        now = datetime.now()

    # Dia da semana: 0=segunda, 6=domingo
    dia_semana = now.weekday() + 1  # 1=segunda
    dias_permitidos = [int(d.strip()) for d in BUSINESS_DAYS.split(",") if d.strip()]
    if dia_semana not in dias_permitidos:
        return False

    hora = now.hour
    return BUSINESS_HOUR_START <= hora < BUSINESS_HOUR_END


def responder_fora_do_horario() -> str:
    """Resposta quando está fora do horário de atendimento."""
    return (
        "No momento estou offline. Meu horário de atendimento é "
        f"das {BUSINESS_HOUR_START:02d}h às {BUSINESS_HOUR_END:02d}h, "
        "em dias úteis. Assim que eu estiver disponível, respondo "
        "sua mensagem. Se for urgente, por favor ligue para o escritório."
    )

# ── Intenções detectáveis ──────────────────────────────────────────────────

PALAVRAS_NFE = [
    "nota fiscal", "nota", "nf-e", "nfe", "nfce", "nfc-e", "ct-e", "cte",
    "danfe", "danfce", "xml", "nf", "notinha", "cupom", "fiscal",
    "sefaz", "nfes", "nfs-e", "nfse",
    "manifestação", "manifestacao", "manifestar",
    "status", "situação", "situacao",
    "conhecimento transporte", "mdf-e", "mdfe",
    "carta de correção", "carta de correcao", "cce",
]

PALAVRAS_ACAO = [
    "emitir", "gerar", "consultar", "quero", "preciso", "preciso de",
    "como faço", "como faz", "cadê", "onde", "status", "validar",
    "segunda via", "2 via", "2ª via", "cancelar", "carta de correção",
    "inutilizar", "manifestar",
]

# Regex para chave de acesso (44 dígitos)
RE_CHAVE_ACESSO = re.compile(r'\b(\d{44})\b')

# Regex para CNPJ
RE_CNPJ = re.compile(r'\b(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})\b')


def detectar_intencao_nfe(texto: str) -> tuple[bool, str, dict]:
    """
    Detecta se a mensagem tem intenção de nota fiscal.
    Retorna (tem_intencao, acao, parametros)
    """
    texto_lower = texto.lower().strip()

    # Extrai chave de acesso de 44 dígitos primeiro (pode vir sem palavras-chave)
    chaves = RE_CHAVE_ACESSO.findall(texto)
    params = {}
    if chaves:
        params["chave"] = chaves[0]

    # Extrai CNPJ
    cnpjs = RE_CNPJ.findall(texto)
    if cnpjs:
        params["cnpj"] = re.sub(r'[./-]', '', cnpjs[0])

    # Se a mensagem é APENAS uma chave de 44 dígitos (ou contém), já é NFe
    if chaves and not any(p in texto_lower for p in PALAVRAS_NFE):
        return True, "chave_detectada", params

    # Palavras de atalho do menu principal / navegação
    PALAVRAS_MENU = [
        "menu", "ajuda", "opções", "opcoes", "o que faz",
        "voltar", "início", "inicio", "atendente", "falar",
        "oi", "olá", "ola", "bom dia", "boa tarde", "boa noite",
        "bom dia!", "boa tarde!", "boa noite!", "saudações", "saudacoes",
    ]

    # Se não menciona nada relacionado a NF, sai
    if not any(p in texto_lower for p in PALAVRAS_NFE + PALAVRAS_MENU):
        return False, "", {}

    if any(p in texto_lower for p in ["atendente", "falar com", "humano", "transferir"]):
        return True, "falar_atendente", params

    if any(p in texto_lower for p in ["status sefaz", "status", "sefaz", "situação", "situacao"]):
        uf_match = re.search(r'\b(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b', texto.upper())
        if uf_match:
            params["uf"] = uf_match.group(1)
            return True, "status_sefaz", params
        if params.get("chave"):
            return True, "consultar_chave", params
        return True, "menu_principal", params

    if any(p in texto_lower for p in ["consultar", "cadê", "onde"]):
        if params.get("chave"):
            return True, "consultar_chave", params
        return True, "menu_principal", params

    if any(p in texto_lower for p in ["emitir", "gerar", "quero nota", "preciso de nota"]):
        return True, "emitir", params

    if "danfe" in texto_lower or "segunda via" in texto_lower or "2 via" in texto_lower or "2ª via" in texto_lower:
        if params.get("chave"):
            return True, "danfe_chave", params
        return True, "danfe", params

    if any(p in texto_lower for p in ["validar", "xml"]):
        return True, "validar_xml", params

    if any(p in texto_lower for p in ["cancelar", "cancelamento"]):
        return True, "cancelar", params

    if any(p in texto_lower for p in ["carta de correção", "carta de correcao", "cc-e", "cce"]):
        return True, "carta_correcao", params

    if any(p in texto_lower for p in ["manifestar", "manifestação", "manifestacao", "ciência", "ciencia", "desconhecimento"]):
        return True, "manifestacao", params

    if any(p in texto_lower for p in ["ajuda", "menu", "opções", "o que faz"]):
        return True, "menu_principal", params

    if params.get("chave"):
        return True, "chave_detectada", params

    return True, "menu_principal", params


def validar_chave_acesso(chave: str) -> tuple[bool, str]:
    """Valida chave de acesso de 44 dígitos com dígito verificador módulo 11."""
    if not chave or len(chave) != 44:
        return False, "Chave deve ter 44 dígitos."

    if not chave.isdigit():
        return False, "Chave deve conter apenas números."

    peso = 2
    soma = 0
    for i in range(43, -1, -1):
        soma += int(chave[i]) * peso
        peso += 1
        if peso > 9:
            peso = 2

    resto = soma % 11
    dv_esperado = 0 if resto in (0, 1) else 11 - resto

    if dv_esperado != int(chave[43]):
        return False, f"Dígito verificador inválido. Esperado: {dv_esperado}, encontrado: {chave[43]}."

    ano = chave[0:2]
    mes = chave[2:4]
    cnpj = chave[6:20]
    modelo = chave[20:22]
    serie = chave[22:25]
    nNF = chave[25:34]

    modelo_nome = {
        "55": "NF-e",
        "65": "NFC-e",
        "57": "CT-e",
        "58": "MDF-e",
    }.get(modelo, f"Modelo {modelo}")

    cnpj_fmt = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"

    info = (
        f"Chave válida. Os dados que extraí dela:\n"
        f"Mês/ano de emissão: {mes}/{ano}\n"
        f"CNPJ do emitente: {cnpj_fmt}\n"
        f"Modelo: {modelo_nome}\n"
        f"Série: {int(serie)} | Número: {int(nNF)}"
    )

    return True, info


def formatar_cnpj(cnpj: str) -> str:
    """Formata CNPJ: XX.XXX.XXX/XXXX-XX"""
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"


def formatar_whatsapp_resposta(texto: str) -> str:
    """
    Formata resposta para WhatsApp (sem markdown).
    """
    texto = re.sub(r'```[\s\S]*?```', '', texto)
    texto = texto.replace('`', '')
    texto = re.sub(r'\*\*(.+?)\*\*', lambda m: m.group(1).upper(), texto)
    texto = texto.replace('*', '')
    return texto.strip()


def extrair_info_xml(xml_path: str) -> Optional[dict]:
    """
    Tenta extrair informações básicas de um XML de NF-e.
    Retorna dict ou None se não for um XML válido.
    """
    try:
        from lxml import etree
    except ImportError:
        log.warning("lxml não instalado. Pulando parsing de XML.")
        return None

    try:
        tree = etree.parse(xml_path)
        root = tree.getroot()
        ns = {"ns": "http://www.portalfiscal.inf.br/nfe"}

        infNFe = root.find(".//ns:infNFe", ns)
        if infNFe is None:
            return None

        chave = infNFe.get("Id", "").replace("NFe", "")
        nProt = root.findtext("ns:protNFe/ns:nProt", "", ns)
        tpAmb = root.findtext("ns:protNFe/ns:tpAmb", "", ns)
        dh_emi = infNFe.findtext("ns:ide/ns:dhEmi", "", ns)
        emit_nome = infNFe.findtext("ns:emit/ns:xNome", "", ns)
        emit_cnpj = infNFe.findtext("ns:emit/ns:CNPJ", "", ns)
        dest_nome = infNFe.findtext("ns:dest/ns:xNome", "", ns)
        dest_cnpj = infNFe.findtext("ns:dest/ns:CNPJ", "", ns)
        dest_cpf = infNFe.findtext("ns:dest/ns:CPF", "", ns)
        vNF = infNFe.findtext(".//ns:vNF", "", ns)

        itens = []
        for det in infNFe.findall("ns:det", ns):
            prod = det.find("ns:prod", ns)
            if prod is not None:
                itens.append({
                    "n_item": det.get("nItem"),
                    "produto": prod.findtext("ns:xProd", "", ns),
                    "qtd": prod.findtext("ns:qCom", "", ns),
                    "valor": prod.findtext("ns:vUnCom", "", ns),
                })

        return {
            "chave": chave,
            "nProt": nProt,
            "tpAmb": tpAmb,
            "dhEmi": dh_emi,
            "emitente": {"nome": emit_nome, "cnpj": emit_cnpj},
            "destinatario": {"nome": dest_nome, "doc": dest_cnpj or dest_cpf},
            "vNF": vNF,
            "itens": itens[:5],
            "total_itens": len(itens),
        }
    except Exception as e:
        log.error("Erro ao extrair XML: %s", e)
        return None


# ── Respostas com tom natural ─────────────────────────────────────────────

def responder_menu_principal(nome_cliente: str = "") -> str:
    """
    Resposta inicial quando o cliente manda mensagem mas sem ação específica.
    """
    if nome_cliente:
        return (
            f"Olá, {nome_cliente}. Por aqui posso ajudar com questões de "
            f"nota fiscal eletrônica e contabilidade. Se tiver uma chave de "
            f"acesso de 44 dígitos pode me mandar que eu consulto, ou se "
            f"preferir me diga o que precisa: emitir, validar XML, DANFE, "
            f"status da SEFAZ, cancelamento, carta de correção ou "
            f"manifestação do destinatário."
        )
    return (
        "Olá. Por aqui posso ajudar com nota fiscal eletrônica e contabilidade. "
        "Pode me mandar uma chave de acesso de 44 dígitos que eu consulto, "
        "ou me diga o que precisa: emitir, validar XML, DANFE, status da "
        "SEFAZ, cancelamento, carta de correção ou manifestação."
    )


def responder_ajuda() -> str:
    """
    Explica de forma natural o que o assistente faz.
    """
    return (
        "O que posso fazer por você:\n\n"
        "Consultar nota fiscal pela chave de acesso de 44 dígitos.\n"
        "Validar arquivo XML de NF-e.\n"
        "Gerar segunda via do DANFE.\n"
        "Verificar.status do serviço SEFAZ por estado.\n"
        "Tirar dúvidas sobre emissão, cancelamento, carta de correção "
        "e manifestação do destinatário.\n\n"
        "É só me mandar a chave, o arquivo XML ou me dizer o que precisa."
    )


def responder_consultar_chave(chave: str) -> str:
    """Resposta para consulta de NF-e pela chave."""
    valido, msg = validar_chave_acesso(chave)
    if not valido:
        return (
            f"Essa chave parece inválida: {msg}\n"
            f"Pode verificar e tentar de novo?"
        )

    return (
        f"{msg}\n\n"
        f"O que deseja fazer com essa nota? Se quiser posso consultar "
        f"o status na SEFAZ, gerar o DANFE ou validar o XML (se tiver "
        f"o arquivo)."
    )


def responder_xml_processado(info: dict) -> str:
    """Resposta após processar XML de NF-e."""
    ambiente = "produção" if info["tpAmb"] == "1" else "homologação"
    status = "autorizada" if info["nProt"] else "sem protocolo (ainda não autorizada)"

    resposta = (
        f"Informações que extraí do XML:\n\n"
        f"Chave: {info['chave']}\n"
        f"Status: {status}\n"
        f"Ambiente: {ambiente}\n"
    )
    if info.get("nProt"):
        resposta += f"Protocolo: {info['nProt']}\n"
    resposta += (
        f"Emissão: {info['dhEmi']}\n\n"
        f"Emitente: {info['emitente']['nome']}\n"
    )
    if info['emitente']['cnpj']:
        resposta += f"CNPJ: {formatar_cnpj(info['emitente']['cnpj'])}\n"
    resposta += (
        f"\nDestinatário: {info['destinatario']['nome']}\n"
        f"Documento: {info['destinatario']['doc'] or '---'}\n\n"
        f"Valor total: R$ {info['vNF']}\n"
    )

    if info["itens"] and info["total_itens"] <= 5:
        resposta += "\nProdutos:\n"
        for item in info["itens"]:
            resposta += f"- {item['produto'][:40]} (qtd: {item['qtd']})\n"

    return formatar_whatsapp_resposta(resposta)


def responder_emitir() -> str:
    """Orientação sobre emissão de NF-e."""
    return (
        "Para emitir uma nota fiscal preciso de algumas informações: "
        "dados do emitente (CNPJ, razão social, IE), dados do destinatário "
        "(CPF ou CNPJ, nome, endereço), descrição dos produtos ou serviços "
        "e os valores com impostos.\n\n"
        "Mas é bom lembrar que a emissão de NF-e envolve responsabilidade "
        "fiscal. Se tiver dúvidas sobre como preencher, posso ajudar. "
        "Se preferir, posso passar para o setor fiscal."
    )


def responder_status_sefaz(uf: str = "") -> str:
    """Resposta para consulta de status SEFAZ."""
    if uf:
        return (
            f"Para consultar o status da SEFAZ {uf.upper()} em tempo real "
            f"é preciso ter o certificado digital A1 configurado no sistema, "
            f"o que é feito pelo setor técnico.\n\n"
            f"Uma alternativa é consultar diretamente pelo site da SEFAZ "
            f"do estado: https://www.sefaz.{uf.lower()}.gov.br\n\n"
            f"Se quiser, posso passar para o setor técnico verificar isso."
        )
    return (
        "Para consultar o status do serviço NF-e da SEFAZ, me informe "
        "qual estado (UF). Por exemplo: status SP, status PR, status MG."
    )


def responder_cancelar() -> str:
    """Orientação sobre cancelamento de NF-e."""
    return (
        "O cancelamento de NF-e pode ser feito em até 24 horas após a "
        "autorização, com uma justificativa do motivo. Para isso é "
        "necessário certificado digital A1.\n\n"
        "Após 24 horas não é mais possível cancelar, apenas fazer uma "
        "carta de correção. Se precisar de ajuda com isso ou quiser "
        "falar com o setor fiscal, é só me avisar."
    )


def responder_manifestacao() -> str:
    """Orientação sobre manifestação do destinatário."""
    return (
        "Sobre manifestação do destinatário, as opções são:\n\n"
        "Ciencia da operação — prazo de até 15 dias.\n"
        "Confirmacao da operação.\n"
        "Desconhecimento da operação.\n"
        "Nao realizacao da operação.\n\n"
        "Importante: a manifestação é irreversível depois de enviada. "
        "Recomendo confirmar com o setor fiscal antes de manifestar. "
        "Se quiser, posso passar para eles."
    )


def responder_falar_atendente() -> str:
    """Transfere para atendente humano."""
    return (
        "Certo, vou registrar sua solicitação e passar para o setor "
        "responsável. Em breve alguém da nossa equipe fiscal entra em "
        "contato. Fique à vontade para mandar mais detalhes enquanto isso."
    )


def responder_danfe(chave: str = "") -> str:
    """Resposta sobre solicitação de DANFE."""
    if chave:
        valido, msg = validar_chave_acesso(chave)
        if valido:
            return (
                f"Recebi a chave para o DANFE. Para gerar o PDF preciso "
                f"do XML autorizado. Se tiver o arquivo XML, pode me "
                f"enviar que eu gero o DANFE. Caso contrário, posso "
                f"passar para o setor fiscal providenciar."
            )
        else:
            return f"Essa chave parece inválida: {msg}"
    return (
        "Para gerar o DANFE preciso da chave de acesso de 44 dígitos "
        "ou do arquivo XML da nota. Pode me mandar um dos dois?"
    )


def responder_validar_xml(attachment_path: str = None) -> str:
    """Resposta sobre validação de XML."""
    if attachment_path:
        info = extrair_info_xml(attachment_path)
        if info:
            return responder_xml_processado(info)
        else:
            return (
                "Não consegui ler esse arquivo como XML de NF-e. Pode "
                "verificar se é um XML de nota fiscal válido e tentar "
                "novamente?"
            )
    return (
        "Pode me enviar o arquivo XML da nota que eu extraio as "
        "informações: emitente, destinatário, itens, valor, e vejo "
        "se tem protocolo de autorização."
    )


def responder_carta_correcao() -> str:
    """Orientação sobre carta de correção."""
    return (
        "A carta de correção (CC-e) serve para corrigir erros em NF-e "
        "já autorizadas. Dá para fazer até 20 correções por nota.\n\n"
        "Mas atenção: não é possível alterar destinatário, valores "
        "principais, CFOP ou NCM pela CC-e.\n\n"
        "Se precisar de ajuda com isso ou quiser falar com o setor "
        "fiscal, é só avisar."
    )


def responder_fora_do_escopo() -> str:
    """Resposta educada para assuntos fora de NF-e."""
    return (
        "Infelizmente não posso ajudar com isso. Meu foco é nota "
        "fiscal eletrônica e contabilidade. Se tiver alguma dúvida "
        "nessa área, pode me chamar."
    )


def responder_opcao_invalida() -> str:
    """Quando não entendeu a mensagem."""
    return (
        "Não entendi muito bem. Para te ajudar melhor, pode me mandar "
        "a chave de acesso da nota, o arquivo XML ou me dizer o que "
        "precisa fazer? Trabalho com consulta, validação, DANFE, "
        "emissão, cancelamento e outros serviços de NF-e."
    )


# ── Handler principal ─────────────────────────────────────────────────────

async def handle_nfe_message(
    texto: str,
    from_number: str,
    nome_cliente: str,
    send_func,
    attachment_path: str = None,
    restricted_mode: bool = True,
) -> str:
    """
    Processa mensagem com intenção de nota fiscal.

    Args:
        texto: Texto da mensagem
        from_number: Número do remetente
        nome_cliente: Nome do cliente (se conhecido)
        send_func: Função assíncrona para enviar mensagem (to, text) -> bool
        attachment_path: Caminho do anexo (XML), se houver
        restricted_mode: Se True, só responde assuntos fiscais

    Returns:
        str: Texto da resposta enviada
    """
    tem_intencao, acao, params = detectar_intencao_nfe(texto)

    if not tem_intencao:
        if restricted_mode:
            resposta = responder_fora_do_escopo()
            if resposta:
                await send_func(from_number, resposta)
            return resposta
        return ""

    # ── Verifica horário de atendimento ────────────────────────────────
    if not dentro_do_horario():
        resposta = responder_fora_do_horario()
        if resposta:
            await send_func(from_number, resposta)
        return resposta

    resposta = ""

    if acao == "menu_principal":
        resposta = responder_menu_principal(nome_cliente)

    elif acao == "ajuda":
        resposta = responder_ajuda()

    elif acao == "consultar_chave":
        resposta = responder_consultar_chave(params["chave"])

    elif acao == "chave_detectada":
        resposta = responder_consultar_chave(params["chave"])

    elif acao == "emitir":
        resposta = responder_emitir()

    elif acao == "danfe" or acao == "danfe_chave":
        resposta = responder_danfe(params.get("chave", ""))

    elif acao == "validar_xml":
        resposta = responder_validar_xml(attachment_path)

    elif acao == "cancelar":
        resposta = responder_cancelar()

    elif acao == "carta_correcao":
        resposta = responder_carta_correcao()

    elif acao == "manifestacao":
        resposta = responder_manifestacao()

    elif acao == "status_sefaz":
        uf = params.get("uf", "")
        resposta = responder_status_sefaz(uf)

    elif acao == "falar_atendente":
        resposta = responder_falar_atendente()

    else:
        resposta = responder_opcao_invalida()

    if resposta:
        await send_func(from_number, resposta)

    return resposta


# ── Função auxiliar para bridge ───────────────────────────────────────────

def is_nfe_topic(texto: str) -> bool:
    """
    Função rápida para a bridge verificar se o assunto é NF-e.
    Útil para decidir se chama o handle_nfe_message ou recusa.
    """
    tem_intencao, _, _ = detectar_intencao_nfe(texto)
    return tem_intencao


# ── CLI para testes ───────────────────────────────────────────────────────

def main_cli():
    """Modo CLI para testar o detector de intenção."""
    print("Assistente NF-e - Modo de Teste\n")

    while True:
        try:
            texto = input("> ")
        except (EOFError, KeyboardInterrupt):
            break

        if texto.lower() in ("sair", "exit", "quit"):
            break

        tem_intencao, acao, params = detectar_intencao_nfe(texto)
        if tem_intencao:
            print(f"  Assunto NF-e detectado. Ação: {acao}")
            if params:
                print(f"  Parâmetros: {json.dumps(params, ensure_ascii=False)}")
        else:
            print("  Fora do escopo (não é NF-e/contabilidade)")
        print()


if __name__ == "__main__":
    main_cli()
