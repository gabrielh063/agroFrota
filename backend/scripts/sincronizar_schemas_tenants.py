import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from sqlalchemy import select

from config import Config
from database.base import TenantBase
from database.session import criar_sessao_central
from database.tenant import criar_engine_tenant
from models.central.tenant import Tenant

# IMPORTANTE:
# carrega todos os models no metadata do TenantBase
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


def sincronizar_tenant(database_name):
    print()
    print("=" * 70)
    print(f"Sincronizando: {database_name}")
    print("=" * 70)

    engine = criar_engine_tenant(
        Config,
        database_name,
    )

    try:
        TenantBase.metadata.create_all(
            bind=engine,
            checkfirst=True,
        )

        print("✅ Schema sincronizado.")

    finally:
        engine.dispose()


def main():
    SessionCentral, _ = criar_sessao_central(
        Config
    )

    session = SessionCentral()

    try:
        tenants = session.execute(
            select(Tenant)
            .where(
                Tenant.ativo.is_(True)
            )
            .order_by(
                Tenant.id
            )
        ).scalars().all()

    finally:
        session.close()

    print(
        f"\nTenants encontrados: "
        f"{len(tenants)}"
    )

    for tenant in tenants:
        sincronizar_tenant(
            tenant.database_name
        )

    print()
    print("=" * 70)
    print("Sincronização concluída.")
    print("=" * 70)


if __name__ == "__main__":
    main()