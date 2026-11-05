from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from config import Config

from middleware.auth import autenticar
from middleware.tenant import resolver_tenant
from middleware.permissions import exigir_permissao

from schemas.permissao import (
    PermissaoCriarSchema,
    PermissaoAtualizarSchema,
    PermissaoRespostaSchema
)

from services.permissao_service import (
    criar_permissao,
    atualizar_permissao,
    listar_permissoes
)


permissoes_bp = Blueprint(
    "permissoes",
    __name__,
    url_prefix="/api/permissoes"
)


@permissoes_bp.get("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("PERFIL_PERMISSAO_GERENCIAR")
def listar_permissoes_route(**kwargs):

    database_name = kwargs["database_name"]

    permissoes = listar_permissoes(
        config=Config,
        database_name=database_name
    )

    return jsonify({
        "success": True,
        "data": [
            PermissaoRespostaSchema.model_validate(
                permissao
            ).model_dump()
            for permissao in permissoes
        ]
    })


@permissoes_bp.post("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("PERFIL_PERMISSAO_GERENCIAR")
def criar_permissao_route(**kwargs):

    database_name = kwargs["database_name"]

    try:

        dados = PermissaoCriarSchema.model_validate(
            request.get_json()
        )

    except ValidationError as erro:

        return jsonify({
            "success": False,
            "message": "Dados inválidos.",
            "errors": erro.errors(include_input=False, include_url=False)
        }), 400

    try:

        permissao = criar_permissao(
            config=Config,
            database_name=database_name,
            codigo=dados.codigo,
            descricao=dados.descricao
        )

    except ValueError as erro:

        return jsonify({
            "success": False,
            "message": str(erro)
        }), 400

    return jsonify({
        "success": True,
        "message": "Permissão criada com sucesso.",
        "data": PermissaoRespostaSchema.model_validate(
            permissao
        ).model_dump()
    }), 201


@permissoes_bp.put("/<int:permissao_id>")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("PERFIL_PERMISSAO_GERENCIAR")
def atualizar_permissao_route(
    permissao_id,
    **kwargs
):

    database_name = kwargs["database_name"]

    try:

        dados = PermissaoAtualizarSchema.model_validate(
            request.get_json()
        )

    except ValidationError as erro:

        return jsonify({
            "success": False,
            "message": "Dados inválidos.",
            "errors": erro.errors(include_input=False, include_url=False)
        }), 400

    try:

        permissao = atualizar_permissao(
            config=Config,
            database_name=database_name,
            permissao_id=permissao_id,
            codigo=dados.codigo,
            descricao=dados.descricao
        )

    except ValueError as erro:

        if str(erro) == "Permissão não encontrada.":

            return jsonify({
                "success": False,
                "message": str(erro)
            }), 404

        return jsonify({
            "success": False,
            "message": str(erro)
        }), 400

    return jsonify({
        "success": True,
        "message": "Permissão atualizada com sucesso.",
        "data": PermissaoRespostaSchema.model_validate(
            permissao
        ).model_dump()
    })