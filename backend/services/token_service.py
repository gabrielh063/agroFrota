from flask_jwt_extended import create_access_token


def criar_token_usuario(
    usuario_id: int,
    tenant_id: int,
    perfil_id: int,
    session_version: int
) -> str:

    token = create_access_token(
        identity=str(usuario_id),
        additional_claims={
            "tenant_id": tenant_id,
            "perfil_id": perfil_id,
            "session_version": session_version
        }
    )

    return token