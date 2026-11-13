"""Rotas do assistente local, com identidade e permissões sempre do servidor."""
import json
import logging
import os
import uuid

from flask import Blueprint, g, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from config import Config
from middleware.auth import autenticar
from middleware.permissions import exigir_permissao
from middleware.tenant import resolver_tenant
from models.tenant.conversa_assistente import ConversaAssistente
from models.tenant.proposta_agendamento import PropostaAgendamento
from services.assistente_operacoes_service import (
    nova_conversa, conversa_autorizada, historico, processar_mensagem,
    confirmar_por_codigo, confirmar_por_id, registrar_resultado_conversa,
)

assistente_ia_bp = Blueprint("assistente_ia", __name__, url_prefix="/api/assistente")
logger = logging.getLogger(__name__)


@assistente_ia_bp.before_request
def _correlacionar_requisicao():
    g.assistant_request_id = uuid.uuid4().hex


@assistente_ia_bp.after_request
def _retornar_correlacao(response):
    response.headers["X-Request-ID"] = getattr(g, "assistant_request_id", "")
    return response


def _erro(msg, status):
    return jsonify({"success": False, "message": msg}), status


def _enabled():
    ambiente = os.getenv("AGROFROTA_ENV", "development").lower()
    return ambiente in {"development", "testing"} or os.getenv("AGROFROTA_ENABLE_ASSISTANT") == "1"


@assistente_ia_bp.get("/conversas")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.VISUALIZAR")
def listar_conversas(**kwargs):
    session = kwargs["tenant_session"]
    context = kwargs["contexto_administrativo"]
    rows = session.scalars(select(ConversaAssistente).where(
        ConversaAssistente.tenant_id == kwargs["tenant_id"],
        ConversaAssistente.database_name == kwargs["database_name"],
        ConversaAssistente.usuario_id == kwargs["usuario_autenticado_id"],
        ConversaAssistente.session_version == context.session_version,
        ConversaAssistente.expira_em > __import__("datetime").datetime.utcnow(),
    ).order_by(ConversaAssistente.atualizada_em.desc()).limit(20)).all()
    return jsonify({"success": True, "conversas": [{
        "id": row.id, "atualizada_em": row.atualizada_em.isoformat(),
        "preview": (historico(row)[-1].get("texto", "") if historico(row) else "Nova conversa"),
    } for row in rows]})


@assistente_ia_bp.post("/conversas")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.VISUALIZAR")
def criar_conversa(**kwargs):
    if not _enabled():
        return _erro("Assistente acadêmico desabilitado fora do desenvolvimento.", 403)
    context = kwargs["contexto_administrativo"]
    row = nova_conversa(kwargs["tenant_session"], tenant_id=kwargs["tenant_id"],
        database_name=kwargs["database_name"], usuario_id=kwargs["usuario_autenticado_id"],
        session_version=context.session_version)
    return jsonify({"success": True, "conversation_id": row.id, "historico": historico(row)}), 201


@assistente_ia_bp.get("/conversas/<string:conversation_id>")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.VISUALIZAR")
def obter_conversa(conversation_id, **kwargs):
    context = kwargs["contexto_administrativo"]
    row = conversa_autorizada(kwargs["tenant_session"], conversation_id,
        tenant_id=kwargs["tenant_id"], database_name=kwargs["database_name"],
        usuario_id=kwargs["usuario_autenticado_id"], session_version=context.session_version)
    if row is None:
        return _erro("Conversa inexistente, expirada ou sem autorização.", 404)
    state = json.loads(row.estado_json or "{}")
    pending = None
    if state.get("proposta_id"):
        p = kwargs["tenant_session"].get(PropostaAgendamento, state["proposta_id"])
        if p and p.consumida_em is None and p.expira_em > __import__("datetime").datetime.utcnow():
            try:
                data = json.loads(p.dados_json or "{}")
            except (ValueError, TypeError):
                data = {}
            pending = {"id": p.id, "operacao": p.operacao, "dados": data,
                "inicio": p.inicio.isoformat(timespec="minutes") if p.inicio else data.get("inicio"),
                "fim": p.fim.isoformat(timespec="minutes") if p.fim else data.get("fim"),
                "expira_em_segundos": max(0, int((p.expira_em - __import__("datetime").datetime.utcnow()).total_seconds()))}
    return jsonify({"success": True, "conversation_id": row.id,
                    "historico": historico(row), "proposta_pendente": pending})


