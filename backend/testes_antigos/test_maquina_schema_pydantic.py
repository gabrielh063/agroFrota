from schemas.maquina import MaquinaCriarSchema


def main():

    maquina = MaquinaCriarSchema(
        identificacao="TR-001",
        modelo="6110J",
        fabricante="John Deere",
        ano=2022,
        localizacao="Pátio Norte"
    )

    print("Schema válido:")
    print(maquina.model_dump())


if __name__ == "__main__":
    main()
