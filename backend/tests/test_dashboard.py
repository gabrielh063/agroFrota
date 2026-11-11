import requests


def test_capacidade_patio(
    base_url,
    auth_headers
):

    resposta = requests.get(
        (
            f"{base_url}"
            "/api/dashboard/capacidade"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    capacidade = dados[
        "capacidade"
    ]

    assert capacidade[
        "total_ativos"
    ] >= 0

    assert capacidade[
        "maquinas"
    ] >= 0

    assert capacidade[
        "equipamentos"
    ] >= 0

    assert (
        capacidade["operando"]
        + capacidade["manutencao"]
        + capacidade["indisponivel"]
        + capacidade["inativo"]
        ==
        capacidade["total_ativos"]
    )


def test_percentuais_capacidade(
    base_url,
    auth_headers
):

    resposta = requests.get(
        (
            f"{base_url}"
            "/api/dashboard/capacidade"
        ),
        headers=auth_headers,
        timeout=10,
    )

    capacidade = resposta.json()[
        "capacidade"
    ]

    if capacidade["base_operacional"] > 0:

        total_percentual = (
            capacidade[
                "percentual_operando"
            ]
            +
            capacidade[
                "percentual_manutencao"
            ]
            +
            capacidade[
                "percentual_indisponivel"
            ]
        )

        assert abs(
            total_percentual - 100
        ) <= 0.02


def test_atividade_de_servicos_retorna_12_meses_autorizados(base_url, auth_headers):
    resposta = requests.get(
        f"{base_url}/api/dashboard/atividade?meses=12",
        headers=auth_headers,
        timeout=10,
    )
    assert resposta.status_code == 200
    atividade = resposta.json()["atividade"]
    assert len(atividade) == 12
    assert all(item["quantidade"] >= 0 for item in atividade)
    assert all("ano" in item and "mes" in item for item in atividade)


def test_dashboard_indisponibilidade(
    base_url,
    auth_headers
):

    resposta = requests.get(
        (
            f"{base_url}"
            "/api/dashboard/"
            "indisponibilidade"
            "?inicio=2026-09-25T00:00:00"
            "&fim=2026-09-25T23:59:59"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    dashboard = dados[
        "dashboard"
    ]

    assert (
        dashboard[
            "tempo_total_parado_horas"
        ]
        >= 0
    )

    assert (
        0
        <= dashboard[
            "percentual_disponibilidade"
        ]
        <= 100
    )


def test_dashboard_periodo_invalido(
    base_url,
    auth_headers
):

    resposta = requests.get(
        (
            f"{base_url}"
            "/api/dashboard/"
            "indisponibilidade"
            "?inicio=2026-09-26T10:00:00"
            "&fim=2026-09-25T10:00:00"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )
