"""Integração acadêmica AgroFrota + Ollama. Não homologada para produção."""
import os
import secrets
import hashlib
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from sqlalchemy import delete, select

from config import Config
from middleware.auth import autenticar
from middleware.permissions import exigir_permissao
from middleware.tenant import resolver_tenant
from models.tenant.ordem_servico import OrdemServico
from models.tenant.proposta_agendamento import PropostaAgendamento
from services.admin_policy import AdministracaoNegada
from services.assistente_ia_service import (
    chamar_ollama, contexto_operacional, horario_local, validar_intervalo,
    responder_consulta_operacional,
)
from services.calendario_service import criar_agendamento
from services.os_policy import consulta_os
from services.assistente_ia_guardrails import extrair_pedido_agendamento, alegacao_agendamento_realizado

assistente_ia_bp = Blueprint("assistente_ia", __name__, url_prefix="/api/assistente")
_TTL = 300


def _apenas_desenvolvimento():
    return os.getenv("AGROFROTA_ENV", "development").lower() in ("development", "testing")


def _erro(msg, status):
    return jsonify({"success": False, "message": msg}), status


def _proposta_nova(session, dados):
    codigo = secrets.token_urlsafe(32)
    agora = datetime.utcnow()
    try:
        session.execute(delete(PropostaAgendamento).where(
            PropostaAgendamento.expira_em < agora,
        ))
        session.add(PropostaAgendamento(
            token_hash=hashlib.sha256(codigo.encode("utf-8")).hexdigest(),
            tenant_id=dados["tenant_id"], database_name=dados["database_name"],
            usuario_id=dados["usuario_id"], session_version=dados["session_version"],
            ordem_id=dados["ordem_id"], inicio=dados["inicio"], fim=dados["fim"],
            expira_em=agora + timedelta(seconds=_TTL),
        ))
        session.commit()
    except Exception:
        session.rollback()
        return None
    return codigo


@assistente_ia_bp.post("/mensagem")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.VISUALIZAR")
def mensagem(**kwargs):
    if not _apenas_desenvolvimento():
        return _erro("Assistente acadêmico desabilitado fora do desenvolvimento.", 403)
    body = request.get_json(silent=True) or {}
    pergunta = body.get("mensagem")
    if not isinstance(pergunta, str) or not 1 <= len(pergunta.strip()) <= 800:
        return _erro("Escreva uma mensagem de 1 a 800 caracteres.", 400)

    session = kwargs["tenant_session"]
    contexto = kwargs["contexto_administrativo"]
    try:
        dados = contexto_operacional(session, contexto)
        # Libera a conexão antes da inferência demorada do modelo.
        session.rollback()
        pedido = extrair_pedido_agendamento(pergunta.strip())
        if pedido is None:
            # Consulta: o modelo jamais tem autorização para gerar uma proposta.
            resposta_operacional = responder_consulta_operacional(pergunta.strip(), dados)
            if resposta_operacional is not None:
                saida = {"intencao": "consulta", "resposta": resposta_operacional, "fontes": []}
            else:
                saida = chamar_ollama(pergunta.strip(), dados)
                # Proteção independente da saída/aderência do modelo ao JSON Schema.
                saida['intencao'] = 'consulta'
        elif pedido['erro']:
            return jsonify({'success': True, 'resposta': pedido['erro'], 'proposta': None})
        else:
            # O usuário informa o NÚMERO da OS, não seu ID interno.
            # OS e horário são determinados pelo servidor, nunca pelo LLM.
            identificada = next((os_ for os_ in dados['ordens_servico']
                                 if os_['numero'] == pedido['numero_os']), None)
            if identificada is None:
                return jsonify({'success': True, 'resposta':
                    f"OS número {pedido['numero_os']} não encontrada na listagem autorizada. "
                    'Confira a página de ordens de serviço.', 'proposta': None})
            saida = {
                'intencao': 'agendar',
                'resposta': 'Preparei uma proposta. Confira OS, data e horário antes de confirmar.',
                'ordem_servico_id': identificada['id'],
                'inicio': pedido['inicio'].isoformat(timespec='minutes'),
                'fim': pedido['fim'].isoformat(timespec='minutes'),
            }
    except AdministracaoNegada:
        return _erro("Não há permissão para esta consulta.", 403)
    except RuntimeError as exc:
        return _erro(str(exc), 503)

    resposta = saida["resposta"].strip()[:2200]
    if saida["intencao"] != "agendar":
        if alegacao_agendamento_realizado(resposta):
            resposta = ('Nenhum agendamento foi realizado. A resposta gerada não '
                       'é confiável; tente reformular sua pergunta técnica.')
        return jsonify({"success": True, "resposta": resposta, "proposta": None,
                        "fontes": saida.get("fontes", [])})
    if not dados["pode_agendar"]:
        return _erro("Seu perfil não tem permissão para agendar serviços.", 403)

    ordem_id = saida.get("ordem_servico_id")
    if type(ordem_id) is not int:
        return jsonify({"success": True, "resposta": "Indique a OS existente que deseja agendar.", "proposta": None})
    autorizadas = {o["id"]: o for o in dados["ordens_servico"]}
    ordem = autorizadas.get(ordem_id)
    if ordem is None or not ordem["ativo"] or ordem["status"] in ("CONCLUIDA", "CANCELADA"):
        return jsonify({"success": True, "resposta": "Não encontrei uma OS aberta e autorizada para esse pedido. Informe o número de uma OS aberta.", "proposta": None})
    try:
        inicio, fim = validar_intervalo(saida.get("inicio"), saida.get("fim"))
    except ValueError as exc:
        return jsonify({"success": True, "resposta": str(exc), "proposta": None})

    # Revalida permissão/escopo após o tempo de processamento do modelo.
    try:
        existente = session.execute(consulta_os(
            session, contexto, "OS.EDITAR",
            select(OrdemServico).where(OrdemServico.id == ordem_id),
        )).scalar_one_or_none()
        if existente is None or not existente.ativo or existente.status in ("CONCLUIDA", "CANCELADA"):
            return _erro("A OS não está mais disponível para agendamento.", 409)
    except AdministracaoNegada:
        return _erro("Sem autorização para alterar esta OS.", 403)
    finally:
        session.rollback()

    codigo = _proposta_nova(session, {
        "tenant_id": kwargs["tenant_id"], "usuario_id": kwargs["usuario_autenticado_id"],
        "session_version": contexto.session_version, "database_name": contexto.database_name,
        "ordem_id": ordem_id, "inicio": inicio, "fim": fim,
    })
    if codigo is None:
        return _erro("Muitas propostas simultâneas. Tente novamente.", 503)
    return jsonify({
        "success": True, "resposta": resposta or "Preparei uma proposta de agendamento.",
        "proposta": {
            "codigo": codigo, "os_id": ordem_id, "os_numero": ordem["numero"],
            "os_titulo": ordem["titulo"],
            "inicio": inicio.isoformat(timespec="minutes"),
            "fim": fim.isoformat(timespec="minutes"),
            "duracao_padrao": not bool(saida.get("fim")),
            "expira_em_segundos": _TTL,
        },
    })


