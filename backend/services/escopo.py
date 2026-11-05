"""Autorização por objeto para sessões e contexto resolvidos pelo servidor."""
from sqlalchemy import false, true
from services.admin_policy import AdministracaoNegada, ContextoAdministrativo, ADMIN_CAPABILITIES, codigos
from services.matriz_acesso import ADMINISTRACAO, ATRIBUICAO, EMPRESA, MATRIZ, PROPRIO
from models.tenant.usuario import Usuario


def escopo_atual(session, contexto, acao):
    if not isinstance(contexto, ContextoAdministrativo) or session.get_bind().url.database != contexto.database_name:
        raise AdministracaoNegada('Contexto de acesso inválido.')
    ator = session.get(Usuario, contexto.usuario_id, populate_existing=True)
    if (ator is None or not ator.ativo or ator.session_version != contexto.session_version
            or ator.perfil is None or not ator.perfil.ativo):
        raise AdministracaoNegada('Ator ou sessão não está ativo.')
    permissoes = codigos(ator.perfil)
    if acao not in permissoes:
        raise AdministracaoNegada('Permissão insuficiente.')
    # Autoridade administrativa efetiva é baseada em capacidades, inclusive
    # perfis personalizados legados; jamais em nome, cargo ou payload.
    if acao in ADMINISTRACAO and ADMIN_CAPABILITIES <= permissoes:
        return EMPRESA
    escopo = MATRIZ.get(ator.perfil.politica_escopo, {}).get(acao)
    if escopo is None:
        raise AdministracaoNegada('Ação sem escopo autorizado.')
    return escopo


def filtro_acesso(session, contexto, acao, *, proprio=None, atribuicao=None):
    """Predicado SQL: colunas próprias e atribuições são escolhidas pelo serviço."""
    escopo = escopo_atual(session, contexto, acao)
    if escopo == EMPRESA:
        return true()
    if escopo == PROPRIO and proprio is not None:
        return proprio == contexto.usuario_id
    if escopo == ATRIBUICAO and atribuicao is not None:
        return atribuicao == contexto.usuario_id
    return false()


def consultar_autorizado(session, contexto, acao, consulta, *, proprio=None, atribuicao=None):
    """Use a mesma consulta com filtro de ID para detalhe e sem ID para lista."""
    return consulta.where(filtro_acesso(session, contexto, acao, proprio=proprio, atribuicao=atribuicao))
