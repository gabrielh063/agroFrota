from sqlalchemy import select

from database.session import criar_sessao_tenant
from models.tenant.permissao import Permissao
from models.tenant.perfil import Perfil
from models.tenant.cargo import Cargo
from models.tenant.usuario import Usuario
from models.tenant.admin_lock import AdminLock
from utils.security import gerar_hash_senha

PERMISSOES_PADRAO = [
    {
        "codigo": "USUARIO_CRIAR",
        "descricao": "Permite criar usuários.",
    },
    {
        "codigo": "USUARIO_VISUALIZAR",
        "descricao": "Permite visualizar usuários.",
    },
    {
        "codigo": "USUARIO_EDITAR",
        "descricao": "Permite editar usuários.",
    },
    {
        "codigo": "USUARIO_DESATIVAR",
        "descricao": "Permite ativar ou desativar usuários.",
    },
    {
        "codigo": "CARGO_CRIAR",
        "descricao": "Permite criar cargos.",
    },
    {
        "codigo": "CARGO_VISUALIZAR",
        "descricao": "Permite visualizar cargos.",
    },
    {
        "codigo": "CARGO_EDITAR",
        "descricao": "Permite editar cargos.",
    },
    {
        "codigo": "PERFIL_CRIAR",
        "descricao": "Permite criar perfis.",
    },
    {
        "codigo": "PERFIL_VISUALIZAR",
        "descricao": "Permite visualizar perfis.",
    },
    {
        "codigo": "PERFIL_EDITAR",
        "descricao": "Permite editar perfis.",
    },
    {
        "codigo": "PERFIL_PERMISSAO_GERENCIAR",
        "descricao": "Permite associar e remover permissões de perfis.",
    },
    {
        "codigo": "MAQUINA_CRIAR",
        "descricao": "Permite cadastrar máquinas.",
    },
    {
        "codigo": "MAQUINA_VISUALIZAR",
        "descricao": "Permite visualizar máquinas.",
    },
    {
        "codigo": "MAQUINA_EDITAR",
        "descricao": "Permite editar máquinas.",
    },
    {
        "codigo": "MAQUINA_DESATIVAR",
        "descricao": "Permite ativar ou desativar máquinas.",
    },
    {
        "codigo": "EQUIPAMENTO_CRIAR",
        "descricao": "Permite cadastrar equipamentos.",
    },
    {
        "codigo": "EQUIPAMENTO_VISUALIZAR",
        "descricao": "Permite visualizar equipamentos.",
    },
    {
        "codigo": "EQUIPAMENTO_EDITAR",
        "descricao": "Permite editar equipamentos.",
    },
    {
        "codigo": "EQUIPAMENTO_DESATIVAR",
        "descricao": "Permite ativar ou desativar equipamentos.",
    },
    {
        "codigo": "OS.CRIAR",
        "descricao": "Permite criar novas ordens de serviço.",
    },
    {
        "codigo": "OS.VISUALIZAR",
        "descricao": "Permite visualizar ordens de serviço.",
    },
    {
        "codigo": "OS.EDITAR",
        "descricao": "Permite editar ordens de serviço.",
    },
    {
        "codigo": "OS.CANCELAR",
        "descricao": "Permite cancelar ordens de serviço.",
    },
    {
        "codigo": "OS.CONCLUIR",
        "descricao": "Permite concluir ordens de serviço.",
    },
    {
        "codigo": "MANUTENCAO.CRIAR",
        "descricao": "Permite registrar manutenções.",
    },
    {
        "codigo": "MANUTENCAO.VISUALIZAR",
        "descricao": "Permite visualizar manutenções.",
    },
    {
        "codigo": "MANUTENCAO.EDITAR",
        "descricao": "Permite editar registros de manutenção.",
    },
    {
        "codigo": "MANUTENCAO.CONCLUIR",
        "descricao": "Permite concluir manutenções.",
    },
    {
        "codigo": "MANUTENCAO.CANCELAR",
        "descricao": "Permite cancelar manutenções.",
    },
    {
        "codigo": "INDISPONIBILIDADE.CRIAR",
        "descricao": "Permite registrar indisponibilidades.",
    },
    {
        "codigo": "INDISPONIBILIDADE.VISUALIZAR",
        "descricao": "Permite visualizar indisponibilidades.",
    },
    {
        "codigo": "INDISPONIBILIDADE.EDITAR",
        "descricao": "Permite editar indisponibilidades.",
    },
    {
        "codigo": "DASHBOARD.VISUALIZAR",
        "descricao": "Permite visualizar o dashboard.",
    },
]

