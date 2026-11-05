from datetime import datetime

from sqlalchemy import select

from models.tenant.agendamento import Agendamento
from models.tenant.ordem_servico import OrdemServico
from models.tenant.usuario import Usuario


STATUS_AGENDAMENTO = {
    "AGENDADO",
    "EM_ANDAMENTO",
    "CONCLUIDO",
    "CANCELADO",
}

_NAO_INFORMADO = object()

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

    ordem_servico = session.execute(
        select(OrdemServico).where(
            OrdemServico.id == ordem_servico_id
        )
    ).scalar_one_or_none()

    if ordem_servico is None:
        raise ValueError(
            "Ordem de serviço não encontrada."
        )

    if not ordem_servico.ativo:
        raise ValueError(
            "A ordem de serviço está inativa."
        )

    if ordem_servico.status in {"CONCLUIDA", "CANCELADA"}:
        raise ValueError(
            "Não é possível agendar uma ordem de serviço concluída ou cancelada."
        )

    if responsavel_id is not None:
        responsavel = session.execute(
            select(Usuario).where(
                Usuario.id == responsavel_id
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


def listar_agendamentos(session):
    return session.execute(
        select(Agendamento).order_by(
            Agendamento.inicio.asc()
        )
    ).scalars().all()

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