from config import Config

from database.central import criar_engine_central
from database.tenant import criar_engine_tenant


def main():
    print("=== TESTE DO BANCO CENTRAL ===")

    engine_central = criar_engine_central(Config)

    with engine_central.connect() as connection:
        resultado = connection.exec_driver_sql(
            "SHOW TABLES"
        )

        print("Tabelas do banco central:")

        for row in resultado:
            print("-", row[0])

    engine_central.dispose()

    print()
    print("=== TESTE DO BANCO TENANT ===")

    engine_tenant = criar_engine_tenant(
        Config,
        "tenant_000001"
    )

    with engine_tenant.connect() as connection:
        resultado = connection.exec_driver_sql(
            "SHOW TABLES"
        )

        print("Tabelas do tenant:")

        for row in resultado:
            print("-", row[0])

    engine_tenant.dispose()


if __name__ == "__main__":
    main()