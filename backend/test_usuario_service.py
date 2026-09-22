from config import Config

from services.usuario_service import criar_usuario


def main():
    database_name = "tenant_000002"

    print("Criando usuário administrador...")

    usuario = criar_usuario(
        config=Config,
        database_name=database_name,
        nome="Administrador",
        username="admin",
        senha="admin123",
        perfil_id=1,
        cargo_id=1,
        email="admin@fazendateste.com"
    )

    print()
    print("Usuário criado com sucesso!")
    print("ID:", usuario.id)
    print("Nome:", usuario.nome)
    print("Username:", usuario.username)
    print("Email:", usuario.email)
    print("Cargo ID:", usuario.cargo_id)
    print("Perfil ID:", usuario.perfil_id)
    print("Ativo:", usuario.ativo)


if __name__ == "__main__":
    main()