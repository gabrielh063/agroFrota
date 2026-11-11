from services.os_policy import iniciar_escrita, consulta_os, autorizar_criacao
from services.escopo import escopo_atual
from services.admin_policy import AdministracaoNegada
from services.auditoria_service import registrar_evento
from sqlalchemy import func, select

from database.session import criar_sessao_tenant

from models.tenant.ordem_servico import OrdemServico
from models.tenant.usuario import Usuario
from models.tenant.maquina import Maquina
from models.tenant.equipamento import Equipamento
from services.operacao_lock import bloquear_operacoes


TIPOS_OS = {
    "SERVICO",
    "MANUTENCAO",
}

PRIORIDADES_OS = {
    "BAIXA",
    "MEDIA",
    "ALTA",
    "URGENTE",
}

STATUS_OS = {
    "ABERTA",
    "EM_ANDAMENTO",
    "CONCLUIDA",
    "CANCELADA",
}

_NAO_INFORMADO = object()

def _validar_relacionamentos(
    session,
    maquina_id: int | None = None,
    equipamento_id: int | None = None,
    operador_id: int | None = None,
    responsavel_id: int | None = None,
) -> None:

    if (
        maquina_id is None
        and equipamento_id is None
    ):
        raise ValueError(
            "A OS deve estar relacionada a uma máquina "
            "ou equipamento."
        )

    if (
        maquina_id is not None
        and equipamento_id is not None
    ):
        raise ValueError(
            "A OS não pode estar relacionada "
            "a uma máquina e equipamento ao mesmo tempo."
        )

    if maquina_id is not None:

        maquina = session.get(
            Maquina,
            maquina_id
        )

        if maquina is None:
            raise ValueError(
                "Máquina não encontrada."
            )

        if not maquina.ativo:
            raise ValueError(
                "Máquina está inativa."
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

        if not equipamento.ativo:
            raise ValueError(
                "Equipamento está inativo."
            )

    if operador_id is not None:

        operador = session.get(
            Usuario,
            operador_id
        )

        if operador is None:
            raise ValueError(
                "Operador não encontrado."
            )

        if not operador.ativo:
            raise ValueError(
                "Operador está inativo."
            )

    if responsavel_id is not None:

        responsavel = session.get(
            Usuario,
            responsavel_id
        )

        if responsavel is None:
            raise ValueError(
                "Responsável não encontrado."
            )

        if not responsavel.ativo:
            raise ValueError(
                "Responsável está inativo."
            )

def _proximo_numero_os(session) -> int:
    lock = bloquear_operacoes(session)
    numero = lock.proximo_numero_os
    lock.proximo_numero_os += 1
    return numero


def criar_ordem_servico(
    config,
    database_name: str,
    tipo: str,
    titulo: str,
    descricao: str | None = None,
    maquina_id: int | None = None,
    equipamento_id: int | None = None,
    operador_id: int | None = None,
    responsavel_id: int | None = None,
    prioridade: str = "MEDIA",
    prazo=None,
    *, contexto=None
) -> OrdemServico:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        ordem = criar_ordem_servico_na_sessao(
            session, tipo=tipo, titulo=titulo, descricao=descricao,
            maquina_id=maquina_id, equipamento_id=equipamento_id,
            operador_id=operador_id, responsavel_id=responsavel_id,
            prioridade=prioridade, prazo=prazo, contexto=contexto,
        )
        session.commit()
        session.refresh(ordem)

        return ordem

    except Exception:

        session.rollback()

        raise

    finally:

        session.close()


def criar_ordem_servico_na_sessao(
    session, *, tipo, titulo, descricao=None, maquina_id=None,
    equipamento_id=None, operador_id=None, responsavel_id=None,
    prioridade="MEDIA", prazo=None, contexto=None,
) -> OrdemServico:
    """Cria e audita uma OS sem commit, para orquestração atômica.

    A sessão e a transação pertencem ao chamador. Rotas manuais continuam
    usando `criar_ordem_servico`, que confirma a própria transação.
    """
    iniciar_escrita(session)
    autorizar_criacao(session, contexto, maquina_id, equipamento_id, operador_id, responsavel_id)
    tipo = tipo.upper()
    prioridade = prioridade.upper()
    if tipo not in TIPOS_OS:
        raise ValueError("Tipo de OS inválido.")
    if prioridade not in PRIORIDADES_OS:
        raise ValueError("Prioridade inválida.")
    if not titulo or len(titulo.strip()) > 150:
        raise ValueError("Título inválido.")

    _validar_relacionamentos(
        session=session, maquina_id=maquina_id, equipamento_id=equipamento_id,
        operador_id=operador_id, responsavel_id=responsavel_id,
    )
    ordem = OrdemServico(
        numero=_proximo_numero_os(session), tipo=tipo, titulo=titulo.strip(),
        descricao=descricao, maquina_id=maquina_id, equipamento_id=equipamento_id,
        operador_id=operador_id, responsavel_id=responsavel_id,
        prioridade=prioridade, status="ABERTA", prazo=prazo, ativo=True,
    )
    session.add(ordem)
    session.flush()
    registrar_evento(session, contexto, "criar_ordem_servico_assistente")
    return ordem


def buscar_ordem_servico(
    config,
    database_name: str,
    ordem_servico_id: int,
    *, contexto=None
) -> OrdemServico | None:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        ordem = session.execute(
            consulta_os(session, contexto, "OS.VISUALIZAR", select(OrdemServico)).where(
                OrdemServico.id == ordem_servico_id
            )
        ).scalar_one_or_none()

        return ordem

    finally:

        session.close()


def listar_ordens_servico(
    config,
    database_name: str,
    apenas_ativas: bool = False,
    *, contexto=None
) -> list[OrdemServico]:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        consulta = select(
            OrdemServico
        ).order_by(
            OrdemServico.numero.desc()
        )

        consulta = consulta_os(session, contexto, "OS.VISUALIZAR", consulta)

        if apenas_ativas:
            consulta = consulta.where(
                OrdemServico.ativo.is_(True)
            )

        ordens = session.execute(
            consulta
        ).scalars().all()

        return list(ordens)

    finally:

        session.close()


def atualizar_ordem_servico(
    config,
    database_name: str,
    ordem_servico_id: int,
    tipo=_NAO_INFORMADO,
    titulo=_NAO_INFORMADO,
    descricao=_NAO_INFORMADO,
    maquina_id=_NAO_INFORMADO,
    equipamento_id=_NAO_INFORMADO,
    operador_id=_NAO_INFORMADO,
    responsavel_id=_NAO_INFORMADO,
    prioridade=_NAO_INFORMADO,
    status=_NAO_INFORMADO,
    prazo=_NAO_INFORMADO,
    *, contexto=None
) -> OrdemServico:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        iniciar_escrita(session)
        if isinstance(status, str):
            status = status.upper()
        acao = "OS.CONCLUIR" if status == "CONCLUIDA" else "OS.CANCELAR" if status == "CANCELADA" else "OS.EDITAR"
        if escopo_atual(session, contexto, acao) != "empresa":
            if any(x is not _NAO_INFORMADO for x in (maquina_id, equipamento_id, operador_id, responsavel_id)):
                raise AdministracaoNegada("Somente gestão pode alterar a atribuição da OS.")

        ordem = session.execute(
            consulta_os(session, contexto, acao, select(OrdemServico)).where(
                OrdemServico.id
                == ordem_servico_id
            )
        ).scalar_one_or_none()


        if ordem is None:
            raise ValueError(
                "Ordem de serviço não encontrada."
            )


        if ordem.status in {
            "CONCLUIDA",
            "CANCELADA"
        }:
            raise ValueError(
                "Não é possível editar uma OS concluída "
                "ou cancelada."
            )


        # =========================
        # TIPO
        # =========================

        if (
            tipo is not _NAO_INFORMADO
            and tipo is not None
        ):

            tipo = tipo.upper()

            if tipo not in TIPOS_OS:
                raise ValueError(
                    "Tipo de OS inválido."
                )

            ordem.tipo = tipo


        # =========================
        # PRIORIDADE
        # =========================

        if (
            prioridade
            is not _NAO_INFORMADO
            and prioridade is not None
        ):

            prioridade = prioridade.upper()

            if (
                prioridade
                not in PRIORIDADES_OS
            ):
                raise ValueError(
                    "Prioridade inválida."
                )

            ordem.prioridade = prioridade


        # =========================
        # STATUS
        # =========================

        if (
            status is not _NAO_INFORMADO
            and status is not None
        ):

            status = status.upper()

            if status not in STATUS_OS:
                raise ValueError(
                    "Status de OS inválido."
                )

            ordem.status = status


        # =========================
        # MÁQUINA / EQUIPAMENTO
        # =========================

        alterou_ativo = (
            maquina_id
            is not _NAO_INFORMADO
            or
            equipamento_id
            is not _NAO_INFORMADO
        )


        if alterou_ativo:

            maquina_final = (
                ordem.maquina_id
                if maquina_id
                is _NAO_INFORMADO
                else maquina_id
            )

            equipamento_final = (
                ordem.equipamento_id
                if equipamento_id
                is _NAO_INFORMADO
                else equipamento_id
            )


            _validar_relacionamentos(
                session=session,
                maquina_id=maquina_final,
                equipamento_id=equipamento_final
            )


            if (
                maquina_id
                is not _NAO_INFORMADO
            ):
                ordem.maquina_id = (
                    maquina_id
                )


            if (
                equipamento_id
                is not _NAO_INFORMADO
            ):
                ordem.equipamento_id = (
                    equipamento_id
                )


        # =========================
        # OPERADOR
        # =========================

        if (
            operador_id
            is not _NAO_INFORMADO
        ):

            if operador_id is not None:

                operador = session.get(
                    Usuario,
                    operador_id
                )

                if operador is None:
                    raise ValueError(
                        "Operador não encontrado."
                    )

                if not operador.ativo:
                    raise ValueError(
                        "Operador está inativo."
                    )

            ordem.operador_id = operador_id


        # =========================
        # RESPONSÁVEL
        # =========================

        if (
            responsavel_id
            is not _NAO_INFORMADO
        ):

            if responsavel_id is not None:

                responsavel = session.get(
                    Usuario,
                    responsavel_id
                )

                if responsavel is None:
                    raise ValueError(
                        "Responsável não encontrado."
                    )

                if not responsavel.ativo:
                    raise ValueError(
                        "Responsável está inativo."
                    )

            ordem.responsavel_id = (
                responsavel_id
            )


        # =========================
        # CAMPOS NORMAIS
        # =========================

        if (
            titulo is not _NAO_INFORMADO
            and titulo is not None
        ):
            ordem.titulo = titulo


        if (
            descricao
            is not _NAO_INFORMADO
        ):
            ordem.descricao = descricao


        if prazo is not _NAO_INFORMADO:
            ordem.prazo = prazo


        # =========================
        # GARANTIA FINAL
        # =========================

        if (
            ordem.maquina_id is None
            and
            ordem.equipamento_id is None
        ):
            raise ValueError(
                "A OS deve estar relacionada a uma máquina "
                "ou equipamento."
            )


        if (
            ordem.maquina_id is not None
            and
            ordem.equipamento_id is not None
        ):
            raise ValueError(
                "A OS não pode estar relacionada "
                "a uma máquina e equipamento ao mesmo tempo."
            )


        registrar_evento(session, contexto, acao)
        session.commit()

        session.refresh(ordem)

        return ordem


    except Exception:

        session.rollback()

        raise


    finally:

        session.close()


def concluir_ordem_servico(
    config,
    database_name: str,
    ordem_servico_id: int,
    *, contexto=None
) -> OrdemServico:

    return atualizar_ordem_servico(
        config=config,
        database_name=database_name,
        ordem_servico_id=ordem_servico_id,
        contexto=contexto,
        status="CONCLUIDA"
    )


def cancelar_ordem_servico(
    config,
    database_name: str,
    ordem_servico_id: int,
    *, contexto=None
) -> OrdemServico:

    return atualizar_ordem_servico(
        config=config,
        database_name=database_name,
        ordem_servico_id=ordem_servico_id,
        contexto=contexto,
        status="CANCELADA"
    )
