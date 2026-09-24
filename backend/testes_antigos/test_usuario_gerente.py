from sqlalchemy import select

from config import Config
from database.session import criar_sessao_tenant
from models.tenant.usuario import Usuario
from services.seed_service import criar_usuario_gerente_padrao
from utils.security import verificar_senha


DATABASE_NAME = "tenant_000003"


def main():

    print("=== CRIANDO USUÁRIO GERENTE ===")

    usuario = criar_usuario_gerente_padrao(
        config=Config,
        database_name=DATABASE_NAME,
        nome="Administrador da Fazenda",
        username="admin",
        senha="Admin@123",
        email="admin@fazendateste.com"
    )

    print(f"ID: {usuario.id}")
    print(f"Nome: {usuario.nome}")
    print(f"Username: {usuario.username}")
    print(f"Email: {usuario.email}")
    print(f"Cargo ID: {usuario.cargo_id}")
    print(f"Perfil ID: {usuario.perfil_id}")
    print(f"Ativo: {usuario.ativo}")

    print("\n=== VALIDANDO SENHA ===")

    senha_valida = verificar_senha(
        "Admin@123",
        usuario.senha_hash
    )

    senha_invalida = verificar_senha(
        "senha_errada",
        usuario.senha_hash
    )

    print(f"Senha correta: {senha_valida}")
    print(f"Senha incorreta: {senha_invalida}")

    print("\n=== VALIDANDO BANCO ===")

    SessionLocal, _ = criar_sessao_tenant(
        Config,
        DATABASE_NAME
    )

    session = SessionLocal()

    try:

        usuario_banco = session.execute(
            select(Usuario).where(
                Usuario.username == "admin"
            )
        ).scalar_one_or_none()

        if usuario_banco is None:
            print("ERRO: usuário não encontrado no banco.")
            return

        print(
            f"Usuário encontrado no banco: "
            f"{usuario_banco.username}"
        )

        print("\n=== RESULTADO ===")

        if usuario_banco.perfil is None:
            print("ERRO: usuário sem perfil.")
            return

        if usuario_banco.perfil.nome != "GERENTE":
            print(
                "ERRO: perfil diferente de GERENTE."
            )
            return

        if usuario_banco.cargo is None:
            print("ERRO: usuário sem cargo.")
            return

        if usuario_banco.cargo.nome != "Gerente":
            print(
                "ERRO: cargo diferente de Gerente."
            )
            return

        if not senha_valida:
            print("ERRO: senha correta não foi validada.")
            return

        if senha_invalida:
            print("ERRO: senha incorreta foi aceita.")
            return

        print("SUCESSO!")
        print("Usuário gerente criado e validado.")

    finally:
        session.close()


if __name__ == "__main__":
    main()