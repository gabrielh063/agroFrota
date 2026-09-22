from config import Config

from services.cargo_service import criar_cargo


def main():
    database_name = "tenant_000002"

    print("Criando cargo...")

    cargo = criar_cargo(
        Config,
        database_name,
        "Gerente",
        "Responsável pela gestão da fazenda."
    )

    print()
    print("Cargo criado com sucesso!")
    print("ID:", cargo.id)
    print("Nome:", cargo.nome)
    print("Descrição:", cargo.descricao)


if __name__ == "__main__":
    main()