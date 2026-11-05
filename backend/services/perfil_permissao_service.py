from services.admin_policy import autorizar, perfil_delegavel, preservar_administrador, AdministracaoNegada
from sqlalchemy import select, update

from database.session import criar_sessao_tenant

from models.tenant.perfil import Perfil
from models.tenant.usuario import Usuario
from models.tenant.permissao import Permissao


def adicionar_permissao_perfil(
    config,
    database_name: str,
    perfil_id: int,
    permissao_id: int,
    contexto=None
) -> Perfil:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        ator, permissoes = autorizar(session, database_name, contexto, "PERFIL_PERMISSAO_GERENCIAR")
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
        if perfil_id == ator.perfil_id:
            raise AdministracaoNegada("Não é permitido modificar permissões do próprio perfil.")

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

        permissao_ids = {
            permissao_existente.id
            for permissao_existente in perfil.permissoes
        }

        if permissao_id in permissao_ids:
            raise ValueError(
                "Esta permissão já está associada ao perfil."
            )

        perfil.permissoes.append(permissao)

        session.execute(update(Usuario).where(Usuario.perfil_id == perfil.id)
                        .values(session_version=Usuario.session_version + 1))
        preservar_administrador(session)
        session.commit()
        session.refresh(perfil)

        return perfil

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def remover_permissao_perfil(
    config,
    database_name: str,
    perfil_id: int,
    permissao_id: int,
    contexto=None
) -> Perfil:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        ator, permissoes = autorizar(session, database_name, contexto, "PERFIL_PERMISSAO_GERENCIAR")
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
        if perfil_id == ator.perfil_id:
            raise AdministracaoNegada("Não é permitido modificar permissões do próprio perfil.")

        permissao = session.execute(
            select(Permissao).where(
                Permissao.id == permissao_id
            )
        ).scalar_one_or_none()

        if permissao is None:
            raise ValueError(
                "Permissão não encontrada."
            )

        permissao_associada = next(
            (
                permissao_existente
                for permissao_existente in perfil.permissoes
                if permissao_existente.id == permissao_id
            ),
            None
        )

        if permissao_associada is None:
            raise ValueError(
                "Esta permissão não está associada ao perfil."
            )

        perfil.permissoes.remove(
            permissao_associada
        )

        session.execute(update(Usuario).where(Usuario.perfil_id == perfil.id)
                        .values(session_version=Usuario.session_version + 1))
        preservar_administrador(session)
        session.commit()
        session.refresh(perfil)

        return perfil

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def listar_permissoes_perfil(
    config,
    database_name: str,
    perfil_id: int
) -> list[Permissao]:

    SessionLocal, _ = criar_sessao_tenant(
        config,
        database_name
    )

    session = SessionLocal()

    try:

        perfil = session.execute(
            select(Perfil).where(
                Perfil.id == perfil_id
            )
        ).scalar_one_or_none()

        if perfil is None:
            raise ValueError(
                "Perfil não encontrado."
            )

        return list(perfil.permissoes)

    finally:
        session.close()