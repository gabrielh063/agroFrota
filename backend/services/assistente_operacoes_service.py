"""Persistência e orquestração segura do chat operacional AgroFrota."""
import hashlib
import json
import secrets
import uuid
from datetime import datetime, timedelta

from sqlalchemy import select

from models.tenant.conversa_assistente import ConversaAssistente
from models.tenant.proposta_agendamento import PropostaAgendamento
from models.tenant.indisponibilidade import Indisponibilidade
from models.tenant.maquina import Maquina
from models.tenant.equipamento import Equipamento
from models.tenant.ordem_servico import OrdemServico
from services.admin_policy import AdministracaoNegada
from services.assistente_conversa_service import (
    iniciar_ou_continuar, localizar_recurso, resumo_proposta, normalizar,
    eh_cancelamento, _parse_data, _parse_horario, _parse_duracao,
)
from services.assistente_ia_guardrails import extrair_pedido_agendamento
from services.assistente_ia_service import (
    chamar_ollama, contexto_operacional, responder_consulta_operacional,
    validar_intervalo, horario_local,
)
from services.auditoria_service import registrar_evento
from services.calendario_service import criar_agendamento
from services.escopo import escopo_atual
from services.ordem_servico_service import criar_ordem_servico_na_sessao
from services.os_policy import consulta_os
from services.os_policy import iniciar_escrita

_TTL_PROPOSTA = 300
_TTL_CONVERSA = 86400
_MAX_MENSAGENS = 30


def nova_conversa(session, *, tenant_id, database_name, usuario_id, session_version):
    now = datetime.utcnow()
    row = ConversaAssistente(
        id=str(uuid.uuid4()), tenant_id=tenant_id, database_name=database_name,
        usuario_id=usuario_id, session_version=session_version,
        estado_json="{}", mensagens_json="[]", expira_em=now + timedelta(seconds=_TTL_CONVERSA),
    )
    session.add(row)
    session.commit()
    return row


def conversa_autorizada(session, conversation_id, *, tenant_id, database_name, usuario_id, session_version, lock=False):
    query = select(ConversaAssistente).where(ConversaAssistente.id == conversation_id)
    if lock:
        query = query.with_for_update()
    row = session.execute(query).scalar_one_or_none()
    now = datetime.utcnow()
    if row is None or row.expira_em <= now:
        return None
    if (row.tenant_id != tenant_id or row.database_name != database_name or
            row.usuario_id != usuario_id or row.session_version != session_version):
        return None
    row.expira_em = now + timedelta(seconds=_TTL_CONVERSA)
    return row


def historico(row):
    try:
        value = json.loads(row.mensagens_json)
        return value if isinstance(value, list) else []
    except (ValueError, TypeError):
        return []


def registrar_resultado_conversa(session, kwargs, conversation_id, proposal_id, message, result):
    context = kwargs["contexto_administrativo"]
    row = conversa_autorizada(session, conversation_id,
        tenant_id=kwargs["tenant_id"], database_name=kwargs["database_name"],
        usuario_id=kwargs["usuario_autenticado_id"], session_version=context.session_version,
        lock=True) if conversation_id else None
    if row is None:
        return False
    state = _state(row)
    if state.get("proposta_id") != proposal_id:
        return False
    _save_state(row, {})
    _append(row, "ia", message, {"resultado": result})
    session.commit()
    return True


def _append(row, role, text, structured=None):
    history = historico(row)
    item = {"origem": role, "texto": str(text)[:2200]}
    if structured:
        item.update(structured)
    history.append(item)
    row.mensagens_json = json.dumps(history[-_MAX_MENSAGENS:], ensure_ascii=False)


def _state(row):
    try:
        value = json.loads(row.estado_json)
        return value if isinstance(value, dict) else {}
    except (ValueError, TypeError):
        return {}


def _save_state(row, value):
    row.estado_json = json.dumps(value, ensure_ascii=False)
    row.atualizada_em = datetime.utcnow()


