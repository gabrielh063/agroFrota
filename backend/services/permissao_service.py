from sqlalchemy import select

from database.session import criar_sessao_tenant

from models.tenant.permissao import Permissao


def criar_permissao(
    config,
    database_name: str,
    codigo: str,
    descricao: str | None = None
) -> Permissao:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        permissao_existente = session.execute(
            select(Permissao).where(
                Permissao.codigo == codigo
            )
        ).scalar_one_or_none()

        if permissao_existente is not None:
            raise ValueError(
                "Já existe uma permissão com este código."
            )

        permissao = Permissao(
            codigo=codigo,
            descricao=descricao
        )

        session.add(permissao)
        session.commit()
        session.refresh(permissao)

        return permissao

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def buscar_permissao(
    config,
    database_name: str,
    permissao_id: int
) -> Permissao | None:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        permissao = session.execute(
            select(Permissao).where(
                Permissao.id == permissao_id
            )
        ).scalar_one_or_none()

        return permissao

    finally:
        session.close()


def atualizar_permissao(
    config,
    database_name: str,
    permissao_id: int,
    codigo: str | None = None,
    descricao: str | None = None
) -> Permissao:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        permissao = session.execute(
            select(Permissao).where(
                Permissao.id == permissao_id
            )
        ).scalar_one_or_none()

        if permissao is None:
            raise ValueError(
                "Permissão não encontrada."
            )

        if codigo is not None:

            permissao_existente = session.execute(
                select(Permissao).where(
                    Permissao.codigo == codigo,
                    Permissao.id != permissao_id
                )
            ).scalar_one_or_none()

            if permissao_existente is not None:
                raise ValueError(
                    "Já existe uma permissão com este código."
                )

            permissao.codigo = codigo

        if descricao is not None:
            permissao.descricao = descricao

        session.commit()
        session.refresh(permissao)

        return permissao

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def listar_permissoes(
    config,
    database_name: str
) -> list[Permissao]:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        permissoes = session.execute(
            select(Permissao).order_by(
                Permissao.id
            )
        ).scalars().all()

        return permissoes

    finally:
        session.close()