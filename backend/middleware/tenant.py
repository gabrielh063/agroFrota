from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt
from sqlalchemy import select

from database.session import (
    criar_sessao_central,
    criar_sessao_tenant,
)
from models.central.tenant import Tenant
from models.tenant.usuario import Usuario
from models.tenant.perfil import Perfil


def resolver_tenant(config):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            tenant_session = None

            tenant_id = kwargs.get(
                "tenant_id"
            )

            usuario_id = kwargs.get(
                "usuario_autenticado_id"
            )

            # ------------------------------------------
            # DADOS OBRIGATÓRIOS VINDOS DO JWT
            # ------------------------------------------

            if tenant_id is None:
                return jsonify({
                    "success": False,
                    "message": "Tenant não identificado.",
                }), 401

            if usuario_id is None:
                return jsonify({
                    "success": False,
                    "message": "Usuário não identificado.",
                }), 401

            try:

                # --------------------------------------
                # BUSCA O TENANT NO BANCO CENTRAL
                # --------------------------------------

                SessionCentral, _ = (
                    criar_sessao_central(
                        config
                    )
                )

                central_session = (
                    SessionCentral()
                )

                try:
                    tenant = (
                        central_session.execute(
                            select(Tenant).where(
                                Tenant.id
                                == tenant_id
                            )
                        )
                        .scalar_one_or_none()
                    )

                finally:
                    central_session.close()

                # --------------------------------------
                # VALIDA TENANT
                # --------------------------------------

                if tenant is None:
                    return jsonify({
                        "success": False,
                        "message":
                            "Tenant não encontrado.",
                    }), 404

                if not tenant.ativo:
                    return jsonify({
                        "success": False,
                        "message":
                            "Tenant está inativo.",
                    }), 403

                # --------------------------------------
                # ABRE O BANCO DO TENANT
                # --------------------------------------

                SessionTenant, _ = (
                    criar_sessao_tenant(
                        config,
                        tenant.database_name,
                    )
                )

                tenant_session = (
                    SessionTenant()
                )

                # --------------------------------------
                # VALIDA O USUÁRIO ATUAL
                # --------------------------------------
                #
                # Não confia apenas no JWT.
                #
                # O usuário precisa:
                # - continuar existindo
                # - continuar ativo
                #
                # --------------------------------------

                usuario = (
                    tenant_session.execute(
                        select(Usuario).where(
                            Usuario.id
                            == usuario_id
                        )
                    )
                    .scalar_one_or_none()
                )

                if usuario is None:

                    tenant_session.close()
                    tenant_session = None

                    return jsonify({
                        "success": False,
                        "message":
                            "Usuário não encontrado.",
                    }), 401

                if not usuario.ativo:

                    tenant_session.close()
                    tenant_session = None

                    return jsonify({
                        "success": False,
                        "message":
                            "Usuário está inativo.",
                    }), 401

                versao = get_jwt().get("session_version")
                if type(versao) is not int or versao != usuario.session_version:
                    tenant_session.close()
                    tenant_session = None
                    return jsonify({"success": False, "message": "Sessão revogada."}), 401

                # --------------------------------------
                # PERFIL ATUAL DO USUÁRIO
                # --------------------------------------
                #
                # Ignora o perfil antigo presente
                # no JWT.
                #
                # Se o usuário era GERENTE quando
                # recebeu o token e depois virou
                # OPERADOR, usamos OPERADOR.
                #
                # --------------------------------------

                perfil_id_atual = (
                    usuario.perfil_id
                )

                if perfil_id_atual is None:

                    tenant_session.close()
                    tenant_session = None

                    return jsonify({
                        "success": False,
                        "message":
                            "Perfil do usuário "
                            "não identificado.",
                    }), 403

                perfil_ativo = tenant_session.execute(
                    select(Perfil.id).where(
                        Perfil.id == perfil_id_atual,
                        Perfil.ativo.is_(True),
                    )
                ).scalar_one_or_none()
                if perfil_ativo is None:
                    tenant_session.close()
                    tenant_session = None
                    return jsonify({"success": False, "message": "Perfil não encontrado ou inativo."}), 403

            except Exception as erro:

                if tenant_session is not None:

                    tenant_session.rollback()
                    tenant_session.close()

                    tenant_session = None

                # Do not expose connection details in logs.

                return jsonify({
                    "success": False,
                    "message":
                        "Não foi possível resolver "
                        "o tenant.",
                }), 500

            # ------------------------------------------
            # CONTEXTO DA REQUISIÇÃO
            # ------------------------------------------

            kwargs["tenant"] = tenant

            kwargs["database_name"] = (
                tenant.database_name
            )

            kwargs["tenant_session"] = (
                tenant_session
            )

            # IMPORTANTE:
            #
            # sobrescreve o perfil que veio do JWT
            # pelo perfil ATUAL salvo no banco.
            kwargs["usuario_perfil_id"] = (
                perfil_id_atual
            )

            # ------------------------------------------
            # EXECUTA A ROTA
            # ------------------------------------------

            try:
                return func(
                    *args,
                    **kwargs,
                )

            except Exception:

                tenant_session.rollback()

                raise

            finally:

                tenant_session.close()

        return wrapper

    return decorator
