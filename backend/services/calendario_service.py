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
    inicio: datetime | None = None,
    fim: datetime | None = None,
    responsavel_id: int | None = None,
    status: str | None = None,
    observacoes: str | None = None,
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

    novo_inicio = (
        inicio if inicio is not None
        else agendamento.inicio
    )

    novo_fim = (
        fim if fim is not None
        else agendamento.fim
    )

    if novo_fim <= novo_inicio:
        raise ValueError(
            "A data/hora final deve ser posterior à inicial."
        )

    if status is not None:
        status = status.upper()

        if status not in STATUS_AGENDAMENTO:
            raise ValueError(
                "Status de agendamento inválido."
            )

        agendamento.status = status

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

        agendamento.responsavel_id = responsavel_id

    agendamento.inicio = novo_inicio
    agendamento.fim = novo_fim

    if observacoes is not None:
        agendamento.observacoes = observacoes

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