from sqlalchemy import select

from database.session import criar_sessao_central
from database.create_database import criar_database_tenant
from database.tenant_schema import criar_schema_tenant

from models.central.tenant import Tenant

from services.seed_service import (
    criar_permissoes_padrao,
    criar_perfis_padrao,
    criar_usuario_gerente_padrao,
)


def criar_tenant(
    config,
    nome: str,
    nome_usuario: str,
    username: str,
    senha: str,
    email: str | None = None
) -> Tenant:

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

    criar_permissoes_padrao(
        config,
        database_name
    )

    criar_perfis_padrao(
        config,
        database_name
    )

    criar_usuario_gerente_padrao(
        config=config,
        database_name=database_name,
        nome=nome_usuario,
        username=username,
        senha=senha,
        email=email
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