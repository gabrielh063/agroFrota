from flask import Blueprint, jsonify, request

from middleware.auth import autenticar
from middleware.tenant import resolver_tenant
from middleware.permissions import exigir_permissao

from config import Config

from schemas.equipamento import (
    EquipamentoCriarSchema,
    EquipamentoAtualizarSchema
)

from services.equipamento_service import (
    criar_equipamento,
    listar_equipamentos,
    atualizar_equipamento
)


equipamentos_bp = Blueprint(
    "equipamentos",
    __name__,
    url_prefix="/api/equipamentos"
)


@equipamentos_bp.get("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("EQUIPAMENTO_VISUALIZAR")
def listar_equipamentos_route(**kwargs):

    database_name = kwargs["database_name"]

    incluir_inativos_param = request.args.get(
        "incluir_inativos",
        "false"
    )

    incluir_inativos = (
        incluir_inativos_param
        .strip()
        .lower()
        in {
            "1",
            "true",
            "sim",
            "yes"
        }
    )

    equipamentos = listar_equipamentos(
        config=Config,
        database_name=database_name,
        incluir_inativos=incluir_inativos
    )

    return jsonify({
        "success": True,
        "data": [
            {
                "id": equipamento.id,
                "identificacao": equipamento.identificacao,
                "nome": equipamento.nome,
                "tipo": equipamento.tipo,
                "fabricante": equipamento.fabricante,
                "modelo": equipamento.modelo,
                "ano": equipamento.ano,
                "localizacao": equipamento.localizacao,
                "status": equipamento.status,
                "ativo": equipamento.ativo
            }
            for equipamento in equipamentos
        ]
    })

@equipamentos_bp.post("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("EQUIPAMENTO_CRIAR")
def criar_equipamento_route(**kwargs):

    database_name = kwargs["database_name"]

    dados = request.get_json(silent=True)

    if dados is None:
        return jsonify({
            "success": False,
            "message": "JSON inválido ou não informado."
        }), 400

    try:

        dados_validos = EquipamentoCriarSchema.model_validate(
            dados
        )

    except Exception as erro:

        return jsonify({
            "success": False,
            "message": "Dados inválidos.",
            "errors": str(erro)
        }), 400

    try:

        equipamento = criar_equipamento(
            config=Config,
            database_name=database_name,
            identificacao=dados_validos.identificacao,
            nome=dados_validos.nome,
            tipo=dados_validos.tipo,
            fabricante=dados_validos.fabricante,
            modelo=dados_validos.modelo,
            ano=dados_validos.ano,
            localizacao=dados_validos.localizacao,
            status=dados_validos.status
        )

    except ValueError as erro:

        return jsonify({
            "success": False,
            "message": str(erro)
        }), 400

    return jsonify({
        "success": True,
        "message": "Equipamento criado com sucesso.",
        "data": {
            "id": equipamento.id,
            "identificacao": equipamento.identificacao,
            "nome": equipamento.nome,
            "tipo": equipamento.tipo,
            "fabricante": equipamento.fabricante,
            "modelo": equipamento.modelo,
            "ano": equipamento.ano,
            "localizacao": equipamento.localizacao,
            "status": equipamento.status,
            "ativo": equipamento.ativo
        }
    }), 201
    
@equipamentos_bp.put("/<int:equipamento_id>")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("EQUIPAMENTO_EDITAR")
def atualizar_equipamento_route(
    equipamento_id,
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

        dados_validos = EquipamentoAtualizarSchema.model_validate(
            dados
        )

    except Exception as erro:

        return jsonify({
            "success": False,
            "message": "Dados inválidos.",
            "errors": str(erro)
        }), 400

    try:

        equipamento = atualizar_equipamento(
            config=Config,
            database_name=database_name,
            equipamento_id=equipamento_id,
            identificacao=dados_validos.identificacao,
            nome=dados_validos.nome,
            tipo=dados_validos.tipo,
            fabricante=dados_validos.fabricante,
            modelo=dados_validos.modelo,
            ano=dados_validos.ano,
            localizacao=dados_validos.localizacao,
            status=dados_validos.status,
            ativo=dados_validos.ativo
        )

    except ValueError as erro:

        if str(erro) == "Equipamento não encontrado.":

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
        "message": "Equipamento atualizado com sucesso.",
        "data": {
            "id": equipamento.id,
            "identificacao": equipamento.identificacao,
            "nome": equipamento.nome,
            "tipo": equipamento.tipo,
            "fabricante": equipamento.fabricante,
            "modelo": equipamento.modelo,
            "ano": equipamento.ano,
            "localizacao": equipamento.localizacao,
            "status": equipamento.status,
            "ativo": equipamento.ativo
        }
    })
    
@equipamentos_bp.patch("/<int:equipamento_id>/desativar")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("EQUIPAMENTO_DESATIVAR")
def desativar_equipamento_route(
    equipamento_id,
    **kwargs
):

    database_name = kwargs["database_name"]

    try:

        equipamento = atualizar_equipamento(
            config=Config,
            database_name=database_name,
            equipamento_id=equipamento_id,
            ativo=False
        )

    except ValueError as erro:

        if str(erro) == "Equipamento não encontrado.":

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
        "message": "Equipamento desativado com sucesso.",
        "data": {
            "id": equipamento.id,
            "identificacao": equipamento.identificacao,
            "ativo": equipamento.ativo
        }
    })
    
@equipamentos_bp.patch("/<int:equipamento_id>/ativar")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("EQUIPAMENTO_DESATIVAR")
def ativar_equipamento_route(
    equipamento_id,
    **kwargs
):

    database_name = kwargs["database_name"]

    try:

        equipamento = atualizar_equipamento(
            config=Config,
            database_name=database_name,
            equipamento_id=equipamento_id,
            ativo=True
        )

    except ValueError as erro:

        if str(erro) == "Equipamento não encontrado.":

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
        "message": "Equipamento ativado com sucesso.",
        "data": {
            "id": equipamento.id,
            "identificacao": equipamento.identificacao,
            "ativo": equipamento.ativo
        }
    })