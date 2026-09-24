from datetime import datetime, timedelta

import requests


def criar_maquina_integracao(
    base_url,
    auth_headers,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-INT-{codigo_unico}",
            "modelo":
                "Modelo Integração",
            "fabricante":
                "Fabricante Teste",
            "ano":
                2025,
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

    return resposta.json()["data"]


def test_indisponibilidade_reflete_no_dashboard_rf06(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    """
    Valida o fluxo:

    máquina
        ->
    indisponibilidade de 4 horas
        ->
    dashboard
        ->
    4 horas paradas
        ->
    83,33% de disponibilidade no período de 24h
    """

    maquina = criar_maquina_integracao(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    resposta = requests.post(
        f"{base_url}/api/indisponibilidades/",
        headers=auth_headers,
        json={
            "maquina_id":
                maquina["id"],
            "inicio":
                "2026-10-15T08:00:00",
            "fim":
                "2026-10-15T12:00:00",
            "motivo":
                "Teste integração dashboard",
            "tipo":
                "QUEBRA",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    indisponibilidade = resposta.json()[
        "indisponibilidade"
    ]

    cleanup_registros_teste(
        "indisponibilidades",
        indisponibilidade["id"],
    )

    assert (
        indisponibilidade["status"]
        == "FINALIZADA"
    )

    resposta = requests.get(
        (
            f"{base_url}"
            "/api/dashboard/indisponibilidade"
            "?inicio=2026-10-15T00:00:00"
            "&fim=2026-10-16T00:00:00"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dashboard = resposta.json()[
        "dashboard"
    ]

    maquina_dashboard = next(
        (
            item
            for item in dashboard["maquinas"]
            if item["id"] == maquina["id"]
        ),
        None,
    )

    assert maquina_dashboard is not None

    assert (
        maquina_dashboard[
            "horas_paradas"
        ]
        == 4.0
    )

    assert abs(
        maquina_dashboard[
            "percentual_disponibilidade"
        ]
        - 83.33
    ) <= 0.01


def test_indisponibilidade_ativa_reflete_capacidade_rf07(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    """
    Valida:

    máquina nova
        ->
    OPERANDO
        ->
    indisponibilidade ativa
        ->
    INDISPONÍVEL
        ->
    cancelamento
        ->
    OPERANDO novamente
    """

    # -------------------------------------------------
    # CAPACIDADE ANTES
    # -------------------------------------------------

    resposta = requests.get(
        (
            f"{base_url}"
            "/api/dashboard/capacidade"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    capacidade_antes = resposta.json()[
        "capacidade"
    ]

    # -------------------------------------------------
    # CRIAR MÁQUINA
    # -------------------------------------------------

    maquina = criar_maquina_integracao(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    resposta = requests.get(
        (
            f"{base_url}"
            "/api/dashboard/capacidade"
        ),
        headers=auth_headers,
        timeout=10,
    )

    capacidade_com_maquina = resposta.json()[
        "capacidade"
    ]

    assert (
        capacidade_com_maquina[
            "total_ativos"
        ]
        ==
        capacidade_antes[
            "total_ativos"
        ] + 1
    )

    assert (
        capacidade_com_maquina[
            "operando"
        ]
        ==
        capacidade_antes[
            "operando"
        ] + 1
    )

    # -------------------------------------------------
    # CRIAR INDISPONIBILIDADE ATIVA
    # -------------------------------------------------

    inicio = (
        datetime.now()
        - timedelta(minutes=5)
    ).replace(
        microsecond=0
    ).isoformat()

    resposta = requests.post(
        f"{base_url}/api/indisponibilidades/",
        headers=auth_headers,
        json={
            "maquina_id":
                maquina["id"],
            "inicio":
                inicio,
            "motivo":
                "Quebra integração RF07",
            "tipo":
                "QUEBRA",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    indisponibilidade = resposta.json()[
        "indisponibilidade"
    ]

    cleanup_registros_teste(
        "indisponibilidades",
        indisponibilidade["id"],
    )

    assert (
        indisponibilidade["status"]
        == "ATIVA"
    )

    # -------------------------------------------------
    # VERIFICAR CAPACIDADE
    # -------------------------------------------------

    resposta = requests.get(
        (
            f"{base_url}"
            "/api/dashboard/capacidade"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    capacidade_indisponivel = (
        resposta.json()["capacidade"]
    )

    assert (
        capacidade_indisponivel[
            "total_ativos"
        ]
        ==
        capacidade_com_maquina[
            "total_ativos"
        ]
    )

    assert (
        capacidade_indisponivel[
            "operando"
        ]
        ==
        capacidade_com_maquina[
            "operando"
        ] - 1
    )

    assert (
        capacidade_indisponivel[
            "indisponivel"
        ]
        ==
        capacidade_com_maquina[
            "indisponivel"
        ] + 1
    )

    # -------------------------------------------------
    # CANCELAR INDISPONIBILIDADE
    # -------------------------------------------------

    resposta = requests.patch(
        (
            f"{base_url}"
            "/api/indisponibilidades/"
            f"{indisponibilidade['id']}"
            "/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    # -------------------------------------------------
    # MÁQUINA DEVE VOLTAR PARA OPERANDO
    # -------------------------------------------------

    resposta = requests.get(
        (
            f"{base_url}"
            "/api/dashboard/capacidade"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    capacidade_final = resposta.json()[
        "capacidade"
    ]

    assert (
        capacidade_final[
            "operando"
        ]
        ==
        capacidade_com_maquina[
            "operando"
        ]
    )

    assert (
        capacidade_final[
            "indisponivel"
        ]
        ==
        capacidade_com_maquina[
            "indisponivel"
        ]
    )