from config import Config

from services.perfil_service import (
    adicionar_permissao_ao_perfil
)


def main():
    database_name = "tenant_000002"

    print("Vinculando permissão ao perfil...")

    perfil = adicionar_permissao_ao_perfil(
        Config,
        database_name,
        perfil_id=1,
        permissao_id=1
    )

    print()
    print("Permissão vinculada com sucesso!")
    print("Perfil:", perfil.nome)

    print("Permissões:")

    for permissao in perfil.permissoes:
        print(
            "-",
            permissao.codigo
        )


if __name__ == "__main__":
    main()