PERFIS_PADRAO = {
    "GERENTE": [
        "USUARIO_CRIAR",
        "USUARIO_VISUALIZAR",
        "USUARIO_EDITAR",
        "USUARIO_DESATIVAR",
        "CARGO_CRIAR",
        "CARGO_VISUALIZAR",
        "CARGO_EDITAR",
        "PERFIL_CRIAR",
        "PERFIL_VISUALIZAR",
        "PERFIL_EDITAR",
        "PERFIL_PERMISSAO_GERENCIAR",
        "MAQUINA_CRIAR",
        "MAQUINA_VISUALIZAR",
        "MAQUINA_EDITAR",
        "MAQUINA_DESATIVAR",
        "EQUIPAMENTO_CRIAR",
        "EQUIPAMENTO_VISUALIZAR",
        "EQUIPAMENTO_EDITAR",
        "EQUIPAMENTO_DESATIVAR",
        "OS.CRIAR",
        "OS.VISUALIZAR",
        "OS.EDITAR",
        "OS.CANCELAR",
        "OS.CONCLUIR",
        "MANUTENCAO.CRIAR",
        "MANUTENCAO.VISUALIZAR",
        "MANUTENCAO.CANCELAR",
        "MANUTENCAO.EDITAR",
        "MANUTENCAO.CONCLUIR",
        "INDISPONIBILIDADE.CRIAR",
        "INDISPONIBILIDADE.VISUALIZAR",
        "INDISPONIBILIDADE.EDITAR",
        "DASHBOARD.VISUALIZAR",
    ],

    "MANUTENCAO": [
        "USUARIO_VISUALIZAR",
        "MAQUINA_VISUALIZAR",
        "MAQUINA_EDITAR",
        "EQUIPAMENTO_VISUALIZAR",
        "EQUIPAMENTO_EDITAR",
        "OS.CRIAR",
        "OS.VISUALIZAR",
        "OS.EDITAR",
        "OS.CONCLUIR",
        "MANUTENCAO.CRIAR",
        "MANUTENCAO.VISUALIZAR",
        "MANUTENCAO.EDITAR",
        "MANUTENCAO.CONCLUIR",
        "MANUTENCAO.CANCELAR",
        "INDISPONIBILIDADE.CRIAR",
        "INDISPONIBILIDADE.VISUALIZAR",
        "INDISPONIBILIDADE.EDITAR",
        "DASHBOARD.VISUALIZAR",
    ],

    "OPERADOR": [
        "MAQUINA_VISUALIZAR",
        "EQUIPAMENTO_VISUALIZAR",
        "OS.CRIAR",
        "OS.VISUALIZAR",
        "MANUTENCAO.VISUALIZAR",
        "INDISPONIBILIDADE.CRIAR",
        "INDISPONIBILIDADE.VISUALIZAR",
    ],
}


def criar_permissoes_padrao(config, database_name):
    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        permissoes_criadas = []

        for dados in PERMISSOES_PADRAO:
            permissao_existente = session.execute(
                select(Permissao).where(
                    Permissao.codigo == dados["codigo"]
                )
            ).scalar_one_or_none()

            if permissao_existente is not None:
                continue

            permissao = Permissao(
                codigo=dados["codigo"],
                descricao=dados["descricao"]
            )

            session.add(permissao)
            permissoes_criadas.append(permissao)

        session.commit()

        return permissoes_criadas

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
        
def criar_perfis_padrao(config, database_name):
    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        perfis_criados = []

        for nome_perfil, codigos_permissoes in PERFIS_PADRAO.items():

            perfil = session.execute(
                select(Perfil).where(
                    Perfil.nome == nome_perfil
                )
            ).scalar_one_or_none()

            if perfil is None:
                perfil = Perfil(
                    nome=nome_perfil,
                    descricao=f"Perfil padrão de {nome_perfil.lower()}.",
                    ativo=True
                )

                session.add(perfil)
                session.flush()

                perfis_criados.append(perfil)

            else:
                # Existing profiles are tenant-owned; never silently grant permissions.
                continue

            codigos_existentes = {
                permissao.codigo
                for permissao in perfil.permissoes
            }

            permissoes = session.execute(
                select(Permissao).where(
                    Permissao.codigo.in_(codigos_permissoes)
                )
            ).scalars().all()

            for permissao in permissoes:
                if permissao.codigo not in codigos_existentes:
                    perfil.permissoes.append(permissao)

        session.commit()

        return perfis_criados

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
        
def criar_usuario_gerente_padrao(
    config,
    database_name: str,
    nome: str,
    username: str,
    senha: str,
    email: str | None = None
) -> Usuario:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        # This path is solely for first-user provisioning.
        session.execute(select(AdminLock.id).where(AdminLock.id == 1).with_for_update()).scalar_one()
        if session.execute(select(Usuario.id).limit(1)).first() is not None:
            raise ValueError("Provisionamento inicial exige empresa sem usuários.")
        perfil = session.execute(
            select(Perfil).where(
                Perfil.nome == "GERENTE"
            )
        ).scalar_one_or_none()

        if perfil is None:
            raise ValueError(
                "Perfil GERENTE não encontrado."
            )

        cargo = session.execute(
            select(Cargo).where(
                Cargo.nome == "Gerente"
            )
        ).scalar_one_or_none()

        if cargo is None:
            cargo = Cargo(
                nome="Gerente",
                descricao="Cargo padrão de gerente.",
                ativo=True
            )

            session.add(cargo)
            session.flush()

        # Provisioning is separate from authenticated administration and only
        # initializes an empty tenant; it cannot add further administrators.
        usuario = Usuario(nome=nome, username=username, email=email,
                          senha_hash=gerar_hash_senha(senha), perfil_id=perfil.id,
                          cargo_id=cargo.id, ativo=True)
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        session.close()
        return usuario

    except Exception:
        session.rollback()
        session.close()
        raise
