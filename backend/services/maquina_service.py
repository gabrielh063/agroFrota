from services.auditoria_service import registrar_evento
from services.ativo_policy import autorizar_ativo
from sqlalchemy import select

from database.session import criar_sessao_tenant

from models.tenant.maquina import Maquina


STATUS_VALIDOS = {
    "OPERANDO",
    "PARADA",
    "MANUTENCAO",
    "INATIVA"
}


def criar_maquina(
    config,
    database_name: str,
    identificacao: str,
    modelo: str,
    fabricante: str,
    ano: int | None = None,
    localizacao: str | None = None,
    status: str = "OPERANDO",
    controla_telemetria: bool = False,
    *, contexto=None
) -> Maquina:

    if status not in STATUS_VALIDOS:
        raise ValueError(
            "Status da máquina inválido."
        )

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        autorizar_ativo(session, contexto, 'MAQUINA_CRIAR', escrita=True)

        maquina_existente = session.execute(
            select(Maquina).where(
                Maquina.identificacao == identificacao
            )
        ).scalar_one_or_none()

        if maquina_existente is not None:
            raise ValueError(
                "Já existe uma máquina com esta identificação."
            )

        maquina = Maquina(
            identificacao=identificacao,
            modelo=modelo,
            fabricante=fabricante,
            ano=ano,
            localizacao=localizacao,
            status=status,
            controla_telemetria=controla_telemetria,
            ativo=True
        )

        session.add(maquina)

        registrar_evento(session, contexto, "criar_maquina")
        session.commit()

        session.refresh(maquina)

        return maquina

    except Exception:

        session.rollback()

        raise

    finally:

        session.close()


def buscar_maquina(
    config,
    database_name: str,
    maquina_id: int,
    *, contexto=None
) -> Maquina | None:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        autorizar_ativo(session, contexto, 'MAQUINA_VISUALIZAR', escrita=False)

        maquina = session.execute(
            select(Maquina).where(
                Maquina.id == maquina_id
            )
        ).scalar_one_or_none()

        return maquina

    finally:

        session.close()
        
def atualizar_maquina(
    config,
    database_name: str,
    maquina_id: int,
    identificacao: str | None = None,
    modelo: str | None = None,
    fabricante: str | None = None,
    ano: int | None = None,
    localizacao: str | None = None,
    status: str | None = None,
    controla_telemetria: bool | None = None,
    ativo: bool | None = None,
    *, contexto=None
) -> Maquina:

    if status is not None and status not in STATUS_VALIDOS:
        raise ValueError(
            "Status da máquina inválido."
        )

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        autorizar_ativo(session, contexto, 'MAQUINA_EDITAR', escrita=True)
        if ativo is not None:
            autorizar_ativo(session, contexto, 'MAQUINA_DESATIVAR')

        maquina = session.execute(
            select(Maquina).where(
                Maquina.id == maquina_id
            )
        ).scalar_one_or_none()

        if maquina is None:
            raise ValueError(
                "Máquina não encontrada."
            )

        if identificacao is not None:

            maquina_existente = session.execute(
                select(Maquina).where(
                    Maquina.identificacao == identificacao,
                    Maquina.id != maquina_id
                )
            ).scalar_one_or_none()

            if maquina_existente is not None:
                raise ValueError(
                    "Já existe uma máquina com esta identificação."
                )

            maquina.identificacao = identificacao

        if modelo is not None:
            maquina.modelo = modelo

        if fabricante is not None:
            maquina.fabricante = fabricante

        if ano is not None:
            maquina.ano = ano

        if localizacao is not None:
            maquina.localizacao = localizacao

        if status is not None:
            maquina.status = status

        if controla_telemetria is not None:
            maquina.controla_telemetria = controla_telemetria

        if ativo is not None:
            maquina.ativo = ativo

        registrar_evento(session, contexto, "atualizar_maquina")
        session.commit()

        session.refresh(maquina)

        return maquina

    except Exception:

        session.rollback()

        raise

    finally:

        session.close()
        
def listar_maquinas(
    config,
    database_name: str,
    incluir_inativas: bool = False,
    *, contexto=None
) -> list[Maquina]:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        autorizar_ativo(session, contexto, 'MAQUINA_VISUALIZAR', escrita=False)

        consulta = select(Maquina).order_by(
            Maquina.id
        )

        if not incluir_inativas:
            consulta = consulta.where(
                Maquina.ativo.is_(True)
            )

        maquinas = session.execute(
            consulta
        ).scalars().all()

        return maquinas

    finally:

        session.close()