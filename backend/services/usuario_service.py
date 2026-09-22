from sqlalchemy import select

from database.session import criar_sessao_tenant

from models.tenant.usuario import Usuario

from utils.security import gerar_hash_senha


def criar_usuario(
    config,
    database_name: str,
    nome: str,
    username: str,
    senha: str,
    perfil_id: int,
    cargo_id: int | None = None,
    email: str | None = None
) -> Usuario:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        usuario_existente = session.execute(
            select(Usuario).where(
                Usuario.username == username
            )
        ).scalar_one_or_none()

        if usuario_existente is not None:
            raise ValueError(
                "Já existe um usuário com este username."
            )

        if email:
            email_existente = session.execute(
                select(Usuario).where(
                    Usuario.email == email
                )
            ).scalar_one_or_none()

            if email_existente is not None:
                raise ValueError(
                    "Já existe um usuário com este email."
                )

        usuario = Usuario(
            nome=nome,
            username=username,
            email=email,
            senha_hash=gerar_hash_senha(senha),
            cargo_id=cargo_id,
            perfil_id=perfil_id,
            ativo=True
        )

        session.add(usuario)
        session.commit()
        session.refresh(usuario)

        return usuario

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()