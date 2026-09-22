from sqlalchemy import select

from database.session import criar_sessao_tenant

from models.tenant.perfil import Perfil
from models.tenant.permissao import Permissao


def criar_perfil(
    config,
    database_name: str,
    nome: str,
    descricao: str | None = None
) -> Perfil:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
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


def adicionar_permissao_ao_perfil(
    config,
    database_name: str,
    perfil_id: int,
    permissao_id: int
) -> Perfil:

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

        if perfil is None:
            raise ValueError(
                "Perfil não encontrado."
            )

        permissao = session.execute(
            select(Permissao).where(
                Permissao.id == permissao_id
            )
        ).scalar_one_or_none()

        if permissao is None:
            raise ValueError(
                "Permissão não encontrada."
            )

        if permissao not in perfil.permissoes:
            perfil.permissoes.append(permissao)

        session.commit()
        session.refresh(perfil)

        return perfil

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()