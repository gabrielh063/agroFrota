from functools import wraps

from flask import jsonify

from flask_jwt_extended import get_jwt

from sqlalchemy import select

from database.session import (
    criar_sessao_central,
    criar_sessao_tenant
)

from models.central.tenant import Tenant


def resolver_tenant(config):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            tenant_session = None

            try:

                # --------------------------------------------------
                # OBTÉM O TENANT A PARTIR DO JWT
                # --------------------------------------------------

                claims = get_jwt()

                tenant_id = claims.get("tenant_id")

                if not tenant_id:
                    return jsonify({
                        "success": False,
                        "message": "Tenant não identificado."
                    }), 401

                # --------------------------------------------------
                # CONSULTA O BANCO CENTRAL
                # --------------------------------------------------

                SessionCentral, _ = criar_sessao_central(
                    config
                )

                central_session = SessionCentral()

                try:

                    tenant = central_session.execute(
                        select(Tenant).where(
                            Tenant.id == int(tenant_id)
                        )
                    ).scalar_one_or_none()

                finally:

                    central_session.close()

                # --------------------------------------------------
                # VALIDA O TENANT
                # --------------------------------------------------

                if tenant is None:
                    return jsonify({
                        "success": False,
                        "message": "Tenant não encontrado."
                    }), 404

                if not tenant.ativo:
                    return jsonify({
                        "success": False,
                        "message": "Tenant está inativo."
                    }), 403

                # --------------------------------------------------
                # ABRE A SESSÃO DO TENANT
                # --------------------------------------------------

                SessionTenant, _ = criar_sessao_tenant(
                    config,
                    tenant.database_name
                )

                tenant_session = SessionTenant()

                # --------------------------------------------------
                # DISPONIBILIZA OS DADOS PARA A ROTA
                # --------------------------------------------------

                kwargs["tenant"] = tenant

                kwargs["database_name"] = (
                    tenant.database_name
                )

                kwargs["tenant_session"] = (
                    tenant_session
                )

                return func(
                    *args,
                    **kwargs
                )

            except Exception:

                if tenant_session is not None:
                    tenant_session.rollback()

                return jsonify({
                    "success": False,
                    "message": "Não foi possível resolver o tenant."
                }), 500

            finally:

                if tenant_session is not None:
                    tenant_session.close()

        return wrapper

    return decorator