from services.auditoria_service import registrar_evento
from services.ativo_policy import autorizar_ativo
from sqlalchemy import select

from database.session import criar_sessao_tenant

from models.tenant.equipamento import Equipamento


STATUS_VALIDOS = {
    "DISPONIVEL",
    "EM_USO",
    "MANUTENCAO",
    "INATIVO"
}


def criar_equipamento(
    config,
    database_name: str,
    identificacao: str,
    nome: str,
    tipo: str,
    fabricante: str | None = None,
    modelo: str | None = None,
    ano: int | None = None,
    localizacao: str | None = None,
    status: str = "DISPONIVEL",
    *, contexto=None
) -> Equipamento:

    if status not in STATUS_VALIDOS:
        raise ValueError(
            "Status do equipamento inválido."
        )

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        autorizar_ativo(session, contexto, 'EQUIPAMENTO_CRIAR', escrita=True)

        equipamento_existente = session.execute(
            select(Equipamento).where(
                Equipamento.identificacao == identificacao
            )
        ).scalar_one_or_none()

        if equipamento_existente is not None:
            raise ValueError(
                "Já existe um equipamento com esta identificação."
            )

        equipamento = Equipamento(
            identificacao=identificacao,
            nome=nome,
            tipo=tipo,
            fabricante=fabricante,
            modelo=modelo,
            ano=ano,
            localizacao=localizacao,
            status=status,
            ativo=True
        )

        session.add(equipamento)
        registrar_evento(session, contexto, "criar_equipamento")
        session.commit()
        session.refresh(equipamento)

        return equipamento

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def buscar_equipamento(
    config,
    database_name: str,
    equipamento_id: int,
    *, contexto=None
) -> Equipamento | None:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        autorizar_ativo(session, contexto, 'EQUIPAMENTO_VISUALIZAR', escrita=False)

        equipamento = session.execute(
            select(Equipamento).where(
                Equipamento.id == equipamento_id
            )
        ).scalar_one_or_none()

        return equipamento

    finally:
        session.close()


def atualizar_equipamento(
    config,
    database_name: str,
    equipamento_id: int,
    identificacao: str | None = None,
    nome: str | None = None,
    tipo: str | None = None,
    fabricante: str | None = None,
    modelo: str | None = None,
    ano: int | None = None,
    localizacao: str | None = None,
    status: str | None = None,
    ativo: bool | None = None,
    *, contexto=None
) -> Equipamento:

    if status is not None and status not in STATUS_VALIDOS:
        raise ValueError(
            "Status do equipamento inválido."
        )

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        autorizar_ativo(session, contexto, 'EQUIPAMENTO_EDITAR', escrita=True)
        if ativo is not None:
            autorizar_ativo(session, contexto, 'EQUIPAMENTO_DESATIVAR')

        equipamento = session.execute(
            select(Equipamento).where(
                Equipamento.id == equipamento_id
            )
        ).scalar_one_or_none()

        if equipamento is None:
            raise ValueError(
                "Equipamento não encontrado."
            )

        if identificacao is not None:

            equipamento_existente = session.execute(
                select(Equipamento).where(
                    Equipamento.identificacao == identificacao,
                    Equipamento.id != equipamento_id
                )
            ).scalar_one_or_none()

            if equipamento_existente is not None:
                raise ValueError(
                    "Já existe um equipamento com esta identificação."
                )

            equipamento.identificacao = identificacao

        if nome is not None:
            equipamento.nome = nome

        if tipo is not None:
            equipamento.tipo = tipo

        if fabricante is not None:
            equipamento.fabricante = fabricante

        if modelo is not None:
            equipamento.modelo = modelo

        if ano is not None:
            equipamento.ano = ano

        if localizacao is not None:
            equipamento.localizacao = localizacao

        if status is not None:
            equipamento.status = status

        if ativo is not None:
            equipamento.ativo = ativo

        registrar_evento(session, contexto, "atualizar_equipamento")
        session.commit()
        session.refresh(equipamento)

        return equipamento

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def listar_equipamentos(
    config,
    database_name: str,
    incluir_inativos: bool = False,
    *, contexto=None
) -> list[Equipamento]:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        autorizar_ativo(session, contexto, 'EQUIPAMENTO_VISUALIZAR', escrita=False)

        consulta = select(Equipamento).order_by(
            Equipamento.id
        )

        if not incluir_inativos:
            consulta = consulta.where(
                Equipamento.ativo.is_(True)
            )

        equipamentos = session.execute(
            consulta
        ).scalars().all()

        return equipamentos

    finally:
        session.close()