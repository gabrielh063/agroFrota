from app import create_app
from config import Config

from services.auth_service import autenticar_usuario
from services.token_service import criar_token_usuario


def main():

    app = create_app()

    with app.app_context():

        database_name = "tenant_000002"

        print("Autenticando usuário...")

        usuario = autenticar_usuario(
            config=Config,
            database_name=database_name,
            username="admin",
            senha="admin123"
        )

        print("Usuário autenticado.")

        token = criar_token_usuario(
            usuario_id=usuario.id,
            tenant_id=2,
            perfil_id=usuario.perfil_id
        )

        print()

        print("JWT criado com sucesso!")

        print()

        print(token)


if __name__ == "__main__":
    main()