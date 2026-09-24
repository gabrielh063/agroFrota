from config import Config
from services.tenant_service import criar_tenant


def main():
    print("Criando novo tenant...")

    tenant = criar_tenant(
        Config,
        "Fazenda Teste"
    )

    print()
    print("Tenant criado com sucesso!")
    print("ID:", tenant.id)
    print("Nome:", tenant.nome)
    print("Banco:", tenant.database_name)


if __name__ == "__main__":
    main()