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