from flask import Blueprint, jsonify, request
from sqlalchemy import select, update

from config import Config

from database.session import (
    criar_sessao_central,
)

from models.central.tenant import Tenant

from services.auth_service import (
    autenticar_usuario,
)

from middleware.auth import autenticar
from middleware.tenant import resolver_tenant
from models.tenant.usuario import Usuario

from services.token_service import (
    criar_token_usuario,
)


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


@auth_bp.post("/login")
def login():

    dados = request.get_json(
        silent=True
    )

    if not dados:

        return jsonify({
            "success": False,
            "message": (
                "Corpo da requisição inválido."
            )
        }), 400

    username = dados.get(
        "username"
    )

    senha = dados.get(
        "senha"
    )

    database_name = dados.get(
        "database_name"
    )

    if (
        not username
        or not senha
        or not database_name
    ):

        return jsonify({
            "success": False,
            "message": (
                "username, senha e database_name "
                "são obrigatórios."
            )
        }), 400

    try:

        # -------------------------------------------------
        # 1. VALIDAR TENANT NA BASE CENTRAL
        # -------------------------------------------------

        SessionCentral, _ = (
            criar_sessao_central(
                Config
            )
        )

        central_session = (
            SessionCentral()
        )

        try:

            tenant = (
                central_session.execute(
                    select(Tenant).where(
                        Tenant.database_name
                        == database_name,

                        Tenant.ativo.is_(True)
                    )
                )
                .scalar_one_or_none()
            )

        finally:

            central_session.close()

        # Não informamos se o tenant existe,
        # está inativo ou é inválido.
        if tenant is None:

            return jsonify({
                "success": False,
                "message": (
                    "Credenciais ou tenant "
                    "inválidos."
                )
            }), 401

        # -------------------------------------------------
        # 2. SOMENTE AGORA ABRIR O BANCO DO TENANT
        # -------------------------------------------------

        usuario = autenticar_usuario(
            config=Config,
            database_name=(
                tenant.database_name
            ),
            username=username,
            senha=senha
        )

        # -------------------------------------------------
        # 3. GERAR JWT
        # -------------------------------------------------

        token = criar_token_usuario(
            usuario_id=usuario.id,
            tenant_id=tenant.id,
            perfil_id=usuario.perfil_id,
            session_version=usuario.session_version
        )

        # -------------------------------------------------
        # 4. RESPOSTA
        # -------------------------------------------------

        return jsonify({
            "success": True,

            "message": (
                "Login realizado com sucesso."
            ),

            "data": {
                "access_token": token,

                "usuario": {
                    "id": usuario.id,
                    "nome": usuario.nome,
                    "username": usuario.username,
                    "email": usuario.email,
                    "perfil_id": (
                        usuario.perfil_id
                    ),
                    "cargo_id": (
                        usuario.cargo_id
                    )
                },

                "tenant": {
                    "id": tenant.id,
                    "nome": tenant.nome,
                    "database_name": (
                        tenant.database_name
                    )
                }
            }
        }), 200

    except ValueError:

        # Não revelamos se o problema foi
        # usuário, senha ou status do usuário.
        return jsonify({
            "success": False,
            "message": (
                "Credenciais ou tenant "
                "inválidos."
            )
        }), 401

    except Exception as erro:

        # Avoid logging connection details or credentials from exceptions.

        return jsonify({
            "success": False,
            "message": (
                "Erro interno ao realizar login."
            )
        }), 500

@auth_bp.post("/logout")
@autenticar()
@resolver_tenant(Config)
def logout(**kwargs):
    session = kwargs["tenant_session"]
    session.execute(
        update(Usuario).where(Usuario.id == kwargs["usuario_autenticado_id"])
        .values(session_version=Usuario.session_version + 1)
    )
    session.commit()
    return jsonify({"success": True, "message": "Sessões revogadas."}), 200


@auth_bp.get("/me")
@autenticar()
@resolver_tenant(Config)
def usuario_atual(**kwargs):
    usuario = kwargs["tenant_session"].get(Usuario, kwargs["usuario_autenticado_id"])
    return jsonify({
        "success": True,
        "data": {
            "usuario": {"id": usuario.id, "nome": usuario.nome,
                        "username": usuario.username, "email": usuario.email,
                        "perfil_id": usuario.perfil_id, "perfil_nome": usuario.perfil.nome,
                        "cargo_id": usuario.cargo_id},
            "tenant": {"id": kwargs["tenant"].id, "nome": kwargs["tenant"].nome},
            "permissoes": sorted(p.codigo for p in usuario.perfil.permissoes),
        },
    }), 200
