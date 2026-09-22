from config import Config

from services.equipamento_service import (
    criar_equipamento,
    buscar_equipamento,
    atualizar_equipamento,
    listar_equipamentos
)


DATABASE_NAME = "tenant_000002"


print("\n1. Criando equipamento...\n")

equipamento = criar_equipamento(
    config=Config,
    database_name=DATABASE_NAME,
    identificacao="IMP-001",
    nome="Grade Niveladora",
    tipo="GRADE",
    fabricante="Baldan",
    modelo="GNV 36",
    ano=2023,
    localizacao="Galpão 2",
    status="DISPONIVEL"
)

print("Equipamento criado com sucesso.")
print(f"ID: {equipamento.id}")
print(f"Identificação: {equipamento.identificacao}")
print(f"Nome: {equipamento.nome}")
print(f"Tipo: {equipamento.tipo}")
print(f"Fabricante: {equipamento.fabricante}")
print(f"Modelo: {equipamento.modelo}")
print(f"Status: {equipamento.status}")
print(f"Ativo: {equipamento.ativo}")


print("\n2. Buscando equipamento...\n")

equipamento = buscar_equipamento(
    config=Config,
    database_name=DATABASE_NAME,
    equipamento_id=equipamento.id
)

if equipamento is None:
    print("Equipamento não encontrado.")
else:
    print("Equipamento encontrado com sucesso.")
    print(f"ID: {equipamento.id}")
    print(f"Identificação: {equipamento.identificacao}")
    print(f"Nome: {equipamento.nome}")
    print(f"Tipo: {equipamento.tipo}")
    print(f"Localização: {equipamento.localizacao}")
    print(f"Status: {equipamento.status}")


print("\n3. Atualizando equipamento...\n")

equipamento = atualizar_equipamento(
    config=Config,
    database_name=DATABASE_NAME,
    equipamento_id=equipamento.id,
    localizacao="Pátio Norte",
    status="EM_USO"
)

print("Equipamento atualizado com sucesso.")
print(f"ID: {equipamento.id}")
print(f"Identificação: {equipamento.identificacao}")
print(f"Nome: {equipamento.nome}")
print(f"Localização: {equipamento.localizacao}")
print(f"Status: {equipamento.status}")
print(f"Ativo: {equipamento.ativo}")


print("\n4. Listando equipamentos...\n")

equipamentos = listar_equipamentos(
    config=Config,
    database_name=DATABASE_NAME
)

print(f"Quantidade encontrada: {len(equipamentos)}")

for equipamento in equipamentos:
    print(
        f"ID: {equipamento.id} | "
        f"Identificação: {equipamento.identificacao} | "
        f"Nome: {equipamento.nome} | "
        f"Tipo: {equipamento.tipo} | "
        f"Status: {equipamento.status} | "
        f"Ativo: {equipamento.ativo}"
    )