from functools import wraps

from flask import jsonify
from flask_jwt_extended import (
    get_jwt,
    verify_jwt_in_request,
)


def autenticar():

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            # ------------------------------------------
            # VALIDA SOMENTE A AUTENTICAÇÃO
            # ------------------------------------------

            try:
                verify_jwt_in_request()

                claims = get_jwt()

                usuario_id = claims.get("sub")
                tenant_id = claims.get("tenant_id")
                perfil_id = claims.get("perfil_id")

                if usuario_id is None:
                    return jsonify({
                        "success": False,
                        "message": "Usuário não identificado.",
                    }), 401

                if tenant_id is None:
                    return jsonify({
                        "success": False,
                        "message": "Tenant não identificado.",
                    }), 401

                if perfil_id is None:
                    return jsonify({
                        "success": False,
                        "message": "Perfil não identificado.",
                    }), 401

                usuario_id = int(usuario_id)
                tenant_id = int(tenant_id)
                perfil_id = int(perfil_id)

                if usuario_id <= 0:
                    return jsonify({
                        "success": False,
                        "message": "Usuário não identificado.",
                    }), 401

                if tenant_id <= 0:
                    return jsonify({
                        "success": False,
                        "message": "Tenant não identificado.",
                    }), 401

                if perfil_id <= 0:
                    return jsonify({
                        "success": False,
                        "message": "Perfil não identificado.",
                    }), 401

            except Exception:
                return jsonify({
                    "success": False,
                    "message": "Token inválido ou expirado.",
                }), 401

            # ------------------------------------------
            # DADOS AUTENTICADOS
            # ------------------------------------------

            kwargs["usuario_autenticado_id"] = usuario_id
            kwargs["tenant_id"] = tenant_id
            kwargs["usuario_perfil_id"] = perfil_id

            # IMPORTANTE:
            # execução da rota fica FORA do try
            # de validação do JWT.
            return func(*args, **kwargs)

        return wrapper

    return decorator