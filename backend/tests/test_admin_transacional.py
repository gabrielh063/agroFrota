"""Administrative policy integration tests: only run through verified disposable bootstrap."""
import os
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
import requests
from sqlalchemy import text

from config import Config
from database.session import criar_sessao_tenant
from services.admin_policy import AdministracaoNegada
from services.usuario_service import atualizar_usuario

DB = os.environ.get('AGROFROTA_TEST_DATABASE', '')
DB_B = os.environ.get('AGROFROTA_TEST_DATABASE_B', '')


def sql(db=DB):
    factory, _ = criar_sessao_tenant(Config, db)
    return factory()


def login(base, db, username, password):
    r = requests.post(base + '/api/auth/login', json={'database_name': db, 'username': username, 'senha': password}, timeout=10)
    assert r.status_code == 200, r.text
    return {'Authorization': 'Bearer ' + r.json()['data']['access_token']}


def profile_id(session, name):
    return session.execute(text('SELECT id FROM perfis WHERE nome=:name'), {'name': name}).scalar_one()


def create_user(base, headers, profile, suffix=None, cargo=None):
    username = 'admin_test_' + (suffix or uuid.uuid4().hex[:10])
    r = requests.post(base + '/api/usuarios/', headers=headers, json={'nome': username, 'username': username, 'senha': 'Senha@12345', 'perfil_id': profile, 'cargo_id': cargo}, timeout=10)
    assert r.status_code == 201, r.text
    return r.json()['data']


def delete_user(session, user_id):
    session.execute(text('DELETE FROM usuarios WHERE id=:id'), {'id': user_id})
    session.commit()


def test_contexto_obrigatorio_no_servico():
    with pytest.raises(AdministracaoNegada):
        atualizar_usuario(Config, DB, usuario_id=1, nome='Sem contexto')


def test_politica_e_ultimo_admin(base_url, auth_headers):
    session = sql()
    manager = profile_id(session, 'GERENTE')
    operator = profile_id(session, 'OPERADOR')
    admin_id = session.execute(text('SELECT id FROM usuarios WHERE username=:name'), {'name': os.environ['AGROFROTA_TEST_USERNAME']}).scalar_one()
    user = None
    profile = None
    try:
        # The seeded legacy manager has real administrative authority.
        user = create_user(base_url, auth_headers, operator)
        response = requests.put(f"{base_url}/api/usuarios/{user['id']}", headers=auth_headers, json={'nome': 'Operador atualizado'}, timeout=10)
        assert response.status_code == 200, response.text
        operator_token = login(base_url, DB, user['username'], 'Senha@12345')
        assert requests.put(f"{base_url}/api/usuarios/{user['id']}", headers=operator_token, json={'perfil_id': manager}, timeout=10).status_code == 403
        assert requests.post(base_url + '/api/perfis/', headers=operator_token, json={'nome': 'Negado'}, timeout=10).status_code == 403
        # A cargo called manager grants nothing to an operator.
        cargo = session.execute(text("SELECT id FROM cargos WHERE nome='Gerente'")).scalar_one()
        assert requests.put(f"{base_url}/api/usuarios/{user['id']}", headers=auth_headers, json={'cargo_id': cargo}, timeout=10).status_code == 200
        assert requests.post(base_url + '/api/perfis/', headers=operator_token, json={'nome': 'AindaNegado'}, timeout=10).status_code == 403
        # Sole admin cannot be removed via either endpoint; denied mutation rolls back other fields.
        for method, path, body in [('patch', f'/api/usuarios/{admin_id}/desativar', None), ('put', f'/api/usuarios/{admin_id}', {'ativo': False, 'nome': 'NaoPersistir'})]:
            response = requests.request(method, base_url + path, headers=auth_headers, json=body, timeout=10)
            assert response.status_code == 403, response.text
        session.rollback()
        row = session.execute(text('SELECT nome, ativo FROM usuarios WHERE id=:id'), {'id': admin_id}).one()
        assert row.nome != 'NaoPersistir' and row.ativo == 1
        assert requests.put(f'{base_url}/api/usuarios/{admin_id}', headers=auth_headers, json={'perfil_id': operator}, timeout=10).status_code == 403
        assert requests.put(f'{base_url}/api/perfis/{manager}', headers=auth_headers, json={'descricao': 'Alteração própria'}, timeout=10).status_code == 403
        assert requests.patch(f'{base_url}/api/perfis/{manager}/desativar', headers=auth_headers, timeout=10).status_code == 403
        perm = session.execute(text("SELECT id FROM permissoes WHERE codigo='USUARIO_CRIAR'")).scalar_one()
        assert requests.delete(f'{base_url}/api/perfis/{manager}/permissoes/{perm}', headers=auth_headers, timeout=10).status_code == 403
        # Profiles containing permissions the actor does not possess cannot be delegated or changed.
        suffix = uuid.uuid4().hex[:10]
        session.execute(text('INSERT INTO permissoes (codigo) VALUES (:codigo)'), {'codigo': 'EXTRA_' + suffix})
        extra = session.execute(text('SELECT id FROM permissoes WHERE codigo=:codigo'), {'codigo': 'EXTRA_' + suffix}).scalar_one()
        session.execute(text('INSERT INTO perfis (nome, ativo) VALUES (:nome, 1)'), {'nome': 'EXTRA_' + suffix})
        profile = session.execute(text('SELECT id FROM perfis WHERE nome=:nome'), {'nome': 'EXTRA_' + suffix}).scalar_one()
        session.execute(text('INSERT INTO perfil_permissoes (perfil_id, permissao_id) VALUES (:p,:v)'), {'p': profile, 'v': extra})
        session.commit()
        r = requests.post(base_url + '/api/usuarios/', headers=auth_headers, json={'nome': 'Negado', 'username': 'negado_' + suffix, 'senha': 'Senha@12345', 'perfil_id': profile}, timeout=10)
        assert r.status_code == 403
        assert requests.put(f"{base_url}/api/usuarios/{user['id']}", headers=auth_headers, json={'perfil_id': profile}, timeout=10).status_code == 403
        assert requests.post(f'{base_url}/api/perfis/{operator}/permissoes', headers=auth_headers, json={'permissao_id': extra}, timeout=10).status_code == 403
        assert requests.post(f'{base_url}/api/perfis/{manager}/permissoes', headers=auth_headers, json={'permissao_id': extra}, timeout=10).status_code == 403
        # Renaming a permission cannot grant authority via an alternate route.
        assert requests.put(f'{base_url}/api/permissoes/{perm}', headers=auth_headers, json={'codigo': 'EXTRA_' + suffix}, timeout=10).status_code == 403
    finally:
        session.rollback()
        if profile is not None:
            session.execute(text('DELETE FROM perfil_permissoes WHERE perfil_id=:id'), {'id': profile})
            session.execute(text('DELETE FROM perfis WHERE id=:id'), {'id': profile})
            session.execute(text('DELETE FROM permissoes WHERE id=:id'), {'id': extra})
        if user:
            session.execute(text('DELETE FROM usuarios WHERE id=:id'), {'id': user['id']})
        session.commit()
        session.close()


