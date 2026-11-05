"""Contratos RF08 em MariaDB exclusivamente descartável."""
import os
import subprocess
import sys
import pytest
from sqlalchemy import Column, Integer, MetaData, Table, select, text
from config import Config
from database.session import criar_sessao_tenant
from models.tenant.usuario import Usuario
from services.admin_policy import AdministracaoNegada, ContextoAdministrativo
from services.escopo import consultar_autorizado, escopo_atual
from services.matriz_acesso import MATRIZ
from services.seed_service import criar_perfis_padrao, criar_permissoes_padrao

DB = os.environ.get('AGROFROTA_TEST_DATABASE', '')
DB_B = os.environ.get('AGROFROTA_TEST_DATABASE_B', '')


def sessao(db=DB):
    factory, engine = criar_sessao_tenant(Config, db)
    return factory(), engine


def contexto(session, db, role):
    username = os.environ['AGROFROTA_TEST_USERNAME'] if role == 'ADMIN_EMPRESA' else 'perfil_' + role.lower()
    user = session.execute(select(Usuario).where(Usuario.username == username)).scalar_one()
    return ContextoAdministrativo(db, user.id, user.session_version)


@pytest.mark.parametrize('role,permitida,negada', [
    ('ADMIN_EMPRESA', 'USUARIO_CRIAR', 'INEXISTENTE'),
    ('DIRETORIA', 'DASHBOARD.VISUALIZAR', 'USUARIO_CRIAR'),
    ('GESTOR_FROTA', 'OS.EDITAR', 'USUARIO_CRIAR'),
    ('ADMINISTRATIVO', 'OS.VISUALIZAR', 'OS.EDITAR'),
    ('MANUTENCAO', 'MANUTENCAO.EDITAR', 'USUARIO_CRIAR'),
    ('OPERADOR', 'OS.VISUALIZAR', 'OS.EDITAR'),
    ('AUDITOR', 'OS.VISUALIZAR', 'USUARIO_CRIAR'),
])
def test_perfis_positivos_e_negativos(base_url, role, permitida, negada):
    session, engine = sessao()
    try:
        ctx = contexto(session, DB, role)
        assert escopo_atual(session, ctx, permitida) == MATRIZ[role][permitida]
        with pytest.raises(AdministracaoNegada):
            escopo_atual(session, ctx, negada)
        with pytest.raises(AdministracaoNegada):
            escopo_atual(session, ContextoAdministrativo(DB_B, ctx.usuario_id, ctx.session_version), permitida)
    finally:
        session.close()
        engine.dispose()


def test_lista_detalhe_proprio_e_atribuicao(base_url):
    session, engine = sessao()
    table = Table('teste_escopo', MetaData(), Column('id', Integer, primary_key=True), Column('dono', Integer), Column('atribuido', Integer), prefixes=['TEMPORARY'])
    try:
        operator = contexto(session, DB, 'OPERADOR')
        maintenance = contexto(session, DB, 'MANUTENCAO')
        admin = contexto(session, DB, 'ADMIN_EMPRESA')
        table.create(session.connection())
        session.execute(table.insert(), [
            {'id': 1, 'dono': operator.usuario_id, 'atribuido': operator.usuario_id},
            {'id': 2, 'dono': maintenance.usuario_id, 'atribuido': maintenance.usuario_id},
            {'id': 3, 'dono': admin.usuario_id, 'atribuido': admin.usuario_id},
        ])
        def ids(ctx, action, **cols):
            stmt = consultar_autorizado(session, ctx, action, select(table.c.id), **cols)
            return session.execute(stmt).scalars().all(), stmt
        assert ids(admin, 'OS.VISUALIZAR', atribuicao=table.c.atribuido)[0] == [1, 2, 3]
        result, statement = ids(operator, 'OS.VISUALIZAR', atribuicao=table.c.atribuido)
        assert result == [1]
        assert session.execute(statement.where(table.c.id == 1)).scalar_one() == 1
        assert session.execute(statement.where(table.c.id == 2)).scalar_one_or_none() is None
        assert ids(maintenance, 'OS.VISUALIZAR', atribuicao=table.c.atribuido)[0] == [2]
        assert ids(operator, 'USUARIO_PROPRIO_VISUALIZAR', proprio=table.c.dono)[0] == [1]
        assert ids(operator, 'OS.VISUALIZAR')[0] == []
        with pytest.raises(AdministracaoNegada):
            ids(operator, 'OS.EDITAR', atribuicao=table.c.atribuido)
    finally:
        session.rollback()
        session.close()
        engine.dispose()


def test_seed_repetido_preserva_permissoes(base_url):
    session, engine = sessao()
    try:
        before = session.execute(text('SELECT perfil_id, permissao_id FROM perfil_permissoes ORDER BY 1,2')).all()
        session.rollback()
        criar_permissoes_padrao(Config, DB)
        criar_perfis_padrao(Config, DB)
        criar_perfis_padrao(Config, DB)
        assert before == session.execute(text('SELECT perfil_id, permissao_id FROM perfil_permissoes ORDER BY 1,2')).all()
        assert set(session.execute(text('SELECT nome, politica_escopo FROM perfis')).all()) >= {(role, role) for role in MATRIZ}
    finally:
        session.close()
        engine.dispose()


