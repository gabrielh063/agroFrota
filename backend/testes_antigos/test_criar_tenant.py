from sqlalchemy import select

from config import Config
from database.session import criar_sessao_tenant
from models.tenant.usuario import Usuario
from models.tenant.perfil import Perfil
from models.tenant.permissao import Permissao

from services.tenant_service import criar_tenant


def main():

    print("=== CRIANDO TENANT COMPLETO ===")

    tenant = criar_tenant(
        config=Config,
        nome="Fazenda Teste Completa",
        nome_usuario="Administrador",
        username="admin",
        senha="Admin@123",
        email="admin@fazendacompleta.com"
    )

    print(f"Tenant ID: {tenant.id}")
    print(f"Nome: {tenant.nome}")
    print(f"Banco: {tenant.database_name}")

    print("\n=== VALIDANDO BANCO DO TENANT ===")

    SessionLocal, _ = criar_sessao_tenant(
        Config,
        tenant.database_name
    )

    session = SessionLocal()

    try:

        permissoes = session.execute(
            select(Permissao)
        ).scalars().all()

        perfis = session.execute(
            select(Perfil)
        ).scalars().all()

        usuarios = session.execute(
            select(Usuario)
        ).scalars().all()

        print(f"Permissões: {len(permissoes)}")
        print(f"Perfis: {len(perfis)}")
        print(f"Usuários: {len(usuarios)}")

        print("\n=== PERFIS ===")

        total_associacoes = 0

        for perfil in perfis:

            quantidade = len(perfil.permissoes)

            total_associacoes += quantidade

            print(
                f"{perfil.id} | "
                f"{perfil.nome} | "
                f"{quantidade} permissões"
            )

        print(
            f"\nTotal de associações: "
            f"{total_associacoes}"
        )

        print("\n=== USUÁRIOS ===")

        for usuario in usuarios:

            print(
                f"{usuario.id} | "
                f"{usuario.username} | "
                f"perfil={usuario.perfil.nome} | "
                f"cargo={usuario.cargo.nome if usuario.cargo else 'Nenhum'} | "
                f"ativo={usuario.ativo}"
            )

        print("\n=== RESULTADO ===")

        if len(permissoes) != 32:
            print("ERRO: deveriam existir 32 permissões.")
            return

        if len(perfis) != 3:
            print("ERRO: deveriam existir 3 perfis.")
            return

        if total_associacoes != 56:
            print("ERRO: deveriam existir 56 associações.")
            return

        if len(usuarios) != 1:
            print("ERRO: deveria existir 1 usuário inicial.")
            return

        usuario = usuarios[0]

        if usuario.username != "admin":
            print("ERRO: username incorreto.")
            return

        if usuario.perfil.nome != "GERENTE":
            print("ERRO: usuário não possui perfil GERENTE.")
            return

        if usuario.cargo is None:
            print("ERRO: usuário não possui cargo.")
            return

        if usuario.cargo.nome != "Gerente":
            print("ERRO: cargo incorreto.")
            return

        if not usuario.ativo:
            print("ERRO: usuário deveria estar ativo.")
            return

        print("SUCESSO!")
        print("Tenant criado completamente.")
        print("Seed + usuário gerente funcionando.")


    finally:
        session.close()


if __name__ == "__main__":
    main()