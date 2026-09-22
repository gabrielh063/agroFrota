from sqlalchemy import select

from database.tenant import criar_engine_tenant
from database.base import TenantBase

from models.tenant import (
    Cargo,
    Perfil,
    Permissao,
)

from database.session import criar_sessao_tenant


PERMISSOES_PADRAO = [
    (
        "DASHBOARD_VISUALIZAR",
        "Visualizar dashboard"
    ),

    (
        "MAQUINA_VISUALIZAR",
        "Visualizar máquinas"
    ),

    (
        "MAQUINA_CRIAR",
        "Cadastrar máquinas"
    ),

    (
        "MAQUINA_EDITAR",
        "Editar máquinas"
    ),

    (
        "EQUIPAMENTO_VISUALIZAR",
        "Visualizar equipamentos"
    ),

    (
        "EQUIPAMENTO_CRIAR",
        "Cadastrar equipamentos"
    ),

    (
        "EQUIPAMENTO_EDITAR",
        "Editar equipamentos"
    ),

    (
        "OS_VISUALIZAR",
        "Visualizar ordens de serviço"
    ),

    (
        "OS_CRIAR",
        "Criar ordens de serviço"
    ),

    (
        "OS_EDITAR",
        "Editar ordens de serviço"
    ),

    (
        "MANUTENCAO_VISUALIZAR",
        "Visualizar manutenções"
    ),

    (
        "MANUTENCAO_REGISTRAR",
        "Registrar manutenção"
    ),

    (
        "CALENDARIO_VISUALIZAR",
        "Visualizar calendário"
    ),

    (
        "CALENDARIO_CRIAR",
        "Criar agendamentos"
    ),
]


def criar_schema_tenant(config, database_name):

    engine = criar_engine_tenant(
        config,
        database_name
    )

    try:

        # Cria somente as tabelas pertencentes ao TenantBase
        TenantBase.metadata.create_all(engine)

        SessionLocal = criar_sessao_tenant(
            config,
            database_name
        )

        session = SessionLocal()

        try:

            # --------------------------------------------------
            # PERMISSÕES
            # --------------------------------------------------

            permissoes_db = []

            for codigo, descricao in PERMISSOES_PADRAO:

                permissao = session.scalar(
                    select(Permissao).where(
                        Permissao.codigo == codigo
                    )
                )

                if permissao is None:

                    permissao = Permissao(
                        codigo=codigo,
                        descricao=descricao
                    )

                    session.add(permissao)

                permissoes_db.append(permissao)

            session.flush()

            # --------------------------------------------------
            # PERFIS
            # --------------------------------------------------

            perfil_gerente = session.scalar(
                select(Perfil).where(
                    Perfil.nome == "GERENTE"
                )
            )

            if perfil_gerente is None:

                perfil_gerente = Perfil(
                    nome="GERENTE",
                    descricao="Administrador da fazenda",
                    permissoes=permissoes_db
                )

                session.add(perfil_gerente)

            # --------------------------------------------------

            perfil_manutencao = session.scalar(
                select(Perfil).where(
                    Perfil.nome == "MANUTENCAO"
                )
            )

            if perfil_manutencao is None:

                permissoes_manutencao = [
                    p
                    for p in permissoes_db
                    if p.codigo in [
                        "OS_VISUALIZAR",
                        "OS_CRIAR",
                        "OS_EDITAR",
                        "MANUTENCAO_VISUALIZAR",
                        "MANUTENCAO_REGISTRAR",
                        "CALENDARIO_VISUALIZAR",
                    ]
                ]

                perfil_manutencao = Perfil(
                    nome="MANUTENCAO",
                    descricao="Funcionário responsável pela manutenção",
                    permissoes=permissoes_manutencao
                )

                session.add(perfil_manutencao)

            # --------------------------------------------------

            perfil_operador = session.scalar(
                select(Perfil).where(
                    Perfil.nome == "OPERADOR"
                )
            )

            if perfil_operador is None:

                permissoes_operador = [
                    p
                    for p in permissoes_db
                    if p.codigo in [
                        "OS_VISUALIZAR",
                        "OS_CRIAR",
                        "MANUTENCAO_VISUALIZAR",
                        "MANUTENCAO_REGISTRAR",
                        "CALENDARIO_VISUALIZAR",
                    ]
                ]

                perfil_operador = Perfil(
                    nome="OPERADOR",
                    descricao="Operador de máquinas",
                    permissoes=permissoes_operador
                )

                session.add(perfil_operador)

            # --------------------------------------------------
            # CARGOS
            # --------------------------------------------------

            cargos_padrao = [
                (
                    "Gerente",
                    "Gerente da fazenda"
                ),

                (
                    "Supervisor de Manutenção",
                    "Supervisor da manutenção"
                ),

                (
                    "Mecânico",
                    "Profissional de manutenção"
                ),

                (
                    "Operador de Máquina",
                    "Operador de máquinas agrícolas"
                ),
            ]

            for nome, descricao in cargos_padrao:

                cargo = session.scalar(
                    select(Cargo).where(
                        Cargo.nome == nome
                    )
                )

                if cargo is None:

                    session.add(
                        Cargo(
                            nome=nome,
                            descricao=descricao
                        )
                    )

            session.commit()

        except Exception:

            session.rollback()
            raise

        finally:

            session.close()

    finally:

        engine.dispose()