import os
import requests


def test_login_valido(
    base_url
):

    resposta = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "username": os.environ["AGROFROTA_TEST_USERNAME"],
            "senha": os.environ["AGROFROTA_TEST_PASSWORD"],
            "database_name":
                os.environ["AGROFROTA_TEST_DATABASE"],
        },
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    assert (
        "access_token"
        in dados["data"]
    )


def test_login_senha_incorreta(
    base_url
):

    resposta = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "username": os.environ["AGROFROTA_TEST_USERNAME"],
            "senha": "SENHA-INCORRETA",
            "database_name":
                os.environ["AGROFROTA_TEST_DATABASE"],
        },
        timeout=10,
    )

    assert resposta.status_code in {
        400,
        401,
    }

    assert (
        resposta.json()["success"]
        is False
    )


def test_rota_protegida_sem_token(
    base_url
):

    resposta = requests.get(
        (
            f"{base_url}"
            "/api/dashboard/capacidade"
        ),
        timeout=10,
    )

    assert resposta.status_code == 401

def test_usuario_atual(base_url, auth_headers):
    resposta = requests.get(f"{base_url}/api/auth/me", headers=auth_headers, timeout=10)
    assert resposta.status_code == 200
    dados = resposta.json()["data"]
    assert dados["usuario"]["username"] == os.environ["AGROFROTA_TEST_USERNAME"]
    assert "USUARIO_CRIAR" in dados["permissoes"]
    assert dados["permissoes"] == sorted(set(dados["permissoes"]))
    assert requests.get(f"{base_url}/api/auth/me", timeout=10).status_code == 401
