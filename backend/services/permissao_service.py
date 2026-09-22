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