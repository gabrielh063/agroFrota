from sqlalchemy import select

from database.session import criar_sessao_tenant

from models.tenant.cargo import Cargo


def criar_cargo(
    config,
    database_name: str,
    nome: str,
    descricao: str | None = None
) -> Cargo:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        cargo_existente = session.execute(
            select(Cargo).where(
                Cargo.nome == nome
            )
        ).scalar_one_or_none()

        if cargo_existente is not None:
            raise ValueError(
                "Já existe um cargo com este nome."
            )

        cargo = Cargo(
            nome=nome,
            descricao=descricao,
            ativo=True
        )

        session.add(cargo)
        session.commit()
        session.refresh(cargo)

        return cargo

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()