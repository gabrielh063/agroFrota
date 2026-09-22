from sqlalchemy.orm import sessionmaker

from database.central import criar_engine_central
from database.tenant import criar_engine_tenant


def criar_sessao_central(config):
    engine = criar_engine_central(config)

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False
    )

    return SessionLocal, engine


def criar_sessao_tenant(config, database_name):
    engine = criar_engine_tenant(
        config,
        database_name
    )

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False
    )

    return SessionLocal, engine