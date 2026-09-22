from config import Config

from services.perfil_service import criar_perfil


def main():
    database_name = "tenant_000002"

    print("Criando perfil...")

    perfil = criar_perfil(
        Config,
        database_name,
        "GERENTE",
        "Acesso administrativo ao sistema."
    )

    print()
    print("Perfil criado com sucesso!")
    print("ID:", perfil.id)
    print("Nome:", perfil.nome)
    print("Descrição:", perfil.descricao)


if __name__ == "__main__":
    main()