from config import Config

from database.base import CentralBase
from database.central import criar_engine_central

from models.central.tenant import Tenant


def main():
    print("Criando conexão com banco central...")

    engine = criar_engine_central(Config)

    print("Criando tabelas centrais...")

    CentralBase.metadata.create_all(engine)

    print("Tabelas criadas com sucesso.")

    print(
        "Tabelas:",
        list(CentralBase.metadata.tables.keys())
    )

    engine.dispose()


if __name__ == "__main__":
    main()