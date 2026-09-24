import requests


def criar_maquina_manutencao(
    base_url,
    auth_headers,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-MAN-MAQ-{codigo_unico}",
            "modelo":
                "Modelo Manutenção",
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


def criar_os_manutencao(
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
                f"OS MANUTENCAO {codigo_unico}",
            "descricao":
                "OS criada para teste de manutenção.",
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


def criar_manutencao_teste(
    base_url,
    auth_headers,
    ordem_servico_id,
):
    resposta = requests.post(
        f"{base_url}/api/manutencoes/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                ordem_servico_id,
            "tipo":
                "PREVENTIVA",
            "inicio":
                "2026-09-25T08:00:00",
            "descricao":
                "Manutenção automatizada.",
            "custo":
                500.00,
            "observacoes":
                "Registro de teste.",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    return resposta.json()[
        "manutencao"
    ]


def preparar_manutencao(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_manutencao(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    manutencao = criar_manutencao_teste(
        base_url,
        auth_headers,
        ordem["id"],
    )

    cleanup_registros_teste(
        "manutencoes",
        manutencao["id"],
    )

    return maquina, ordem, manutencao


def test_listar_manutencoes(
    base_url,
    auth_headers,
):
    resposta = requests.get(
        f"{base_url}/api/manutencoes/",
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    assert isinstance(
        dados["manutencoes"],
        list,
    )


def test_criar_manutencao_valida(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_manutencao(
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
        f"{base_url}/api/manutencoes/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                ordem["id"],
            "tipo":
                "PREVENTIVA",
            "inicio":
                "2026-09-25T08:00:00",
            "descricao":
                "Troca de filtros.",
            "custo":
                850.50,
            "observacoes":
                "Teste automatizado.",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    dados = resposta.json()

    assert dados["success"] is True

    manutencao = dados[
        "manutencao"
    ]

    cleanup_registros_teste(
        "manutencoes",
        manutencao["id"],
    )

    assert (
        manutencao["ordem_servico_id"]
        == ordem["id"]
    )

    assert (
        manutencao["tipo"]
        == "PREVENTIVA"
    )

    assert (
        manutencao["status"]
        == "EM_ANDAMENTO"
    )

    assert manutencao["fim"] is None


def test_buscar_manutencao_por_id(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, manutencao = preparar_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.get(
        (
            f"{base_url}/api/manutencoes/"
            f"{manutencao['id']}"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    assert (
        dados["manutencao"]["id"]
        == manutencao["id"]
    )


def test_buscar_manutencao_inexistente(
    base_url,
    auth_headers,
):
    resposta = requests.get(
        (
            f"{base_url}/api/manutencoes/"
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


def test_tipo_manutencao_invalido(
    base_url,
    auth_headers,
):
    resposta = requests.post(
        f"{base_url}/api/manutencoes/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                1,
            "tipo":
                "EMERGENCIAL",
            "inicio":
                "2026-09-25T08:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_custo_manutencao_negativo(
    base_url,
    auth_headers,
):
    resposta = requests.post(
        f"{base_url}/api/manutencoes/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                1,
            "tipo":
                "PREVENTIVA",
            "inicio":
                "2026-09-25T08:00:00",
            "custo":
                -100,
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_periodo_manutencao_invalido(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_manutencao(
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
        f"{base_url}/api/manutencoes/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                ordem["id"],
            "tipo":
                "PREVENTIVA",
            "inicio":
                "2026-09-25T12:00:00",
            "fim":
                "2026-09-25T08:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_manutencao_os_inexistente(
    base_url,
    auth_headers,
):
    resposta = requests.post(
        f"{base_url}/api/manutencoes/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                987654321,
            "tipo":
                "PREVENTIVA",
            "inicio":
                "2026-09-25T08:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["message"]
        == "Ordem de serviço não encontrada."
    )


def test_nao_criar_manutencao_os_cancelada(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_manutencao(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    resposta_cancelar = requests.patch(
        (
            f"{base_url}/api/ordens-servico/"
            f"{ordem['id']}/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert (
        resposta_cancelar.status_code
        == 200
    )

    resposta = requests.post(
        f"{base_url}/api/manutencoes/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                ordem["id"],
            "tipo":
                "PREVENTIVA",
            "inicio":
                "2026-09-25T08:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_nao_criar_manutencao_os_concluida(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_manutencao(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    resposta_concluir = requests.patch(
        (
            f"{base_url}/api/ordens-servico/"
            f"{ordem['id']}/concluir"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert (
        resposta_concluir.status_code
        == 200
    )

    resposta = requests.post(
        f"{base_url}/api/manutencoes/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                ordem["id"],
            "tipo":
                "PREVENTIVA",
            "inicio":
                "2026-09-25T08:00:00",
        },
        timeout=10,
    )

    if resposta.status_code == 201:

        manutencao_criada = resposta.json().get(
            "manutencao"
        )

        if manutencao_criada:

            cleanup_registros_teste(
                "manutencoes",
                manutencao_criada["id"],
            )
    
    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_responsavel_manutencao_inexistente(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_manutencao(
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
        f"{base_url}/api/manutencoes/",
        headers=auth_headers,
        json={
            "ordem_servico_id":
                ordem["id"],
            "responsavel_id":
                987654321,
            "tipo":
                "PREVENTIVA",
            "inicio":
                "2026-09-25T08:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["message"]
        == "Responsável não encontrado."
    )


def test_atualizar_manutencao(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, manutencao = preparar_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.put(
        (
            f"{base_url}/api/manutencoes/"
            f"{manutencao['id']}"
        ),
        headers=auth_headers,
        json={
            "tipo":
                "CORRETIVA",
            "descricao":
                "Descrição atualizada.",
            "custo":
                975.75,
            "observacoes":
                "Atualização de teste.",
        },
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    atualizada = dados[
        "manutencao"
    ]

    assert (
        atualizada["tipo"]
        == "CORRETIVA"
    )

    assert (
        atualizada["descricao"]
        == "Descrição atualizada."
    )


def test_atualizar_periodo_invalido(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, manutencao = preparar_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.put(
        (
            f"{base_url}/api/manutencoes/"
            f"{manutencao['id']}"
        ),
        headers=auth_headers,
        json={
            "inicio":
                "2026-09-25T15:00:00",
            "fim":
                "2026-09-25T10:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 400


def test_status_manutencao_invalido(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, manutencao = preparar_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.put(
        (
            f"{base_url}/api/manutencoes/"
            f"{manutencao['id']}"
        ),
        headers=auth_headers,
        json={
            "status":
                "FINALIZADA"
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_atualizar_manutencao_inexistente(
    base_url,
    auth_headers,
):
    resposta = requests.put(
        (
            f"{base_url}/api/manutencoes/"
            "987654321"
        ),
        headers=auth_headers,
        json={
            "descricao":
                "Teste"
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["message"]
        == "Manutenção não encontrada."
    )


def test_concluir_manutencao(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, manutencao = preparar_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.patch(
        (
            f"{base_url}/api/manutencoes/"
            f"{manutencao['id']}/concluir"
        ),
        headers=auth_headers,
        json={
            "fim":
                "2026-09-25T13:00:00"
        },
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    assert (
        dados["manutencao"]["status"]
        == "CONCLUIDA"
    )

    assert (
        dados["manutencao"]["fim"]
        == "2026-09-25T13:00:00"
    )


def test_concluir_manutencao_fim_invalido(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, manutencao = preparar_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.patch(
        (
            f"{base_url}/api/manutencoes/"
            f"{manutencao['id']}/concluir"
        ),
        headers=auth_headers,
        json={
            "fim":
                "2026-09-25T07:00:00"
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_cancelar_manutencao(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, manutencao = preparar_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.patch(
        (
            f"{base_url}/api/manutencoes/"
            f"{manutencao['id']}/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    assert (
        resposta.json()[
            "manutencao"
        ]["status"]
        == "CANCELADA"
    )


def test_nao_editar_manutencao_concluida(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, manutencao = preparar_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    concluir = requests.patch(
        (
            f"{base_url}/api/manutencoes/"
            f"{manutencao['id']}/concluir"
        ),
        headers=auth_headers,
        json={
            "fim":
                "2026-09-25T13:00:00"
        },
        timeout=10,
    )

    assert concluir.status_code == 200

    resposta = requests.put(
        (
            f"{base_url}/api/manutencoes/"
            f"{manutencao['id']}"
        ),
        headers=auth_headers,
        json={
            "descricao":
                "Não deveria alterar."
        },
        timeout=10,
    )

    assert resposta.status_code == 400


def test_nao_editar_manutencao_cancelada(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, manutencao = preparar_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    cancelar = requests.patch(
        (
            f"{base_url}/api/manutencoes/"
            f"{manutencao['id']}/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert cancelar.status_code == 200

    resposta = requests.put(
        (
            f"{base_url}/api/manutencoes/"
            f"{manutencao['id']}"
        ),
        headers=auth_headers,
        json={
            "descricao":
                "Não deveria alterar."
        },
        timeout=10,
    )

    assert resposta.status_code == 400


def test_nao_cancelar_manutencao_concluida(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, manutencao = preparar_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    concluir = requests.patch(
        (
            f"{base_url}/api/manutencoes/"
            f"{manutencao['id']}/concluir"
        ),
        headers=auth_headers,
        json={
            "fim":
                "2026-09-25T13:00:00"
        },
        timeout=10,
    )

    assert concluir.status_code == 200

    resposta = requests.patch(
        (
            f"{base_url}/api/manutencoes/"
            f"{manutencao['id']}/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 400


def test_nao_concluir_manutencao_cancelada(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, _, manutencao = preparar_manutencao(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    cancelar = requests.patch(
        (
            f"{base_url}/api/manutencoes/"
            f"{manutencao['id']}/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert cancelar.status_code == 200

    resposta = requests.patch(
        (
            f"{base_url}/api/manutencoes/"
            f"{manutencao['id']}/concluir"
        ),
        headers=auth_headers,
        json={
            "fim":
                "2026-09-25T13:00:00"
        },
        timeout=10,
    )

    assert resposta.status_code == 400


def test_manutencoes_sem_token(
    base_url,
):
    resposta = requests.get(
        f"{base_url}/api/manutencoes/",
        timeout=10,
    )

    assert resposta.status_code == 401