def test_perda_de_perfil_e_token_antigo(base_url, auth_headers):
    session = sql()
    manager, operator = profile_id(session, 'GERENTE'), profile_id(session, 'OPERADOR')
    user = create_user(base_url, auth_headers, manager)
    try:
        old = login(base_url, DB, user['username'], 'Senha@12345')
        assert requests.put(f"{base_url}/api/usuarios/{user['id']}", headers=auth_headers, json={'perfil_id': operator}, timeout=10).status_code == 200
        assert requests.post(base_url + '/api/perfis/', headers=old, json={'nome': 'TokenAntigo'}, timeout=10).status_code == 403
    finally:
        delete_user(session, user['id'])
        session.close()


def test_concorrencia_entre_dois_administradores(base_url):
    session = sql(DB_B)
    manager = profile_id(session, 'GERENTE')
    first_id = session.execute(text('SELECT id FROM usuarios WHERE username=:name'), {'name': os.environ['AGROFROTA_TEST_USERNAME_B']}).scalar_one()
    first = login(base_url, DB_B, os.environ['AGROFROTA_TEST_USERNAME_B'], os.environ['AGROFROTA_TEST_PASSWORD_B'])
    second_user = create_user(base_url, first, manager)
    second = login(base_url, DB_B, second_user['username'], 'Senha@12345')
    barrier = threading.Barrier(2, timeout=10)
    def disable(headers, target):
        barrier.wait()
        return requests.patch(f'{base_url}/api/usuarios/{target}/desativar', headers=headers, timeout=15).status_code
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(disable, first, second_user['id']), pool.submit(disable, second, first_id)]
            statuses = sorted(f.result(timeout=20) for f in futures)
        # The losing request can be rejected either by middleware after its
        # actor was deactivated (401), or by the serialized service (403).
        assert statuses[0] == 200 and statuses[1] in (401, 403)
        session.rollback()
        states = session.execute(text('SELECT ativo FROM usuarios WHERE id IN (:a,:b) ORDER BY id'), {'a': first_id, 'b': second_user['id']}).scalars().all()
        assert sorted(states) == [0, 1]
    finally:
        session.rollback()
        session.execute(text('UPDATE usuarios SET ativo=1 WHERE id=:id'), {'id': first_id})
        session.execute(text('DELETE FROM usuarios WHERE id=:id'), {'id': second_user['id']})
        session.commit()
        session.close()


