from config import Config

from database.session import criar_sessao_tenant
from services.seed_service import (
    criar_permissoes_padrao,
    criar_perfis_padrao,
)


DATABASE_NAME = "tenant_000002"


def main():
    print("=== PERMISSÕES ===")

    permissoes_criadas = criar_permissoes_padrao(
        config=Config,
        database_name=DATABASE_NAME
    )

    print(
        f"Permissões criadas nesta execução: "
        f"{len(permissoes_criadas)}"
    )

    print("\n=== PERFIS ===")

    perfis_criados = criar_perfis_padrao(
        config=Config,
        database_name=DATABASE_NAME
    )

    print(
        f"Perfis criados nesta execução: "
        f"{len(perfis_criados)}"
    )

    SessionLocal, _ = criar_sessao_tenant(
        Config,
        DATABASE_NAME
    )

    session = SessionLocal()

    try:
        from models.tenant.perfil import Perfil

        perfis = session.query(Perfil).order_by(
            Perfil.id
        ).all()

        print("\n=== PERFIS EXISTENTES ===")

        for perfil in perfis:
            print(
                f"\n{perfil.id} | "
                f"{perfil.nome} | "
                f"ativo={perfil.ativo}"
            )

            print(
                f"Permissões: "
                f"{len(perfil.permissoes)}"
            )

            for permissao in perfil.permissoes:
                print(
                    f"  - {permissao.codigo}"
                )

    finally:
        session.close()


if __name__ == "__main__":
    main()