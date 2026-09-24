import sys
from pathlib import Path
import os
import uuid

import pytest
import requests

from sqlalchemy import text

from config import Config
from database.session import criar_sessao_tenant


BACKEND_DIR = Path(
    __file__
).resolve().parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(BACKEND_DIR)
    )


BASE_URL = os.getenv(
    "AGROFROTA_BASE_URL",
    "http://127.0.0.1:5001"
)

DATABASE_NAME = os.getenv(
    "AGROFROTA_TEST_DATABASE",
    "tenant_000004"
)

USERNAME = os.getenv(
    "AGROFROTA_TEST_USERNAME",
    "admin"
)

PASSWORD = os.getenv(
    "AGROFROTA_TEST_PASSWORD",
    "Admin@123"
)


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def token():

    resposta = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": USERNAME,
            "senha": PASSWORD,
            "database_name": DATABASE_NAME,
        },
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True
    assert "access_token" in dados["data"]

    return dados["data"]["access_token"]


@pytest.fixture(scope="session")
def auth_headers(token):

    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


@pytest.fixture
def codigo_unico():
    """
    Gera um código único para cada teste.

    Isso evita conflito com registros antigos
    ou com execuções anteriores dos testes.
    """

    return uuid.uuid4().hex[:10].upper()


@pytest.fixture
def cleanup_registros_teste():
    """
    Remove do banco os registros criados
    durante os testes.

    Atualmente utilizada para máquinas
    e equipamentos.
    """

    registros = []

    def registrar(
        tabela: str,
        registro_id: int,
    ):
        registros.append(
            (
                tabela,
                registro_id,
            )
        )

    yield registrar

    tabelas_permitidas = {
        "maquinas",
        "equipamentos",
        "ordens_servico",
        "agendamentos",
        "manutencoes",
        "indisponibilidades",
    }

    if not registros:
        return

    SessionTenant, _ = criar_sessao_tenant(
        Config,
        DATABASE_NAME,
    )

    session = SessionTenant()

    try:

        for tabela, registro_id in reversed(
            registros
        ):

            if tabela not in tabelas_permitidas:
                continue

            session.execute(
                text(
                    f"""
                    DELETE FROM {tabela}
                    WHERE id = :registro_id
                    """
                ),
                {
                    "registro_id":
                        registro_id
                },
            )

        session.commit()

    except Exception:

        session.rollback()
        raise

    finally:

        session.close()