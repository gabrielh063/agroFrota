from config import Config

from services.cargo_service import (
    criar_cargo,
    buscar_cargo,
    atualizar_cargo,
    listar_cargos
)


DATABASE_NAME = "tenant_000002"


print("\n1. Criando cargo...")

cargo = criar_cargo(
    config=Config,
    database_name=DATABASE_NAME,
    nome="Mecânico",
    descricao="Responsável pela manutenção das máquinas."
)

print("Cargo criado com sucesso.")
print("ID:", cargo.id)
print("Nome:", cargo.nome)
print("Descrição:", cargo.descricao)
print("Ativo:", cargo.ativo)


print("\n2. Buscando cargo...")

cargo_encontrado = buscar_cargo(
    config=Config,
    database_name=DATABASE_NAME,
    cargo_id=cargo.id
)

if cargo_encontrado is None:
    print("Cargo não encontrado.")
else:
    print("Cargo encontrado com sucesso.")
    print("ID:", cargo_encontrado.id)
    print("Nome:", cargo_encontrado.nome)
    print("Descrição:", cargo_encontrado.descricao)
    print("Ativo:", cargo_encontrado.ativo)


print("\n3. Atualizando cargo...")

cargo_atualizado = atualizar_cargo(
    config=Config,
    database_name=DATABASE_NAME,
    cargo_id=cargo.id,
    descricao="Responsável pela manutenção preventiva e corretiva."
)

print("Cargo atualizado com sucesso.")
print("ID:", cargo_atualizado.id)
print("Nome:", cargo_atualizado.nome)
print("Descrição:", cargo_atualizado.descricao)
print("Ativo:", cargo_atualizado.ativo)


print("\n4. Listando cargos...")

cargos = listar_cargos(
    config=Config,
    database_name=DATABASE_NAME
)

print("Quantidade encontrada:", len(cargos))

for cargo in cargos:
    print(
        "ID:", cargo.id,
        "| Nome:", cargo.nome,
        "| Descrição:", cargo.descricao,
        "| Ativo:", cargo.ativo
    )