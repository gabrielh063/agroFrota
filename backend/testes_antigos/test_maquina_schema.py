from config import Config

from database.tenant_schema import criar_schema_tenant


def main():

    database_name = "tenant_000002"

    print(
        f"Criando/verificando schema do tenant: "
        f"{database_name}"
    )

    criar_schema_tenant(
        Config,
        database_name
    )

    print("Schema atualizado com sucesso.")


if __name__ == "__main__":
    main()