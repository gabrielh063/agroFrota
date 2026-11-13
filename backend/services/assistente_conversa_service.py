"""Fluxos conversacionais determinísticos para operações AgroFrota.

O modelo de linguagem não escolhe IDs nem autoriza gravações. Este módulo
mantém o rascunho estruturado e consulta apenas registros do tenant atual.
"""
import re
import unicodedata
from datetime import datetime, timedelta

from sqlalchemy import or_, select

from models.tenant.agendamento import Agendamento
from models.tenant.equipamento import Equipamento
from models.tenant.indisponibilidade import Indisponibilidade
from models.tenant.maquina import Maquina
from models.tenant.ordem_servico import OrdemServico
from services.admin_policy import AdministracaoNegada
from services.escopo import escopo_atual
from services.assistente_ia_service import horario_local


def normalizar(value):
    value = unicodedata.normalize("NFKD", (value or "").lower())
    return "".join(c for c in value if not unicodedata.combining(c))


def eh_cancelamento(texto):
    t = normalizar(texto)
    return any(x in t for x in ("cancela essa proposta", "cancele a proposta", "deixa pra la", "desisti", "cancela"))


def _parse_data(texto, estado):
    t = normalizar(texto)
    agora = horario_local()
    dia = estado.get("data")
    match = re.search(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\b", t)
    if match:
        ano = int(match[3] or agora.year)
        try:
            result = datetime(ano, int(match[2]), int(match[1])).date()
            if not match[3] and result < agora.date():
                result = result.replace(year=ano + 1)
            return result.isoformat()
        except ValueError:
            return dia
    if re.search(r"\bdia\s+\d{1,2}\s+(?:desse|deste)\s+mes", t):
        day = int(re.search(r"\bdia\s+(\d{1,2})", t)[1])
        try:
            result = agora.date().replace(day=day)
            if result < agora.date():
                next_month = (agora.date().replace(day=1) + timedelta(days=32)).replace(day=1)
                result = next_month.replace(day=day)
            return result.isoformat()
        except ValueError:
            return dia
    relative = (("depois de amanha", 2), ("amanha", 1), ("hoje", 0))
    for word, offset in relative:
        if re.search(rf"\b{word}\b", t):
            return (agora.date() + timedelta(days=offset)).isoformat()
    days = {"segunda": 0, "terca": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sabado": 5, "domingo": 6}
    for word, weekday in days.items():
        if re.search(rf"\b{word}(?:-feira)?\b", t):
            delta = (weekday - agora.weekday()) % 7 or 7
            return (agora.date() + timedelta(days=delta)).isoformat()
    return dia


def _parse_horario(texto, estado):
    t = normalizar(texto)
    match = re.search(r"\b(?:as\s+)?(\d{1,2})(?::(\d{2})|h(\d{2})?)\b", t)
    if not match:
        return estado.get("hora")
    hour, minute = int(match[1]), int(match[2] or match[3] or 0)
    if hour > 23 or minute > 59:
        return estado.get("hora")
    return f"{hour:02d}:{minute:02d}"


def _parse_duracao(texto, estado):
    t = normalizar(texto)
    nums = {"uma": 1, "um": 1, "duas": 2, "dois": 2, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8}
    match = re.search(r"\bpor\s+(uma|um|duas|dois|tres|quatro|cinco|seis|sete|oito|\d{1,2})\s*(?:horas?|h)\b", t)
    if not match:
        return estado.get("duracao_horas")
    value = int(match[1]) if match[1].isdigit() else nums[match[1]]
    return value if 1 <= value <= 8 else estado.get("duracao_horas")


def _extrair_titulo(texto, estado):
    t = normalizar(texto)
    if "titulo" in estado:
        return estado["titulo"]
    patterns = (
        (r"colheita\s+(?:de|do|da)\s+sil(?:o|agem)", "Colheita de silagem", "SERVICO"),
        (r"colheita\s+de\s+([\w -]{2,50})", None, "SERVICO"),
        (r"revis(?:ao|ar)(?:\s+preventiva)?(?:\s+do\s+trator)?", "Revisão preventiva", "MANUTENCAO"),
        (r"troca\s+do\s+filtro\s+hidraulico", "Troca do filtro hidráulico", "MANUTENCAO"),
        (r"troc(?:ar|a)\s+(?:o\s+)?filtro\s+hidraulico", "Troca do filtro hidráulico", "MANUTENCAO"),
        (r"verificar\s+(?:os\s+)?freios", "Verificação dos freios", "MANUTENCAO"),
        (r"vazamento\s+hidraulico", "Correção de vazamento hidráulico", "MANUTENCAO"),
        (r"inspec(?:ao|ionar)\s+(?:o\s+)?sistema\s+hidraulico", "Inspeção do sistema hidráulico", "MANUTENCAO"),
    )
    for pattern, title, kind in patterns:
        m = re.search(pattern, t)
        if m:
            return title or ("Colheita de " + m[1].strip().title(), kind)

    return estado.get("titulo")


def _servico(texto):
    t = normalizar(texto)
    if any(x in t for x in ("colheita", "plantio", "pulverizacao", "transporte", "servico")):
        return "SERVICO"
    if any(x in t for x in ("revis", "manutenc", "troca", "filtro", "freio", "vazamento", "inspec")):
        return "MANUTENCAO"
    return "MANUTENCAO"


def _categoria(texto, estado):
    t = normalizar(texto)
    if re.search(r"\btrator(?:es)?\b", t):
        return "TRATOR"
    if re.search(r"\bcolheitadeira(?:s)?\b", t):
        return "COLHEITADEIRA"
    if re.search(r"\bpulverizador(?:es)?\b", t):
        return "PULVERIZADOR"
    if re.search(r"\bcaminh(?:ao|oes)\b", t):
        return "CAMINHAO"
    if re.search(r"\b(?:equipamento|implemento)(?:s)?\b", t):
        return "EQUIPAMENTO"
    return estado.get("categoria")


def iniciar_ou_continuar(texto, estado):
    """Atualiza rascunho sem executar escrita. Retorna estado/ação."""
    t = normalizar(texto)
    if eh_cancelamento(texto):
        return {}, {"tipo": "cancelada", "resposta": "Cancelei a proposta. Nenhuma alteração foi gravada."}
    if not estado.get("operacao"):
        if re.search(r"\b(?:os|ordem de servico)\s*(?:#|n(?:umero)?\s*)?\d+", t):
            return {}, {"tipo": "legado"}
        available_question = any(x in t for x in ("disponivel", "disponiveis", "livre", "livres"))
        explicit_operation = re.search(r"\b(crie|criar|abre|abrir|registre|registrar|preciso|quero|agenda|agende|agendar|marque|marcar|programe|programar)\b", t)
        resource_named = any(x in t for x in ("trator", "colheitadeira", "pulverizador", "caminhao", "equipamento", "implemento"))
        if available_question and resource_named and not explicit_operation:
            estado = {"operacao": "CONSULTAR_DISPONIBILIDADE", "estado_proposta": "CONSULTANDO"}
        else:
            verbo = re.search(r"\b(crie|criar|abre|abrir|registre|registrar|preciso|quero|agenda|agende|agendar|marque|marcar|programe|programar)\b", t)
            assunto = any(x in t for x in ("colheita", "revis", "manutenc", "troca", "filtro", "freio", "vazamento", "inspec", "os ", "ordem de servico"))
            if not verbo or not assunto:
                return {}, {"tipo": "consulta"}
            agendar = any(x in t for x in ("agenda", "agende", "agendar", "marque", "marcar", "programe", "programar"))
            estado = {"operacao": "CRIAR_OS_E_AGENDAR" if agendar else "CRIAR_OS", "estado_proposta": "COLETANDO"}
            estado["tipo"] = _servico(texto)
            estado["mensagem_inicial"] = texto[:800]
    else:
        estado = dict(estado)

    # Pequenas correções e respostas de continuação atualizam só os campos citados.
    title = _extrair_titulo(texto, estado)
    if isinstance(title, tuple):
        estado["titulo"], estado["tipo"] = title
    elif title:
        estado["titulo"] = title
    elif not estado.get("titulo"):
        estado["titulo"] = "Ordem de serviço"

    if "urgente" in t and not re.search(r"\bnao\s+(?:e\s+)?urgente\b", t):
        estado["prioridade"] = "URGENTE"
    elif "prioridade alta" in t:
        estado["prioridade"] = "ALTA"
    elif "prioridade baixa" in t:
        estado["prioridade"] = "BAIXA"
    elif "prioridade media" in t:
        estado["prioridade"] = "MEDIA"
    estado.setdefault("prioridade", "MEDIA")
    estado.setdefault("descricao", texto.strip()[:1800])
    estado["categoria"] = _categoria(texto, estado)
    estado["data"] = _parse_data(texto, estado)
    estado["hora"] = _parse_horario(texto, estado)
    estado["duracao_horas"] = _parse_duracao(texto, estado)
    state_res = re.search(r"\b(?:maquina|equipamento)\s+(?:numero\s+|#)?(\d+)\b", t)
    if state_res:
        estado["recurso_referencia"] = state_res[1]
        estado.pop("recurso_id", None)
    if any(x in t for x in ("outra opcao", "outras opcoes", "qualquer uma", "pode escolher", "escolhe uma", "disponivel")):
        estado.pop("recurso_id", None)

    if estado["operacao"] == "CONSULTAR_DISPONIBILIDADE":
        if not estado.get("categoria"):
            return estado, {"tipo": "pergunta", "resposta": "Que tipo de máquina devo procurar?"}
        if estado.get("data") and not estado.get("hora"):
            return estado, {"tipo": "pergunta", "resposta": "A que horas você pretende usar a máquina?"}
        if estado.get("data") and estado.get("hora") and not estado.get("duracao_horas"):
            return estado, {"tipo": "pergunta", "resposta": "Por quanto tempo você precisa do recurso nesse horário?"}
        estado["titulo"] = "Disponibilidade"  # não será usado para gravar uma OS
        return estado, {"tipo": "selecionar_recurso"}
    if not estado.get("titulo") or estado["titulo"] == "Ordem de serviço":
        return estado, {"tipo": "pergunta", "resposta": "Qual serviço devo registrar na ordem de serviço?"}
    if not estado.get("categoria"):
        return estado, {"tipo": "pergunta", "resposta": "Qual tipo de recurso devo considerar: trator, colheitadeira, outra máquina ou equipamento?"}
    if estado["operacao"] == "CRIAR_OS_E_AGENDAR":
        if not estado.get("data"):
            return estado, {"tipo": "pergunta", "resposta": "Para qual dia devo agendar o serviço?"}
        if not estado.get("hora"):
            return estado, {"tipo": "pergunta", "resposta": "A que horas o serviço deve começar?"}
        if not estado.get("duracao_horas"):
            return estado, {"tipo": "pergunta", "resposta": "Qual duração prevista em horas?"}
    return estado, {"tipo": "selecionar_recurso"}


def _categorias_match(registro, categoria, equipamento=False):
    if equipamento and categoria == "EQUIPAMENTO":
        return True
    value = normalizar(getattr(registro, "categoria", None) or (registro.tipo if equipamento else ""))
    return value == normalizar(categoria) or (categoria == "TRATOR" and value in {"trator", "tratores"})


def localizar_recurso(session, contexto, estado, inicio=None, fim=None):
    categoria = estado["categoria"]
    if categoria in {"TRATOR", "COLHEITADEIRA", "PULVERIZADOR", "CAMINHAO"}:
        escopo_atual(session, contexto, "MAQUINA_VISUALIZAR")
        records = [("maquina", x) for x in session.scalars(select(Maquina).where(Maquina.ativo.is_(True)).order_by(Maquina.id)).all()
                   if _categorias_match(x, categoria)]
    else:
        escopo_atual(session, contexto, "EQUIPAMENTO_VISUALIZAR")
        records = [("equipamento", x) for x in session.scalars(select(Equipamento).where(Equipamento.ativo.is_(True)).order_by(Equipamento.id)).all()
                   if _categorias_match(x, categoria, equipamento=True)]

    reference = estado.get("recurso_referencia")
    if reference:
        records = [(kind, obj) for kind, obj in records
                   if str(obj.id) == reference or obj.identificacao.lower() == reference.lower()]
    available = []
    for kind, obj in records:
        status = normalizar(obj.status)
        if status not in {"operando", "disponivel"}:
            continue
        if inicio is not None and fim is not None:
            resource_filter = (OrdemServico.maquina_id == obj.id if kind == "maquina"
                               else OrdemServico.equipamento_id == obj.id)
            conflict = session.scalar(select(Agendamento.id).join(
                OrdemServico, Agendamento.ordem_servico_id == OrdemServico.id
            ).where(Agendamento.status != "CANCELADO", Agendamento.inicio < fim,
                    Agendamento.fim > inicio, resource_filter).limit(1))
            if conflict:
                continue
            ind_filter = (Indisponibilidade.maquina_id == obj.id if kind == "maquina"
                          else Indisponibilidade.equipamento_id == obj.id)
            unavailable = session.scalar(select(Indisponibilidade.id).where(
                ind_filter, Indisponibilidade.status == "ATIVA",
                Indisponibilidade.inicio < fim,
                or_(Indisponibilidade.fim.is_(None), Indisponibilidade.fim > inicio),
            ).limit(1))
            if unavailable:
                continue
        available.append({"tipo": kind, "id": obj.id, "identificacao": obj.identificacao,
                          "modelo": obj.modelo if kind == "maquina" else obj.nome,
                          "fabricante": getattr(obj, "fabricante", None), "status": obj.status})

    if reference and len(available) == 1:
        estado["recurso_id"] = available[0]["id"]
        estado["recurso_tipo"] = available[0]["tipo"]
        return available, None
    selected = estado.get("recurso_id")
    if selected and any(x["id"] == selected for x in available):
        return available, next(x for x in available if x["id"] == selected)
    return available, None


def resumo_proposta(estado, recurso):
    start = None
    end = None
    if estado.get("data") and estado.get("hora"):
        start = datetime.fromisoformat(estado["data"] + "T" + estado["hora"])
        end = start + timedelta(hours=estado["duracao_horas"])
    return {
        "operacao": estado["operacao"], "tipo": estado["tipo"],
        "titulo": estado["titulo"], "descricao": estado.get("descricao") or "Registrado a partir da solicitação do usuário; detalhes sujeitos à inspeção.",
        "prioridade": estado.get("prioridade", "MEDIA"),
        "recurso_tipo": recurso["tipo"], "recurso_id": recurso["id"],
        "recurso_identificacao": recurso["identificacao"],
        "inicio": start.isoformat(timespec="minutes") if start else None,
        "fim": end.isoformat(timespec="minutes") if end else None,
        "responsavel_id": None, "operador_id": None,
    }