def _proposal_payload(proposta):
    try:
        return json.loads(proposta.dados_json or "{}")
    except (ValueError, TypeError):
        return {}


def _propose(session, row, context, kwargs, state, data, *, op, order_id=None, start=None, end=None):
    now = datetime.utcnow()
    code = secrets.token_urlsafe(32)
    proposal = PropostaAgendamento(
        token_hash=hashlib.sha256(code.encode()).hexdigest(),
        tenant_id=kwargs["tenant_id"], database_name=context.database_name,
        usuario_id=kwargs["usuario_autenticado_id"], session_version=context.session_version,
        ordem_id=order_id, inicio=start, fim=end, operacao=op,
        dados_json=json.dumps(data, ensure_ascii=False),
        chave_idempotencia=secrets.token_hex(32),
        expira_em=now + timedelta(seconds=_TTL_PROPOSTA), criada_em=now,
    )
    session.add(proposal)
    session.flush()
    state["estado_proposta"] = "AGUARDANDO_CONFIRMACAO"
    state["proposta_id"] = proposal.id
    _save_state(row, state)
    _append(row, "ia", "Revise a proposta. Nada foi gravado ainda.", {"proposta": {
        "id": proposal.id, "operacao": op, "titulo": data.get("titulo"),
        "descricao": data.get("descricao"), "tipo": data.get("tipo"),
        "prioridade": data.get("prioridade"), "recurso_identificacao": data.get("recurso_identificacao"),
        "inicio": start.isoformat(timespec="minutes") if start else None,
        "fim": end.isoformat(timespec="minutes") if end else None,
        "expira_em_segundos": _TTL_PROPOSTA,
    }})
    session.commit()
    return {"proposta": {"codigo": code, "id": proposal.id, "operacao": op,
                         "dados": data, "inicio": start.isoformat(timespec="minutes") if start else data.get("inicio"),
                         "fim": end.isoformat(timespec="minutes") if end else data.get("fim"),
                         "expira_em_segundos": _TTL_PROPOSTA}}


def _frase_opcoes(texto, options):
    t = normalizar(texto)
    if not options:
        return None
    match = __import__("re").search(r"\b(?:maquina|equipamento)\s+(?:numero\s+|#)?(\d+)\b", t)
    if match:
        for item in options:
            if str(item["id"]) == match[1] or normalizar(item["identificacao"]) == match[1]:
                return item
    index = {"primeiro": 0, "primeira": 0, "1": 0, "segundo": 1, "segunda": 1, "2": 1,
             "terceiro": 2, "terceira": 2, "3": 2}
    for word, i in index.items():
        if word in t and i < len(options):
            return options[i]
    for item in options:
        if normalizar(item["identificacao"]) in t:
            return item
    return None


def _cancelar_pendente(session, state):
    proposal_id = state.get("proposta_id")
    if proposal_id:
        proposal = session.execute(select(PropostaAgendamento).where(
            PropostaAgendamento.id == proposal_id
        ).with_for_update()).scalar_one_or_none()
        if proposal and proposal.consumida_em is None:
            proposal.consumida_em = datetime.utcnow()
    return {}


