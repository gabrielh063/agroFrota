import requests


def criar_maquina_para_os(
    base_url,
    auth_headers,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-OS-MAQ-{codigo_unico}",

            "modelo":
                "Modelo OS",

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


def criar_equipamento_para_os(
    base_url,
    auth_headers,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/equipamentos/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-OS-EQP-{codigo_unico}",

            "nome":
                "Equipamento OS",

            "tipo":
                "Implemento",

            "fabricante":
                "Fabricante Teste",

            "modelo":
                "Modelo Teste",

            "ano":
                2025,

            "localizacao":
                "Pátio Teste",

            "status":
                "DISPONIVEL",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    return resposta.json()["data"]


def criar_os_maquina(
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
                f"OS TESTE {codigo_unico}",

            "descricao":
                "Ordem criada pelos testes automatizados.",

            "maquina_id":
                maquina_id,

            "prioridade":
                "MEDIA",

            "prazo":
                "2026-10-10T17:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    return resposta.json()[
        "ordem_servico"
    ]


def test_listar_ordens_servico(
    base_url,
    auth_headers,
):
    resposta = requests.get(
        f"{base_url}/api/ordens-servico/",
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["sucesso"] is True

    assert isinstance(
        dados["ordens_servico"],
        list,
    )

    assert dados[
        "quantidade"
    ] == len(
        dados["ordens_servico"]
    )


def test_criar_os_com_maquina(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_para_os(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    resposta = requests.post(
        f"{base_url}/api/ordens-servico/",
        headers=auth_headers,
        json={
            "tipo":
                "MANUTENCAO",

            "titulo":
                "Manutenção preventiva teste",

            "descricao":
                "Teste automatizado",

            "maquina_id":
                maquina["id"],

            "prioridade":
                "ALTA",

            "prazo":
                "2026-10-15T12:00:00",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    dados = resposta.json()

    assert dados["sucesso"] is True

    ordem = dados["ordem_servico"]

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    assert ordem["id"] > 0
    assert ordem["numero"] > 0

    assert ordem[
        "maquina_id"
    ] == maquina["id"]

    assert ordem[
        "equipamento_id"
    ] is None

    assert ordem[
        "tipo"
    ] == "MANUTENCAO"

    assert ordem[
        "prioridade"
    ] == "ALTA"

    assert ordem[
        "status"
    ] == "ABERTA"

    assert ordem["ativo"] is True


def test_criar_os_com_equipamento(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    equipamento = (
        criar_equipamento_para_os(
            base_url,
            auth_headers,
            codigo_unico,
        )
    )

    cleanup_registros_teste(
        "equipamentos",
        equipamento["id"],
    )

    resposta = requests.post(
        f"{base_url}/api/ordens-servico/",
        headers=auth_headers,
        json={
            "tipo":
                "SERVICO",

            "titulo":
                "Serviço em equipamento",

            "equipamento_id":
                equipamento["id"],

            "prioridade":
                "MEDIA",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    ordem = resposta.json()[
        "ordem_servico"
    ]

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    assert (
        ordem["equipamento_id"]
        == equipamento["id"]
    )

    assert ordem[
        "maquina_id"
    ] is None

    assert ordem[
        "status"
    ] == "ABERTA"


def test_buscar_os_por_id(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_para_os(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_maquina(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    resposta = requests.get(
        (
            f"{base_url}/api/ordens-servico/"
            f"{ordem['id']}"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["sucesso"] is True

    assert (
        dados["ordem_servico"]["id"]
        == ordem["id"]
    )


def test_buscar_os_inexistente(
    base_url,
    auth_headers,
):
    resposta = requests.get(
        (
            f"{base_url}/api/ordens-servico/"
            "987654321"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 404

    dados = resposta.json()

    assert dados["sucesso"] is False


def test_os_sem_maquina_e_sem_equipamento(
    base_url,
    auth_headers,
):
    resposta = requests.post(
        f"{base_url}/api/ordens-servico/",
        headers=auth_headers,
        json={
            "tipo":
                "SERVICO",

            "titulo":
                "OS sem recurso",

            "prioridade":
                "MEDIA",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    dados = resposta.json()

    assert dados["sucesso"] is False

    assert (
        "máquina ou equipamento"
        in dados["erro"].lower()
    )


def test_os_com_maquina_e_equipamento(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_para_os(
        base_url,
        auth_headers,
        codigo_unico,
    )

    equipamento = (
        criar_equipamento_para_os(
            base_url,
            auth_headers,
            codigo_unico,
        )
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    cleanup_registros_teste(
        "equipamentos",
        equipamento["id"],
    )

    resposta = requests.post(
        f"{base_url}/api/ordens-servico/",
        headers=auth_headers,
        json={
            "tipo":
                "SERVICO",

            "titulo":
                "OS inválida",

            "maquina_id":
                maquina["id"],

            "equipamento_id":
                equipamento["id"],
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    dados = resposta.json()

    assert dados["sucesso"] is False


def test_os_tipo_invalido(
    base_url,
    auth_headers,
):
    resposta = requests.post(
        f"{base_url}/api/ordens-servico/",
        headers=auth_headers,
        json={
            "tipo":
                "OUTRO",

            "titulo":
                "Teste tipo inválido",

            "maquina_id":
                1,
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    dados = resposta.json()

    assert dados["sucesso"] is False


def test_os_prioridade_invalida(
    base_url,
    auth_headers,
):
    resposta = requests.post(
        f"{base_url}/api/ordens-servico/",
        headers=auth_headers,
        json={
            "tipo":
                "SERVICO",

            "titulo":
                "Teste prioridade",

            "maquina_id":
                1,

            "prioridade":
                "CRITICA",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["sucesso"]
        is False
    )


def test_atualizar_os(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_para_os(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_maquina(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    resposta = requests.put(
        (
            f"{base_url}/api/ordens-servico/"
            f"{ordem['id']}"
        ),
        headers=auth_headers,
        json={
            "titulo":
                "Título atualizado",

            "prioridade":
                "URGENTE",

            "status":
                "EM_ANDAMENTO",
        },
        timeout=10,
    )

    assert resposta.status_code == 200

    atualizada = resposta.json()[
        "ordem_servico"
    ]

    assert (
        atualizada["titulo"]
        == "Título atualizado"
    )

    assert (
        atualizada["prioridade"]
        == "URGENTE"
    )

    assert (
        atualizada["status"]
        == "EM_ANDAMENTO"
    )


def test_concluir_os(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_para_os(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_maquina(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    resposta = requests.patch(
        (
            f"{base_url}/api/ordens-servico/"
            f"{ordem['id']}/concluir"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["sucesso"] is True

    assert (
        dados["ordem_servico"]["status"]
        == "CONCLUIDA"
    )


def test_cancelar_os(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_para_os(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_maquina(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    resposta = requests.patch(
        (
            f"{base_url}/api/ordens-servico/"
            f"{ordem['id']}/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["sucesso"] is True

    assert (
        dados["ordem_servico"]["status"]
        == "CANCELADA"
    )


def test_nao_editar_os_concluida(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_para_os(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_maquina(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    concluir = requests.patch(
        (
            f"{base_url}/api/ordens-servico/"
            f"{ordem['id']}/concluir"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert concluir.status_code == 200

    resposta = requests.put(
        (
            f"{base_url}/api/ordens-servico/"
            f"{ordem['id']}"
        ),
        headers=auth_headers,
        json={
            "titulo":
                "Não deve alterar"
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    dados = resposta.json()

    assert dados["sucesso"] is False

    assert (
        "concluída"
        in dados["erro"].lower()
        or
        "concluida"
        in dados["erro"].lower()
    )


def test_nao_editar_os_cancelada(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_para_os(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    ordem = criar_os_maquina(
        base_url,
        auth_headers,
        maquina["id"],
        codigo_unico,
    )

    cleanup_registros_teste(
        "ordens_servico",
        ordem["id"],
    )

    cancelar = requests.patch(
        (
            f"{base_url}/api/ordens-servico/"
            f"{ordem['id']}/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert cancelar.status_code == 200

    resposta = requests.put(
        (
            f"{base_url}/api/ordens-servico/"
            f"{ordem['id']}"
        ),
        headers=auth_headers,
        json={
            "titulo":
                "Não deve alterar"
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["sucesso"]
        is False
    )


def test_listar_apenas_ativas(
    base_url,
    auth_headers,
):
    resposta = requests.get(
        (
            f"{base_url}/api/ordens-servico/"
            "?apenas_ativas=true"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["sucesso"] is True

    for ordem in dados[
        "ordens_servico"
    ]:
        assert ordem["ativo"] is True


def test_ordens_servico_sem_token(
    base_url,
):
    resposta = requests.get(
        f"{base_url}/api/ordens-servico/",
        timeout=10,
    )

    assert resposta.status_code == 401


def test_os_maquina_inexistente_nao_deve_gerar_500(
    base_url,
    auth_headers,
):
    resposta = requests.post(
        f"{base_url}/api/ordens-servico/",
        headers=auth_headers,
        json={
            "tipo":
                "SERVICO",

            "titulo":
                "Máquina inexistente",

            "maquina_id":
                987654321,

            "prioridade":
                "MEDIA",
        },
        timeout=10,
    )

    assert resposta.status_code in {
        400,
        404,
    }

    assert resposta.status_code != 500