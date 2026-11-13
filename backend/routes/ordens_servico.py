from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from config import Config
from middleware.auth import autenticar
from middleware.tenant import resolver_tenant
from middleware.permissions import exigir_permissao

from schemas.ordem_servico import (
    OrdemServicoCriarSchema,
    OrdemServicoAtualizarSchema,
    OrdemServicoRespostaSchema,
)

from services.ordem_servico_service import (
    criar_ordem_servico,
    buscar_ordem_servico,
    listar_ordens_servico,
    atualizar_ordem_servico,
    concluir_ordem_servico,
    cancelar_ordem_servico,
)


ordens_servico_bp = Blueprint(
    "ordens_servico",
    __name__,
    url_prefix="/api/ordens-servico"
)


@ordens_servico_bp.post("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.CRIAR")
def criar(**kwargs):
    try:
        dados = OrdemServicoCriarSchema(
            **request.get_json()
        )

        ordem = criar_ordem_servico(
            config=Config,
        contexto=kwargs["contexto_administrativo"],
            database_name=kwargs["database_name"],
            **dados.model_dump()
        )

        return jsonify({
            "sucesso": True,
            "ordem_servico": OrdemServicoRespostaSchema.model_validate(
                ordem
            ).model_dump(mode="json")
        }), 201

    except ValidationError as erro:
        return jsonify({
            "sucesso": False,
            "erro": "Dados inválidos.",
            "detalhes": erro.errors(
                include_context=False
            )
        }), 400

    except ValueError as erro:
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 400


@ordens_servico_bp.get("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.VISUALIZAR")
def listar(**kwargs):
    apenas_ativas = request.args.get(
        "apenas_ativas",
        "false"
    ).lower() == "true"

    ordens = listar_ordens_servico(
        config=Config,
        contexto=kwargs["contexto_administrativo"],
        database_name=kwargs["database_name"],
        apenas_ativas=apenas_ativas
    )

    return jsonify({
        "sucesso": True,
        "quantidade": len(ordens),
        "ordens_servico": [
            OrdemServicoRespostaSchema.model_validate(
                ordem
            ).model_dump(mode="json")
            for ordem in ordens
        ]
    }), 200


@ordens_servico_bp.get("/<int:ordem_servico_id>")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.VISUALIZAR")
def buscar(ordem_servico_id, **kwargs):
    ordem = buscar_ordem_servico(
        config=Config,
        contexto=kwargs["contexto_administrativo"],
        database_name=kwargs["database_name"],
        ordem_servico_id=ordem_servico_id
    )

    if ordem is None:
        return jsonify({
            "sucesso": False,
            "erro": "Ordem de serviço não encontrada."
        }), 404

    return jsonify({
        "sucesso": True,
        "ordem_servico": OrdemServicoRespostaSchema.model_validate(
            ordem
        ).model_dump(mode="json")
    }), 200


@ordens_servico_bp.put("/<int:ordem_servico_id>")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.EDITAR")
def atualizar(ordem_servico_id, **kwargs):
    try:
        dados = OrdemServicoAtualizarSchema(
            **request.get_json()
        )

        ordem = atualizar_ordem_servico(
            config=Config,
        contexto=kwargs["contexto_administrativo"],
            database_name=kwargs["database_name"],
            ordem_servico_id=ordem_servico_id,
            **dados.model_dump(exclude_unset=True)
        )

        return jsonify({
            "sucesso": True,
            "ordem_servico": OrdemServicoRespostaSchema.model_validate(
                ordem
            ).model_dump(mode="json")
        }), 200

    except ValidationError as erro:
        return jsonify({
            "sucesso": False,
            "erro": "Dados inválidos.",
            "detalhes": erro.errors(
                include_context=False
            )
        }), 400

    except ValueError as erro:
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 400


@ordens_servico_bp.patch("/<int:ordem_servico_id>/concluir")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.CONCLUIR")
def concluir(ordem_servico_id, **kwargs):
    try:
        ordem = concluir_ordem_servico(
            config=Config,
        contexto=kwargs["contexto_administrativo"],
            database_name=kwargs["database_name"],
            ordem_servico_id=ordem_servico_id
        )

        return jsonify({
            "sucesso": True,
            "mensagem": "Ordem de serviço concluída.",
            "ordem_servico": OrdemServicoRespostaSchema.model_validate(
                ordem
            ).model_dump(mode="json")
        }), 200

    except ValueError as erro:
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 400


@ordens_servico_bp.patch("/<int:ordem_servico_id>/cancelar")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.CANCELAR")
def cancelar(ordem_servico_id, **kwargs):
    try:
        ordem = cancelar_ordem_servico(
            config=Config,
        contexto=kwargs["contexto_administrativo"],
            database_name=kwargs["database_name"],
            ordem_servico_id=ordem_servico_id
        )

        return jsonify({
            "sucesso": True,
            "mensagem": "Ordem de serviço cancelada.",
            "ordem_servico": OrdemServicoRespostaSchema.model_validate(
                ordem
            ).model_dump(mode="json")
        }), 200

    except ValueError as erro:
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 400