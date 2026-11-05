from sqlalchemy import select
from models.tenant.operacao_lock import OperacaoLock


def bloquear_operacoes(session):
    """Acquire before any operational read; held until commit or rollback."""
    lock = session.execute(select(OperacaoLock).where(OperacaoLock.id == 1)
                           .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
    if lock is None:
        raise RuntimeError('Controle operacional indisponível; aplique as migrações.')
    return lock
