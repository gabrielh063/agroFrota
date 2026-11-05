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
    ""
)

USERNAME = os.getenv(
    "AGROFROTA_TEST_USERNAME",
    ""
)

PASSWORD = os.getenv(
    "AGROFROTA_TEST_PASSWORD",
    ""
)


def _exigir_ambiente_descartavel():
    """Fail closed before HTTP tests or destructive fixture cleanup."""
    from urllib.parse import urlparse

    host = urlparse(BASE_URL).hostname
    if (os.getenv("AGROFROTA_TEST_DISPOSABLE") != "1"
            or host not in {"127.0.0.1", "localhost", "::1"}
            or Config.DB_HOST not in {"127.0.0.1", "localhost", "::1"}
            or not DATABASE_NAME.startswith("agrofrota_test_")
            or not Config.DB_NAME.startswith("agrofrota_test_")):
        pytest.fail("Testes de integração exigem ambiente descartável local explícito e banco agrofrota_test_*. ", pytrace=False)

    # The server must identify itself as the dedicated disposable instance.
    expected_dir = os.getenv("AGROFROTA_TEST_DATADIR", "")
    marker = os.getenv("AGROFROTA_TEST_MARKER", "")
    if not expected_dir.startswith("/tmp/agrofrota-db-") or len(marker) < 32:
        pytest.fail("Identidade do servidor descartável ausente.", pytrace=False)
    from database.session import criar_sessao_central
    Session, engine = criar_sessao_central(Config)
    try:
        with Session() as session:
            datadir = session.execute(text("SELECT @@datadir")).scalar_one()
            found = session.execute(text("SELECT marker FROM disposable_marker LIMIT 1")).scalar_one()
        if os.path.realpath(datadir) != os.path.realpath(expected_dir) or found != marker:
            pytest.fail("Identidade do servidor descartável não confere.", pytrace=False)
    except Exception:
        pytest.fail("Não foi possível verificar a identidade do servidor descartável.", pytrace=False)
    finally:
        engine.dispose()


@pytest.fixture(autouse=True)
def _validar_segundo_tenant(request):
    if request.node.path.name in {"test_multitenant.py", "test_permissoes_rf08.py", "test_revogacao_acesso.py"}:
        _exigir_ambiente_descartavel()
    if request.node.path.name == "test_multitenant.py":
        other = os.getenv("AGROFROTA_TEST_DATABASE_B", "")
        if not other.startswith("agrofrota_test_") or other == DATABASE_NAME:
            pytest.fail("Segundo tenant descartável distinto é obrigatório.", pytrace=False)


@pytest.fixture(scope="session")
def base_url():
    _exigir_ambiente_descartavel()
    return BASE_URL


@pytest.fixture(scope="session")
def token():

    _exigir_ambiente_descartavel()
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

    _exigir_ambiente_descartavel()
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