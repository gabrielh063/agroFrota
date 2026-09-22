from sqlalchemy import select

from database.session import criar_sessao_central
from database.create_database import criar_database_tenant
from database.tenant_schema import criar_schema_tenant

from models.central.tenant import Tenant


def criar_tenant(config, nome: str) -> Tenant:
    SessionLocal, _ = criar_sessao_central(config)

    session = SessionLocal()

    try:
        tenant = Tenant(
            nome=nome,
            database_name=""
        )

        session.add(tenant)
        session.flush()

        database_name = f"tenant_{tenant.id:06d}"

        tenant.database_name = database_name

        session.commit()

        tenant_id = tenant.id

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

    criar_database_tenant(
        config,
        database_name
    )

    criar_schema_tenant(
        config,
        database_name
    )

    SessionLocal, _ = criar_sessao_central(config)

    session = SessionLocal()

    try:
        tenant = session.execute(
            select(Tenant).where(
                Tenant.id == tenant_id
            )
        ).scalar_one()

        return tenant

    finally:
        session.close()