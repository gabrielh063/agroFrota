import requests


def test_token_invalido(
    base_url
):

    resposta = requests.get(
        (
            f"{base_url}"
            "/api/dashboard/capacidade"
        ),
        headers={
            "Authorization":
                "Bearer TOKEN_INVALIDO"
        },
        timeout=10,
    )

    assert resposta.status_code == 401


def test_sql_injection_login(
    base_url
):

    resposta = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "username":
                "' OR 1=1 --",

            "senha":
                "' OR 1=1 --",

            "database_name":
                "tenant_000004",
        },
        timeout=10,
    )

    assert resposta.status_code != 200


def test_database_inexistente(
    base_url
):
    resposta = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "username": "admin",
            "senha": "Admin@123",
            "database_name": "tenant_999999",
        },
        timeout=10,
    )

    assert resposta.status_code in {
        401,
        404,
    }

    dados = resposta.json()

    assert dados["success"] is False

    assert "message" in dados
    
def test_payload_vazio_login(
    base_url
):

    resposta = requests.post(
        f"{base_url}/api/auth/login",
        json={},
        timeout=10,
    )

    assert resposta.status_code in {
        400,
        401,
        422,
    }