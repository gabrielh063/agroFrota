from functools import wraps

from flask import jsonify

from sqlalchemy import select

from models.tenant.perfil import Perfil


def exigir_permissao(codigo_permissao: str):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            tenant_session = kwargs.get(
                "tenant_session"
            )

            perfil_id = kwargs.get(
                "usuario_perfil_id"
            )

            if tenant_session is None:
                return jsonify({
                    "success": False,
                    "message": "Sessão do tenant não encontrada."
                }), 500

            if perfil_id is None:
                return jsonify({
                    "success": False,
                    "message": "Perfil do usuário não identificado."
                }), 403

            perfil = tenant_session.execute(
                select(Perfil).where(
                    Perfil.id == perfil_id,
                    Perfil.ativo.is_(True)
                )
            ).scalar_one_or_none()

            if perfil is None:
                return jsonify({
                    "success": False,
                    "message": "Perfil não encontrado ou inativo."
                }), 403

            possui_permissao = any(
                permissao.codigo == codigo_permissao
                for permissao in perfil.permissoes
            )

            if not possui_permissao:
                return jsonify({
                    "success": False,
                    "message": (
                        "Usuário não possui a permissão "
                        f"'{codigo_permissao}'."
                    )
                }), 403

            return func(*args, **kwargs)

        return wrapper

    return decorator