def _novo_fluxo(session, row, kwargs, text, state, context):
    state, action = iniciar_ou_continuar(text, state)
    if action["tipo"] == "consulta":
        return None
    if action["tipo"] == "cancelada":
        _cancelar_pendente(session, _state(row))
        state = {}
        _save_state(row, state)
        _append(row, "ia", action["resposta"])
        return {"resposta": action["resposta"], "proposta": None}
    if action["tipo"] == "pergunta":
        _save_state(row, state)
        _append(row, "ia", action["resposta"])
        return {"resposta": action["resposta"], "proposta": None}

    # A data e a duração são determinadas pelo backend, não pelo LLM.
    start = end = None
    if state["operacao"] in {"CRIAR_OS_E_AGENDAR", "CONSULTAR_DISPONIBILIDADE"} and state.get("data") and state.get("hora") and state.get("duracao_horas"):
        start = datetime.fromisoformat(state["data"] + "T" + state["hora"])
        end = start + timedelta(hours=state["duracao_horas"])
        try:
            start, end = validar_intervalo(start.isoformat(), end.isoformat())
        except ValueError as exc:
            state.pop("data", None)
            _save_state(row, state)
            _append(row, "ia", str(exc))
            return {"resposta": str(exc), "proposta": None}

    options = state.get("opcoes_recurso", [])
    picked = _frase_opcoes(text, options)
    if picked:
        state["recurso_id"] = picked["id"]
        state["recurso_tipo"] = picked["tipo"]
        state.pop("opcoes_recurso", None)
    try:
        available, selected = localizar_recurso(session, context, state, start, end)
    except AdministracaoNegada:
        response = "Seu perfil não pode consultar esse tipo de recurso. Peça à gestão para verificar a permissão."
        _append(row, "ia", response)
        return {"resposta": response, "proposta": None}

    if not available:
        response = (f"Não encontrei {state['categoria'].lower()} livre nesse intervalo."
                    if start else f"Não encontrei {state['categoria'].lower()} ativo e operacional.")
        unclassified = session.scalar(select(Maquina.id).where(Maquina.ativo.is_(True), Maquina.categoria.is_(None)).limit(1))
        if state["categoria"] in {"TRATOR", "COLHEITADEIRA", "PULVERIZADOR", "CAMINHAO"} and unclassified:
            response += " Alguns cadastros antigos não têm categoria; classifique-os na tela de Maquinários para incluí-los com segurança."
        _save_state(row, state)
        _append(row, "ia", response)
        if state["operacao"] == "CONSULTAR_DISPONIBILIDADE":
            _save_state(row, {})
        return {"resposta": response, "proposta": None}
    if state["operacao"] == "CONSULTAR_DISPONIBILIDADE":
        response = "Encontrei estas opções livres nesse período:\n" + "\n".join(
            f"{i + 1}. {x['identificacao']} — {x['fabricante'] or ''} {x['modelo']}".strip()
            for i, x in enumerate(available[:8])
        ) if start else "Estes recursos estão ativos e operacionais agora:\n" + "\n".join(
            f"{i + 1}. {x['identificacao']} — {x['fabricante'] or ''} {x['modelo']}".strip()
            for i, x in enumerate(available[:8])
        )
        _save_state(row, {})
        _append(row, "ia", response, {"opcoes_recurso": available[:8]})
        return {"resposta": response, "proposta": None, "opcoes_recurso": available[:8]}
    if selected is None and len(available) > 1:
        state["opcoes_recurso"] = available[:8]
        response = "Encontrei estas opções reais" + (" livres nesse horário:" if start else " operacionais:") + "\n" + "\n".join(
            f"{i + 1}. {x['identificacao']} — {x['fabricante'] or ''} {x['modelo']}".strip()
            for i, x in enumerate(available[:8])
        ) + "\nQual delas você prefere?"
        _save_state(row, state)
        _append(row, "ia", response, {"opcoes_recurso": available[:8]})
        return {"resposta": response, "proposta": None, "opcoes_recurso": available[:8]}
    if selected is None:
        selected = available[0]
        state["recurso_id"] = selected["id"]
        state["recurso_tipo"] = selected["tipo"]

    try:
        escopo_atual(session, context, "OS.CRIAR")
        if start:
            escopo_atual(session, context, "OS.EDITAR")
    except AdministracaoNegada:
        response = "Seu perfil não tem permissão para criar esta ordem" + (" e agendá-la." if start else ".")
        _append(row, "ia", response)
        return {"resposta": response, "proposta": None}, 403

    data = resumo_proposta(state, selected)
    state["texto_proposta"] = normalizar(text)
    return _propose(session, row, context, kwargs, state, data, op=state["operacao"], start=start, end=end)


