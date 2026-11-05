"""Tenant-local administrative authorization; callers supply server-resolved context."""
from dataclasses import dataclass
from sqlalchemy import select
from models.tenant.admin_lock import AdminLock
from models.tenant.perfil import Perfil
from models.tenant.usuario import Usuario

# The minimum capabilities needed to recover and manage tenant administration.
ADMIN_CAPABILITIES = frozenset({
    'USUARIO_CRIAR', 'USUARIO_EDITAR', 'USUARIO_DESATIVAR',
    'PERFIL_CRIAR', 'PERFIL_EDITAR', 'PERFIL_PERMISSAO_GERENCIAR',
})


class AdministracaoNegada(Exception):
    pass


@dataclass(frozen=True)
class ContextoAdministrativo:
    database_name: str
    usuario_id: int
    session_version: int


def codigos(perfil):
    return {p.codigo for p in perfil.permissoes}


def autorizar(session, database_name, contexto, permissao):
    if not isinstance(contexto, ContextoAdministrativo) or contexto.database_name != database_name:
        raise AdministracaoNegada('Contexto administrativo inválido.')
    # Must be the first read in this transaction: serialize all writers, across workers.
    lock = session.execute(select(AdminLock.id).where(AdminLock.id == 1).with_for_update()).scalar_one_or_none()
    if lock is None:
        raise AdministracaoNegada('Controle administrativo indisponível; aplique as migrações.')
    ator = session.get(Usuario, contexto.usuario_id)
    if (ator is None or not ator.ativo or ator.session_version != contexto.session_version
            or ator.perfil is None or not ator.perfil.ativo):
        raise AdministracaoNegada('Ator ou sessão não está ativo.')
    permissoes = codigos(ator.perfil)
    if not ADMIN_CAPABILITIES <= permissoes or permissao not in permissoes:
        raise AdministracaoNegada('Autoridade administrativa insuficiente.')
    return ator, permissoes


def perfil_delegavel(session, perfil_id, permissoes, *, ativo=True):
    perfil = session.get(Perfil, perfil_id)
    if perfil is None or (ativo and not perfil.ativo):
        raise AdministracaoNegada('Perfil inexistente ou inativo.')
    if not codigos(perfil) <= permissoes:
        raise AdministracaoNegada('Perfil excede a autoridade delegável.')
    return perfil


def preservar_administrador(session):
    session.flush()
    usuarios = session.execute(select(Usuario).where(Usuario.ativo.is_(True))).scalars().unique().all()
    if not any(u.perfil and u.perfil.ativo and ADMIN_CAPABILITIES <= codigos(u.perfil) for u in usuarios):
        raise AdministracaoNegada('A empresa deve manter um administrador ativo.')
