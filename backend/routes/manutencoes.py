from flask import Blueprint, jsonify, request

from config import Config
from middleware.auth import autenticar
from middleware.permissions import exigir_permissao
from middleware.tenant import resolver_tenant

from schemas.manutencao import (
    ManutencaoAtualizarSchema,
    ManutencaoCriarSchema,
    ManutencaoRespostaSchema,
)

from services.manutencao_service import (
    atualizar_manutencao,
    buscar_manutencao,
    cancelar_manutencao,
    concluir_manutencao,
    criar_manutencao,
    listar_manutencoes,
)


manutencoes_bp = Blueprint(
    "manutencoes",
    __name__,
    url_prefix="/api/manutencoes"
)


@manutencoes_bp.post("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("MANUTENCAO.CRIAR")
def criar(**kwargs):
    tenant_session = kwargs["tenant_session"]

    try:
        data = request.get_json(silent=True) or {}

        dados = ManutencaoCriarSchema.model_validate(data)

        manutencao = criar_manutencao(
            session=tenant_session,
            ordem_servico_id=dados.ordem_servico_id,
            inicio=dados.inicio,
            tipo=dados.tipo,
            responsavel_id=dados.responsavel_id,
            fim=dados.fim,
            descricao=dados.descricao,
            custo=dados.custo,
            observacoes=dados.observacoes,
        )

        return jsonify({
            "success": True,
            "message": "Manutenção criada com sucesso.",
            "manutencao": ManutencaoRespostaSchema.model_validate(
                manutencao
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
            "message": "Erro interno ao criar manutenção."
        }), 500


@manutencoes_bp.get("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("MANUTENCAO.VISUALIZAR")
def listar(**kwargs):
    tenant_session = kwargs["tenant_session"]

    manutencoes = listar_manutencoes(
        tenant_session
    )

    return jsonify({
        "success": True,
        "manutencoes": [
            ManutencaoRespostaSchema.model_validate(
                manutencao
            ).model_dump(mode="json")
            for manutencao in manutencoes
        ]
    })


@manutencoes_bp.get("/<int:manutencao_id>")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("MANUTENCAO.VISUALIZAR")
def buscar(manutencao_id, **kwargs):
    tenant_session = kwargs["tenant_session"]

    manutencao = buscar_manutencao(
        tenant_session,
        manutencao_id
    )

    if manutencao is None:
        return jsonify({
            "success": False,
            "message": "Manutenção não encontrada."
        }), 404

    return jsonify({
        "success": True,
        "manutencao": ManutencaoRespostaSchema.model_validate(
            manutencao
        ).model_dump(mode="json")
    })


@manutencoes_bp.put("/<int:manutencao_id>")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("MANUTENCAO.EDITAR")
def atualizar(manutencao_id, **kwargs):
    tenant_session = kwargs["tenant_session"]

    try:
        data = request.get_json(silent=True) or {}

        dados = ManutencaoAtualizarSchema.model_validate(data)

        manutencao = atualizar_manutencao(
            session=tenant_session,
            manutencao_id=manutencao_id,
            responsavel_id=dados.responsavel_id,
            tipo=dados.tipo,
            inicio=dados.inicio,
            fim=dados.fim,
            descricao=dados.descricao,
            custo=dados.custo,
            status=dados.status,
            observacoes=dados.observacoes,
        )

        return jsonify({
            "success": True,
            "message": "Manutenção atualizada com sucesso.",
            "manutencao": ManutencaoRespostaSchema.model_validate(
                manutencao
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
            "message": "Erro interno ao atualizar manutenção."
        }), 500


@manutencoes_bp.patch("/<int:manutencao_id>/concluir")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("MANUTENCAO.CONCLUIR")
def concluir(manutencao_id, **kwargs):
    tenant_session = kwargs["tenant_session"]

    try:
        data = request.get_json(silent=True) or {}

        fim = None

        if data.get("fim"):
            dados = ManutencaoAtualizarSchema.model_validate({
                "fim": data["fim"]
            })

            fim = dados.fim

        manutencao = concluir_manutencao(
            session=tenant_session,
            manutencao_id=manutencao_id,
            fim=fim,
        )

        return jsonify({
            "success": True,
            "message": "Manutenção concluída com sucesso.",
            "manutencao": ManutencaoRespostaSchema.model_validate(
                manutencao
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
            "message": "Erro interno ao concluir manutenção."
        }), 500


@manutencoes_bp.patch("/<int:manutencao_id>/cancelar")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("MANUTENCAO.CANCELAR")
def cancelar(manutencao_id, **kwargs):
    tenant_session = kwargs["tenant_session"]

    try:
        manutencao = cancelar_manutencao(
            tenant_session,
            manutencao_id
        )

        return jsonify({
            "success": True,
            "message": "Manutenção cancelada com sucesso.",
            "manutencao": ManutencaoRespostaSchema.model_validate(
                manutencao
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
            "message": "Erro interno ao cancelar manutenção."
        }), 400