@assistente_ia_bp.post("/mensagem")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.VISUALIZAR")
def mensagem(**kwargs):
    if not _enabled():
        return _erro("Assistente acadêmico desabilitado fora do desenvolvimento.", 403)
    body = request.get_json(silent=True) or {}
    text = body.get("mensagem")
    conversation_id = body.get("conversation_id")
    if not isinstance(text, str) or not 1 <= len(text.strip()) <= 800:
        return _erro("Escreva uma mensagem de 1 a 800 caracteres.", 400)
    if conversation_id is not None and (not isinstance(conversation_id, str) or len(conversation_id) != 36):
        return _erro("Identificador de conversa inválido.", 400)
    session = kwargs["tenant_session"]
    try:
        result = processar_mensagem(session, kwargs, conversation_id, text.strip())
        status = 200
        if isinstance(result, tuple):
            result, status = result
        elif result.get("status") and result.get("error"):
            status = result["status"]
        return jsonify({"success": status < 400, **result}), status
    except RuntimeError as exc:
        session.rollback()
        logger.warning("Central de Operações indisponível request_id=%s exception_type=%s.",
                       g.assistant_request_id, type(exc).__name__)
        return _erro("A Central de Operações está temporariamente indisponível. Tente novamente.", 503)
    except OperationalError as exc:
        session.rollback()
        logger.warning("Recursos de dados indisponíveis na Central request_id=%s exception_type=%s.",
                       g.assistant_request_id, type(exc).__name__)
        return _erro("A Central de Operações está temporariamente indisponível. Tente novamente.", 503)
    except Exception as exc:
        session.rollback()
        logger.error("Falha ao processar mensagem na Central de Operações request_id=%s exception_type=%s.",
                     g.assistant_request_id, type(exc).__name__)
        return _erro("Não consegui processar a mensagem. Nenhuma alteração foi confirmada.", 500)


@assistente_ia_bp.post("/confirmar")
@autenticar()
@resolver_tenant(Config)
def confirmar(**kwargs):
    if not _enabled():
        return _erro("Assistente acadêmico desabilitado fora do desenvolvimento.", 403)
    body = request.get_json(silent=True) or {}
    session = kwargs["tenant_session"]
    proposal_id = body.get("proposta_id")
    code = body.get("codigo")
    if proposal_id is not None:
        if type(proposal_id) is not int or proposal_id <= 0:
            return _erro("Proposta inválida.", 400)
        result = confirmar_por_id(session, kwargs, proposal_id, idempotent=True)
    elif isinstance(code, str) and len(code) <= 128:
        result = confirmar_por_codigo(session, kwargs, code)
    else:
        return _erro("Informe a proposta que deseja confirmar.", 400)
    if "error" in result:
        return _erro(result["error"], result.get("status", 409))
    conversation_id = body.get("conversation_id")
    if isinstance(conversation_id, str):
        os_number = (result.get("result") or {}).get("os_numero")
        agendamento_id = (result.get("result") or {}).get("agendamento_id")
        operation = (result.get("result") or {}).get("operacao")
        message = (f"Agendamento #{agendamento_id} confirmado para a OS #{os_number}."
                   if operation == "AGENDAR_OS" and os_number and agendamento_id else
                   f"OS #{os_number} criada e agendamento #{agendamento_id} confirmado."
                   if os_number and agendamento_id else
                   f"OS #{os_number} criada." if os_number else
                   f"Agendamento #{agendamento_id} confirmado.")
        registrar_resultado_conversa(session, kwargs, conversation_id, proposal_id, message, result.get("result"))
    operation_result = result.get("result") or {}
    appointment = None
    if operation_result.get("agendamento_id"):
        appointment = {"id": operation_result["agendamento_id"],
            "ordem_servico_id": operation_result.get("os_id"),
            "inicio": operation_result.get("inicio"), "fim": operation_result.get("fim")}
    return jsonify({"success": True, "message": result["message"], **operation_result,
                    "agendamento": appointment, "resultado": operation_result,
                    "idempotente": result.get("idempotente", False)}), result.get("status", 200)
