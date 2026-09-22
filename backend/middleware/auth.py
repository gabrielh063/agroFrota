from functools import wraps

from flask import jsonify

from flask_jwt_extended import (
    get_jwt,
    verify_jwt_in_request
)


def autenticar():

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            try:
                verify_jwt_in_request()

                claims = get_jwt()

                usuario_id = claims.get("sub")
                tenant_id = claims.get("tenant_id")
                perfil_id = claims.get("perfil_id")

                if not usuario_id:
                    return jsonify({
                        "success": False,
                        "message": "Usuário não identificado."
                    }), 401

                if not tenant_id:
                    return jsonify({
                        "success": False,
                        "message": "Tenant não identificado."
                    }), 401

                if not perfil_id:
                    return jsonify({
                        "success": False,
                        "message": "Perfil não identificado."
                    }), 401

                kwargs["usuario_id"] = int(usuario_id)
                kwargs["tenant_id"] = int(tenant_id)
                kwargs["perfil_id"] = int(perfil_id)

                return func(*args, **kwargs)

            except Exception:
                return jsonify({
                    "success": False,
                    "message": "Token inválido ou expirado."
                }), 401

        return wrapper

    return decorator