@assistente_ia_bp.post("/confirmar")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.EDITAR")
def confirmar(**kwargs):
    if not _apenas_desenvolvimento():
        return _erro("Assistente acadêmico desabilitado fora do desenvolvimento.", 403)
    body = request.get_json(silent=True) or {}
    codigo = body.get("codigo")
    if not isinstance(codigo, str) or len(codigo) > 128:
        return _erro("Código da proposta inválido.", 400)
    session = kwargs["tenant_session"]
    token_hash = hashlib.sha256(codigo.encode("utf-8")).hexdigest()
    proposta = session.execute(
        select(PropostaAgendamento)
        .where(PropostaAgendamento.token_hash == token_hash)
        .with_for_update()
    ).scalar_one_or_none()
    if proposta is None or proposta.expira_em < datetime.utcnow() or proposta.consumida_em is not None:
        return _erro("Proposta inexistente, expirada ou já utilizada. Faça um novo pedido.", 409)

    contexto = kwargs["contexto_administrativo"]
    if (proposta.tenant_id != kwargs["tenant_id"] or
        proposta.usuario_id != kwargs["usuario_autenticado_id"] or
        proposta.session_version != contexto.session_version or
        proposta.database_name != contexto.database_name):
        return _erro("A proposta pertence a outra sessão.", 403)
    try:
        os_ = session.execute(consulta_os(
            session, contexto, "OS.EDITAR",
            select(OrdemServico).where(OrdemServico.id == proposta.ordem_id),
        )).scalar_one_or_none()
        if os_ is None or not os_.ativo or os_.status in ("CONCLUIDA", "CANCELADA"):
            return _erro("OS não encontrada ou encerrada. Faça um novo pedido.", 409)
        if proposta.inicio <= horario_local():
            return _erro("O horário informado já passou. Faça um novo pedido.", 409)
        proposta.consumida_em = datetime.utcnow()
        registro = criar_agendamento(
            session=session, ordem_servico_id=proposta.ordem_id,
            inicio=proposta.inicio, fim=proposta.fim,
            observacoes="Criado pelo assistente de IA acadêmico após confirmação explícita.",
        )
        return jsonify({
            "success": True, "message": "Agendamento confirmado no AgroFrota.",
            "agendamento": {"id": registro.id, "ordem_servico_id": registro.ordem_servico_id,
                            "inicio": registro.inicio.isoformat(timespec="minutes"),
                            "fim": registro.fim.isoformat(timespec="minutes")},
        })
    except AdministracaoNegada:
        session.rollback()
        return _erro("Permissão ou escopo insuficiente para este agendamento.", 403)
    except ValueError as exc:
        session.rollback()
        return _erro(f"Agendamento não realizado: {str(exc)}", 409)
    except Exception:
        session.rollback()
        return _erro("Não foi possível concluir o agendamento. Confira o calendário e tente novamente.", 500)
