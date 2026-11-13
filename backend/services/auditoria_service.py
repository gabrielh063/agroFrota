from sqlalchemy import select
from models.tenant.auditoria import EventoAuditoria
from services.admin_policy import AdministracaoNegada, ContextoAdministrativo
from services.escopo import escopo_atual
from services.matriz_acesso import EMPRESA


def registrar_evento(session, contexto, operacao):
    if (not isinstance(contexto, ContextoAdministrativo)
            or session.get_bind().url.database != contexto.database_name):
        raise AdministracaoNegada('Contexto de auditoria inválido.')
    # Caller has authorized the operation in this transaction. No separate commit.
    session.add(EventoAuditoria(ator_id=contexto.usuario_id, operacao=operacao))


def listar_eventos(session, contexto, limite=100, offset=0):
    if escopo_atual(session, contexto, 'AUDITORIA.VISUALIZAR') != EMPRESA:
        raise AdministracaoNegada('Leitura da auditoria não autorizada.')
    if not 1 <= limite <= 200 or offset < 0:
        raise ValueError('Paginação inválida.')
    return session.scalars(select(EventoAuditoria).order_by(EventoAuditoria.id.desc())
                           .limit(limite).offset(offset)).all()
