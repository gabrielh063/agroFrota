from sqlalchemy import select
from sqlalchemy.orm import Session

from models.tenant.indisponibilidade import Indisponibilidade
from models.tenant.maquina import Maquina
from models.tenant.equipamento import Equipamento
from models.tenant.manutencao import Manutencao
from models.tenant.agendamento import Agendamento
from models.tenant.ordem_servico import OrdemServico
from services.os_policy import iniciar_escrita

from schemas.indisponibilidade import (
    IndisponibilidadeCriarSchema,
    IndisponibilidadeAtualizarSchema,
    TIPOS_INDISPONIBILIDADE,
    STATUS_INDISPONIBILIDADE,
)


def _validar_tipo(tipo: str) -> None:
    if tipo not in TIPOS_INDISPONIBILIDADE:
        raise ValueError(
            f"Tipo de indisponibilidade inválido. "
            f"Permitidos: {', '.join(sorted(TIPOS_INDISPONIBILIDADE))}."
        )


def _validar_status(status: str) -> None:
    if status not in STATUS_INDISPONIBILIDADE:
        raise ValueError(
            f"Status inválido. "
            f"Permitidos: {', '.join(sorted(STATUS_INDISPONIBILIDADE))}."
        )


def _validar_recurso(
    session: Session,
    maquina_id: int | None,
    equipamento_id: int | None,
) -> None:

    if maquina_id is None and equipamento_id is None:
        raise ValueError(
            "Informe uma máquina ou um equipamento."
        )

    if maquina_id is not None and equipamento_id is not None:
        raise ValueError(
            "Informe apenas uma máquina ou um equipamento."
        )

    if maquina_id is not None:
        maquina = session.get(Maquina, maquina_id)

        if maquina is None:
            raise ValueError(
                "Máquina não encontrada."
            )

    if equipamento_id is not None:
        equipamento = session.get(
            Equipamento,
            equipamento_id
        )

        if equipamento is None:
            raise ValueError(
                "Equipamento não encontrado."
            )


def _validar_manutencao(
    session: Session,
    manutencao_id: int | None,
) -> None:

    if manutencao_id is None:
        return

    manutencao = session.get(
        Manutencao,
        manutencao_id
    )

    if manutencao is None:
        raise ValueError(
            "Manutenção não encontrada."
        )


def _validar_sem_agendamento_no_periodo(
    session: Session,
    maquina_id: int | None,
    equipamento_id: int | None,
    inicio,
    fim,
    excluir_id: int | None = None,
) -> None:
    recurso = (OrdemServico.maquina_id == maquina_id if maquina_id is not None
               else OrdemServico.equipamento_id == equipamento_id)
    consulta = (
        select(Agendamento.id)
        .join(OrdemServico, Agendamento.ordem_servico_id == OrdemServico.id)
        .where(
            recurso,
            Agendamento.status != "CANCELADO",
            Agendamento.inicio < fim if fim is not None else True,
            Agendamento.fim > inicio,
        )
    )
    if excluir_id is not None:
        consulta = consulta.where(Agendamento.id != excluir_id)
    if session.execute(consulta.with_for_update()).first() is not None:
        raise ValueError("Há um agendamento ativo para este recurso no período.")


def criar_indisponibilidade(
    session: Session,
    dados: IndisponibilidadeCriarSchema,
) -> Indisponibilidade:

    iniciar_escrita(session)

    _validar_tipo(dados.tipo)

    _validar_recurso(
        session,
        dados.maquina_id,
        dados.equipamento_id,
    )

    _validar_manutencao(
        session,
        dados.manutencao_id,
    )

    if dados.fim is not None and dados.fim <= dados.inicio:
        raise ValueError(
            "O fim deve ser posterior ao início."
        )

    _validar_sem_agendamento_no_periodo(
        session, dados.maquina_id, dados.equipamento_id,
        dados.inicio, dados.fim,
    )

    registro = Indisponibilidade(
        maquina_id=dados.maquina_id,
        equipamento_id=dados.equipamento_id,
        manutencao_id=dados.manutencao_id,
        inicio=dados.inicio,
        fim=dados.fim,
        motivo=dados.motivo,
        tipo=dados.tipo,
        observacoes=dados.observacoes,
        status=(
            "FINALIZADA"
            if dados.fim is not None
            else "ATIVA"
        ),
    )

    session.add(registro)
    session.commit()
    session.refresh(registro)

    return registro


def buscar_indisponibilidade(
    session: Session,
    indisponibilidade_id: int,
) -> Indisponibilidade | None:

    return session.get(
        Indisponibilidade,
        indisponibilidade_id,
    )


def listar_indisponibilidades(
    session: Session,
    status: str | None = None,
    maquina_id: int | None = None,
    equipamento_id: int | None = None,
) -> list[Indisponibilidade]:

    consulta = select(Indisponibilidade)

    if status is not None:
        _validar_status(status)

        consulta = consulta.where(
            Indisponibilidade.status == status
        )

    if maquina_id is not None:
        consulta = consulta.where(
            Indisponibilidade.maquina_id == maquina_id
        )

    if equipamento_id is not None:
        consulta = consulta.where(
            Indisponibilidade.equipamento_id == equipamento_id
        )

    consulta = consulta.order_by(
        Indisponibilidade.inicio.desc()
    )

    return list(
        session.scalars(consulta).all()
    )


def atualizar_indisponibilidade(
    session: Session,
    indisponibilidade_id: int,
    dados: IndisponibilidadeAtualizarSchema,
) -> Indisponibilidade:

    iniciar_escrita(session)

    registro = buscar_indisponibilidade(
        session,
        indisponibilidade_id,
    )

    if registro is None:
        raise ValueError(
            "Indisponibilidade não encontrada."
        )

    if registro.status in {
        "FINALIZADA",
        "CANCELADA",
    }:
        raise ValueError(
            "Não é possível alterar uma indisponibilidade finalizada ou cancelada."
        )

    maquina_id = (
        dados.maquina_id
        if dados.maquina_id is not None
        else registro.maquina_id
    )

    equipamento_id = (
        dados.equipamento_id
        if dados.equipamento_id is not None
        else registro.equipamento_id
    )

    _validar_recurso(
        session,
        maquina_id,
        equipamento_id,
    )

    if dados.manutencao_id is not None:
        _validar_manutencao(
            session,
            dados.manutencao_id,
        )

    if dados.tipo is not None:
        _validar_tipo(dados.tipo)

    if dados.status is not None:
        _validar_status(dados.status)

    inicio = (
        dados.inicio
        if dados.inicio is not None
        else registro.inicio
    )

    fim = (
        dados.fim
        if dados.fim is not None
        else registro.fim
    )

    if fim is not None and fim <= inicio:
        raise ValueError(
            "O fim deve ser posterior ao início."
        )

    status_final = dados.status if dados.status is not None else registro.status
    if status_final != "CANCELADA":
        _validar_sem_agendamento_no_periodo(
            session, maquina_id, equipamento_id, inicio, fim,
            excluir_id=registro.id,
        )

    if dados.maquina_id is not None:
        registro.maquina_id = dados.maquina_id

    if dados.equipamento_id is not None:
        registro.equipamento_id = dados.equipamento_id

    if dados.manutencao_id is not None:
        registro.manutencao_id = dados.manutencao_id

    if dados.inicio is not None:
        registro.inicio = dados.inicio

    if dados.fim is not None:
        registro.fim = dados.fim

    if dados.motivo is not None:
        registro.motivo = dados.motivo

    if dados.tipo is not None:
        registro.tipo = dados.tipo

    if dados.observacoes is not None:
        registro.observacoes = dados.observacoes

    if dados.status is not None:
        registro.status = dados.status

    if registro.fim is not None and registro.status == "ATIVA":
        registro.status = "FINALIZADA"

    session.commit()
    session.refresh(registro)

    return registro


def finalizar_indisponibilidade(
    session: Session,
    indisponibilidade_id: int,
    fim,
) -> Indisponibilidade:

    iniciar_escrita(session)

    registro = buscar_indisponibilidade(
        session,
        indisponibilidade_id,
    )

    if registro is None:
        raise ValueError(
            "Indisponibilidade não encontrada."
        )

    if registro.status != "ATIVA":
        raise ValueError(
            "A indisponibilidade não está ativa."
        )

    if fim <= registro.inicio:
        raise ValueError(
            "O fim deve ser posterior ao início."
        )

    registro.fim = fim
    registro.status = "FINALIZADA"

    session.commit()
    session.refresh(registro)

    return registro


def cancelar_indisponibilidade(
    session: Session,
    indisponibilidade_id: int,
) -> Indisponibilidade:

    iniciar_escrita(session)

    registro = buscar_indisponibilidade(
        session,
        indisponibilidade_id,
    )

    if registro is None:
        raise ValueError(
            "Indisponibilidade não encontrada."
        )

    if registro.status == "FINALIZADA":
        raise ValueError(
            "Não é possível cancelar uma indisponibilidade finalizada."
        )

    if registro.status == "CANCELADA":
        raise ValueError(
            "A indisponibilidade já está cancelada."
        )

    registro.status = "CANCELADA"

    session.commit()
    session.refresh(registro)

    return registro
