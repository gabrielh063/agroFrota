from datetime import datetime

from sqlalchemy import or_, select

from models.tenant.agendamento import Agendamento
from models.tenant.ordem_servico import OrdemServico
from models.tenant.usuario import Usuario
from models.tenant.maquina import Maquina
from models.tenant.equipamento import Equipamento
from models.tenant.indisponibilidade import Indisponibilidade


STATUS_AGENDAMENTO = {
    "AGENDADO",
    "EM_ANDAMENTO",
    "CONCLUIDO",
    "CANCELADO",
}

_NAO_INFORMADO = object()

# Locking reads use the current committed state under MariaDB REPEATABLE READ.
# Resources are always locked in machine, equipment, responsible order.
def _validar_disponibilidade(session, ordem_id, responsavel_id, inicio, fim, excluir_id=None):
    ordem = session.execute(
        select(OrdemServico).where(OrdemServico.id == ordem_id).with_for_update()
    ).scalar_one_or_none()
    if ordem is None or not ordem.ativo or ordem.status in {"CONCLUIDA", "CANCELADA"}:
        raise ValueError("Ordem de serviço inexistente, inativa ou encerrada.")
    if (ordem.maquina_id is None) == (ordem.equipamento_id is None):
        raise ValueError("A ordem deve ter exatamente um recurso.")
    for model, ident in ((Maquina, ordem.maquina_id), (Equipamento, ordem.equipamento_id), (Usuario, responsavel_id)):
        if ident is not None:
            recurso = session.execute(select(model).where(model.id == ident).with_for_update()).scalar_one_or_none()
            if recurso is None or not recurso.ativo:
                raise ValueError("Recurso ou responsável inexistente ou inativo.")
    recurso_os = (OrdemServico.maquina_id == ordem.maquina_id if ordem.maquina_id is not None
                  else OrdemServico.equipamento_id == ordem.equipamento_id)
    condicoes = [recurso_os]
    if responsavel_id is not None:
        condicoes.append(Agendamento.responsavel_id == responsavel_id)
    consulta = (select(Agendamento.id).join(OrdemServico, Agendamento.ordem_servico_id == OrdemServico.id)
                .where(Agendamento.status != "CANCELADO", Agendamento.inicio < fim,
                       Agendamento.fim > inicio, or_(*condicoes)))
    if excluir_id is not None:
        consulta = consulta.where(Agendamento.id != excluir_id)
    if session.execute(consulta.with_for_update()).first() is not None:
        raise ValueError("Conflito com outro agendamento.")
    recurso_indisponivel = (Indisponibilidade.maquina_id == ordem.maquina_id if ordem.maquina_id is not None
                           else Indisponibilidade.equipamento_id == ordem.equipamento_id)
    if session.execute(select(Indisponibilidade.id).where(
        recurso_indisponivel, Indisponibilidade.status != "CANCELADA",
        Indisponibilidade.inicio < fim,
        or_(Indisponibilidade.fim.is_(None), Indisponibilidade.fim > inicio),
    ).with_for_update()).first() is not None:
        raise ValueError("Recurso indisponível no período.")


def criar_agendamento(
    session,
    ordem_servico_id: int,
    inicio: datetime,
    fim: datetime,
    responsavel_id: int | None = None,
    observacoes: str | None = None,
):
    if fim <= inicio:
        raise ValueError(
            "A data/hora final deve ser posterior à inicial."
        )

    _validar_disponibilidade(session, ordem_servico_id, responsavel_id, inicio, fim)

    agendamento = Agendamento(
        ordem_servico_id=ordem_servico_id,
        responsavel_id=responsavel_id,
        inicio=inicio,
        fim=fim,
        status="AGENDADO",
        observacoes=observacoes,
    )

    session.add(agendamento)
    session.commit()
    session.refresh(agendamento)

    return agendamento


def buscar_agendamento(session, agendamento_id: int):
    return session.execute(
        select(Agendamento).where(
            Agendamento.id == agendamento_id
        )
    ).scalar_one_or_none()


def listar_agendamentos(session, inicio=None, fim=None, limite=100, offset=0):
    consulta = select(Agendamento)
    if inicio is not None:
        consulta = consulta.where(Agendamento.fim > inicio)
    if fim is not None:
        consulta = consulta.where(Agendamento.inicio < fim)
    return session.execute(consulta.order_by(Agendamento.inicio.asc(), Agendamento.id.asc())
                           .limit(limite).offset(offset)).scalars().all()

def atualizar_agendamento(
    session,
    agendamento_id: int,
    inicio=_NAO_INFORMADO,
    fim=_NAO_INFORMADO,
    responsavel_id=_NAO_INFORMADO,
    status=_NAO_INFORMADO,
    observacoes=_NAO_INFORMADO,
):
    agendamento = buscar_agendamento(
        session,
        agendamento_id
    )

    if agendamento is None:
        raise ValueError(
            "Agendamento não encontrado."
        )

    if agendamento.status in {
        "CONCLUIDO",
        "CANCELADO",
    }:
        raise ValueError(
            "Não é possível alterar um agendamento "
            "concluído ou cancelado."
        )


    # =========================
    # DATAS
    # =========================

    novo_inicio = (
        agendamento.inicio
        if inicio is _NAO_INFORMADO
        or inicio is None
        else inicio
    )

    novo_fim = (
        agendamento.fim
        if fim is _NAO_INFORMADO
        or fim is None
        else fim
    )


    if novo_fim <= novo_inicio:
        raise ValueError(
            "A data/hora final deve ser posterior à inicial."
        )


    # =========================
    # STATUS
    # =========================

    if (
        status is not _NAO_INFORMADO
        and status is not None
    ):
        status = status.upper()

        if status not in STATUS_AGENDAMENTO:
            raise ValueError(
                "Status de agendamento inválido."
            )



    transicoes = {"AGENDADO": {"AGENDADO", "EM_ANDAMENTO", "CANCELADO"},
                  "EM_ANDAMENTO": {"EM_ANDAMENTO", "CONCLUIDO", "CANCELADO"}}
    novo_status = agendamento.status if status is _NAO_INFORMADO or status is None else status
    if novo_status not in transicoes[agendamento.status]:
        raise ValueError("Transição de status inválida.")
    novo_responsavel = agendamento.responsavel_id if responsavel_id is _NAO_INFORMADO else responsavel_id
    if novo_status != "CANCELADO":
        _validar_disponibilidade(session, agendamento.ordem_servico_id, novo_responsavel,
                                novo_inicio, novo_fim, agendamento.id)

    # =========================
    # RESPONSÁVEL
    # =========================

    if responsavel_id is not _NAO_INFORMADO:

        if responsavel_id is not None:

            responsavel = session.execute(
                select(Usuario).where(
                    Usuario.id
                    == responsavel_id
                )
            ).scalar_one_or_none()

            if responsavel is None:
                raise ValueError(
                    "Responsável não encontrado."
                )

            if not responsavel.ativo:
                raise ValueError(
                    "O responsável está inativo."
                )

        agendamento.responsavel_id = (
            responsavel_id
        )


    # =========================
    # OBSERVAÇÕES
    # =========================

    if observacoes is not _NAO_INFORMADO:
        agendamento.observacoes = (
            observacoes
        )


    # =========================
    # SALVAR
    # =========================

    if status is not _NAO_INFORMADO and status is not None:
        agendamento.status = status
    agendamento.inicio = novo_inicio
    agendamento.fim = novo_fim

    session.commit()
    session.refresh(agendamento)

    return agendamento

def cancelar_agendamento(session, agendamento_id: int):
    agendamento = buscar_agendamento(
        session,
        agendamento_id
    )

    if agendamento is None:
        raise ValueError(
            "Agendamento não encontrado."
        )

    if agendamento.status == "CONCLUIDO":
        raise ValueError(
            "Não é possível cancelar um agendamento concluído."
        )

    agendamento.status = "CANCELADO"

    session.commit()
    session.refresh(agendamento)

    return agendamento