def test_delegacao_limitada_e_autoalteracao(base_url, auth_headers):
    session = sql()
    suffix = uuid.uuid4().hex[:10]
    manager = profile_id(session, 'GERENTE')
    # Build a synthetic administrative profile with only the minimum capabilities.
    required = ('USUARIO_CRIAR', 'USUARIO_EDITAR', 'USUARIO_DESATIVAR', 'PERFIL_CRIAR', 'PERFIL_EDITAR', 'PERFIL_PERMISSAO_GERENCIAR')
    session.execute(text('INSERT INTO perfis (nome, ativo) VALUES (:nome, 1)'), {'nome': 'LIMITADO_' + suffix})
    limited = session.execute(text('SELECT id FROM perfis WHERE nome=:nome'), {'nome': 'LIMITADO_' + suffix}).scalar_one()
    for code in required:
        session.execute(text('INSERT INTO perfil_permissoes (perfil_id, permissao_id) SELECT :id, id FROM permissoes WHERE codigo=:code'), {'id': limited, 'code': code})
    session.commit()
    user = create_user(base_url, auth_headers, limited)
    try:
        headers = login(base_url, DB, user['username'], 'Senha@12345')
        assert requests.put(f"{base_url}/api/usuarios/{user['id']}", headers=headers, json={'perfil_id': manager}, timeout=10).status_code == 403
        r = requests.post(base_url + '/api/usuarios/', headers=headers, json={'nome': 'Negado', 'username': 'negado_' + suffix, 'senha': 'Senha@12345', 'perfil_id': manager}, timeout=10)
        assert r.status_code == 403
        extra = session.execute(text("SELECT id FROM permissoes WHERE codigo='OS.EDITAR'")).scalar_one()
        assert requests.post(f'{base_url}/api/perfis/{limited}/permissoes', headers=headers, json={'permissao_id': extra}, timeout=10).status_code == 403
        # Even another profile cannot acquire a permission outside the actor's set.
        operator = profile_id(session, 'OPERADOR')
        assert requests.post(f'{base_url}/api/perfis/{operator}/permissoes', headers=headers, json={'permissao_id': extra}, timeout=10).status_code == 403
    finally:
        session.rollback()
        session.execute(text('DELETE FROM usuarios WHERE id=:id'), {'id': user['id']})
        session.execute(text('DELETE FROM perfil_permissoes WHERE perfil_id=:id'), {'id': limited})
        session.execute(text('DELETE FROM perfis WHERE id=:id'), {'id': limited})
        session.commit()
        session.close()


def test_objeto_de_outro_tenant_nao_e_alterado(base_url, auth_headers):
    other = sql(DB_B)
    marker = 'OUTRO_' + uuid.uuid4().hex[:10]
    other.execute(text('INSERT INTO perfis (id, nome, ativo) VALUES (900001, :nome, 1)'), {'nome': marker})
    other.commit()
    try:
        response = requests.put(base_url + '/api/perfis/900001', headers=auth_headers, json={'nome': 'INVASAO'}, timeout=10)
        assert response.status_code in (403, 404), response.text
        other.rollback()
        assert other.execute(text('SELECT nome FROM perfis WHERE id=900001')).scalar_one() == marker
    finally:
        other.rollback()
        other.execute(text('DELETE FROM perfis WHERE id=900001'))
        other.commit()
        other.close()


def test_remocao_de_admin_com_outro_preservado(base_url, auth_headers):
    session = sql()
    manager = profile_id(session, 'GERENTE')
    user = create_user(base_url, auth_headers, manager)
    try:
        response = requests.patch(f"{base_url}/api/usuarios/{user['id']}/desativar", headers=auth_headers, timeout=10)
        assert response.status_code == 200, response.text
        session.rollback()
        assert session.execute(text('SELECT COUNT(*) FROM usuarios WHERE ativo=1 AND perfil_id=:perfil'), {'perfil': manager}).scalar_one() >= 1
    finally:
        delete_user(session, user['id'])
        session.close()


def test_permissoes_genericas_nao_concedem_administracao(base_url, auth_headers):
    session = sql()
    suffix = uuid.uuid4().hex[:10]
    session.execute(text('INSERT INTO perfis (nome, ativo) VALUES (:nome, 1)'), {'nome': 'GEN_' + suffix})
    profile = session.execute(text('SELECT id FROM perfis WHERE nome=:nome'), {'nome': 'GEN_' + suffix}).scalar_one()
    session.execute(text("INSERT INTO perfil_permissoes (perfil_id, permissao_id) SELECT :id, id FROM permissoes WHERE codigo IN ('USUARIO_EDITAR','PERFIL_EDITAR')"), {'id': profile})
    session.commit()
    user = create_user(base_url, auth_headers, profile)
    try:
        headers = login(base_url, DB, user['username'], 'Senha@12345')
        assert requests.put(f"{base_url}/api/usuarios/{user['id']}", headers=headers, json={'nome': 'Negado'}, timeout=10).status_code == 403
        assert requests.put(f'{base_url}/api/perfis/{profile}', headers=headers, json={'nome': 'Negado'}, timeout=10).status_code == 403
    finally:
        session.rollback()
        session.execute(text('DELETE FROM usuarios WHERE id=:id'), {'id': user['id']})
        session.execute(text('DELETE FROM perfil_permissoes WHERE perfil_id=:id'), {'id': profile})
        session.execute(text('DELETE FROM perfis WHERE id=:id'), {'id': profile})
        session.commit()
        session.close()


def test_servicos_concorrentes_serializados(base_url):
    from unittest.mock import patch
    from services.admin_policy import ContextoAdministrativo, autorizar as original

    session = sql(DB_B)
    manager = profile_id(session, 'GERENTE')
    first_id = session.execute(text('SELECT id FROM usuarios WHERE username=:name'), {'name': os.environ['AGROFROTA_TEST_USERNAME_B']}).scalar_one()
    first_headers = login(base_url, DB_B, os.environ['AGROFROTA_TEST_USERNAME_B'], os.environ['AGROFROTA_TEST_PASSWORD_B'])
    second = create_user(base_url, first_headers, manager)
    session.rollback()
    versions = dict(session.execute(text('SELECT id, session_version FROM usuarios WHERE id IN (:a, :b)'), {'a': first_id, 'b': second['id']}).all())
    barrier = threading.Barrier(2, timeout=10)

    def synchronized(session_, db, context, permission):
        barrier.wait()
        return original(session_, db, context, permission)

    def attempt(actor, target):
        try:
            atualizar_usuario(Config, DB_B, target, ativo=False,
                              contexto=ContextoAdministrativo(DB_B, actor, versions[actor]))
            return 'commit'
        except AdministracaoNegada:
            return 'negada'

    try:
        with patch('services.usuario_service.autorizar', synchronized):
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = [pool.submit(attempt, first_id, second['id']), pool.submit(attempt, second['id'], first_id)]
                assert sorted(f.result(timeout=20) for f in results) == ['commit', 'negada']
        session.rollback()
        active = session.execute(text('SELECT ativo FROM usuarios WHERE id IN (:a,:b)'), {'a': first_id, 'b': second['id']}).scalars().all()
        assert sorted(active) == [0, 1]
    finally:
        session.rollback()
        session.execute(text('UPDATE usuarios SET ativo=1 WHERE id=:id'), {'id': first_id})
        session.execute(text('DELETE FROM usuarios WHERE id=:id'), {'id': second['id']})
        session.commit()
        session.close()


def test_admin_gerencia_permissoes_de_outro_perfil(base_url, auth_headers):
    session = sql()
    suffix = uuid.uuid4().hex[:10]
    session.execute(text('INSERT INTO perfis (nome, ativo) VALUES (:nome, 1)'), {'nome': 'GERENCIAVEL_' + suffix})
    profile = session.execute(text('SELECT id FROM perfis WHERE nome=:nome'), {'nome': 'GERENCIAVEL_' + suffix}).scalar_one()
    permission = session.execute(text("SELECT id FROM permissoes WHERE codigo='OS.EDITAR'")).scalar_one()
    session.commit()
    try:
        url = f'{base_url}/api/perfis/{profile}/permissoes'
        added = requests.post(url, headers=auth_headers, json={'permissao_id': permission}, timeout=10)
        assert added.status_code == 201, added.text
        removed = requests.delete(f'{url}/{permission}', headers=auth_headers, timeout=10)
        assert removed.status_code == 200, removed.text
    finally:
        session.rollback()
        session.execute(text('DELETE FROM perfil_permissoes WHERE perfil_id=:id'), {'id': profile})
        session.execute(text('DELETE FROM perfis WHERE id=:id'), {'id': profile})
        session.commit()
        session.close()
