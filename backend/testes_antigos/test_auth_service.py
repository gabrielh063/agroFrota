from config import Config
from services.auth_service import autenticar_usuario


DATABASE_NAME = "tenant_000004"


def main():

    print("=== TESTE DE LOGIN ===")

    print("\n1. Senha correta")

    usuario = autenticar_usuario(
        config=Config,
        database_name=DATABASE_NAME,
        username="admin",
        senha="Admin@123"
    )

    print(f"Usuário: {usuario.username}")
    print(f"Nome: {usuario.nome}")
    print(f"Perfil ID: {usuario.perfil_id}")
    print(f"Cargo ID: {usuario.cargo_id}")
    print(f"Ativo: {usuario.ativo}")

    print("\n2. Senha incorreta")

    try:

        autenticar_usuario(
            config=Config,
            database_name=DATABASE_NAME,
            username="admin",
            senha="senha_errada"
        )

        print("ERRO: senha incorreta foi aceita.")

    except ValueError as erro:

        print(f"Bloqueado corretamente: {erro}")

    print("\n3. Usuário inexistente")

    try:

        autenticar_usuario(
            config=Config,
            database_name=DATABASE_NAME,
            username="nao_existe",
            senha="Admin@123"
        )

        print("ERRO: usuário inexistente foi aceito.")

    except ValueError as erro:

        print(f"Bloqueado corretamente: {erro}")

    print("\n=== RESULTADO ===")
    print("SUCESSO! Serviço de autenticação funcionando.")


if __name__ == "__main__":
    main()