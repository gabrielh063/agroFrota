from services.auditoria_service import registrar_evento
from services.admin_policy import autorizar, perfil_delegavel, preservar_administrador, AdministracaoNegada
from sqlalchemy import select

from database.session import criar_sessao_tenant

from models.tenant.permissao import Permissao


def criar_permissao(
    config,
    database_name: str,
    codigo: str,
    descricao: str | None = None,
    contexto=None
) -> Permissao:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        autorizar(session, database_name, contexto, "PERFIL_PERMISSAO_GERENCIAR")
        permissao_existente = session.execute(
            select(Permissao).where(
                Permissao.codigo == codigo
            )
        ).scalar_one_or_none()

        if permissao_existente is not None:
            raise ValueError(
                "Já existe uma permissão com este código."
            )

        permissao = Permissao(
            codigo=codigo,
            descricao=descricao
        )

        session.add(permissao)
        registrar_evento(session, contexto, "criar_permissao")
        session.commit()
        session.refresh(permissao)

        return permissao

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def buscar_permissao(
    config,
    database_name: str,
    permissao_id: int,
    contexto=None
) -> Permissao | None:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        from services.escopo import escopo_atual
        from services.matriz_acesso import EMPRESA
        if escopo_atual(session, contexto, "PERFIL_PERMISSAO_GERENCIAR") != EMPRESA:
            raise AdministracaoNegada("Escopo administrativo insuficiente.")

        permissao = session.execute(
            select(Permissao).where(
                Permissao.id == permissao_id
            )
        ).scalar_one_or_none()

        return permissao

    finally:
        session.close()


def atualizar_permissao(
    config,
    database_name: str,
    permissao_id: int,
    codigo: str | None = None,
    descricao: str | None = None,
    contexto=None
) -> Permissao:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        ator, permissoes = autorizar(session, database_name, contexto, "PERFIL_PERMISSAO_GERENCIAR")
        permissao = session.execute(
            select(Permissao).where(
                Permissao.id == permissao_id
            )
        ).scalar_one_or_none()

        if permissao is None:
            raise ValueError(
                "Permissão não encontrada."
            )

        if permissao.codigo not in permissoes:
            raise AdministracaoNegada("Permissão excede a autoridade delegável.")
        if codigo is not None and codigo != permissao.codigo:
            raise AdministracaoNegada("Códigos de permissão são imutáveis.")

        if codigo is not None:

            permissao_existente = session.execute(
                select(Permissao).where(
                    Permissao.codigo == codigo,
                    Permissao.id != permissao_id
                )
            ).scalar_one_or_none()

            if permissao_existente is not None:
                raise ValueError(
                    "Já existe uma permissão com este código."
                )

            permissao.codigo = codigo

        if descricao is not None:
            permissao.descricao = descricao

        registrar_evento(session, contexto, "atualizar_permissao")
        session.commit()
        session.refresh(permissao)

        return permissao

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def listar_permissoes(
    config,
    database_name: str,
    contexto=None
) -> list[Permissao]:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:
        from services.escopo import escopo_atual
        from services.matriz_acesso import EMPRESA
        if escopo_atual(session, contexto, "PERFIL_PERMISSAO_GERENCIAR") != EMPRESA:
            raise AdministracaoNegada("Escopo administrativo insuficiente.")

        permissoes = session.execute(
            select(Permissao).order_by(
                Permissao.id
            )
        ).scalars().all()

        return permissoes

    finally:
        session.close()