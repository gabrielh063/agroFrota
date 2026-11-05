from sqlalchemy import select
from models.tenant.admin_lock import AdminLock
from models.tenant.usuario import Usuario
from models.tenant.ordem_servico import OrdemServico
from services.admin_policy import AdministracaoNegada
from services.escopo import consultar_autorizado, escopo_atual
from services.operacao_lock import bloquear_operacoes


def iniciar_escrita(session):
    if session.scalar(select(AdminLock.id).where(AdminLock.id == 1).with_for_update()) is None:
        raise AdministracaoNegada('Controle administrativo indisponível.')
    bloquear_operacoes(session)


def consulta_os(session, contexto, acao, consulta):
    # escopo_atual validates context before any actor dereference.
    escopo_atual(session, contexto, acao)
    ator = session.get(Usuario, contexto.usuario_id)
    coluna = (OrdemServico.operador_id if ator.perfil.politica_escopo == 'OPERADOR'
              else OrdemServico.responsavel_id)
    return consultar_autorizado(session, contexto, acao, consulta, atribuicao=coluna)


def autorizar_criacao(session, contexto, maquina_id, equipamento_id, operador_id, responsavel_id):
    if escopo_atual(session, contexto, 'OS.CRIAR') == 'empresa':
        return
    # A current assigned OS is the persisted source of the operator's resource
    # assignment. Supplying the actor ID in the new payload is never sufficient.
    recurso = (OrdemServico.maquina_id == maquina_id if maquina_id is not None
               else OrdemServico.equipamento_id == equipamento_id)
    vinculo = session.scalar(select(OrdemServico.id).where(
        recurso, OrdemServico.operador_id == contexto.usuario_id,
        OrdemServico.ativo.is_(True), OrdemServico.status.in_(['ABERTA', 'EM_ANDAMENTO'])).limit(1))
    if vinculo is None or operador_id != contexto.usuario_id or responsavel_id is not None:
        raise AdministracaoNegada('Recurso sem atribuição operacional autorizada.')
