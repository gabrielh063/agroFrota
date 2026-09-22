from config import Config

from services.permissao_service import criar_permissao


def main():
    database_name = "tenant_000002"

    print("Criando permissão...")

    permissao = criar_permissao(
        Config,
        database_name,
        "USUARIO_CRIAR",
        "Permite criar usuários."
    )

    print()
    print("Permissão criada com sucesso!")
    print("ID:", permissao.id)
    print("Código:", permissao.codigo)
    print("Descrição:", permissao.descricao)


if __name__ == "__main__":
    main()