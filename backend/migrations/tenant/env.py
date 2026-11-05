import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy import pool


# --------------------------------------------------
# CAMINHO DO BACKEND
# --------------------------------------------------

BACKEND_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(BACKEND_DIR)
    )


# --------------------------------------------------
# IMPORTS DO AGROFROTA
# --------------------------------------------------

from config import Config
from database.base import TenantBase


# --------------------------------------------------
# CARREGA TODOS OS MODELS TENANT
# --------------------------------------------------
#
# Esses imports são necessários para registrar
# todas as tabelas no TenantBase.metadata.
#

from models.tenant.admin_lock import AdminLock
from models.tenant.operacao_lock import OperacaoLock
from models.tenant.auditoria import EventoAuditoria
from models.tenant.usuario import Usuario
from models.tenant.cargo import Cargo
from models.tenant.perfil import Perfil
from models.tenant.permissao import Permissao
from models.tenant.maquina import Maquina
from models.tenant.equipamento import Equipamento
from models.tenant.ordem_servico import OrdemServico
from models.tenant.agendamento import Agendamento
from models.tenant.manutencao import Manutencao
from models.tenant.indisponibilidade import Indisponibilidade


# --------------------------------------------------
# CONFIGURAÇÃO ALEMBIC
# --------------------------------------------------

config = context.config

if config.config_file_name is not None:
    fileConfig(
        config.config_file_name
    )


target_metadata = TenantBase.metadata


# --------------------------------------------------
# BANCO TENANT
# --------------------------------------------------

def obter_database_name() -> str:

    database_name = os.getenv(
        "AGROFROTA_TENANT_DB"
    )

    if not database_name:
        raise RuntimeError(
            "Variável AGROFROTA_TENANT_DB "
            "não foi definida."
        )

    return database_name


def obter_database_url():

    database_name = (
        obter_database_name()
    )

    return URL.create(
        drivername="mysql+pymysql",
        username=Config.DB_USER,
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=database_name,
        query={
            "charset": "utf8mb4"
        },
    )


# --------------------------------------------------
# OFFLINE
# --------------------------------------------------

def run_migrations_offline() -> None:

    url = obter_database_url()

    context.configure(
        url=url.render_as_string(
            hide_password=False
        ),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# --------------------------------------------------
# ONLINE
# --------------------------------------------------

def run_migrations_online() -> None:

    connectable = create_engine(
        obter_database_url(),
        poolclass=pool.NullPool,
        future=True,
    )

    try:

        with connectable.connect() as connection:

            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
                compare_server_default=True,
            )

            with context.begin_transaction():
                context.run_migrations()

    finally:
        connectable.dispose()


# --------------------------------------------------
# EXECUÇÃO
# --------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
