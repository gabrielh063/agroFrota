"""Assets are company-scoped for the seven standard policies."""
from sqlalchemy import select
from models.tenant.admin_lock import AdminLock
from services.admin_policy import AdministracaoNegada
from services.escopo import escopo_atual
from services.matriz_acesso import EMPRESA


def autorizar_ativo(session, contexto, acao, escrita=False):
    if escrita:
        # Same order as administrative revocation; hold through business commit.
        lock = session.scalar(select(AdminLock.id).where(AdminLock.id == 1).with_for_update())
        if lock is None:
            raise AdministracaoNegada('Controle administrativo indisponível.')
    if escopo_atual(session, contexto, acao) != EMPRESA:
        raise AdministracaoNegada('Escopo do ativo não autorizado.')
