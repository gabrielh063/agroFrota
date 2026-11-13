from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from config import Config

from middleware.auth import autenticar
from middleware.tenant import resolver_tenant
from middleware.permissions import exigir_permissao

from schemas.usuario import (
    UsuarioCriarSchema,
    UsuarioAtualizarSchema,
    UsuarioRespostaSchema,
    UsuarioAlterarSenhaSchema
)

from services.usuario_service import (
    criar_usuario,
    buscar_usuario,
    atualizar_usuario,
    listar_usuarios,
    alterar_senha_usuario
)


usuarios_bp = Blueprint(
    "usuarios",
    __name__,
    url_prefix="/api/usuarios"
)


@usuarios_bp.get("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("USUARIO_VISUALIZAR")
def listar(**kwargs):
    database_name = kwargs["database_name"]

    apenas_ativos = request.args.get(
        "apenas_ativos",
        "false"
    ).lower() == "true"

    usuarios = listar_usuarios(
        config=Config,
        database_name=database_name,
        apenas_ativos=apenas_ativos,
        contexto=kwargs["contexto_administrativo"]
    )

    data = [
        UsuarioRespostaSchema.model_validate(usuario).model_dump()
        for usuario in usuarios
    ]

    return jsonify({
        "success": True,
        "data": data
    }), 200


@usuarios_bp.post("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("USUARIO_CRIAR")
def criar(**kwargs):
    database_name = kwargs["database_name"]

    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({
            "success": False,
            "message": "Corpo da requisição inválido."
        }), 400

    try:
        dados_validos = UsuarioCriarSchema.model_validate(dados)
    except ValidationError as erro:
        return jsonify({
            "success": False,
            "message": "Dados inválidos.",
            "errors": erro.errors(include_input=False, include_url=False)
        }), 400

    try:
        usuario = criar_usuario(
            contexto=kwargs["contexto_administrativo"],
            config=Config,
            database_name=database_name,
            nome=dados_validos.nome,
            username=dados_validos.username,
            senha=dados_validos.senha,
            email=dados_validos.email,
            cargo_id=dados_validos.cargo_id,
            perfil_id=dados_validos.perfil_id
        )

        data = UsuarioRespostaSchema.model_validate(
            usuario
        ).model_dump()

        return jsonify({
            "success": True,
            "message": "Usuário criado com sucesso.",
            "data": data
        }), 201

    except ValueError as erro:
        return jsonify({
            "success": False,
            "message": str(erro)
        }), 400


@usuarios_bp.get("/<int:usuario_id>")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("USUARIO_VISUALIZAR")
def buscar(usuario_id, **kwargs):
    print("Buscar usuário com ID:", usuario_id)
    database_name = kwargs["database_name"]

    usuario = buscar_usuario(
        config=Config,
        database_name=database_name,
        usuario_id=usuario_id,
        contexto=kwargs["contexto_administrativo"]
    )

    if usuario is None:
        return jsonify({
            "success": False,
            "message": "Usuário não encontrado."
        }), 404

    data = UsuarioRespostaSchema.model_validate(
        usuario
    ).model_dump()

    return jsonify({
        "success": True,
        "data": data
    }), 200


@usuarios_bp.put("/<int:usuario_id>")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("USUARIO_EDITAR")
def atualizar(usuario_id, **kwargs):
    database_name = kwargs["database_name"]

    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({
            "success": False,
            "message": "Corpo da requisição inválido."
        }), 400

    try:
        dados_validos = UsuarioAtualizarSchema.model_validate(dados)
    except ValidationError as erro:
        return jsonify({
            "success": False,
            "message": "Dados inválidos.",
            "errors": erro.errors(include_input=False, include_url=False)
        }), 400

    try:
        usuario = atualizar_usuario(
            contexto=kwargs["contexto_administrativo"],
            config=Config,
            database_name=database_name,
            usuario_id=usuario_id,
            nome=dados_validos.nome,
            username=dados_validos.username,
            email=dados_validos.email,
            cargo_id=dados_validos.cargo_id,
            perfil_id=dados_validos.perfil_id,
            ativo=dados_validos.ativo
        )

        data = UsuarioRespostaSchema.model_validate(
            usuario
        ).model_dump()

        return jsonify({
            "success": True,
            "message": "Usuário atualizado com sucesso.",
            "data": data
        }), 200

    except ValueError as erro:
        return jsonify({
            "success": False,
            "message": str(erro)
        }), 400


@usuarios_bp.patch("/<int:usuario_id>/desativar")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("USUARIO_DESATIVAR")
def desativar(usuario_id, **kwargs):
    database_name = kwargs["database_name"]

    try:
        usuario = atualizar_usuario(
            contexto=kwargs["contexto_administrativo"],
            config=Config,
            database_name=database_name,
            usuario_id=usuario_id,
            ativo=False
        )

        data = UsuarioRespostaSchema.model_validate(
            usuario
        ).model_dump()

        return jsonify({
            "success": True,
            "message": "Usuário desativado com sucesso.",
            "data": data
        }), 200

    except ValueError as erro:
        return jsonify({
            "success": False,
            "message": str(erro)
        }), 404


@usuarios_bp.patch("/<int:usuario_id>/ativar")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("USUARIO_DESATIVAR")
def ativar(usuario_id, **kwargs):
    database_name = kwargs["database_name"]

    try:
        usuario = atualizar_usuario(
            contexto=kwargs["contexto_administrativo"],
            config=Config,
            database_name=database_name,
            usuario_id=usuario_id,
            ativo=True
        )

        data = UsuarioRespostaSchema.model_validate(
            usuario
        ).model_dump()

        return jsonify({
            "success": True,
            "message": "Usuário ativado com sucesso.",
            "data": data
        }), 200

    except ValueError as erro:
        return jsonify({
            "success": False,
            "message": str(erro)
        }), 404
        
@usuarios_bp.put("/<int:usuario_id>/senha")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("USUARIO_EDITAR")
def alterar_senha(usuario_id, **kwargs):

    database_name = kwargs["database_name"]

    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({
            "success": False,
            "message": "Corpo da requisição inválido."
        }), 400

    try:

        dados_validos = UsuarioAlterarSenhaSchema.model_validate(
            dados
        )

    except ValidationError as erro:

        return jsonify({
            "success": False,
            "message": "Dados inválidos.",
            "errors": erro.errors(include_input=False, include_url=False)
        }), 400

    try:

        usuario = alterar_senha_usuario(
            config=Config,
            database_name=database_name,
            usuario_id=usuario_id,
            senha_atual=dados_validos.senha_atual,
            nova_senha=dados_validos.nova_senha,
            contexto=kwargs["contexto_administrativo"]
        )

        data = UsuarioRespostaSchema.model_validate(
            usuario
        ).model_dump()

        return jsonify({
            "success": True,
            "message": "Senha alterada com sucesso.",
            "data": data
        }), 200

    except ValueError as erro:

        return jsonify({
            "success": False,
            "message": str(erro)
        }), 400