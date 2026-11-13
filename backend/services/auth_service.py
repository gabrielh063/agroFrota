from datetime import datetime

from sqlalchemy import select

from database.session import criar_sessao_tenant

from models.tenant.usuario import Usuario
from models.tenant.perfil import Perfil

from utils.security import verificar_senha


def autenticar_usuario(
    config,
    database_name: str,
    username: str,
    senha: str
) -> Usuario:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        usuario = session.execute(
            select(Usuario).where(
                Usuario.username == username
            )
        ).scalar_one_or_none()

        if usuario is None:
            raise ValueError(
                "Usuário ou senha inválidos."
            )

        if not usuario.ativo:
            raise ValueError(
                "Usuário está inativo."
            )

        perfil_ativo = session.execute(
            select(Perfil.id).where(
                Perfil.id == usuario.perfil_id, Perfil.ativo.is_(True)
            )
        ).scalar_one_or_none()
        if perfil_ativo is None:
            raise ValueError("Perfil inativo ou inexistente.")

        if not verificar_senha(
            senha,
            usuario.senha_hash
        ):
            raise ValueError(
                "Usuário ou senha inválidos."
            )

        usuario.ultimo_login = datetime.utcnow()

        session.commit()

        session.refresh(usuario)

        return usuario

    except Exception:

        session.rollback()

        raise

    finally:

        session.close()
