import os
import uuid

import requests
from sqlalchemy import text

from config import Config
from database.session import criar_sessao_tenant


DATABASE_NAME = os.environ.get("AGROFROTA_TEST_DATABASE", "")


def abrir_sessao():
    SessionTenant, _ = criar_sessao_tenant(
        Config,
        DATABASE_NAME,
    )

    return SessionTenant()


def buscar_ids_gerente_operador_cargo():
    session = abrir_sessao()

    try:
        gerente_id = session.execute(
            text("""
                SELECT id
                FROM perfis
                WHERE nome = 'ADMIN_EMPRESA'
                  AND ativo = 1
                LIMIT 1
            """)
        ).scalar_one()

        operador_id = session.execute(
            text("""
                SELECT id
                FROM perfis
                WHERE nome = 'OPERADOR'
                  AND ativo = 1
                LIMIT 1
            """)
        ).scalar_one()

        cargo_id = session.execute(
            text("""
                SELECT id
                FROM cargos
                WHERE ativo = 1
                ORDER BY id
                LIMIT 1
            """)
        ).scalar_one()

        return (
            gerente_id,
            operador_id,
            cargo_id,
        )

    finally:
        session.close()


def criar_usuario_teste(
    base_url,
    auth_headers,
):
    (
        gerente_id,
        operador_id,
        cargo_id,
    ) = buscar_ids_gerente_operador_cargo()

    sufixo = uuid.uuid4().hex[:10]

    username = f"revogacao_{sufixo}"
    senha = "Revogacao@123"

    resposta = requests.post(
        f"{base_url}/api/usuarios/",
        headers=auth_headers,
        json={
            "nome":
                "Usuário Teste Revogação",
            "username":
                username,
            "senha":
                senha,
            "cargo_id":
                cargo_id,
            "perfil_id":
                gerente_id,
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    usuario = resposta.json()["data"]

    return {
        "id":
            usuario["id"],
        "username":
            username,
        "senha":
            senha,
        "gerente_id":
            gerente_id,
        "operador_id":
            operador_id,
    }


def login_usuario(
    base_url,
    usuario,
):
    resposta = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "username":
                usuario["username"],
            "senha":
                usuario["senha"],
            "database_name":
                DATABASE_NAME,
        },
        timeout=10,
    )

    assert resposta.status_code == 200

    token = resposta.json()[
        "data"
    ]["access_token"]

    return {
        "Authorization":
            f"Bearer {token}",
        "Content-Type":
            "application/json",
    }


def excluir_usuario_teste(
    usuario_id,
):
    session = abrir_sessao()

    try:
        session.execute(
            text("""
                DELETE FROM usuarios
                WHERE id = :usuario_id
            """),
            {
                "usuario_id":
                    usuario_id
            },
        )

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def test_usuario_ativo_com_token_valido(
    base_url,
    auth_headers,
):
    usuario = criar_usuario_teste(
        base_url,
        auth_headers,
    )

    try:
        headers = login_usuario(
            base_url,
            usuario,
        )

        resposta = requests.get(
            f"{base_url}/api/usuarios/",
            headers=headers,
            timeout=10,
        )

        assert resposta.status_code == 200

    finally:
        excluir_usuario_teste(
            usuario["id"]
        )


def test_token_usuario_desativado_deve_ser_bloqueado(
    base_url,
    auth_headers,
):
    usuario = criar_usuario_teste(
        base_url,
        auth_headers,
    )

    headers = login_usuario(
        base_url,
        usuario,
    )

    session = abrir_sessao()

    try:
        session.execute(
            text("""
                UPDATE usuarios
                SET ativo = 0
                WHERE id = :usuario_id
            """),
            {
                "usuario_id":
                    usuario["id"]
            },
        )

        session.commit()

        resposta = requests.get(
            f"{base_url}/api/usuarios/",
            headers=headers,
            timeout=10,
        )

        # Um usuário desativado não deve continuar
        # utilizando um JWT emitido anteriormente.
        assert resposta.status_code == 401

        dados = resposta.json()

        assert dados["success"] is False

    finally:
        session.rollback()

        session.execute(
            text("""
                UPDATE usuarios
                SET ativo = 1
                WHERE id = :usuario_id
            """),
            {
                "usuario_id":
                    usuario["id"]
            },
        )

        session.commit()
        session.close()

        excluir_usuario_teste(
            usuario["id"]
        )


