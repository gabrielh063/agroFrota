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


def buscar_cargo(
    config,
    database_name: str,
    cargo_id: int
) -> Cargo | None:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        cargo = session.execute(
            select(Cargo).where(
                Cargo.id == cargo_id
            )
        ).scalar_one_or_none()

        return cargo

    finally:
        session.close()


def atualizar_cargo(
    config,
    database_name: str,
    cargo_id: int,
    nome: str | None = None,
    descricao: str | None = None,
    ativo: bool | None = None
) -> Cargo:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        cargo = session.execute(
            select(Cargo).where(
                Cargo.id == cargo_id
            )
        ).scalar_one_or_none()

        if cargo is None:
            raise ValueError(
                "Cargo não encontrado."
            )

        if nome is not None:

            cargo_existente = session.execute(
                select(Cargo).where(
                    Cargo.nome == nome,
                    Cargo.id != cargo_id
                )
            ).scalar_one_or_none()

            if cargo_existente is not None:
                raise ValueError(
                    "Já existe um cargo com este nome."
                )

            cargo.nome = nome

        if descricao is not None:
            cargo.descricao = descricao

        if ativo is not None:
            cargo.ativo = ativo

        session.commit()
        session.refresh(cargo)

        return cargo

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def listar_cargos(
    config,
    database_name: str,
    incluir_inativos: bool = False
) -> list[Cargo]:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        consulta = select(Cargo).order_by(
            Cargo.id
        )

        if not incluir_inativos:
            consulta = consulta.where(
                Cargo.ativo.is_(True)
            )

        cargos = session.execute(
            consulta
        ).scalars().all()

        return cargos

    finally:
        session.close()