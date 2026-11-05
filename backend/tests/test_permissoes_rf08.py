import os
import uuid

import pytest
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


@pytest.fixture(scope="module")
def usuario_operador(
    base_url,
    auth_headers,
):
    """
    Cria um usuário real com o perfil OPERADOR
    para validar o middleware de permissões.
    """

    session = abrir_sessao()

    try:
        perfil = session.execute(
            text("""
                SELECT id
                FROM perfis
                WHERE nome = 'OPERADOR'
                  AND ativo = 1
                LIMIT 1
            """)
        ).mappings().first()

        assert perfil is not None

        cargo = session.execute(
            text("""
                SELECT id
                FROM cargos
                WHERE ativo = 1
                ORDER BY id
                LIMIT 1
            """)
        ).mappings().first()

        assert cargo is not None

        perfil_id = perfil["id"]
        cargo_id = cargo["id"]

    finally:
        session.close()

    sufixo = uuid.uuid4().hex[:10]

    username = (
        f"operador_teste_{sufixo}"
    )

    senha = "Teste@1234"

    resposta = requests.post(
        f"{base_url}/api/usuarios/",
        headers=auth_headers,
        json={
            "nome":
                "Operador Teste RF08",
            "username":
                username,
            "senha":
                senha,
            "cargo_id":
                cargo_id,
            "perfil_id":
                perfil_id,
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    usuario = resposta.json()["data"]

    yield {
        "id":
            usuario["id"],
        "username":
            username,
        "senha":
            senha,
        "perfil_id":
            perfil_id,
        "cargo_id":
            cargo_id,
    }

    # Limpeza independente do resultado dos testes.
    session = abrir_sessao()

    try:
        session.execute(
            text("""
                DELETE FROM usuarios
                WHERE id = :usuario_id
            """),
            {
                "usuario_id":
                    usuario["id"]
            },
        )

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


@pytest.fixture(scope="module")
def operador_headers(
    base_url,
    usuario_operador,
):
    resposta = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "username":
                usuario_operador[
                    "username"
                ],
            "senha":
                usuario_operador[
                    "senha"
                ],
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


def buscar_perfil_operador(
    base_url,
    auth_headers,
):
    resposta = requests.get(
        f"{base_url}/api/perfis/",
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    perfis = resposta.json()["data"]

    return next(
        (
            perfil
            for perfil in perfis
            if perfil["nome"] == "OPERADOR"
        ),
        None,
    )


def test_seed_possui_perfil_operador(
    base_url,
    auth_headers,
):
    perfil = buscar_perfil_operador(
        base_url,
        auth_headers,
    )

    assert perfil is not None

    assert perfil["ativo"] is True


def test_seed_permissoes_operador(
    base_url,
    auth_headers,
):
    perfil = buscar_perfil_operador(
        base_url,
        auth_headers,
    )

    resposta = requests.get(
        (
            f"{base_url}/api/perfis/"
            f"{perfil['id']}/permissoes"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    codigos = {
        permissao["codigo"]
        for permissao
        in resposta.json()["data"]
    }

    # OPERADOR deve possuir.
    assert "OS.CRIAR" in codigos
    assert "OS.VISUALIZAR" in codigos

    assert (
        "MAQUINA_VISUALIZAR"
        in codigos
    )

    assert (
        "EQUIPAMENTO_VISUALIZAR"
        in codigos
    )

    assert (
        "INDISPONIBILIDADE.CRIAR"
        in codigos
    )

    # OPERADOR não deve possuir.
    assert "OS.EDITAR" not in codigos
    assert "OS.CONCLUIR" not in codigos
    assert "OS.CANCELAR" not in codigos

    assert (
        "USUARIO_CRIAR"
        not in codigos
    )

    assert (
        "USUARIO_VISUALIZAR"
        not in codigos
    )

    assert (
        "MAQUINA_CRIAR"
        not in codigos
    )

    assert (
        "EQUIPAMENTO_CRIAR"
        not in codigos
    )


def test_operador_pode_visualizar_os(
    base_url,
    operador_headers,
):
    resposta = requests.get(
        f"{base_url}/api/ordens-servico/",
        headers=operador_headers,
        timeout=10,
    )

    assert resposta.status_code == 200


def test_operador_pode_criar_os(
    base_url,
    auth_headers,
    operador_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    # A máquina é criada pelo gerente/admin,
    # já que o OPERADOR não possui
    # MAQUINA_CRIAR.

    resposta = requests.post(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        json={
            "identificacao":
                f"RF08-MAQ-{codigo_unico}",
            "modelo":
                "Modelo RF08",
            "fabricante":
                "Fabricante Teste",
            "ano":
                2025,
            "status":
                "OPERANDO",
            "controla_telemetria":
                False,
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    maquina = resposta.json()["data"]

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    resposta = requests.post(
        f"{base_url}/api/ordens-servico/",
        headers=operador_headers,
        json={
            "tipo":
                "SERVICO",
            "titulo":
                "OS criada por OPERADOR",
            "descricao":
                "Teste RF08",
            "maquina_id":
                maquina["id"],
            "prioridade":
                "MEDIA",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    ordem = resposta.json()[
        "ordem_servico"
    ]

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )


def test_operador_nao_pode_editar_os(
    base_url,
    operador_headers,
):
    resposta = requests.put(
        (
            f"{base_url}/api/ordens-servico/"
            "987654321"
        ),
        headers=operador_headers,
        json={
            "titulo":
                "Tentativa indevida"
        },
        timeout=10,
    )

    # A permissão deve ser verificada
    # antes mesmo de verificar o ID.
    assert resposta.status_code == 403

    dados = resposta.json()

    assert dados["success"] is False

    assert "OS.EDITAR" in dados["message"]


def test_operador_nao_pode_concluir_os(
    base_url,
    operador_headers,
):
    resposta = requests.patch(
        (
            f"{base_url}/api/ordens-servico/"
            "987654321/concluir"
        ),
        headers=operador_headers,
        timeout=10,
    )

    assert resposta.status_code == 403

    assert (
        "OS.CONCLUIR"
        in resposta.json()["message"]
    )


def test_operador_nao_pode_cancelar_os(
    base_url,
    operador_headers,
):
    resposta = requests.patch(
        (
            f"{base_url}/api/ordens-servico/"
            "987654321/cancelar"
        ),
        headers=operador_headers,
        timeout=10,
    )

    assert resposta.status_code == 403

    assert (
        "OS.CANCELAR"
        in resposta.json()["message"]
    )


def test_operador_nao_pode_listar_usuarios(
    base_url,
    operador_headers,
):
    resposta = requests.get(
        f"{base_url}/api/usuarios/",
        headers=operador_headers,
        timeout=10,
    )

    assert resposta.status_code == 403

    assert (
        "USUARIO_VISUALIZAR"
        in resposta.json()["message"]
    )


def test_operador_nao_pode_criar_usuario(
    base_url,
    operador_headers,
):
    resposta = requests.post(
        f"{base_url}/api/usuarios/",
        headers=operador_headers,
        json={},
        timeout=10,
    )

    # Mesmo com corpo inválido,
    # a autorização deve acontecer antes.
    assert resposta.status_code == 403

    assert (
        "USUARIO_CRIAR"
        in resposta.json()["message"]
    )


def test_operador_nao_pode_editar_usuario(
    base_url,
    operador_headers,
):
    resposta = requests.put(
        (
            f"{base_url}/api/usuarios/"
            "987654321"
        ),
        headers=operador_headers,
        json={
            "nome":
                "Tentativa"
        },
        timeout=10,
    )

    assert resposta.status_code == 403

    assert (
        "USUARIO_EDITAR"
        in resposta.json()["message"]
    )


def test_operador_nao_pode_desativar_usuario(
    base_url,
    operador_headers,
):
    resposta = requests.patch(
        (
            f"{base_url}/api/usuarios/"
            "987654321/desativar"
        ),
        headers=operador_headers,
        timeout=10,
    )

    assert resposta.status_code == 403

    assert (
        "USUARIO_DESATIVAR"
        in resposta.json()["message"]
    )


def test_operador_pode_visualizar_maquinas(
    base_url,
    operador_headers,
):
    resposta = requests.get(
        f"{base_url}/api/maquinas/",
        headers=operador_headers,
        timeout=10,
    )

    assert resposta.status_code == 200


def test_operador_nao_pode_criar_maquina(
    base_url,
    operador_headers,
):
    resposta = requests.post(
        f"{base_url}/api/maquinas/",
        headers=operador_headers,
        json={},
        timeout=10,
    )

    # Deve parar na autorização,
    # não na validação do JSON.
    assert resposta.status_code == 403


def test_operador_nao_pode_editar_maquina(
    base_url,
    operador_headers,
):
    resposta = requests.put(
        (
            f"{base_url}/api/maquinas/"
            "987654321"
        ),
        headers=operador_headers,
        json={
            "modelo":
                "Tentativa RF08"
        },
        timeout=10,
    )

    assert resposta.status_code == 403


def test_operador_pode_visualizar_equipamentos(
    base_url,
    operador_headers,
):
    resposta = requests.get(
        f"{base_url}/api/equipamentos/",
        headers=operador_headers,
        timeout=10,
    )

    assert resposta.status_code == 200


def test_operador_nao_pode_criar_equipamento(
    base_url,
    operador_headers,
):
    resposta = requests.post(
        f"{base_url}/api/equipamentos/",
        headers=operador_headers,
        json={},
        timeout=10,
    )

    assert resposta.status_code == 403


def test_operador_nao_pode_editar_equipamento(
    base_url,
    operador_headers,
):
    resposta = requests.put(
        (
            f"{base_url}/api/equipamentos/"
            "987654321"
        ),
        headers=operador_headers,
        json={
            "nome":
                "Tentativa RF08"
        },
        timeout=10,
    )

    assert resposta.status_code == 403


def test_operador_nao_pode_listar_perfis(
    base_url,
    operador_headers,
):
    """
    OPERADOR não possui PERFIL_VISUALIZAR.
    """

    resposta = requests.get(
        f"{base_url}/api/perfis/",
        headers=operador_headers,
        timeout=10,
    )

    assert resposta.status_code == 403


def test_operador_nao_pode_criar_perfil(
    base_url,
    operador_headers,
):
    resposta = requests.post(
        f"{base_url}/api/perfis/",
        headers=operador_headers,
        json={},
        timeout=10,
    )

    assert resposta.status_code == 403


def test_operador_nao_pode_listar_permissoes(
    base_url,
    operador_headers,
):
    """
    O catálogo de permissões é administrativo.
    """

    resposta = requests.get(
        f"{base_url}/api/permissoes/",
        headers=operador_headers,
        timeout=10,
    )

    assert resposta.status_code == 403


def test_operador_nao_pode_gerenciar_permissoes_perfil(
    base_url,
    operador_headers,
    usuario_operador,
):
    resposta = requests.get(
        (
            f"{base_url}/api/perfis/"
            f"{usuario_operador['perfil_id']}"
            "/permissoes"
        ),
        headers=operador_headers,
        timeout=10,
    )

    assert resposta.status_code == 403


def test_perfil_inativo_bloqueia_acesso(
    base_url,
    operador_headers,
    usuario_operador,
):
    """
    Mesmo com JWT válido, perfil inativo
    deve ser bloqueado pelo middleware.
    """

    session = abrir_sessao()

    try:
        session.execute(
            text("""
                UPDATE perfis
                SET ativo = 0
                WHERE id = :perfil_id
            """),
            {
                "perfil_id":
                    usuario_operador[
                        "perfil_id"
                    ]
            },
        )

        session.commit()

        resposta = requests.get(
            f"{base_url}/api/ordens-servico/",
            headers=operador_headers,
            timeout=10,
        )

        assert resposta.status_code == 403

        dados = resposta.json()

        assert dados["success"] is False

        assert (
            dados["message"]
            ==
            "Perfil não encontrado ou inativo."
        )

    finally:
        session.rollback()

        session.execute(
            text("""
                UPDATE perfis
                SET ativo = 1
                WHERE id = :perfil_id
            """),
            {
                "perfil_id":
                    usuario_operador[
                        "perfil_id"
                    ]
            },
        )

        session.commit()
        session.close()


def test_rf08_sem_token(
    base_url,
):
    resposta = requests.get(
        f"{base_url}/api/usuarios/",
        timeout=10,
    )

    assert resposta.status_code == 401