def test_token_antigo_nao_deve_manter_perfil_gerente(
    base_url,
    auth_headers,
):
    usuario = criar_usuario_teste(
        base_url,
        auth_headers,
    )

    headers = login_usuario(
        base_url,
        usuario,
    )

    session = abrir_sessao()

    try:
        # O token foi emitido enquanto o usuário
        # era GERENTE.
        #
        # Agora ele passa a ser OPERADOR.
        session.execute(
            text("""
                UPDATE usuarios
                SET perfil_id = :perfil_id
                WHERE id = :usuario_id
            """),
            {
                "perfil_id":
                    usuario["operador_id"],
                "usuario_id":
                    usuario["id"],
            },
        )

        session.commit()

        resposta = requests.get(
            f"{base_url}/api/usuarios/",
            headers=headers,
            timeout=10,
        )

        # OPERADOR não possui USUARIO_VISUALIZAR.
        #
        # O sistema deve usar o perfil ATUAL
        # armazenado no banco, e não continuar
        # confiando no perfil antigo do JWT.
        assert resposta.status_code == 403

        dados = resposta.json()

        assert dados["success"] is False

    finally:
        session.rollback()

        session.execute(
            text("""
                UPDATE usuarios
                SET perfil_id = :perfil_id
                WHERE id = :usuario_id
            """),
            {
                "perfil_id":
                    usuario["gerente_id"],
                "usuario_id":
                    usuario["id"],
            },
        )

        session.commit()
        session.close()

        excluir_usuario_teste(
            usuario["id"]
        )


def test_token_usuario_excluido_deve_ser_bloqueado(
    base_url,
    auth_headers,
):
    usuario = criar_usuario_teste(
        base_url,
        auth_headers,
    )

    headers = login_usuario(
        base_url,
        usuario,
    )

    # Remove o usuário depois de o JWT já
    # ter sido emitido.
    excluir_usuario_teste(
        usuario["id"]
    )

    resposta = requests.get(
        f"{base_url}/api/usuarios/",
        headers=headers,
        timeout=10,
    )

    assert resposta.status_code == 401

    assert (
        resposta.json()["success"]
        is False
    )

def test_logout_revoga_todas_as_sessoes_e_novo_login_funciona(base_url, auth_headers):
    usuario = criar_usuario_teste(base_url, auth_headers)
    try:
        primeira = login_usuario(base_url, usuario)
        segunda = login_usuario(base_url, usuario)
        assert requests.post(f"{base_url}/api/auth/logout", headers=primeira, timeout=10).status_code == 200
        for headers in (primeira, segunda):
            assert requests.get(f"{base_url}/api/usuarios/", headers=headers, timeout=10).status_code == 401
        nova = login_usuario(base_url, usuario)
        assert requests.get(f"{base_url}/api/usuarios/", headers=nova, timeout=10).status_code == 200
    finally:
        excluir_usuario_teste(usuario['id'])


def test_mudanca_de_senha_revoga_token_antigo(base_url, auth_headers):
    usuario = criar_usuario_teste(base_url, auth_headers)
    try:
        headers = login_usuario(base_url, usuario)
        resposta = requests.put(f"{base_url}/api/usuarios/{usuario['id']}/senha", headers=headers,
                                json={'senha_atual': usuario['senha'], 'nova_senha': 'OutraSenha@123'}, timeout=10)
        assert resposta.status_code == 200
        assert requests.get(f"{base_url}/api/usuarios/", headers=headers, timeout=10).status_code == 401
        usuario['senha'] = 'OutraSenha@123'
        nova = login_usuario(base_url, usuario)
        assert requests.get(f"{base_url}/api/usuarios/", headers=nova, timeout=10).status_code == 200
    finally:
        excluir_usuario_teste(usuario['id'])


def test_perfil_inativo_impede_login_e_rota_sem_permissao(base_url, auth_headers):
    usuario = criar_usuario_teste(base_url, auth_headers)
    headers = login_usuario(base_url, usuario)
    session = abrir_sessao()
    try:
        # Perfil exclusivo, para não afetar os demais usuários sintéticos.
        nome = 'INATIVO_' + uuid.uuid4().hex[:12]
        session.execute(text('INSERT INTO perfis (nome, ativo) VALUES (:nome, 1)'), {'nome': nome})
        perfil_id = session.execute(text('SELECT id FROM perfis WHERE nome = :nome'), {'nome': nome}).scalar_one()
        session.execute(text('UPDATE usuarios SET perfil_id = :perfil WHERE id = :id'), {'perfil': perfil_id, 'id': usuario['id']})
        session.commit()
        session.execute(text('UPDATE perfis SET ativo = 0 WHERE id = :id'), {'id': perfil_id})
        session.commit()
        assert requests.post(f'{base_url}/api/auth/logout', headers=headers, timeout=10).status_code == 403
        resposta = requests.post(f'{base_url}/api/auth/login', json={
            'username': usuario['username'], 'senha': usuario['senha'], 'database_name': DATABASE_NAME,
        }, timeout=10)
        assert resposta.status_code == 401
    finally:
        session.rollback()
        session.execute(text('UPDATE usuarios SET perfil_id = :perfil WHERE id = :id'), {'perfil': usuario['gerente_id'], 'id': usuario['id']})
        if 'perfil_id' in locals():
            session.execute(text('DELETE FROM perfis WHERE id = :id'), {'id': perfil_id})
        session.commit()
        session.close()
        excluir_usuario_teste(usuario['id'])
