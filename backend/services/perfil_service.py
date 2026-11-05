from services.admin_policy import autorizar, perfil_delegavel, preservar_administrador, AdministracaoNegada
from sqlalchemy import select

from database.session import criar_sessao_tenant

from models.tenant.perfil import Perfil


def criar_perfil(
    config,
    database_name: str,
    nome: str,
    descricao: str | None = None,
    contexto=None
) -> Perfil:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        autorizar(session, database_name, contexto, "PERFIL_CRIAR")
        perfil_existente = session.execute(
            select(Perfil).where(
                Perfil.nome == nome
            )
        ).scalar_one_or_none()

        if perfil_existente is not None:
            raise ValueError(
                "Já existe um perfil com este nome."
            )

        perfil = Perfil(
            nome=nome,
            descricao=descricao,
            ativo=True
        )

        session.add(perfil)
        session.commit()
        session.refresh(perfil)

        return perfil

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def buscar_perfil(
    config,
    database_name: str,
    perfil_id: int
) -> Perfil | None:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        perfil = session.execute(
            select(Perfil).where(
                Perfil.id == perfil_id
            )
        ).scalar_one_or_none()

        return perfil

    finally:
        session.close()


def atualizar_perfil(
    config,
    database_name: str,
    perfil_id: int,
    nome: str | None = None,
    descricao: str | None = None,
    ativo: bool | None = None,
    contexto=None
) -> Perfil:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        ator, permissoes = autorizar(session, database_name, contexto, "PERFIL_EDITAR")
        perfil = session.execute(
            select(Perfil).where(
                Perfil.id == perfil_id
            )
        ).scalar_one_or_none()

        if perfil is None:
            raise ValueError(
                "Perfil não encontrado."
            )

        perfil_delegavel(session, perfil_id, permissoes, ativo=False)
        if perfil.id == ator.perfil_id:
            raise AdministracaoNegada("Não é permitido alterar o próprio perfil.")

        if nome is not None:

            perfil_existente = session.execute(
                select(Perfil).where(
                    Perfil.nome == nome,
                    Perfil.id != perfil_id
                )
            ).scalar_one_or_none()

            if perfil_existente is not None:
                raise ValueError(
                    "Já existe um perfil com este nome."
                )

            perfil.nome = nome

        if descricao is not None:
            perfil.descricao = descricao

        if ativo is not None:
            perfil.ativo = ativo

        preservar_administrador(session)
        session.commit()
        session.refresh(perfil)

        return perfil

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def listar_perfis(
    config,
    database_name: str,
    incluir_inativos: bool = False
) -> list[Perfil]:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        consulta = select(Perfil).order_by(
            Perfil.id
        )

        if not incluir_inativos:
            consulta = consulta.where(
                Perfil.ativo.is_(True)
            )

        perfis = session.execute(
            consulta
        ).scalars().all()

        return perfis

    finally:
        session.close()
