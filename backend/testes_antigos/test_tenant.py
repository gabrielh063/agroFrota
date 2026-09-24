from config import Config

from database.tenant_schema import criar_schema_tenant


def main():
    database_name = "tenant_000001"

    print(
        f"Criando schema do tenant: {database_name}"
    )

    criar_schema_tenant(
        Config,
        database_name
    )

    print("Schema criado com sucesso.")


if __name__ == "__main__":
    main()