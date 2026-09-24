import requests


def criar_maquina_teste(
    base_url,
    auth_headers,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-MAQ-{codigo_unico}",

            "modelo":
                "Modelo Teste",

            "fabricante":
                "Fabricante Teste",

            "ano":
                2025,

            "localizacao":
                "Pátio de Testes",

            "status":
                "OPERANDO",

            "controla_telemetria":
                False,
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    return resposta.json()["data"]


def test_listar_maquinas(
    base_url,
    auth_headers,
):
    resposta = requests.get(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True
    assert isinstance(
        dados["data"],
        list,
    )


def test_criar_maquina_valida(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    resposta = requests.post(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-MAQ-{codigo_unico}",

            "modelo":
                "6110 Teste",

            "fabricante":
                "John Deere",

            "ano":
                2024,

            "localizacao":
                "Pátio Teste",

            "status":
                "OPERANDO",

            "controla_telemetria":
                False,
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    dados = resposta.json()

    assert dados["success"] is True

    maquina = dados["data"]

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    assert maquina["id"] > 0

    assert maquina[
        "identificacao"
    ] == f"TEST-MAQ-{codigo_unico}"

    assert maquina[
        "status"
    ] == "OPERANDO"

    assert maquina[
        "ativo"
    ] is True


def test_maquina_aparece_na_listagem(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_teste(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    resposta = requests.get(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    maquinas = resposta.json()["data"]

    encontrada = any(
        item["id"] == maquina["id"]
        for item in maquinas
    )

    assert encontrada is True


def test_criar_maquina_sem_campo_obrigatorio(
    base_url,
    auth_headers,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-MAQ-{codigo_unico}",

            # modelo ausente

            "fabricante":
                "Fabricante Teste",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    dados = resposta.json()

    assert dados["success"] is False
    assert dados["message"] == "Dados inválidos."


def test_criar_maquina_ano_invalido(
    base_url,
    auth_headers,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-MAQ-{codigo_unico}",

            "modelo":
                "Teste",

            "fabricante":
                "Teste",

            "ano":
                1899,
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_criar_maquina_status_invalido(
    base_url,
    auth_headers,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-MAQ-{codigo_unico}",

            "modelo":
                "Teste",

            "fabricante":
                "Teste",

            "status":
                "QUEBRADA",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_nao_permitir_maquina_duplicada(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    identificacao = (
        f"TEST-MAQ-{codigo_unico}"
    )

    payload = {
        "identificacao":
            identificacao,

        "modelo":
            "Teste",

        "fabricante":
            "Teste",

        "status":
            "OPERANDO",
    }

    primeira = requests.post(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        json=payload,
        timeout=10,
    )

    assert primeira.status_code == 201

    maquina = primeira.json()["data"]

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    segunda = requests.post(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        json=payload,
        timeout=10,
    )

    assert segunda.status_code == 400

    dados = segunda.json()

    assert dados["success"] is False

    assert (
        "existe"
        in dados["message"].lower()
    )


def test_atualizar_maquina(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_teste(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    resposta = requests.put(
        (
            f"{base_url}/api/maquinas/"
            f"{maquina['id']}"
        ),
        headers=auth_headers,
        json={
            "localizacao":
                "Galpão Central",

            "status":
                "MANUTENCAO",

            "controla_telemetria":
                True,
        },
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    assert (
        dados["data"]["localizacao"]
        == "Galpão Central"
    )

    assert (
        dados["data"]["status"]
        == "MANUTENCAO"
    )

    assert (
        dados["data"][
            "controla_telemetria"
        ]
        is True
    )


def test_atualizar_maquina_inexistente(
    base_url,
    auth_headers,
):
    resposta = requests.put(
        (
            f"{base_url}/api/maquinas/"
            "987654321"
        ),
        headers=auth_headers,
        json={
            "status":
                "OPERANDO"
        },
        timeout=10,
    )

    assert resposta.status_code == 404

    dados = resposta.json()

    assert dados["success"] is False

    assert (
        dados["message"]
        == "Máquina não encontrada."
    )


def test_desativar_e_ativar_maquina(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_teste(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    resposta = requests.patch(
        (
            f"{base_url}/api/maquinas/"
            f"{maquina['id']}/desativar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    assert (
        resposta.json()[
            "data"
        ]["ativo"]
        is False
    )

    resposta = requests.patch(
        (
            f"{base_url}/api/maquinas/"
            f"{maquina['id']}/ativar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    assert (
        resposta.json()[
            "data"
        ]["ativo"]
        is True
    )


def test_maquinas_sem_token(
    base_url,
):
    resposta = requests.get(
        f"{base_url}/api/maquinas/",
        timeout=10,
    )

    assert resposta.status_code == 401


def test_maquina_json_invalido(
    base_url,
    auth_headers,
):
    resposta = requests.post(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        data="{JSON INVALIDO",
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )