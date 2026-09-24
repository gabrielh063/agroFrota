from flask import Blueprint, jsonify, request

from middleware.auth import autenticar
from middleware.tenant import resolver_tenant
from middleware.permissions import exigir_permissao

from config import Config

from schemas.maquina import MaquinaCriarSchema, MaquinaAtualizarSchema

from services.maquina_service import (
    criar_maquina,
    listar_maquinas,
    atualizar_maquina
)


maquinas_bp = Blueprint(
    "maquinas",
    __name__,
    url_prefix="/api/maquinas"
)


@maquinas_bp.get("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("MAQUINA_VISUALIZAR")
def listar_maquinas_route(**kwargs):

    database_name = kwargs["database_name"]

    incluir_inativas_param = request.args.get(
        "incluir_inativas",
        "false"
    )

    incluir_inativas = (
        incluir_inativas_param
        .strip()
        .lower()
        in {
            "1",
            "true",
            "sim",
            "yes"
        }
    )

    maquinas = listar_maquinas(
        config=Config,
        database_name=database_name,
        incluir_inativas=incluir_inativas
    )

    return jsonify({
        "success": True,
        "data": [
            {
                "id": maquina.id,
                "identificacao": maquina.identificacao,
                "modelo": maquina.modelo,
                "fabricante": maquina.fabricante,
                "ano": maquina.ano,
                "localizacao": maquina.localizacao,
                "status": maquina.status,
                "controla_telemetria":
                    maquina.controla_telemetria,
                "ativo": maquina.ativo
            }
            for maquina in maquinas
        ]
    })
    
@maquinas_bp.post("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("MAQUINA_CRIAR")
def criar_maquina_route(**kwargs):

    database_name = kwargs["database_name"]

    dados = request.get_json(silent=True)

    if dados is None:
        return jsonify({
            "success": False,
            "message": "JSON inválido ou não informado."
        }), 400

    try:

        dados_validos = MaquinaCriarSchema.model_validate(
            dados
        )

    except Exception as erro:

        return jsonify({
            "success": False,
            "message": "Dados inválidos.",
            "errors": str(erro)
        }), 400

    try:

        maquina = criar_maquina(
            config=Config,
            database_name=database_name,
            identificacao=dados_validos.identificacao,
            modelo=dados_validos.modelo,
            fabricante=dados_validos.fabricante,
            ano=dados_validos.ano,
            localizacao=dados_validos.localizacao,
            status=dados_validos.status,
            controla_telemetria=dados_validos.controla_telemetria
        )

    except ValueError as erro:

        return jsonify({
            "success": False,
            "message": str(erro)
        }), 400

    return jsonify({
        "success": True,
        "message": "Máquina criada com sucesso.",
        "data": {
            "id": maquina.id,
            "identificacao": maquina.identificacao,
            "modelo": maquina.modelo,
            "fabricante": maquina.fabricante,
            "ano": maquina.ano,
            "localizacao": maquina.localizacao,
            "status": maquina.status,
            "controla_telemetria": maquina.controla_telemetria,
            "ativo": maquina.ativo
        }
    }), 201
    
@maquinas_bp.put("/<int:maquina_id>")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("MAQUINA_EDITAR")
def atualizar_maquina_route(
    maquina_id,
    **kwargs
):

    database_name = kwargs["database_name"]

    dados = request.get_json(silent=True)

    if dados is None:
        return jsonify({
            "success": False,
            "message": "JSON inválido ou não informado."
        }), 400

    try:

        dados_validos = MaquinaAtualizarSchema.model_validate(
            dados
        )

    except Exception as erro:

        return jsonify({
            "success": False,
            "message": "Dados inválidos.",
            "errors": str(erro)
        }), 400

    try:

        maquina = atualizar_maquina(
            config=Config,
            database_name=database_name,
            maquina_id=maquina_id,
            identificacao=dados_validos.identificacao,
            modelo=dados_validos.modelo,
            fabricante=dados_validos.fabricante,
            ano=dados_validos.ano,
            localizacao=dados_validos.localizacao,
            status=dados_validos.status,
            controla_telemetria=dados_validos.controla_telemetria,
            ativo=dados_validos.ativo
        )

    except ValueError as erro:

        if str(erro) == "Máquina não encontrada.":

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
        "message": "Máquina atualizada com sucesso.",
        "data": {
            "id": maquina.id,
            "identificacao": maquina.identificacao,
            "modelo": maquina.modelo,
            "fabricante": maquina.fabricante,
            "ano": maquina.ano,
            "localizacao": maquina.localizacao,
            "status": maquina.status,
            "controla_telemetria": maquina.controla_telemetria,
            "ativo": maquina.ativo
        }
    })
    
@maquinas_bp.patch("/<int:maquina_id>/desativar")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("MAQUINA_DESATIVAR")
def desativar_maquina_route(
    maquina_id,
    **kwargs
):

    database_name = kwargs["database_name"]

    try:

        maquina = atualizar_maquina(
            config=Config,
            database_name=database_name,
            maquina_id=maquina_id,
            ativo=False
        )

    except ValueError as erro:

        if str(erro) == "Máquina não encontrada.":

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
        "message": "Máquina desativada com sucesso.",
        "data": {
            "id": maquina.id,
            "identificacao": maquina.identificacao,
            "ativo": maquina.ativo
        }
    })
    
@maquinas_bp.patch("/<int:maquina_id>/ativar")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("MAQUINA_DESATIVAR")
def ativar_maquina_route(
    maquina_id,
    **kwargs
):

    database_name = kwargs["database_name"]

    try:

        maquina = atualizar_maquina(
            config=Config,
            database_name=database_name,
            maquina_id=maquina_id,
            ativo=True
        )

    except ValueError as erro:

        if str(erro) == "Máquina não encontrada.":

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
        "message": "Máquina ativada com sucesso.",
        "data": {
            "id": maquina.id,
            "identificacao": maquina.identificacao,
            "ativo": maquina.ativo
        }
    })