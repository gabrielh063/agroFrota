import os
import uuid

import pytest
import requests
from sqlalchemy import select, text

from config import Config
from database.session import (
    criar_sessao_central,
    criar_sessao_tenant,
)
from models.central.tenant import Tenant


TENANT_A_ID = int(os.getenv("AGROFROTA_TEST_TENANT_A_ID", "4"))
TENANT_A_DB = os.getenv(
    "AGROFROTA_TEST_DATABASE",
    "",
)

TENANT_B_ID = int(os.getenv("AGROFROTA_TEST_TENANT_B_ID", "5"))
TENANT_B_DB = os.getenv(
    "AGROFROTA_TEST_DATABASE_B",
    "",
)

TENANT_B_USERNAME = os.getenv(
    "AGROFROTA_TEST_USERNAME_B",
    "",
)

TENANT_B_PASSWORD = os.getenv(
    "AGROFROTA_TEST_PASSWORD_B",
    "",
)


def abrir_sessao_tenant(
    database_name,
):
    SessionTenant, _ = criar_sessao_tenant(
        Config,
        database_name,
    )

    return SessionTenant()


def maquina_existe_no_banco(
    database_name,
    identificacao,
):
    session = abrir_sessao_tenant(
        database_name
    )

    try:
        resultado = session.execute(
            text("""
                SELECT
                    id,
                    identificacao
                FROM maquinas
                WHERE identificacao = :identificacao
                LIMIT 1
            """),
            {
                "identificacao":
                    identificacao
            },
        ).mappings().first()

        return resultado

    finally:
        session.close()


def excluir_maquina(
    database_name,
    maquina_id,
):
    session = abrir_sessao_tenant(
        database_name
    )

    try:
        session.execute(
            text("""
                DELETE FROM maquinas
                WHERE id = :maquina_id
            """),
            {
                "maquina_id":
                    maquina_id
            },
        )

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


@pytest.fixture(scope="module")
def token_tenant_b(
    base_url,
):
    resposta = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "username":
                TENANT_B_USERNAME,
            "senha":
                TENANT_B_PASSWORD,
            "database_name":
                TENANT_B_DB,
        },
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    assert (
        dados["data"]["tenant"]["id"]
        == TENANT_B_ID
    )

    assert (
        dados["data"]["tenant"]["database_name"]
        == TENANT_B_DB
    )

    return dados["data"]["access_token"]


@pytest.fixture(scope="module")
def headers_tenant_b(
    token_tenant_b,
):
    return {
        "Authorization":
            f"Bearer {token_tenant_b}",
        "Content-Type":
            "application/json",
    }


@pytest.fixture(scope="module")
def dados_isolamento(
    base_url,
    auth_headers,
    headers_tenant_b,
):
    """
    Cria uma máquina identificável em cada tenant.

    A limpeza é executada diretamente no banco correto
    ao final de toda a bateria.
    """

    sufixo = uuid.uuid4().hex[:10].upper()

    identificacao_a = (
        f"ISOLAMENTO-A-{sufixo}"
    )

    identificacao_b = (
        f"ISOLAMENTO-B-{sufixo}"
    )

    resposta_a = requests.post(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        json={
            "identificacao":
                identificacao_a,
            "modelo":
                "Modelo Tenant A",
            "fabricante":
                "AgroFrota Teste",
            "ano":
                2025,
            "localizacao":
                "Tenant A",
            "status":
                "OPERANDO",
            "controla_telemetria":
                False,
        },
        timeout=10,
    )

    assert resposta_a.status_code == 201

    maquina_a = resposta_a.json()["data"]

    resposta_b = requests.post(
        f"{base_url}/api/maquinas/",
        headers=headers_tenant_b,
        json={
            "identificacao":
                identificacao_b,
            "modelo":
                "Modelo Tenant B",
            "fabricante":
                "AgroFrota Teste",
            "ano":
                2025,
            "localizacao":
                "Tenant B",
            "status":
                "OPERANDO",
            "controla_telemetria":
                False,
        },
        timeout=10,
    )

    assert resposta_b.status_code == 201

    maquina_b = resposta_b.json()["data"]

    yield {
        "a": {
            "id":
                maquina_a["id"],
            "identificacao":
                identificacao_a,
        },
        "b": {
            "id":
                maquina_b["id"],
            "identificacao":
                identificacao_b,
        },
    }

    excluir_maquina(
        TENANT_A_DB,
        maquina_a["id"],
    )

    excluir_maquina(
        TENANT_B_DB,
        maquina_b["id"],
    )


def test_login_tenant_b_valido(
    base_url,
):
    resposta = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "username":
                TENANT_B_USERNAME,
            "senha":
                TENANT_B_PASSWORD,
            "database_name":
                TENANT_B_DB,
        },
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    assert (
        dados["data"]["tenant"]["id"]
        == TENANT_B_ID
    )

    assert (
        dados["data"]["tenant"]["database_name"]
        == TENANT_B_DB
    )


def test_credencial_tenant_b_nao_autentica_no_tenant_a(
    base_url,
):
    resposta = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "username":
                TENANT_B_USERNAME,
            "senha":
                TENANT_B_PASSWORD,
            "database_name":
                TENANT_A_DB,
        },
        timeout=10,
    )

    assert resposta.status_code == 401

    assert resposta.json()["success"] is False


