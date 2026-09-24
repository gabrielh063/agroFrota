import requests


def criar_equipamento_teste(
    base_url,
    auth_headers,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/equipamentos/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-EQP-{codigo_unico}",

            "nome":
                "Implemento Teste",

            "tipo":
                "Implemento",

            "fabricante":
                "Fabricante Teste",

            "modelo":
                "Modelo Teste",

            "ano":
                2025,

            "localizacao":
                "Pátio de Testes",

            "status":
                "DISPONIVEL",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    return resposta.json()["data"]


def test_listar_equipamentos(
    base_url,
    auth_headers,
):
    resposta = requests.get(
        f"{base_url}/api/equipamentos/",
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


def test_criar_equipamento_valido(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    resposta = requests.post(
        f"{base_url}/api/equipamentos/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-EQP-{codigo_unico}",

            "nome":
                "Grade Teste",

            "tipo":
                "Grade",

            "fabricante":
                "Fabricante Teste",

            "modelo":
                "GT-01",

            "ano":
                2024,

            "localizacao":
                "Pátio Teste",

            "status":
                "DISPONIVEL",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    dados = resposta.json()

    assert dados["success"] is True

    equipamento = dados["data"]

    cleanup_registros_teste(
        "equipamentos",
        equipamento["id"],
    )

    assert equipamento["id"] > 0

    assert (
        equipamento["status"]
        == "DISPONIVEL"
    )

    assert equipamento[
        "ativo"
    ] is True


def test_equipamento_aparece_na_listagem(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    equipamento = criar_equipamento_teste(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "equipamentos",
        equipamento["id"],
    )

    resposta = requests.get(
        f"{base_url}/api/equipamentos/",
        headers=auth_headers,
        timeout=10,
    )

    equipamentos = resposta.json()[
        "data"
    ]

    encontrado = any(
        item["id"]
        == equipamento["id"]
        for item in equipamentos
    )

    assert encontrado is True


def test_criar_equipamento_sem_nome(
    base_url,
    auth_headers,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/equipamentos/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-EQP-{codigo_unico}",

            "tipo":
                "Implemento",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_criar_equipamento_ano_invalido(
    base_url,
    auth_headers,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/equipamentos/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-EQP-{codigo_unico}",

            "nome":
                "Teste",

            "tipo":
                "Implemento",

            "ano":
                2200,
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_criar_equipamento_status_invalido(
    base_url,
    auth_headers,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/equipamentos/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-EQP-{codigo_unico}",

            "nome":
                "Teste",

            "tipo":
                "Implemento",

            "status":
                "QUEBRADO",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_nao_permitir_equipamento_duplicado(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    identificacao = (
        f"TEST-EQP-{codigo_unico}"
    )

    payload = {
        "identificacao":
            identificacao,

        "nome":
            "Implemento Teste",

        "tipo":
            "Implemento",

        "status":
            "DISPONIVEL",
    }

    primeira = requests.post(
        f"{base_url}/api/equipamentos/",
        headers=auth_headers,
        json=payload,
        timeout=10,
    )

    assert primeira.status_code == 201

    equipamento = primeira.json()[
        "data"
    ]

    cleanup_registros_teste(
        "equipamentos",
        equipamento["id"],
    )

    segunda = requests.post(
        f"{base_url}/api/equipamentos/",
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


def test_atualizar_equipamento(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    equipamento = criar_equipamento_teste(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "equipamentos",
        equipamento["id"],
    )

    resposta = requests.put(
        (
            f"{base_url}/api/equipamentos/"
            f"{equipamento['id']}"
        ),
        headers=auth_headers,
        json={
            "localizacao":
                "Galpão B",

            "status":
                "EM_USO",
        },
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    assert (
        dados["data"]["localizacao"]
        == "Galpão B"
    )

    assert (
        dados["data"]["status"]
        == "EM_USO"
    )


def test_atualizar_equipamento_inexistente(
    base_url,
    auth_headers,
):
    resposta = requests.put(
        (
            f"{base_url}/api/equipamentos/"
            "987654321"
        ),
        headers=auth_headers,
        json={
            "status":
                "DISPONIVEL"
        },
        timeout=10,
    )

    assert resposta.status_code == 404

    dados = resposta.json()

    assert dados["success"] is False

    assert (
        dados["message"]
        == "Equipamento não encontrado."
    )


def test_desativar_e_ativar_equipamento(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    equipamento = criar_equipamento_teste(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "equipamentos",
        equipamento["id"],
    )

    resposta = requests.patch(
        (
            f"{base_url}/api/equipamentos/"
            f"{equipamento['id']}"
            "/desativar"
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
            f"{base_url}/api/equipamentos/"
            f"{equipamento['id']}"
            "/ativar"
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


def test_equipamentos_sem_token(
    base_url,
):
    resposta = requests.get(
        f"{base_url}/api/equipamentos/",
        timeout=10,
    )

    assert resposta.status_code == 401


def test_equipamento_json_invalido(
    base_url,
    auth_headers,
):
    resposta = requests.post(
        f"{base_url}/api/equipamentos/",
        headers=auth_headers,
        data="{JSON INVALIDO",
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )
    