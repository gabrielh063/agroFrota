from flask import Blueprint, jsonify, request

from config import Config

from middleware.auth import autenticar
from middleware.permissions import exigir_permissao
from middleware.tenant import resolver_tenant

from schemas.indisponibilidade import (
    IndisponibilidadeAtualizarSchema,
    IndisponibilidadeCriarSchema,
    IndisponibilidadeRespostaSchema,
)

from services.indisponibilidade_service import (
    atualizar_indisponibilidade,
    buscar_indisponibilidade,
    cancelar_indisponibilidade,
    criar_indisponibilidade,
    finalizar_indisponibilidade,
    listar_indisponibilidades,
)


indisponibilidades_bp = Blueprint(
    "indisponibilidades",
    __name__,
    url_prefix="/api/indisponibilidades"
)


@indisponibilidades_bp.post("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.EDITAR")
def criar(**kwargs):

    tenant_session = kwargs["tenant_session"]

    try:
        data = request.get_json(silent=True) or {}

        dados = IndisponibilidadeCriarSchema.model_validate(
            data
        )

        indisponibilidade = criar_indisponibilidade(
            session=tenant_session,
            dados=dados,
        )

        return jsonify({
            "success": True,
            "message": "Indisponibilidade criada com sucesso.",
            "indisponibilidade": (
                IndisponibilidadeRespostaSchema
                .model_validate(indisponibilidade)
                .model_dump(mode="json")
            )
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
            "message": "Erro interno ao criar indisponibilidade."
        }), 500


@indisponibilidades_bp.get("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.VISUALIZAR")
def listar(**kwargs):

    tenant_session = kwargs["tenant_session"]

    try:
        status = request.args.get("status")

        maquina_id = request.args.get(
            "maquina_id",
            type=int
        )

        equipamento_id = request.args.get(
            "equipamento_id",
            type=int
        )

        indisponibilidades = listar_indisponibilidades(
            session=tenant_session,
            status=status,
            maquina_id=maquina_id,
            equipamento_id=equipamento_id,
        )

        return jsonify({
            "success": True,
            "indisponibilidades": [
                IndisponibilidadeRespostaSchema
                .model_validate(indisponibilidade)
                .model_dump(mode="json")
                for indisponibilidade
                in indisponibilidades
            ]
        })

    except ValueError as erro:

        return jsonify({
            "success": False,
            "message": str(erro)
        }), 400

    except Exception:

        return jsonify({
            "success": False,
            "message": "Erro interno ao listar indisponibilidades."
        }), 500


@indisponibilidades_bp.get(
    "/<int:indisponibilidade_id>"
)
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.VISUALIZAR")
def buscar(indisponibilidade_id, **kwargs):

    tenant_session = kwargs["tenant_session"]

    indisponibilidade = buscar_indisponibilidade(
        tenant_session,
        indisponibilidade_id
    )

    if indisponibilidade is None:

        return jsonify({
            "success": False,
            "message": "Indisponibilidade não encontrada."
        }), 404

    return jsonify({
        "success": True,
        "indisponibilidade": (
            IndisponibilidadeRespostaSchema
            .model_validate(indisponibilidade)
            .model_dump(mode="json")
        )
    })


@indisponibilidades_bp.put(
    "/<int:indisponibilidade_id>"
)
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.EDITAR")
def atualizar(indisponibilidade_id, **kwargs):

    tenant_session = kwargs["tenant_session"]

    try:
        data = request.get_json(silent=True) or {}

        dados = IndisponibilidadeAtualizarSchema.model_validate(
            data
        )

        indisponibilidade = atualizar_indisponibilidade(
            session=tenant_session,
            indisponibilidade_id=indisponibilidade_id,
            dados=dados,
        )

        return jsonify({
            "success": True,
            "message": (
                "Indisponibilidade atualizada com sucesso."
            ),
            "indisponibilidade": (
                IndisponibilidadeRespostaSchema
                .model_validate(indisponibilidade)
                .model_dump(mode="json")
            )
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
            "message": (
                "Erro interno ao atualizar indisponibilidade."
            )
        }), 500


@indisponibilidades_bp.patch(
    "/<int:indisponibilidade_id>/finalizar"
)
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.EDITAR")
def finalizar(indisponibilidade_id, **kwargs):

    tenant_session = kwargs["tenant_session"]

    try:
        data = request.get_json(silent=True) or {}

        if not data.get("fim"):

            return jsonify({
                "success": False,
                "message": "Informe a data/hora de fim."
            }), 400

        dados = IndisponibilidadeAtualizarSchema.model_validate({
            "fim": data["fim"]
        })

        indisponibilidade = finalizar_indisponibilidade(
            session=tenant_session,
            indisponibilidade_id=indisponibilidade_id,
            fim=dados.fim,
        )

        return jsonify({
            "success": True,
            "message": (
                "Indisponibilidade finalizada com sucesso."
            ),
            "indisponibilidade": (
                IndisponibilidadeRespostaSchema
                .model_validate(indisponibilidade)
                .model_dump(mode="json")
            )
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
            "message": (
                "Erro interno ao finalizar indisponibilidade."
            )
        }), 500


@indisponibilidades_bp.patch(
    "/<int:indisponibilidade_id>/cancelar"
)
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.CANCELAR")
def cancelar(indisponibilidade_id, **kwargs):

    tenant_session = kwargs["tenant_session"]

    try:
        indisponibilidade = cancelar_indisponibilidade(
            tenant_session,
            indisponibilidade_id
        )

        return jsonify({
            "success": True,
            "message": (
                "Indisponibilidade cancelada com sucesso."
            ),
            "indisponibilidade": (
                IndisponibilidadeRespostaSchema
                .model_validate(indisponibilidade)
                .model_dump(mode="json")
            )
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
            "message": (
                "Erro interno ao cancelar indisponibilidade."
            )
        }), 500