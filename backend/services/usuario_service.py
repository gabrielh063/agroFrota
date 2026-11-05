from services.auditoria_service import registrar_evento
from services.admin_policy import autorizar, perfil_delegavel, preservar_administrador, AdministracaoNegada
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
    email: str | None = None,
    contexto=None
) -> Usuario:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        ator, permissoes = autorizar(session, database_name, contexto, "USUARIO_CRIAR")
        perfil_delegavel(session, perfil_id, permissoes)
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

        registrar_evento(session, contexto, "criar_usuario")
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
    usuario_id: int,
    contexto=None
) -> Usuario | None:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        from services.escopo import consultar_autorizado
        consulta = consultar_autorizado(session, contexto, "USUARIO_VISUALIZAR",
                                        select(Usuario).where(Usuario.id == usuario_id), proprio=Usuario.id)
        return session.execute(consulta).scalar_one_or_none()

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
    ativo: bool | None = None,
    contexto=None
) -> Usuario:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        ator, permissoes = autorizar(session, database_name, contexto, "USUARIO_DESATIVAR" if ativo is not None else "USUARIO_EDITAR")
        usuario = session.execute(
            select(Usuario).where(
                Usuario.id == usuario_id
            )
        ).scalar_one_or_none()

        if usuario is None:
            raise ValueError(
                "Usuário não encontrado."
            )

        perfil_delegavel(session, usuario.perfil_id, permissoes, ativo=False)
        if perfil_id is not None:
            if usuario.id == ator.id and perfil_id != usuario.perfil_id:
                raise AdministracaoNegada("Não é permitido alterar o próprio perfil.")
            perfil_delegavel(session, perfil_id, permissoes)

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

        if (perfil_id is not None and perfil_id != usuario.perfil_id) or (ativo is not None and ativo != usuario.ativo):
            session.execute(update(Usuario).where(Usuario.id == usuario.id)
                            .values(session_version=Usuario.session_version + 1))

        if perfil_id is not None:
            usuario.perfil_id = perfil_id

        if ativo is not None:
            usuario.ativo = ativo

        preservar_administrador(session)
        registrar_evento(session, contexto, "atualizar_usuario")
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
    apenas_ativos: bool = False,
    contexto=None
) -> list[Usuario]:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        from services.escopo import consultar_autorizado
        consulta = consultar_autorizado(session, contexto, "USUARIO_VISUALIZAR",
                                        select(Usuario).order_by(Usuario.id), proprio=Usuario.id)

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
    nova_senha: str,
    contexto=None
) -> Usuario:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        autorizar(session, database_name, contexto, "USUARIO_EDITAR")

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
        registrar_evento(session, contexto, "alterar_senha_usuario")
        session.commit()

        session.refresh(usuario)

        return usuario

    except Exception:

        session.rollback()

        raise

    finally:

        session.close()