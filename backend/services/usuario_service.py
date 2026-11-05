from sqlalchemy import select, update

from database.session import criar_sessao_tenant
from models.tenant.usuario import Usuario
from utils.security import gerar_hash_senha, verificar_senha


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


def buscar_usuario(
    config,
    database_name: str,
    usuario_id: int
) -> Usuario | None:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        usuario = session.execute(
            select(Usuario).where(
                Usuario.id == usuario_id
            )
        ).scalar_one_or_none()

        return usuario

    finally:

        session.close()


def atualizar_usuario(
    config,
    database_name: str,
    usuario_id: int,
    nome: str | None = None,
    username: str | None = None,
    email: str | None = None,
    cargo_id: int | None = None,
    perfil_id: int | None = None,
    ativo: bool | None = None
) -> Usuario:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        usuario = session.execute(
            select(Usuario).where(
                Usuario.id == usuario_id
            )
        ).scalar_one_or_none()

        if usuario is None:
            raise ValueError(
                "Usuário não encontrado."
            )

        if username is not None:

            outro_usuario = session.execute(
                select(Usuario).where(
                    Usuario.username == username,
                    Usuario.id != usuario_id
                )
            ).scalar_one_or_none()

            if outro_usuario is not None:
                raise ValueError(
                    "Já existe um usuário com este username."
                )

            usuario.username = username

        if email is not None:

            outro_usuario = session.execute(
                select(Usuario).where(
                    Usuario.email == email,
                    Usuario.id != usuario_id
                )
            ).scalar_one_or_none()

            if outro_usuario is not None:
                raise ValueError(
                    "Já existe um usuário com este email."
                )

            usuario.email = email

        if nome is not None:
            usuario.nome = nome

        if cargo_id is not None:
            usuario.cargo_id = cargo_id

        if perfil_id is not None:
            usuario.perfil_id = perfil_id

        if ativo is not None:
            usuario.ativo = ativo

        session.commit()

        session.refresh(usuario)

        return usuario

    except Exception:

        session.rollback()

        raise

    finally:

        session.close()


def listar_usuarios(
    config,
    database_name: str,
    apenas_ativos: bool = False
) -> list[Usuario]:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        consulta = select(Usuario).order_by(
            Usuario.id
        )

        if apenas_ativos:

            consulta = consulta.where(
                Usuario.ativo.is_(True)
            )

        usuarios = session.execute(
            consulta
        ).scalars().all()

        return list(usuarios)

    finally:

        session.close()
        
def alterar_senha_usuario(
    config,
    database_name: str,
    usuario_id: int,
    senha_atual: str,
    nova_senha: str
) -> Usuario:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        usuario = session.execute(
            select(Usuario).where(
                Usuario.id == usuario_id
            )
        ).scalar_one_or_none()

        if usuario is None:
            raise ValueError(
                "Usuário não encontrado."
            )

        if not verificar_senha(
            senha_atual,
            usuario.senha_hash
        ):
            raise ValueError(
                "Senha atual inválida."
            )

        usuario.senha_hash = gerar_hash_senha(
            nova_senha
        )
        session.execute(
            update(Usuario).where(Usuario.id == usuario_id)
            .values(session_version=Usuario.session_version + 1)
        )
        session.commit()

        session.refresh(usuario)

        return usuario

    except Exception:

        session.rollback()

        raise

    finally:

        session.close()