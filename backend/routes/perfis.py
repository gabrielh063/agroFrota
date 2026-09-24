from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from config import Config

from middleware.auth import autenticar
from middleware.tenant import resolver_tenant
from middleware.permissions import exigir_permissao

from schemas.perfil import (
    PerfilCriarSchema,
    PerfilAtualizarSchema,
    PerfilRespostaSchema
)

from services.perfil_service import (
    criar_perfil,
    atualizar_perfil,
    listar_perfis
)


perfis_bp = Blueprint(
    "perfis",
    __name__,
    url_prefix="/api/perfis"
)


@perfis_bp.get("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("PERFIL_VISUALIZAR")
def listar_perfis_route(**kwargs):

    database_name = kwargs["database_name"]

    incluir_inativos = (
        request.args.get(
            "incluir_inativos",
            "false"
        ).lower() == "true"
    )

    perfis = listar_perfis(
        config=Config,
        database_name=database_name,
        incluir_inativos=incluir_inativos
    )

    return jsonify({
        "success": True,
        "data": [
            PerfilRespostaSchema.model_validate(
                perfil
            ).model_dump()
            for perfil in perfis
        ]
    })


@perfis_bp.post("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("PERFIL_CRIAR")
def criar_perfil_route(**kwargs):

    database_name = kwargs["database_name"]

    try:

        dados = PerfilCriarSchema.model_validate(
            request.get_json()
        )

    except ValidationError as erro:

        return jsonify({
            "success": False,
            "message": "Dados inválidos.",
            "errors": erro.errors()
        }), 400

    try:

        perfil = criar_perfil(
            config=Config,
            database_name=database_name,
            nome=dados.nome,
            descricao=dados.descricao
        )

    except ValueError as erro:

        return jsonify({
            "success": False,
            "message": str(erro)
        }), 400

    return jsonify({
        "success": True,
        "message": "Perfil criado com sucesso.",
        "data": PerfilRespostaSchema.model_validate(
            perfil
        ).model_dump()
    }), 201


@perfis_bp.put("/<int:perfil_id>")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("PERFIL_EDITAR")
def atualizar_perfil_route(
    perfil_id,
    **kwargs
):

    database_name = kwargs["database_name"]

    try:

        dados = PerfilAtualizarSchema.model_validate(
            request.get_json()
        )

    except ValidationError as erro:

        return jsonify({
            "success": False,
            "message": "Dados inválidos.",
            "errors": erro.errors()
        }), 400

    try:

        perfil = atualizar_perfil(
            config=Config,
            database_name=database_name,
            perfil_id=perfil_id,
            nome=dados.nome,
            descricao=dados.descricao,
            ativo=dados.ativo
        )

    except ValueError as erro:

        if str(erro) == "Perfil não encontrado.":

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
        "message": "Perfil atualizado com sucesso.",
        "data": PerfilRespostaSchema.model_validate(
            perfil
        ).model_dump()
    })


@perfis_bp.patch("/<int:perfil_id>/desativar")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("PERFIL_DESATIVAR")
def desativar_perfil_route(
    perfil_id,
    **kwargs
):

    database_name = kwargs["database_name"]

    try:

        perfil = atualizar_perfil(
            config=Config,
            database_name=database_name,
            perfil_id=perfil_id,
            ativo=False
        )

    except ValueError as erro:

        return jsonify({
            "success": False,
            "message": str(erro)
        }), 404

    return jsonify({
        "success": True,
        "message": "Perfil desativado com sucesso.",
        "data": PerfilRespostaSchema.model_validate(
            perfil
        ).model_dump()
    })


@perfis_bp.patch("/<int:perfil_id>/ativar")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("PERFIL_ATIVAR")
def ativar_perfil_route(
    perfil_id,
    **kwargs
):

    database_name = kwargs["database_name"]

    try:

        perfil = atualizar_perfil(
            config=Config,
            database_name=database_name,
            perfil_id=perfil_id,
            ativo=True
        )

    except ValueError as erro:

        return jsonify({
            "success": False,
            "message": str(erro)
        }), 404

    return jsonify({
        "success": True,
        "message": "Perfil ativado com sucesso.",
        "data": PerfilRespostaSchema.model_validate(
            perfil
        ).model_dump()
    })