from datetime import datetime

from flask import Blueprint, jsonify, request

from config import Config
from middleware.auth import autenticar
from middleware.permissions import exigir_permissao
from middleware.tenant import resolver_tenant

from schemas.agendamento import (
    AgendamentoAtualizarSchema,
    AgendamentoCriarSchema,
    AgendamentoRespostaSchema,
)

from services.calendario_service import (
    atualizar_agendamento,
    buscar_agendamento,
    cancelar_agendamento,
    criar_agendamento,
    listar_agendamentos,
)


calendario_bp = Blueprint(
    "calendario",
    __name__,
    url_prefix="/api/calendario"
)


@calendario_bp.post("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.EDITAR")
def criar(**kwargs):
    tenant_session = kwargs["tenant_session"]

    try:
        data = request.get_json(silent=True) or {}

        dados = AgendamentoCriarSchema.model_validate(data)

        agendamento = criar_agendamento(
            session=tenant_session,
            ordem_servico_id=dados.ordem_servico_id,
            inicio=dados.inicio,
            fim=dados.fim,
            responsavel_id=dados.responsavel_id,
            observacoes=dados.observacoes,
        )

        return jsonify({
            "success": True,
            "message": "Agendamento criado com sucesso.",
            "agendamento": AgendamentoRespostaSchema.model_validate(
                agendamento
            ).model_dump(mode="json")
        }), 201

    except ValueError as erro:
        tenant_session.rollback()

        return jsonify({
            "success": False,
            "message": str(erro)
        }), 400

    except Exception:
        tenant_session.rollback()

        return jsonify({
            "success": False,
            "message": "Erro interno ao criar agendamento."
        }), 500


@calendario_bp.get("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.VISUALIZAR")
def listar(**kwargs):
    tenant_session = kwargs["tenant_session"]

    try:
        inicio = datetime.fromisoformat(request.args["inicio"]) if request.args.get("inicio") else None
        fim = datetime.fromisoformat(request.args["fim"]) if request.args.get("fim") else None
        limite = int(request.args.get("limite", 100))
        offset = int(request.args.get("offset", 0))
        if not 1 <= limite <= 200 or offset < 0 or (inicio and fim and inicio >= fim):
            raise ValueError()
        agendamentos = listar_agendamentos(tenant_session, inicio, fim, limite, offset)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Filtros de agenda inválidos."}), 400

    return jsonify({
        "success": True,
        "agendamentos": [
            AgendamentoRespostaSchema.model_validate(
                agendamento
            ).model_dump(mode="json")
            for agendamento in agendamentos
        ]
    })


@calendario_bp.get("/<int:agendamento_id>")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.VISUALIZAR")
def buscar(agendamento_id, **kwargs):
    tenant_session = kwargs["tenant_session"]

    agendamento = buscar_agendamento(
        tenant_session,
        agendamento_id
    )

    if agendamento is None:
        return jsonify({
            "success": False,
            "message": "Agendamento não encontrado."
        }), 404

    return jsonify({
        "success": True,
        "agendamento": AgendamentoRespostaSchema.model_validate(
            agendamento
        ).model_dump(mode="json")
    })


@calendario_bp.put("/<int:agendamento_id>")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.EDITAR")
def atualizar(agendamento_id, **kwargs):
    tenant_session = kwargs["tenant_session"]

    try:
        data = request.get_json(silent=True) or {}

        dados = AgendamentoAtualizarSchema.model_validate(data)

        dados_atualizacao = dados.model_dump(
            exclude_unset=True
        )

        agendamento = atualizar_agendamento(
            session=tenant_session,
            agendamento_id=agendamento_id,
            **dados_atualizacao,
        )

        return jsonify({
            "success": True,
            "message": "Agendamento atualizado com sucesso.",
            "agendamento": AgendamentoRespostaSchema.model_validate(
                agendamento
            ).model_dump(mode="json")
        })

    except ValueError as erro:
        tenant_session.rollback()

        return jsonify({
            "success": False,
            "message": str(erro)
        }), 400

    except Exception:
        tenant_session.rollback()

        return jsonify({
            "success": False,
            "message": "Erro interno ao atualizar agendamento."
        }), 500


@calendario_bp.patch("/<int:agendamento_id>/cancelar")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.EDITAR")
def cancelar(agendamento_id, **kwargs):
    tenant_session = kwargs["tenant_session"]

    try:
        agendamento = cancelar_agendamento(
            tenant_session,
            agendamento_id
        )

        return jsonify({
            "success": True,
            "message": "Agendamento cancelado com sucesso.",
            "agendamento": AgendamentoRespostaSchema.model_validate(
                agendamento
            ).model_dump(mode="json")
        })

    except ValueError as erro:
        tenant_session.rollback()

        return jsonify({
            "success": False,
            "message": str(erro)
        }), 400

    except Exception:
        tenant_session.rollback()

        return jsonify({
            "success": False,
            "message": "Erro interno ao cancelar agendamento."
        }), 500