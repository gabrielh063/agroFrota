import requests


def criar_maquina_calendario(
    base_url,
    auth_headers,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-CAL-MAQ-{codigo_unico}",
            "modelo":
                "Modelo Calendário",
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


def criar_os_calendario(
    base_url,
    auth_headers,
    maquina_id,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/ordens-servico/",
        headers=auth_headers,
        json={
            "tipo":
                "MANUTENCAO",
            "titulo":
                f"OS CALENDARIO {codigo_unico}",
            "descricao":
                "OS criada para teste de calendário.",
            "maquina_id":
                maquina_id,
            "prioridade":
                "MEDIA",
            "prazo":
                "2026-10-20T17:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    return resposta.json()[
        "ordem_servico"
    ]


def criar_agendamento_teste(
    base_url,
    auth_headers,
    ordem_servico_id,
):
    resposta = requests.post(
        f"{base_url}/api/calendario/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                ordem_servico_id,
            "inicio":
                "2026-10-10T08:00:00",
            "fim":
                "2026-10-10T12:00:00",
            "observacoes":
                "Agendamento de teste.",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    return resposta.json()[
        "agendamento"
    ]


def preparar_agendamento(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_calendario(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_calendario(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    agendamento = criar_agendamento_teste(
        base_url,
        auth_headers,
        ordem["id"],
    )

    cleanup_registros_teste(
        "agendamentos",
        agendamento["id"],
    )

    return (
        maquina,
        ordem,
        agendamento,
    )


def test_listar_agendamentos(
    base_url,
    auth_headers,
):
    resposta = requests.get(
        f"{base_url}/api/calendario/",
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    assert isinstance(
        dados["agendamentos"],
        list,
    )


def test_criar_agendamento_valido(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_calendario(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_calendario(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    resposta = requests.post(
        f"{base_url}/api/calendario/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                ordem["id"],
            "inicio":
                "2026-10-11T08:00:00",
            "fim":
                "2026-10-11T12:00:00",
            "observacoes":
                "Manutenção programada.",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    dados = resposta.json()

    assert dados["success"] is True

    agendamento = dados[
        "agendamento"
    ]

    cleanup_registros_teste(
        "agendamentos",
        agendamento["id"],
    )

    assert agendamento[
        "ordem_servico_id"
    ] == ordem["id"]

    assert agendamento[
        "status"
    ] == "AGENDADO"

    assert agendamento[
        "inicio"
    ] == "2026-10-11T08:00:00"

    assert agendamento[
        "fim"
    ] == "2026-10-11T12:00:00"


def test_buscar_agendamento_por_id(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, agendamento = preparar_agendamento(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.get(
        (
            f"{base_url}/api/calendario/"
            f"{agendamento['id']}"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    assert (
        dados["agendamento"]["id"]
        == agendamento["id"]
    )


def test_buscar_agendamento_inexistente(
    base_url,
    auth_headers,
):
    resposta = requests.get(
        (
            f"{base_url}/api/calendario/"
            "987654321"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 404

    assert (
        resposta.json()["success"]
        is False
    )


def test_agendamento_periodo_invalido(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_calendario(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_calendario(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    resposta = requests.post(
        f"{base_url}/api/calendario/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                ordem["id"],
            "inicio":
                "2026-10-11T12:00:00",
            "fim":
                "2026-10-11T08:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_agendamento_inicio_igual_fim(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_calendario(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_calendario(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    resposta = requests.post(
        f"{base_url}/api/calendario/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                ordem["id"],
            "inicio":
                "2026-10-11T10:00:00",
            "fim":
                "2026-10-11T10:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 400


def test_agendamento_os_inexistente(
    base_url,
    auth_headers,
):
    resposta = requests.post(
        f"{base_url}/api/calendario/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                987654321,
            "inicio":
                "2026-10-11T08:00:00",
            "fim":
                "2026-10-11T12:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    dados = resposta.json()

    assert dados["success"] is False

    assert (
        dados["message"]
        == "Ordem de serviço não encontrada."
    )


def test_agendamento_responsavel_inexistente(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_calendario(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_calendario(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    resposta = requests.post(
        f"{base_url}/api/calendario/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                ordem["id"],
            "responsavel_id":
                987654321,
            "inicio":
                "2026-10-11T08:00:00",
            "fim":
                "2026-10-11T12:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    dados = resposta.json()

    assert dados["success"] is False

    assert (
        dados["message"]
        == "Responsável não encontrado."
    )


def test_nao_agendar_os_concluida(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_calendario(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_calendario(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    conclusao = requests.patch(
        (
            f"{base_url}/api/ordens-servico/"
            f"{ordem['id']}/concluir"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert conclusao.status_code == 200

    resposta = requests.post(
        f"{base_url}/api/calendario/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                ordem["id"],
            "inicio":
                "2026-10-11T08:00:00",
            "fim":
                "2026-10-11T12:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_nao_agendar_os_cancelada(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_calendario(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_calendario(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    cancelamento = requests.patch(
        (
            f"{base_url}/api/ordens-servico/"
            f"{ordem['id']}/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert cancelamento.status_code == 200

    resposta = requests.post(
        f"{base_url}/api/calendario/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                ordem["id"],
            "inicio":
                "2026-10-11T08:00:00",
            "fim":
                "2026-10-11T12:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 400


def test_atualizar_agendamento(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, agendamento = preparar_agendamento(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.put(
        (
            f"{base_url}/api/calendario/"
            f"{agendamento['id']}"
        ),
        headers=auth_headers,
        json={
            "inicio":
                "2026-10-10T09:00:00",
            "fim":
                "2026-10-10T13:00:00",
            "status":
                "EM_ANDAMENTO",
            "observacoes":
                "Horário atualizado.",
        },
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    atualizado = dados[
        "agendamento"
    ]

    assert (
        atualizado["status"]
        == "EM_ANDAMENTO"
    )

    assert (
        atualizado["inicio"]
        == "2026-10-10T09:00:00"
    )

    assert (
        atualizado["fim"]
        == "2026-10-10T13:00:00"
    )


def test_atualizar_agendamento_periodo_invalido(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, agendamento = preparar_agendamento(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.put(
        (
            f"{base_url}/api/calendario/"
            f"{agendamento['id']}"
        ),
        headers=auth_headers,
        json={
            "inicio":
                "2026-10-10T14:00:00",
            "fim":
                "2026-10-10T10:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_status_agendamento_invalido(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, agendamento = preparar_agendamento(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.put(
        (
            f"{base_url}/api/calendario/"
            f"{agendamento['id']}"
        ),
        headers=auth_headers,
        json={
            "status":
                "FINALIZADO"
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_atualizar_agendamento_inexistente(
    base_url,
    auth_headers,
):
    resposta = requests.put(
        (
            f"{base_url}/api/calendario/"
            "987654321"
        ),
        headers=auth_headers,
        json={
            "status":
                "EM_ANDAMENTO"
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["message"]
        == "Agendamento não encontrado."
    )


def test_cancelar_agendamento(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, agendamento = preparar_agendamento(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.patch(
        (
            f"{base_url}/api/calendario/"
            f"{agendamento['id']}"
            "/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    assert (
        dados["agendamento"]["status"]
        == "CANCELADO"
    )


def test_nao_cancelar_agendamento_concluido(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, agendamento = preparar_agendamento(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    inicio_execucao = requests.put(
        f"{base_url}/api/calendario/{agendamento['id']}",
        headers=auth_headers, json={"status": "EM_ANDAMENTO"}, timeout=10,
    )
    assert inicio_execucao.status_code == 200

    conclusao = requests.put(
        (
            f"{base_url}/api/calendario/"
            f"{agendamento['id']}"
        ),
        headers=auth_headers,
        json={
            "status":
                "CONCLUIDO"
        },
        timeout=10,
    )

    assert conclusao.status_code == 200

    resposta = requests.patch(
        (
            f"{base_url}/api/calendario/"
            f"{agendamento['id']}"
            "/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_nao_editar_agendamento_cancelado(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, agendamento = preparar_agendamento(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    cancelar = requests.patch(
        (
            f"{base_url}/api/calendario/"
            f"{agendamento['id']}"
            "/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert cancelar.status_code == 200

    resposta = requests.put(
        (
            f"{base_url}/api/calendario/"
            f"{agendamento['id']}"
        ),
        headers=auth_headers,
        json={
            "observacoes":
                "Não deveria ser alterado."
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_nao_editar_agendamento_concluido(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, agendamento = preparar_agendamento(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    inicio_execucao = requests.put(
        f"{base_url}/api/calendario/{agendamento['id']}",
        headers=auth_headers, json={"status": "EM_ANDAMENTO"}, timeout=10,
    )
    assert inicio_execucao.status_code == 200

    conclusao = requests.put(
        (
            f"{base_url}/api/calendario/"
            f"{agendamento['id']}"
        ),
        headers=auth_headers,
        json={
            "status":
                "CONCLUIDO"
        },
        timeout=10,
    )

    assert conclusao.status_code == 200

    resposta = requests.put(
        (
            f"{base_url}/api/calendario/"
            f"{agendamento['id']}"
        ),
        headers=auth_headers,
        json={
            "observacoes":
                "Não deveria ser alterado."
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_calendario_sem_token(
    base_url,
):
    resposta = requests.get(
        f"{base_url}/api/calendario/",
        timeout=10,
    )

    assert resposta.status_code == 401