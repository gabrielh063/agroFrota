from database.base import TenantBase
from database.tenant import criar_engine_tenant

from models.tenant.usuario import Usuario
from models.tenant.cargo import Cargo
from models.tenant.perfil import Perfil
from models.tenant.permissao import Permissao
from models.tenant.maquina import Maquina
from models.tenant.equipamento import Equipamento  
from models.tenant.ordem_servico import OrdemServico
from models.tenant.agendamento import Agendamento
from models.tenant.manutencao import Manutencao
from models.tenant.indisponibilidade import Indisponibilidade


def criar_schema_tenant(config, database_name):
    engine = criar_engine_tenant(
        config,
        database_name
    )

    try:
        TenantBase.metadata.create_all(engine)
    finally:
        engine.dispose()