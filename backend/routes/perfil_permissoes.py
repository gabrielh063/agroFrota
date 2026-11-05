from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from config import Config

from middleware.auth import autenticar
from middleware.tenant import resolver_tenant
from middleware.permissions import exigir_permissao

from schemas.perfil_permissao import (
    PerfilPermissaoSchema
)

from schemas.permissao import (
    PermissaoRespostaSchema
)

from services.perfil_permissao_service import (
    adicionar_permissao_perfil,
    remover_permissao_perfil,
    listar_permissoes_perfil
)


perfil_permissoes_bp = Blueprint(
    "perfil_permissoes",
    __name__,
    url_prefix="/api/perfis"
)


@perfil_permissoes_bp.get(
    "/<int:perfil_id>/permissoes"
)
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("PERFIL_PERMISSAO_GERENCIAR")
def listar_permissoes_perfil_route(
    perfil_id,
    **kwargs
):

    database_name = kwargs["database_name"]

    try:

        permissoes = listar_permissoes_perfil(
            config=Config,
            database_name=database_name,
            perfil_id=perfil_id
        )

    except ValueError as erro:

        return jsonify({
            "success": False,
            "message": str(erro)
        }), 404

    return jsonify({
        "success": True,
        "data": [
            PermissaoRespostaSchema.model_validate(
                permissao
            ).model_dump()
            for permissao in permissoes
        ]
    })


@perfil_permissoes_bp.post(
    "/<int:perfil_id>/permissoes"
)
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("PERFIL_PERMISSAO_GERENCIAR")
def adicionar_permissao_perfil_route(
    perfil_id,
    **kwargs
):

    database_name = kwargs["database_name"]

    try:

        dados = PerfilPermissaoSchema.model_validate(
            request.get_json()
        )

    except ValidationError as erro:

        return jsonify({
            "success": False,
            "message": "Dados inválidos.",
            "errors": erro.errors(include_input=False, include_url=False)
        }), 400

    try:

        perfil = adicionar_permissao_perfil(
            contexto=kwargs["contexto_administrativo"],
            config=Config,
            database_name=database_name,
            perfil_id=perfil_id,
            permissao_id=dados.permissao_id
        )

    except ValueError as erro:

        mensagem = str(erro)

        if mensagem in [
            "Perfil não encontrado.",
            "Permissão não encontrada."
        ]:

            return jsonify({
                "success": False,
                "message": mensagem
            }), 404

        return jsonify({
            "success": False,
            "message": mensagem
        }), 400

    return jsonify({
        "success": True,
        "message": "Permissão associada ao perfil com sucesso.",
        "data": {
            "perfil_id": perfil.id,
            "permissoes": [
                PermissaoRespostaSchema.model_validate(
                    permissao
                ).model_dump()
                for permissao in perfil.permissoes
            ]
        }
    }), 201


@perfil_permissoes_bp.delete(
    "/<int:perfil_id>/permissoes/<int:permissao_id>"
)
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("PERFIL_PERMISSAO_GERENCIAR")
def remover_permissao_perfil_route(
    perfil_id,
    permissao_id,
    **kwargs
):

    database_name = kwargs["database_name"]

    try:

        perfil = remover_permissao_perfil(
            contexto=kwargs["contexto_administrativo"],
            config=Config,
            database_name=database_name,
            perfil_id=perfil_id,
            permissao_id=permissao_id
        )

    except ValueError as erro:

        mensagem = str(erro)

        if mensagem in [
            "Perfil não encontrado.",
            "Permissão não encontrada."
        ]:

            return jsonify({
                "success": False,
                "message": mensagem
            }), 404

        return jsonify({
            "success": False,
            "message": mensagem
        }), 400

    return jsonify({
        "success": True,
        "message": "Permissão removida do perfil com sucesso.",
        "data": {
            "perfil_id": perfil.id,
            "permissoes": [
                PermissaoRespostaSchema.model_validate(
                    permissao
                ).model_dump()
                for permissao in perfil.permissoes
            ]
        }
    })