def test_migracao_legada_nao_acrescenta_permissoes(base_url):
    session, engine = sessao(DB_B)
    env = dict(os.environ, AGROFROTA_TENANT_DB=DB_B)
    saved = session.execute(text('SELECT id, politica_escopo FROM perfis')).all()
    versions = dict(session.execute(text("SELECT u.id, u.session_version FROM usuarios u JOIN perfis p ON p.id=u.perfil_id WHERE p.nome IN ('OPERADOR','MANUTENCAO')")).all())
    session.close()
    def alembic(command, revision):
        subprocess.run([sys.executable, '-m', 'alembic', '-c', 'alembic-tenant.ini', command, revision], env=env, check=True, capture_output=True)
    try:
        alembic('downgrade', '9b3b4b41d220')
        with engine.begin() as c:
            c.execute(text("INSERT INTO perfis (nome, ativo) VALUES ('GERENTE',1), ('LEGADO_CUSTOM',1)"))
            ids = dict(c.execute(text("SELECT nome, id FROM perfis WHERE nome IN ('GERENTE','LEGADO_CUSTOM')")).all())
            permission = c.execute(text("SELECT id FROM permissoes WHERE codigo='OS.VISUALIZAR'")).scalar_one()
            for pid in ids.values():
                c.execute(text('INSERT INTO perfil_permissoes VALUES (:p,:v)'), {'p': pid, 'v': permission})
            before = c.execute(text('SELECT perfil_id, permissao_id FROM perfil_permissoes ORDER BY 1,2')).all()
        alembic('upgrade', 'a71f82c9d410')
        with engine.begin() as c:
            assert c.execute(text('SELECT perfil_id, permissao_id FROM perfil_permissoes ORDER BY 1,2')).all() == before
            result = dict(c.execute(text("SELECT nome, politica_escopo FROM perfis WHERE nome IN ('GERENTE','LEGADO_CUSTOM')")).all())
            assert result == {'GERENTE': 'ADMIN_EMPRESA', 'LEGADO_CUSTOM': None}
            for uid, version in versions.items():
                assert c.execute(text('SELECT session_version FROM usuarios WHERE id=:id'), {'id': uid}).scalar_one() == version + 1
    finally:
        with engine.begin() as c:
            for pid, policy in saved:
                c.execute(text('UPDATE perfis SET politica_escopo=:policy WHERE id=:id'), {'id': pid, 'policy': policy})
            c.execute(text("DELETE FROM perfil_permissoes WHERE perfil_id IN (SELECT id FROM perfis WHERE nome IN ('GERENTE','LEGADO_CUSTOM'))"))
            c.execute(text("DELETE FROM perfis WHERE nome IN ('GERENTE','LEGADO_CUSTOM')"))
        engine.dispose()


def test_tenant_sessao_mismatch_e_registro_local(base_url):
    a, engine_a = sessao(DB)
    b, engine_b = sessao(DB_B)
    try:
        ctx_a = contexto(a, DB, 'OPERADOR')
        user_b = b.execute(select(Usuario).where(Usuario.username == 'perfil_operador')).scalar_one()
        ctx_b = ContextoAdministrativo(DB_B, user_b.id, user_b.session_version)
        with pytest.raises(AdministracaoNegada):
            consultar_autorizado(b, ctx_a, 'USUARIO_PROPRIO_VISUALIZAR', select(Usuario), proprio=Usuario.id)
        stmt = consultar_autorizado(b, ctx_b, 'USUARIO_PROPRIO_VISUALIZAR', select(Usuario), proprio=Usuario.id)
        result = b.execute(stmt).scalars().all()
        assert [u.id for u in result] == [user_b.id]
        assert b.execute(stmt.where(Usuario.id != user_b.id)).scalar_one_or_none() is None
    finally:
        a.close(); b.close(); engine_a.dispose(); engine_b.dispose()


def test_leituras_e_senha_exigem_contexto_no_servico(base_url):
    from services.usuario_service import alterar_senha_usuario, buscar_usuario, listar_usuarios
    from services.cargo_service import buscar_cargo, listar_cargos
    from services.perfil_service import buscar_perfil, listar_perfis
    from services.permissao_service import buscar_permissao, listar_permissoes
    from services.perfil_permissao_service import listar_permissoes_perfil
    chamadas = [
        lambda: listar_usuarios(Config, DB), lambda: buscar_usuario(Config, DB, 1),
        lambda: listar_cargos(Config, DB), lambda: buscar_cargo(Config, DB, 1),
        lambda: listar_perfis(Config, DB), lambda: buscar_perfil(Config, DB, 1),
        lambda: listar_permissoes(Config, DB), lambda: buscar_permissao(Config, DB, 1),
        lambda: listar_permissoes_perfil(Config, DB, 1),
        lambda: alterar_senha_usuario(Config, DB, 1, 'antiga', 'nova'),
    ]
    for chamada in chamadas:
        with pytest.raises(AdministracaoNegada):
            chamada()
