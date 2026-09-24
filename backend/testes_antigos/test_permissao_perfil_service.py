from config import Config

from services.perfil_permissao_service import (
    adicionar_permissao_perfil,
    remover_permissao_perfil,
    listar_permissoes_perfil,
)


DATABASE_NAME = "tenant_000002"

PERFIL_ID = 2
PERMISSAO_ID = 3


print("1. Testando perfil inexistente...")

try:

    adicionar_permissao_perfil(
        config=Config,
        database_name=DATABASE_NAME,
        perfil_id=9999,
        permissao_id=PERMISSAO_ID
    )

    print("ERRO: deveria ter rejeitado o perfil inexistente.")

except ValueError as erro:

    print(f"OK: {erro}")


print()
print("2. Testando permissão inexistente...")

try:

    adicionar_permissao_perfil(
        config=Config,
        database_name=DATABASE_NAME,
        perfil_id=PERFIL_ID,
        permissao_id=9999
    )

    print("ERRO: deveria ter rejeitado a permissão inexistente.")

except ValueError as erro:

    print(f"OK: {erro}")


print()
print("3. Testando remoção de permissão não associada...")

try:

    remover_permissao_perfil(
        config=Config,
        database_name=DATABASE_NAME,
        perfil_id=PERFIL_ID,
        permissao_id=3
    )

    print("ERRO: deveria ter rejeitado a remoção.")

except ValueError as erro:

    print(f"OK: {erro}")


print()
print("4. Confirmando permissões atuais do perfil...")

try:

    permissoes = listar_permissoes_perfil(
        config=Config,
        database_name=DATABASE_NAME,
        perfil_id=PERFIL_ID
    )

    print(
        f"Quantidade encontrada: {len(permissoes)}"
    )

    for permissao in permissoes:

        print(
            f"ID: {permissao.id} | "
            f"Código: {permissao.codigo} | "
            f"Descrição: {permissao.descricao}"
        )

except ValueError as erro:

    print(f"Erro: {erro}")