from datetime import datetime

from sqlalchemy import select

from models.tenant.manutencao import Manutencao
from models.tenant.ordem_servico import OrdemServico
from models.tenant.usuario import Usuario


TIPOS_MANUTENCAO = {
    "PREVENTIVA",
    "CORRETIVA",
    "PREDITIVA",
}

STATUS_MANUTENCAO = {
    "EM_ANDAMENTO",
    "CONCLUIDA",
    "CANCELADA",
}


def criar_manutencao(
    session,
    ordem_servico_id: int,
    inicio: datetime,
    tipo: str,
    responsavel_id: int | None = None,
    fim: datetime | None = None,
    descricao: str | None = None,
    custo=None,
    observacoes: str | None = None,
):
    tipo = tipo.upper()

    if tipo not in TIPOS_MANUTENCAO:
        raise ValueError(
            "Tipo de manutenção inválido."
        )

    if fim is not None and fim <= inicio:
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

    if ordem_servico.status in {
        "CONCLUIDA",
        "CANCELADA",
    }:
        raise ValueError(
            "Não é possível criar manutenção para "
            "uma OS concluída ou cancelada."
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

    manutencao = Manutencao(
        ordem_servico_id=ordem_servico_id,
        responsavel_id=responsavel_id,
        tipo=tipo,
        inicio=inicio,
        fim=fim,
        descricao=descricao,
        custo=custo,
        status=(
            "CONCLUIDA"
            if fim is not None
            else "EM_ANDAMENTO"
        ),
        observacoes=observacoes,
    )

    session.add(manutencao)
    session.commit()
    session.refresh(manutencao)

    return manutencao


def buscar_manutencao(session, manutencao_id: int):
    return session.execute(
        select(Manutencao).where(
            Manutencao.id == manutencao_id
        )
    ).scalar_one_or_none()


def listar_manutencoes(session):
    return session.execute(
        select(Manutencao).order_by(
            Manutencao.inicio.desc()
        )
    ).scalars().all()


def atualizar_manutencao(
    session,
    manutencao_id: int,
    responsavel_id: int | None = None,
    tipo: str | None = None,
    inicio: datetime | None = None,
    fim: datetime | None = None,
    descricao: str | None = None,
    custo=None,
    status: str | None = None,
    observacoes: str | None = None,
):
    manutencao = buscar_manutencao(
        session,
        manutencao_id
    )

    if manutencao is None:
        raise ValueError(
            "Manutenção não encontrada."
        )

    if manutencao.status in {"CONCLUIDA", "CANCELADA"}:
        raise ValueError(
            "Não é possível editar uma manutenção finalizada."
        )

    novo_inicio = (
        inicio
        if inicio is not None
        else manutencao.inicio
    )

    novo_fim = (
        fim
        if fim is not None
        else manutencao.fim
    )

    if novo_fim is not None and novo_fim <= novo_inicio:
        raise ValueError(
            "A data/hora final deve ser posterior à inicial."
        )

    if tipo is not None:
        tipo = tipo.upper()

        if tipo not in TIPOS_MANUTENCAO:
            raise ValueError(
                "Tipo de manutenção inválido."
            )

        manutencao.tipo = tipo

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

        manutencao.responsavel_id = responsavel_id

    if inicio is not None:
        manutencao.inicio = inicio

    if fim is not None:
        manutencao.fim = fim

    if descricao is not None:
        manutencao.descricao = descricao

    if custo is not None:
        manutencao.custo = custo

    if status is not None:
        status = status.upper()

        if status not in STATUS_MANUTENCAO:
            raise ValueError(
                "Status de manutenção inválido."
            )

        manutencao.status = status

    if observacoes is not None:
        manutencao.observacoes = observacoes

    session.commit()
    session.refresh(manutencao)

    return manutencao


def concluir_manutencao(
    session,
    manutencao_id: int,
    fim: datetime | None = None,
):
    manutencao = buscar_manutencao(
        session,
        manutencao_id
    )

    if manutencao is None:
        raise ValueError(
            "Manutenção não encontrada."
        )

    if manutencao.status == "CANCELADA":
        raise ValueError(
            "Não é possível concluir uma manutenção cancelada."
        )

    if manutencao.status == "CONCLUIDA":
        raise ValueError(
            "A manutenção já está concluída."
        )

    data_fim = fim or datetime.utcnow()

    if data_fim <= manutencao.inicio:
        raise ValueError(
            "A data/hora final deve ser posterior à inicial."
        )

    manutencao.fim = data_fim
    manutencao.status = "CONCLUIDA"

    session.commit()
    session.refresh(manutencao)

    return manutencao


def cancelar_manutencao(
    session,
    manutencao_id: int,
):
    manutencao = buscar_manutencao(
        session,
        manutencao_id
    )

    if manutencao is None:
        raise ValueError(
            "Manutenção não encontrada."
        )

    if manutencao.status == "CONCLUIDA":
        raise ValueError(
            "Não é possível cancelar uma manutenção concluída."
        )

    if manutencao.status == "CANCELADA":
        raise ValueError(
            "A manutenção já está cancelada."
        )

    manutencao.status = "CANCELADA"

    session.commit()
    session.refresh(manutencao)

    return manutencao