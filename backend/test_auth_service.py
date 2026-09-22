from config import Config

from services.auth_service import autenticar_usuario


def main():
    database_name = "tenant_000002"

    print("Testando autenticação...")

    usuario = autenticar_usuario(
        config=Config,
        database_name=database_name,
        username="admin",
        senha="aadmin123"
    )

    print()
    print("Autenticação realizada com sucesso!")
    print("ID:", usuario.id)
    print("Nome:", usuario.nome)
    print("Username:", usuario.username)
    print("Perfil ID:", usuario.perfil_id)
    print("Cargo ID:", usuario.cargo_id)


if __name__ == "__main__":
    main()