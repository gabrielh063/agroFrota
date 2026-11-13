"""One-shot seed for the dedicated persistent deployment only."""
import json
import os
from pathlib import Path
import sys

from sqlalchemy import func, select

from config import Config
from database.session import criar_sessao_central, criar_sessao_tenant
from models.central.tenant import Tenant
from models.tenant.cargo import Cargo
from models.tenant.maquina import Maquina
from models.tenant.operacao_lock import OperacaoLock
from models.tenant.ordem_servico import OrdemServico
from models.tenant.perfil import Perfil
from models.tenant.usuario import Usuario
from services.matriz_acesso import MATRIZ
from services.seed_service import (
    criar_perfis_padrao,
    criar_permissoes_padrao,
    criar_usuario_gerente_padrao,
)
from utils.security import gerar_hash_senha


CENTRAL_DB = "agrofrota_central"
TENANT_DB = "agrofrota_tenant"
EXPECTED = {
    "admin_demo": ("Demonstração Gerente", "ADMIN_EMPRESA"),
    "diretoria_demo": ("Demonstração Diretoria", "DIRETORIA"),
    "gestor_frota_demo": ("Demonstração Gestor de Frota", "GESTOR_FROTA"),
    "administrativo_demo": ("Demonstração Administrativo", "ADMINISTRATIVO"),
    "manutencao_demo": ("Demonstração Manutenção", "MANUTENCAO"),
    "operador_demo": ("Demonstração Operador", "OPERADOR"),
    "auditor_demo": ("Demonstração Auditor", "AUDITOR"),
}


def load_credentials():
    filename = os.environ.get("DEMO_CREDENTIALS_FILE", "/run/secrets/demo_credentials")
    data = json.loads(Path(filename).read_text(encoding="utf-8"))
    if set(data) != set(EXPECTED) or any(not isinstance(data[name], str) or len(data[name]) < 32 for name in EXPECTED):
        raise RuntimeError("Arquivo de credenciais de demonstração inválido.")
    return data


def provision():
    if os.environ.get("AGROFROTA_ENV") != "production" or Config.DB_NAME != CENTRAL_DB:
        raise RuntimeError("Seed persistente recusado fora da instalação AgroFrota dedicada.")

    credentials = load_credentials()
    SessionCentral, central_engine = criar_sessao_central(Config)
    try:
        with SessionCentral.begin() as session:
            tenants = session.execute(select(Tenant)).scalars().all()
            if tenants:
                if len(tenants) == 1 and tenants[0].database_name == TENANT_DB:
                    raise RuntimeError("Tenant já existe; provisionamento não é repetível sobre dados existentes.")
                raise RuntimeError("Banco central contém tenants inesperados; seed recusado.")
            tenant = Tenant(nome="AgroFrota Demonstração", database_name=TENANT_DB, ativo=True)
            session.add(tenant)
    finally:
        central_engine.dispose()

    criar_permissoes_padrao(Config, TENANT_DB)
    criar_perfis_padrao(Config, TENANT_DB)
    criar_usuario_gerente_padrao(
        Config, TENANT_DB, EXPECTED["admin_demo"][0], "admin_demo",
        credentials["admin_demo"]
    )

    SessionTenant, tenant_engine = criar_sessao_tenant(Config, TENANT_DB)
    try:
        with SessionTenant.begin() as session:
            existing = session.scalar(select(func.count()).select_from(Usuario))
            if existing != 1:
                raise RuntimeError("Tenant não está no estado limpo esperado; seed interrompido.")
            profiles = {
                profile.nome: profile
                for profile in session.execute(select(Perfil)).scalars()
            }
            if set(MATRIZ) - set(profiles):
                raise RuntimeError("Perfis esperados ausentes após a migração/seed.")
            manager = session.execute(select(Usuario).where(Usuario.username == "admin_demo")).scalar_one()
            manager_cargo = session.get(Cargo, manager.cargo_id)
            if manager_cargo is None:
                raise RuntimeError("Cargo do gerente inicial ausente.")
            for username, (name, profile_name) in EXPECTED.items():
                if username == "admin_demo":
                    continue
                session.add(Usuario(
                    nome=name, username=username,
                    senha_hash=gerar_hash_senha(credentials[username]),
                    perfil_id=profiles[profile_name].id, ativo=True,
                ))
            machine = Maquina(
                identificacao="DEMO-TRATOR-01", modelo="Trator demonstração",
                fabricante="AgroFrota Acadêmico", ano=2024,
                localizacao="Talhão demonstrativo", status="OPERANDO",
                controla_telemetria=False, ativo=True,
            )
            session.add(machine)
            session.flush()
            users = {user.username: user for user in session.execute(select(Usuario)).scalars()}
            operation_lock = session.get(OperacaoLock, 1)
            if operation_lock is None:
                raise RuntimeError("Contador transacional de OS ausente.")
            for username, title in (
                ("manutencao_demo", "Revisão demonstrativa atribuída à Manutenção"),
                ("operador_demo", "Inspeção demonstrativa do Operador"),
            ):
                session.add(OrdemServico(
                    numero=operation_lock.proximo_numero_os,
                    tipo="MANUTENCAO", titulo=title,
                    descricao="Registro fictício para apresentação acadêmica.",
                    maquina_id=machine.id, operador_id=users[username].id,
                    responsavel_id=users[username].id, prioridade="MEDIA",
                    status="ABERTA", ativo=True,
                ))
                operation_lock.proximo_numero_os += 1
    finally:
        tenant_engine.dispose()

    print("Seed persistente concluído: tenant, sete perfis, máquina fictícia e duas OS demonstrativas.")
    print("As credenciais permanecem no arquivo local protegido do operador.")


if __name__ == "__main__":
    try:
        provision()
    except Exception as error:
        print(f"Provisionamento interrompido: {error}", file=sys.stderr)
        raise SystemExit(1)
