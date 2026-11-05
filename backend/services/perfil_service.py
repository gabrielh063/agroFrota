from services.admin_policy import autorizar, perfil_delegavel, preservar_administrador, AdministracaoNegada
from sqlalchemy import select, update

from database.session import criar_sessao_tenant

from models.tenant.perfil import Perfil
from models.tenant.usuario import Usuario


def criar_perfil(
    config,
    database_name: str,
    nome: str,
    descricao: str | None = None,
    contexto=None
) -> Perfil:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        autorizar(session, database_name, contexto, "PERFIL_CRIAR")
        perfil_existente = session.execute(
            select(Perfil).where(
                Perfil.nome == nome
            )
        ).scalar_one_or_none()

        if perfil_existente is not None:
            raise ValueError(
                "Já existe um perfil com este nome."
            )

        perfil = Perfil(
            nome=nome,
            descricao=descricao,
            ativo=True
        )

        session.add(perfil)
        session.commit()
        session.refresh(perfil)

        return perfil

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def buscar_perfil(
    config,
    database_name: str,
    perfil_id: int,
    contexto=None
) -> Perfil | None:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        from services.escopo import escopo_atual
        from services.matriz_acesso import EMPRESA
        if escopo_atual(session, contexto, "PERFIL_VISUALIZAR") != EMPRESA:
            raise AdministracaoNegada("Escopo administrativo insuficiente.")

        perfil = session.execute(
            select(Perfil).where(
                Perfil.id == perfil_id
            )
        ).scalar_one_or_none()

        return perfil

    finally:
        session.close()


def atualizar_perfil(
    config,
    database_name: str,
    perfil_id: int,
    nome: str | None = None,
    descricao: str | None = None,
    ativo: bool | None = None,
    contexto=None
) -> Perfil:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        ator, permissoes = autorizar(session, database_name, contexto, "PERFIL_EDITAR")
        perfil = session.execute(
            select(Perfil).where(
                Perfil.id == perfil_id
            )
        ).scalar_one_or_none()

        if perfil is None:
            raise ValueError(
                "Perfil não encontrado."
            )

        perfil_delegavel(session, perfil_id, permissoes, ativo=False)
        if perfil.id == ator.perfil_id:
            raise AdministracaoNegada("Não é permitido alterar o próprio perfil.")

        if nome is not None:

            perfil_existente = session.execute(
                select(Perfil).where(
                    Perfil.nome == nome,
                    Perfil.id != perfil_id
                )
            ).scalar_one_or_none()

            if perfil_existente is not None:
                raise ValueError(
                    "Já existe um perfil com este nome."
                )

            perfil.nome = nome

        if descricao is not None:
            perfil.descricao = descricao

        if ativo is not None and ativo != perfil.ativo:
            session.execute(update(Usuario).where(Usuario.perfil_id == perfil.id)
                            .values(session_version=Usuario.session_version + 1))

        if ativo is not None:
            perfil.ativo = ativo

        preservar_administrador(session)
        session.commit()
        session.refresh(perfil)

        return perfil

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def listar_perfis(
    config,
    database_name: str,
    incluir_inativos: bool = False,
    contexto=None
) -> list[Perfil]:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        from services.escopo import escopo_atual
        from services.matriz_acesso import EMPRESA
        if escopo_atual(session, contexto, "PERFIL_VISUALIZAR") != EMPRESA:
            raise AdministracaoNegada("Escopo administrativo insuficiente.")

        consulta = select(Perfil).order_by(
            Perfil.id
        )

        if not incluir_inativos:
            consulta = consulta.where(
                Perfil.ativo.is_(True)
            )

        perfis = session.execute(
            consulta
        ).scalars().all()

        return perfis

    finally:
        session.close()
