from config import Config

from services.permissao_service import (
    criar_permissao,
    buscar_permissao,
    atualizar_permissao,
    listar_permissoes
)


DATABASE_NAME = "tenant_000002"


print("\n1. Criando permissão...")

permissao = criar_permissao(
    config=Config,
    database_name=DATABASE_NAME,
    codigo="OS.CRIAR",
    descricao="Permite criar ordens de serviço."
)

print("Permissão criada com sucesso.")
print("ID:", permissao.id)
print("Código:", permissao.codigo)
print("Descrição:", permissao.descricao)


print("\n2. Buscando permissão...")

permissao_encontrada = buscar_permissao(
    config=Config,
    database_name=DATABASE_NAME,
    permissao_id=permissao.id
)

if permissao_encontrada is None:
    print("Permissão não encontrada.")
else:
    print("Permissão encontrada com sucesso.")
    print("ID:", permissao_encontrada.id)
    print("Código:", permissao_encontrada.codigo)
    print("Descrição:", permissao_encontrada.descricao)


print("\n3. Atualizando permissão...")

permissao_atualizada = atualizar_permissao(
    config=Config,
    database_name=DATABASE_NAME,
    permissao_id=permissao.id,
    descricao="Permite criar novas ordens de serviço."
)

print("Permissão atualizada com sucesso.")
print("ID:", permissao_atualizada.id)
print("Código:", permissao_atualizada.codigo)
print("Descrição:", permissao_atualizada.descricao)


print("\n4. Listando permissões...")

permissoes = listar_permissoes(
    config=Config,
    database_name=DATABASE_NAME
)

print("Quantidade encontrada:", len(permissoes))

for permissao in permissoes:
    print(
        "ID:", permissao.id,
        "| Código:", permissao.codigo,
        "| Descrição:", permissao.descricao
    )