def _continuar_agendamento_existente(session, row, kwargs, state, text, context):
    state = dict(state)
    state["data"] = _parse_data(text, state)
    state["hora"] = _parse_horario(text, state)
    hours = _parse_duracao(text, {"duracao_horas": None})
    if hours is not None:
        state["duracao_minutos"] = hours * 60
    if not state.get("data"):
        response = "Para qual dia devo mover a OS?"
    elif not state.get("hora"):
        response = "A que horas devo agendar essa OS?"
    elif not state.get("duracao_minutos"):
        response = "Qual duração prevista em horas?"
    else:
        start = datetime.fromisoformat(state["data"] + "T" + state["hora"])
        end = start + timedelta(minutes=state["duracao_minutos"])
        try:
            start, end = validar_intervalo(start.isoformat(), end.isoformat())
            escopo_atual(session, context, "OS.EDITAR")
            order = session.execute(consulta_os(session, context, "OS.EDITAR",
                select(OrdemServico).where(OrdemServico.id == state["ordem_id"]))).scalar_one_or_none()
            if order is None or not order.ativo or order.status in {"CONCLUIDA", "CANCELADA"}:
                return {"error": "A OS não está mais aberta ou autorizada.", "status": 409}
            from services.calendario_service import _validar_disponibilidade
            _validar_disponibilidade(session, order.id, None, start, end)
        except AdministracaoNegada:
            return {"error": "Seu perfil não tem permissão para agendar essa OS.", "status": 403}
        except ValueError as exc:
            response = f"Esse horário não está disponível: {exc}. Informe outra data ou horário."
        else:
            state["texto_proposta"] = normalizar(text)
            data = {"ordem_id": order.id, "os_numero": order.numero, "os_titulo": order.titulo}
            return _propose(session, row, context, kwargs, state, data,
                            op="AGENDAR_OS", order_id=order.id, start=start, end=end)
    _save_state(row, state)
    _append(row, "ia", response)
    return {"resposta": response, "proposta": None}