def test_tenant_a_enxerga_apenas_sua_maquina(
    base_url,
    auth_headers,
    dados_isolamento,
):
    resposta = requests.get(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    maquinas = resposta.json()["data"]

    identificacoes = {
        maquina["identificacao"]
        for maquina in maquinas
    }

    assert (
        dados_isolamento["a"]["identificacao"]
        in identificacoes
    )

    assert (
        dados_isolamento["b"]["identificacao"]
        not in identificacoes
    )


def test_tenant_b_enxerga_apenas_sua_maquina(
    base_url,
    headers_tenant_b,
    dados_isolamento,
):
    resposta = requests.get(
        f"{base_url}/api/maquinas/",
        headers=headers_tenant_b,
        timeout=10,
    )

    assert resposta.status_code == 200

    maquinas = resposta.json()["data"]

    identificacoes = {
        maquina["identificacao"]
        for maquina in maquinas
    }

    assert (
        dados_isolamento["b"]["identificacao"]
        in identificacoes
    )

    assert (
        dados_isolamento["a"]["identificacao"]
        not in identificacoes
    )


def test_dados_foram_gravados_nos_bancos_corretos(
    dados_isolamento,
):
    maquina_a_no_a = maquina_existe_no_banco(
        TENANT_A_DB,
        dados_isolamento["a"]["identificacao"],
    )

    maquina_a_no_b = maquina_existe_no_banco(
        TENANT_B_DB,
        dados_isolamento["a"]["identificacao"],
    )

    maquina_b_no_b = maquina_existe_no_banco(
        TENANT_B_DB,
        dados_isolamento["b"]["identificacao"],
    )

    maquina_b_no_a = maquina_existe_no_banco(
        TENANT_A_DB,
        dados_isolamento["b"]["identificacao"],
    )

    assert maquina_a_no_a is not None
    assert maquina_a_no_b is None

    assert maquina_b_no_b is not None
    assert maquina_b_no_a is None


def test_header_nao_consegue_trocar_tenant(
    base_url,
    auth_headers,
    dados_isolamento,
):
    headers = dict(auth_headers)

    headers["X-Tenant-ID"] = str(
        TENANT_B_ID
    )

    headers["X-Database-Name"] = (
        TENANT_B_DB
    )

    resposta = requests.get(
        f"{base_url}/api/maquinas/",
        headers=headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    maquinas = resposta.json()["data"]

    identificacoes = {
        maquina["identificacao"]
        for maquina in maquinas
    }

    # O JWT continua sendo do tenant A.
    assert (
        dados_isolamento["a"]["identificacao"]
        in identificacoes
    )

    assert (
        dados_isolamento["b"]["identificacao"]
        not in identificacoes
    )


def test_querystring_nao_consegue_trocar_tenant(
    base_url,
    auth_headers,
    dados_isolamento,
):
    resposta = requests.get(
        (
            f"{base_url}/api/maquinas/"
            f"?tenant_id={TENANT_B_ID}"
            f"&database_name={TENANT_B_DB}"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    identificacoes = {
        maquina["identificacao"]
        for maquina
        in resposta.json()["data"]
    }

    assert (
        dados_isolamento["a"]["identificacao"]
        in identificacoes
    )

    assert (
        dados_isolamento["b"]["identificacao"]
        not in identificacoes
    )


def test_criacao_com_header_falso_permanece_no_tenant_do_jwt(
    base_url,
    auth_headers,
):
    sufixo = uuid.uuid4().hex[:10].upper()

    identificacao = (
        f"HEADER-FALSO-{sufixo}"
    )

    headers = dict(auth_headers)

    headers["X-Tenant-ID"] = str(
        TENANT_B_ID
    )

    headers["X-Database-Name"] = (
        TENANT_B_DB
    )

    resposta = requests.post(
        f"{base_url}/api/maquinas/",
        headers=headers,
        json={
            "identificacao":
                identificacao,
            "modelo":
                "Tentativa Troca Tenant",
            "fabricante":
                "AgroFrota",
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

    try:
        registro_a = maquina_existe_no_banco(
            TENANT_A_DB,
            identificacao,
        )

        registro_b = maquina_existe_no_banco(
            TENANT_B_DB,
            identificacao,
        )

        assert registro_a is not None
        assert registro_b is None

    finally:
        excluir_maquina(
            TENANT_A_DB,
            maquina["id"],
        )


def test_token_adulterado_e_rejeitado(
    base_url,
    token,
):
    partes = token.split(".")

    assert len(partes) == 3

    payload = partes[1]

    primeiro = payload[0]

    novo_primeiro = (
        "A"
        if primeiro != "A"
        else "B"
    )

    payload_adulterado = (
        novo_primeiro
        + payload[1:]
    )

    token_adulterado = ".".join([
        partes[0],
        payload_adulterado,
        partes[2],
    ])

    resposta = requests.get(
        f"{base_url}/api/maquinas/",
        headers={
            "Authorization":
                f"Bearer {token_adulterado}"
        },
        timeout=10,
    )

    assert resposta.status_code == 401

    assert resposta.json()["success"] is False


def test_tenant_inativo_bloqueia_token_existente(
    base_url,
    headers_tenant_b,
):
    SessionCentral, _ = criar_sessao_central(
        Config
    )

    session = SessionCentral()

    try:
        tenant = session.execute(
            select(Tenant).where(
                Tenant.id == TENANT_B_ID
            )
        ).scalar_one()

        tenant.ativo = False

        session.commit()

        resposta = requests.get(
            f"{base_url}/api/maquinas/",
            headers=headers_tenant_b,
            timeout=10,
        )

        assert resposta.status_code == 403

        dados = resposta.json()

        assert dados["success"] is False

        assert (
            dados["message"]
            == "Tenant está inativo."
        )

    finally:
        session.rollback()

        tenant = session.execute(
            select(Tenant).where(
                Tenant.id == TENANT_B_ID
            )
        ).scalar_one()

        tenant.ativo = True

        session.commit()
        session.close()