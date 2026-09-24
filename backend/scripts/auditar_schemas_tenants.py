import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import inspect, select

from config import Config
from database.session import criar_sessao_central
from database.tenant import criar_engine_tenant
from models.central.tenant import Tenant


BANCO_REFERENCIA = "tenant_000005"


def obter_schema(database_name):
    engine = criar_engine_tenant(
        Config,
        database_name,
    )

    try:
        inspector = inspect(engine)

        schema = {}

        for tabela in sorted(
            inspector.get_table_names()
        ):
            colunas = {}

            for coluna in inspector.get_columns(
                tabela
            ):
                colunas[coluna["name"]] = {
                    "tipo": str(coluna["type"]),
                    "nullable": coluna["nullable"],
                    "default": str(
                        coluna.get("default")
                    ),
                }

            fks = []

            for fk in inspector.get_foreign_keys(
                tabela
            ):
                fks.append({
                    "colunas":
                        tuple(
                            fk.get(
                                "constrained_columns",
                                [],
                            )
                        ),
                    "tabela_referenciada":
                        fk.get("referred_table"),
                    "colunas_referenciadas":
                        tuple(
                            fk.get(
                                "referred_columns",
                                [],
                            )
                        ),
                })

            indices = []

            for indice in inspector.get_indexes(
                tabela
            ):
                indices.append({
                    "nome":
                        indice.get("name"),
                    "colunas":
                        tuple(
                            indice.get(
                                "column_names",
                                [],
                            )
                        ),
                    "unique":
                        indice.get(
                            "unique",
                            False,
                        ),
                })

            schema[tabela] = {
                "colunas": colunas,
                "fks": fks,
                "indices": indices,
            }

        return schema

    finally:
        engine.dispose()


def comparar_schemas(
    banco,
    referencia,
):
    atual = obter_schema(banco)

    tabelas_atual = set(
        atual.keys()
    )

    tabelas_referencia = set(
        referencia.keys()
    )

    faltando = (
        tabelas_referencia
        - tabelas_atual
    )

    extras = (
        tabelas_atual
        - tabelas_referencia
    )

    print()
    print("=" * 70)
    print(banco)
    print("=" * 70)

    print(
        "Tabelas:",
        len(tabelas_atual),
    )

    if faltando:
        print("\nTABELAS FALTANDO:")

        for tabela in sorted(faltando):
            print(
                "  -",
                tabela,
            )

    if extras:
        print("\nTABELAS EXTRAS:")

        for tabela in sorted(extras):
            print(
                "  -",
                tabela,
            )

    tabelas_comuns = (
        tabelas_atual
        & tabelas_referencia
    )

    encontrou_diferenca = (
        bool(faltando)
        or bool(extras)
    )

    for tabela in sorted(
        tabelas_comuns
    ):
        atual_tabela = atual[tabela]
        ref_tabela = referencia[tabela]

        colunas_atual = set(
            atual_tabela["colunas"].keys()
        )

        colunas_ref = set(
            ref_tabela["colunas"].keys()
        )

        colunas_faltando = (
            colunas_ref
            - colunas_atual
        )

        colunas_extras = (
            colunas_atual
            - colunas_ref
        )

        diferencas = []

        for coluna in sorted(
            colunas_atual & colunas_ref
        ):
            valor_atual = (
                atual_tabela["colunas"][
                    coluna
                ]
            )

            valor_ref = (
                ref_tabela["colunas"][
                    coluna
                ]
            )

            if valor_atual != valor_ref:
                diferencas.append(
                    (
                        coluna,
                        valor_atual,
                        valor_ref,
                    )
                )

        if (
            colunas_faltando
            or colunas_extras
            or diferencas
        ):
            encontrou_diferenca = True

            print(
                f"\nTABELA: {tabela}"
            )

            if colunas_faltando:
                print(
                    "  Colunas faltando:"
                )

                for coluna in sorted(
                    colunas_faltando
                ):
                    print(
                        "   -",
                        coluna,
                    )

            if colunas_extras:
                print(
                    "  Colunas extras:"
                )

                for coluna in sorted(
                    colunas_extras
                ):
                    print(
                        "   -",
                        coluna,
                    )

            for (
                coluna,
                valor_atual,
                valor_ref,
            ) in diferencas:
                print(
                    f"  Coluna diferente: "
                    f"{coluna}"
                )

                print(
                    "    atual:",
                    valor_atual,
                )

                print(
                    "    ref:  ",
                    valor_ref,
                )

    if not encontrou_diferenca:
        print(
            "\n✅ Estrutura compatível "
            "com o banco de referência."
        )


def main():
    SessionCentral, _ = (
        criar_sessao_central(
            Config
        )
    )

    session = SessionCentral()

    try:
        tenants = session.execute(
            select(Tenant)
            .where(
                Tenant.ativo.is_(True)
            )
            .order_by(
                Tenant.id
            )
        ).scalars().all()

    finally:
        session.close()

    print(
        "\nBanco de referência:",
        BANCO_REFERENCIA,
    )

    referencia = obter_schema(
        BANCO_REFERENCIA
    )

    print(
        "Tabelas de referência:",
        len(referencia),
    )

    for tenant in tenants:

        comparar_schemas(
            tenant.database_name,
            referencia,
        )


if __name__ == "__main__":
    main()