def processar_mensagem(session, kwargs, conversation_id, text):
    context = kwargs["contexto_administrativo"]
    row = conversa_autorizada(session, conversation_id,
        tenant_id=kwargs["tenant_id"], database_name=kwargs["database_name"],
        usuario_id=kwargs["usuario_autenticado_id"], session_version=context.session_version,
        lock=True) if conversation_id else None
    if conversation_id and row is None:
        return {"error": "Conversa inexistente, expirada ou sem autorização.", "status": 404}
    if row is None:
        row = nova_conversa(session, tenant_id=kwargs["tenant_id"], database_name=kwargs["database_name"],
            usuario_id=kwargs["usuario_autenticado_id"], session_version=context.session_version)
    messages = historico(row)
    _append(row, "usuario", text)
    state = _state(row)

    if state.get("estado_proposta") == "AGUARDANDO_CONFIRMACAO" and eh_cancelamento(text):
        _cancelar_pendente(session, state)
        state = {}
        _save_state(row, state)
        answer = "Cancelei a proposta. Nenhuma alteração foi gravada."
        _append(row, "ia", answer)
        session.commit()
        return {"conversation_id": row.id, "resposta": answer, "proposta": None, "historico": historico(row)}

    if state.get("proposta_id") and normalizar(text) in {
        state.get("texto_proposta", ""), normalizar(state.get("mensagem_inicial", ""))
    }:
        pending = session.get(PropostaAgendamento, state["proposta_id"])
        if pending and pending.consumida_em is None and pending.expira_em > datetime.utcnow():
            answer = "A proposta desta conversa continua aguardando sua confirmação."
            _append(row, "ia", answer)
            session.commit()
            payload = _proposal_payload(pending)
            return {"conversation_id": row.id, "resposta": answer,
                "proposta": {"id": pending.id, "operacao": pending.operacao, "dados": payload,
                    "inicio": pending.inicio.isoformat(timespec="minutes") if pending.inicio else payload.get("inicio"),
                    "fim": pending.fim.isoformat(timespec="minutes") if pending.fim else payload.get("fim"),
                    "expira_em_segundos": max(0, int((pending.expira_em - datetime.utcnow()).total_seconds()))},
                "historico": historico(row)}

    # A textual confirmation uses exactly the same locked confirmation path as the card.
    if state.get("proposta_id") and normalizar(text).strip(" .!?") in {"pode confirmar", "confirmo", "confirmar", "pode criar", "sim confirmar"}:
        result = confirmar_por_id(session, kwargs, state["proposta_id"], idempotent=True)
        answer = result.get("message") or result.get("error") or "Não consegui confirmar a proposta."
        state = {}
        _save_state(row, state)
        _append(row, "ia", answer, {"resultado": result.get("result")})
        session.commit()
        return {"conversation_id": row.id, "resposta": answer, "proposta": None,
                "resultado": result.get("result"), "historico": historico(row)}, result.get("status", 200)

    if state.get("operacao"):
        operational_answer = responder_consulta_operacional(text, contexto_operacional(session, context))
        if operational_answer is not None:
            _append(row, "ia", operational_answer)
            _save_state(row, state)
            session.commit()
            return {"conversation_id": row.id, "resposta": operational_answer,
                    "proposta": None, "historico": historico(row)}

    # Alterar qualquer campo invalida a confirmação anterior. A proposta antiga
    # fica consumida como cancelada e precisa ser apresentada novamente.
    if state.get("proposta_id"):
        _cancelar_pendente(session, state)
        state.pop("proposta_id", None)
        state["estado_proposta"] = "COLETANDO"

    if state.get("operacao") == "AGENDAR_OS":
        response = _continuar_agendamento_existente(session, row, kwargs, state, text, context)
        if "error" in response:
            return response
        if "proposta" in response:
            session.commit()
            return {"conversation_id": row.id, "historico": historico(row),
                    "resposta": "Revise o novo horário antes de confirmar.", **response}
        session.commit()
        return {"conversation_id": row.id, "historico": historico(row), **response}

    # Explicit OS number means scheduling an existing order; retain the prior contract.
    legacy = extrair_pedido_agendamento(text)
    if legacy and legacy.get("numero_os"):
        data = contexto_operacional(session, context)
        order = next((o for o in data["ordens_servico"] if o["numero"] == legacy["numero_os"]), None)
        if not order:
            answer = f"Não encontrei a OS #{legacy['numero_os']} na sua listagem autorizada."
            _append(row, "ia", answer)
            session.commit()
            return {"conversation_id": row.id, "resposta": answer, "proposta": None, "historico": historico(row)}
        if legacy.get("erro"):
            _append(row, "ia", legacy["erro"])
            session.commit()
            return {"conversation_id": row.id, "resposta": legacy["erro"], "proposta": None, "historico": historico(row)}
        try:
            escopo_atual(session, context, "OS.EDITAR")
        except AdministracaoNegada:
            return {"error": "Seu perfil não tem permissão para agendar OS.", "status": 403}
        start, end = legacy["inicio"], legacy["fim"]
        try:
            from services.calendario_service import _validar_disponibilidade
            _validar_disponibilidade(session, order["id"], None, start, end)
        except ValueError as exc:
            response = f"A OS #{order['numero']} não está livre nesse intervalo: {exc}. Informe outro horário."
            _append(row, "ia", response)
            session.commit()
            return {"conversation_id": row.id, "resposta": response, "proposta": None,
                    "historico": historico(row)}
        data_os = {"ordem_id": order["id"], "os_numero": order["numero"], "os_titulo": order["titulo"]}
        state = {"operacao": "AGENDAR_OS", "estado_proposta": "COLETANDO",
                 "ordem_id": order["id"], "numero_os": order["numero"],
                 "data": start.date().isoformat(), "hora": start.strftime("%H:%M"),
                 "duracao_minutos": int((end - start).total_seconds() // 60),
                 "mensagem_inicial": text[:800], "texto_proposta": normalizar(text)}
        response = _propose(session, row, context, kwargs, state, data_os,
                            op="AGENDAR_OS", order_id=order["id"], start=start, end=end)
        session.rollback()  # _propose commits; rollback only closes any read transaction.
        return {**response, "conversation_id": row.id, "historico": historico(row)}

    output = _novo_fluxo(session, row, kwargs, text, state, context)
    if output is None:
        data = contexto_operacional(session, context)
        session.rollback()
        answer = responder_consulta_operacional(text, data)
        if answer is None:
            response = chamar_ollama(text, data, historico(row)[:-1])
            answer = response.get("resposta", "Não consegui responder agora.")
            sources = response.get("fontes", [])
        else:
            sources = []
        _append(row, "ia", answer, {"fontes": sources} if sources else None)
        _save_state(row, state)
        session.commit()
        return {"conversation_id": row.id, "resposta": answer, "proposta": None,
                "fontes": sources, "historico": historico(row)}
    if isinstance(output, tuple):
        result, status = output
        session.commit()
        return {"conversation_id": row.id, "historico": historico(row), **result}, status
    if "proposta" in output:
        session.commit()
        return {"conversation_id": row.id, "historico": historico(row),
                "resposta": "Revise a proposta antes de confirmar. Nada foi gravado ainda.", **output}
    session.commit()
    return {"conversation_id": row.id, "historico": historico(row), **output}


def confirmar_por_id(session, kwargs, proposal_id, idempotent=False):
    context = kwargs["contexto_administrativo"]
    proposal = session.execute(select(PropostaAgendamento).where(
        PropostaAgendamento.id == proposal_id
    ).with_for_update()).scalar_one_or_none()
    if proposal is None:
        return {"error": "Proposta não encontrada.", "status": 404}
    if (proposal.tenant_id != kwargs["tenant_id"] or proposal.database_name != context.database_name or
            proposal.usuario_id != kwargs["usuario_autenticado_id"] or proposal.session_version != context.session_version):
        return {"error": "Proposta pertence a outra sessão.", "status": 403}
    if proposal.consumida_em is not None:
        if proposal.resultado_os_id or proposal.resultado_agendamento_id:
            payload = _proposal_payload(proposal)
            result = {"os_id": proposal.resultado_os_id, "agendamento_id": proposal.resultado_agendamento_id,
                      "operacao": proposal.operacao,
                      "inicio": proposal.inicio.isoformat(timespec="minutes") if proposal.inicio else payload.get("inicio"),
                      "fim": proposal.fim.isoformat(timespec="minutes") if proposal.fim else payload.get("fim")}
            if proposal.resultado_os_id:
                os_ = session.get(OrdemServico, proposal.resultado_os_id)
                result["os_numero"] = os_.numero if os_ else None
            return {"message": "Esta proposta já foi confirmada.", "result": result,
                    "idempotente": True, "status": 200}
        return {"error": "Proposta cancelada, expirada ou já utilizada.", "status": 409}
    if proposal.expira_em < datetime.utcnow():
        return {"error": "Proposta expirada. Faça um novo pedido.", "status": 409}
    try:
        payload = _proposal_payload(proposal)
        if proposal.operacao == "AGENDAR_OS":
            escopo_atual(session, context, "OS.EDITAR")
            os_ = session.execute(consulta_os(session, context, "OS.EDITAR",
                select(OrdemServico).where(OrdemServico.id == proposal.ordem_id))).scalar_one_or_none()
            if os_ is None or not os_.ativo or os_.status in {"CONCLUIDA", "CANCELADA"}:
                return {"error": "A OS foi encerrada ou deixou de estar autorizada.", "status": 409}
            if proposal.inicio is None or proposal.inicio <= horario_local():
                return {"error": "O horário solicitado já passou.", "status": 409}
            appointment = criar_agendamento(session, os_.id, proposal.inicio, proposal.fim,
                observacoes="Agendamento criado pelo assistente após confirmação explícita.", commit=False)
            registrar_evento(session, context, "agendar_os_assistente")
            result = {"os_id": os_.id, "os_numero": os_.numero, "agendamento_id": appointment.id,
                      "inicio": proposal.inicio.isoformat(timespec="minutes"),
                      "fim": proposal.fim.isoformat(timespec="minutes")}
        else:
            escopo_atual(session, context, "OS.CRIAR")
            iniciar_escrita(session)
            kind = payload["recurso_tipo"]
            model = Maquina if kind == "maquina" else Equipamento
            asset = session.execute(select(model).where(model.id == payload["recurso_id"]).with_for_update()).scalar_one_or_none()
            if asset is None or not asset.ativo or normalizar(asset.status) not in {"operando", "disponivel"}:
                return {"error": "O recurso deixou de estar ativo e operacional. Faça uma nova proposta.", "status": 409}
            if proposal.operacao == "CRIAR_OS_E_AGENDAR":
                escopo_atual(session, context, "OS.EDITAR")
            order = criar_ordem_servico_na_sessao(
                session, tipo=payload["tipo"], titulo=payload["titulo"], descricao=payload["descricao"],
                maquina_id=asset.id if kind == "maquina" else None,
                equipamento_id=asset.id if kind == "equipamento" else None,
                operador_id=payload.get("operador_id"), responsavel_id=payload.get("responsavel_id"),
                prioridade=payload["prioridade"], contexto=context,
            )
            appointment = None
            if proposal.operacao == "CRIAR_OS_E_AGENDAR":
                start, end = datetime.fromisoformat(payload["inicio"]), datetime.fromisoformat(payload["fim"])
                if start <= horario_local():
                    raise ValueError("O horário da proposta já passou.")
                appointment = criar_agendamento(session, order.id, start, end,
                    observacoes="Criado junto da OS pelo assistente após confirmação explícita.", commit=False)
                registrar_evento(session, context, "agendar_os_assistente")
            result = {"os_id": order.id, "os_numero": order.numero,
                      "agendamento_id": appointment.id if appointment else None,
                      "inicio": payload.get("inicio"), "fim": payload.get("fim")}
        proposal.resultado_os_id = result.get("os_id")
        proposal.resultado_agendamento_id = result.get("agendamento_id")
        proposal.consumida_em = datetime.utcnow()
        session.commit()
        result["operacao"] = proposal.operacao
        return {"message": (f"Agendamento confirmado para a OS #{result.get('os_numero')}." if proposal.operacao == "AGENDAR_OS"
                else "Ordem de serviço e agendamento confirmados." if result.get("agendamento_id")
                else "Ordem de serviço criada."),
                "result": result, "idempotente": False, "status": 200}
    except AdministracaoNegada:
        session.rollback()
        return {"error": "Permissão, sessão ou escopo insuficiente para concluir a operação.", "status": 403}
    except ValueError as exc:
        session.rollback()
        return {"error": f"Não gravei alterações: {exc}", "status": 409}
    except Exception:
        session.rollback()
        return {"error": "A operação falhou e foi revertida. Confira a agenda antes de tentar novamente.", "status": 500}


def confirmar_por_codigo(session, kwargs, code):
    proposal = session.execute(select(PropostaAgendamento.id).where(
        PropostaAgendamento.token_hash == hashlib.sha256(code.encode()).hexdigest()
    )).scalar_one_or_none()
    if proposal is None:
        return {"error": "Proposta inexistente, expirada ou inválida.", "status": 409}
    return confirmar_por_id(session, kwargs, proposal)
