from sqlalchemy import select
from models.tenant.operacao_lock import OperacaoLock
from models.tenant.agendamento import Agendamento
from models.tenant.ordem_servico import OrdemServico


def bloquear_operacoes(session):
    """Acquire before any operational read; held until commit or rollback."""
    lock = session.execute(select(OperacaoLock).where(OperacaoLock.id == 1)
                           .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
    if lock is None:
        raise RuntimeError('Controle operacional indisponível; aplique as migrações.')
    return lock


def ha_agendamento_aberto(session, *, ordem_id=None, maquina_id=None, equipamento_id=None):
    consulta = (select(Agendamento.id)
                .join(OrdemServico, Agendamento.ordem_servico_id == OrdemServico.id)
                .where(Agendamento.status.in_(("AGENDADO", "EM_ANDAMENTO"))))
    if ordem_id is not None:
        consulta = consulta.where(OrdemServico.id == ordem_id)
    elif maquina_id is not None:
        consulta = consulta.where(OrdemServico.maquina_id == maquina_id)
    elif equipamento_id is not None:
        consulta = consulta.where(OrdemServico.equipamento_id == equipamento_id)
    else:
        raise ValueError("Informe a OS ou o recurso da consulta operacional.")
    return session.execute(consulta.limit(1)).first() is not None
