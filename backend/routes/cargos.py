from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from config import Config

from middleware.auth import autenticar
from middleware.tenant import resolver_tenant

from schemas.cargo import (
    CargoCriarSchema,
    CargoAtualizarSchema,
    CargoRespostaSchema
)

from services.cargo_service import (
    criar_cargo,
    atualizar_cargo,
    listar_cargos
)


cargos_bp = Blueprint(
    "cargos",
    __name__,
    url_prefix="/api/cargos"
)


@cargos_bp.get("/")
@autenticar()
@resolver_tenant(Config)
def listar_cargos_route(**kwargs):

    database_name = kwargs["database_name"]

    incluir_inativos = request.args.get(
        "incluir_inativos",
        "false"
    ).lower() == "true"

    cargos = listar_cargos(
        config=Config,
        database_name=database_name,
        incluir_inativos=incluir_inativos
    )

    return jsonify({
        "success": True,
        "data": [
            CargoRespostaSchema.model_validate(
                cargo
            ).model_dump()
            for cargo in cargos
        ]
    })


@cargos_bp.post("/")
@autenticar()
@resolver_tenant(Config)
def criar_cargo_route(**kwargs):

    database_name = kwargs["database_name"]

    try:

        dados = CargoCriarSchema.model_validate(
            request.get_json()
        )

    except ValidationError as erro:

        return jsonify({
            "success": False,
            "message": "Dados inválidos.",
            "errors": erro.errors()
        }), 400

    try:

        cargo = criar_cargo(
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
        "message": "Cargo criado com sucesso.",
        "data": CargoRespostaSchema.model_validate(
            cargo
        ).model_dump()
    }), 201


@cargos_bp.put("/<int:cargo_id>")
@autenticar()
@resolver_tenant(Config)
def atualizar_cargo_route(
    cargo_id,
    **kwargs
):

    database_name = kwargs["database_name"]

    try:

        dados = CargoAtualizarSchema.model_validate(
            request.get_json()
        )

    except ValidationError as erro:

        return jsonify({
            "success": False,
            "message": "Dados inválidos.",
            "errors": erro.errors()
        }), 400

    try:

        cargo = atualizar_cargo(
            config=Config,
            database_name=database_name,
            cargo_id=cargo_id,
            nome=dados.nome,
            descricao=dados.descricao,
            ativo=dados.ativo
        )

    except ValueError as erro:

        if str(erro) == "Cargo não encontrado.":

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
        "message": "Cargo atualizado com sucesso.",
        "data": CargoRespostaSchema.model_validate(
            cargo
        ).model_dump()
    })


@cargos_bp.patch("/<int:cargo_id>/desativar")
@autenticar()
@resolver_tenant(Config)
def desativar_cargo_route(
    cargo_id,
    **kwargs
):

    database_name = kwargs["database_name"]

    try:

        cargo = atualizar_cargo(
            config=Config,
            database_name=database_name,
            cargo_id=cargo_id,
            ativo=False
        )

    except ValueError as erro:

        if str(erro) == "Cargo não encontrado.":

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
        "message": "Cargo desativado com sucesso.",
        "data": {
            "id": cargo.id,
            "nome": cargo.nome,
            "ativo": cargo.ativo
        }
    })


@cargos_bp.patch("/<int:cargo_id>/ativar")
@autenticar()
@resolver_tenant(Config)
def ativar_cargo_route(
    cargo_id,
    **kwargs
):

    database_name = kwargs["database_name"]

    try:

        cargo = atualizar_cargo(
            config=Config,
            database_name=database_name,
            cargo_id=cargo_id,
            ativo=True
        )

    except ValueError as erro:

        if str(erro) == "Cargo não encontrado.":

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
        "message": "Cargo ativado com sucesso.",
        "data": {
            "id": cargo.id,
            "nome": cargo.nome,
            "ativo": cargo.ativo
        }
    })