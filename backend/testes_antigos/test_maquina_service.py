from config import Config

from services.maquina_service import listar_maquinas


def main():

    print("Listando máquinas...")

    maquinas = listar_maquinas(
        config=Config,
        database_name="tenant_000002"
    )

    print()
    print(f"Quantidade encontrada: {len(maquinas)}")
    print()

    for maquina in maquinas:

        print(
            f"ID: {maquina.id} | "
            f"Identificação: {maquina.identificacao} | "
            f"Modelo: {maquina.modelo} | "
            f"Fabricante: {maquina.fabricante} | "
            f"Status: {maquina.status} | "
            f"Ativo: {maquina.ativo}"
        )


if __name__ == "__main__":
    main()