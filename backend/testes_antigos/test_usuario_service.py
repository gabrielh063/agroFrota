from config import Config
from database.session import criar_sessao_tenant
from models.tenant.usuario import Usuario

from services.usuario_service import (
    criar_usuario,
    buscar_usuario,
    atualizar_usuario,
    listar_usuarios,
)


DATABASE_NAME = "tenant_000004"


def main():

    print("=== 1. CRIAR USUÁRIO ===")

    usuario = criar_usuario(
        config=Config,
        database_name=DATABASE_NAME,
        nome="João da Silva",
        username="joao",
        senha="Joao@123",
        email="joao@fazenda.com",
        cargo_id=1,
        perfil_id=2
    )

    print(f"ID: {usuario.id}")
    print(f"Nome: {usuario.nome}")
    print(f"Username: {usuario.username}")
    print(f"Perfil: {usuario.perfil_id}")
    print(f"Cargo: {usuario.cargo_id}")
    print(f"Ativo: {usuario.ativo}")


    print("\n=== 2. BUSCAR USUÁRIO ===")

    usuario_encontrado = buscar_usuario(
        config=Config,
        database_name=DATABASE_NAME,
        usuario_id=usuario.id
    )

    if usuario_encontrado is None:
        print("ERRO: usuário não encontrado.")
        return

    print(
        f"Usuário encontrado: "
        f"{usuario_encontrado.username}"
    )


    print("\n=== 3. TESTAR DUPLICIDADE DE USERNAME ===")

    try:

        criar_usuario(
            config=Config,
            database_name=DATABASE_NAME,
            nome="Outro Usuário",
            username="joao",
            senha="Outra@123",
            email="outro@fazenda.com",
            cargo_id=1,
            perfil_id=2
        )

        print(
            "ERRO: username duplicado foi aceito."
        )

    except ValueError as erro:

        print(
            f"Bloqueado corretamente: {erro}"
        )


    print("\n=== 4. ATUALIZAR USUÁRIO ===")

    usuario_atualizado = atualizar_usuario(
        config=Config,
        database_name=DATABASE_NAME,
        usuario_id=usuario.id,
        nome="João da Silva Atualizado",
        email="joao.atualizado@fazenda.com"
    )

    print(
        f"Nome: {usuario_atualizado.nome}"
    )

    print(
        f"Email: {usuario_atualizado.email}"
    )


    print("\n=== 5. LISTAR USUÁRIOS ===")

    usuarios = listar_usuarios(
        config=Config,
        database_name=DATABASE_NAME
    )

    print(
        f"Total de usuários: {len(usuarios)}"
    )

    for usuario_item in usuarios:

        print(
            f"{usuario_item.id} | "
            f"{usuario_item.username} | "
            f"ativo={usuario_item.ativo}"
        )


    print("\n=== 6. DESATIVAR USUÁRIO ===")

    usuario_atualizado = atualizar_usuario(
        config=Config,
        database_name=DATABASE_NAME,
        usuario_id=usuario.id,
        ativo=False
    )

    print(
        f"Usuário ativo: "
        f"{usuario_atualizado.ativo}"
    )


    print("\n=== 7. LISTAR SOMENTE ATIVOS ===")

    usuarios_ativos = listar_usuarios(
        config=Config,
        database_name=DATABASE_NAME,
        apenas_ativos=True
    )

    print(
        f"Usuários ativos: "
        f"{len(usuarios_ativos)}"
    )


    print("\n=== RESULTADO ===")

    if usuario_atualizado.ativo:
        print(
            "ERRO: usuário deveria estar inativo."
        )
        return

    print(
        "SUCESSO! Usuario service funcionando."
    )


if __name__ == "__main__":
    main()