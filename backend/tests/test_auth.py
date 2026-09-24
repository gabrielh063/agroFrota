import requests


def test_login_valido(
    base_url
):

    resposta = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "username": "admin",
            "senha": "Admin@123",
            "database_name":
                "tenant_000004",
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
            "username": "admin",
            "senha": "SENHA-INCORRETA",
            "database_name":
                "tenant_000004",
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