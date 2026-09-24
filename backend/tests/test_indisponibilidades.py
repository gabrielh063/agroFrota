import requests


def criar_maquina_indisponibilidade(
    base_url,
    auth_headers,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/maquinas/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-IND-MAQ-{codigo_unico}",
            "modelo":
                "Modelo Indisponibilidade",
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


def criar_equipamento_indisponibilidade(
    base_url,
    auth_headers,
    codigo_unico,
):
    resposta = requests.post(
        f"{base_url}/api/equipamentos/",
        headers=auth_headers,
        json={
            "identificacao":
                f"TEST-IND-EQP-{codigo_unico}",
            "nome":
                "Equipamento Teste",
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


def criar_indisponibilidade_teste(
    base_url,
    auth_headers,
    maquina_id,
):
    resposta = requests.post(
        f"{base_url}/api/indisponibilidades/",
        headers=auth_headers,
        json={
            "maquina_id":
                maquina_id,
            "inicio":
                "2026-10-15T08:00:00",
            "motivo":
                "Teste automatizado",
            "tipo":
                "QUEBRA",
            "observacoes":
                "Indisponibilidade de teste.",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    return resposta.json()[
        "indisponibilidade"
    ]


def preparar_indisponibilidade(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_indisponibilidade(
        base_url,
        auth_headers,
        codigo_unico,
    )

    cleanup_registros_teste(
        "maquinas",
        maquina["id"],
    )

    indisponibilidade = (
        criar_indisponibilidade_teste(
            base_url,
            auth_headers,
            maquina["id"],
        )
    )

    cleanup_registros_teste(
        "indisponibilidades",
        indisponibilidade["id"],
    )

    return maquina, indisponibilidade


def test_listar_indisponibilidades(
    base_url,
    auth_headers,
):
    resposta = requests.get(
        f"{base_url}/api/indisponibilidades/",
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    assert isinstance(
        dados["indisponibilidades"],
        list,
    )


def test_criar_indisponibilidade_maquina(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_indisponibilidade(
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
            "motivo":
                "Falha hidráulica",
            "tipo":
                "QUEBRA",
            "observacoes":
                "Teste automatizado.",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    dados = resposta.json()

    assert dados["success"] is True

    registro = dados[
        "indisponibilidade"
    ]

    cleanup_registros_teste(
        "indisponibilidades",
        registro["id"],
    )

    assert (
        registro["maquina_id"]
        == maquina["id"]
    )

    assert registro[
        "equipamento_id"
    ] is None

    assert registro[
        "status"
    ] == "ATIVA"

    assert registro[
        "tipo"
    ] == "QUEBRA"


def test_criar_indisponibilidade_equipamento(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    equipamento = (
        criar_equipamento_indisponibilidade(
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
        f"{base_url}/api/indisponibilidades/",
        headers=auth_headers,
        json={
            "equipamento_id":
                equipamento["id"],
            "inicio":
                "2026-10-15T08:00:00",
            "motivo":
                "Aguardando peça",
            "tipo":
                "FALTA_PECA",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    registro = resposta.json()[
        "indisponibilidade"
    ]

    cleanup_registros_teste(
        "indisponibilidades",
        registro["id"],
    )

    assert (
        registro["equipamento_id"]
        == equipamento["id"]
    )

    assert registro[
        "maquina_id"
    ] is None


def test_criar_indisponibilidade_com_fim(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_indisponibilidade(
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
                "Parada concluída",
            "tipo":
                "MANUTENCAO",
        },
        timeout=10,
    )

    assert resposta.status_code == 201

    registro = resposta.json()[
        "indisponibilidade"
    ]

    cleanup_registros_teste(
        "indisponibilidades",
        registro["id"],
    )

    assert (
        registro["status"]
        == "FINALIZADA"
    )


def test_buscar_indisponibilidade_por_id(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, registro = preparar_indisponibilidade(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.get(
        (
            f"{base_url}/api/indisponibilidades/"
            f"{registro['id']}"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    assert (
        dados["indisponibilidade"]["id"]
        == registro["id"]
    )


def test_buscar_indisponibilidade_inexistente(
    base_url,
    auth_headers,
):
    resposta = requests.get(
        (
            f"{base_url}/api/indisponibilidades/"
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


def test_indisponibilidade_sem_recurso(
    base_url,
    auth_headers,
):
    resposta = requests.post(
        f"{base_url}/api/indisponibilidades/",
        headers=auth_headers,
        json={
            "inicio":
                "2026-10-15T08:00:00",
            "motivo":
                "Teste inválido",
            "tipo":
                "QUEBRA",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["success"]
        is False
    )


def test_indisponibilidade_com_maquina_e_equipamento(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_indisponibilidade(
        base_url,
        auth_headers,
        codigo_unico,
    )

    equipamento = (
        criar_equipamento_indisponibilidade(
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
        f"{base_url}/api/indisponibilidades/",
        headers=auth_headers,
        json={
            "maquina_id":
                maquina["id"],
            "equipamento_id":
                equipamento["id"],
            "inicio":
                "2026-10-15T08:00:00",
            "motivo":
                "Teste inválido",
            "tipo":
                "QUEBRA",
        },
        timeout=10,
    )

    assert resposta.status_code == 400


def test_indisponibilidade_maquina_inexistente(
    base_url,
    auth_headers,
):
    resposta = requests.post(
        f"{base_url}/api/indisponibilidades/",
        headers=auth_headers,
        json={
            "maquina_id":
                987654321,
            "inicio":
                "2026-10-15T08:00:00",
            "motivo":
                "Teste",
            "tipo":
                "QUEBRA",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["message"]
        == "Máquina não encontrada."
    )


def test_indisponibilidade_equipamento_inexistente(
    base_url,
    auth_headers,
):
    resposta = requests.post(
        f"{base_url}/api/indisponibilidades/",
        headers=auth_headers,
        json={
            "equipamento_id":
                987654321,
            "inicio":
                "2026-10-15T08:00:00",
            "motivo":
                "Teste",
            "tipo":
                "QUEBRA",
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["message"]
        == "Equipamento não encontrado."
    )


def test_tipo_indisponibilidade_invalido(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_indisponibilidade(
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
            "motivo":
                "Teste",
            "tipo":
                "QUALQUER_COISA",
        },
        timeout=10,
    )

    assert resposta.status_code == 400


def test_periodo_indisponibilidade_invalido(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    maquina = criar_maquina_indisponibilidade(
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
                "2026-10-15T12:00:00",
            "fim":
                "2026-10-15T08:00:00",
            "motivo":
                "Teste",
            "tipo":
                "QUEBRA",
        },
        timeout=10,
    )

    assert resposta.status_code == 400


def test_filtrar_indisponibilidades_ativas(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, registro = preparar_indisponibilidade(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.get(
        (
            f"{base_url}/api/indisponibilidades/"
            "?status=ATIVA"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    registros = resposta.json()[
        "indisponibilidades"
    ]

    ids = [
        item["id"]
        for item in registros
    ]

    assert registro["id"] in ids


def test_filtro_status_invalido(
    base_url,
    auth_headers,
):
    resposta = requests.get(
        (
            f"{base_url}/api/indisponibilidades/"
            "?status=INVALIDO"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 400


def test_atualizar_indisponibilidade(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, registro = preparar_indisponibilidade(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.put(
        (
            f"{base_url}/api/indisponibilidades/"
            f"{registro['id']}"
        ),
        headers=auth_headers,
        json={
            "motivo":
                "Motivo atualizado",
            "tipo":
                "FALTA_PECA",
            "observacoes":
                "Atualização automatizada.",
        },
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    atualizada = dados[
        "indisponibilidade"
    ]

    assert (
        atualizada["motivo"]
        == "Motivo atualizado"
    )

    assert (
        atualizada["tipo"]
        == "FALTA_PECA"
    )


def test_atualizar_indisponibilidade_inexistente(
    base_url,
    auth_headers,
):
    resposta = requests.put(
        (
            f"{base_url}/api/indisponibilidades/"
            "987654321"
        ),
        headers=auth_headers,
        json={
            "motivo":
                "Teste"
        },
        timeout=10,
    )

    assert resposta.status_code == 400

    assert (
        resposta.json()["message"]
        == "Indisponibilidade não encontrada."
    )


def test_finalizar_indisponibilidade(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, registro = preparar_indisponibilidade(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.patch(
        (
            f"{base_url}/api/indisponibilidades/"
            f"{registro['id']}/finalizar"
        ),
        headers=auth_headers,
        json={
            "fim":
                "2026-10-15T12:00:00"
        },
        timeout=10,
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["success"] is True

    assert (
        dados["indisponibilidade"]["status"]
        == "FINALIZADA"
    )

    assert (
        dados["indisponibilidade"]["fim"]
        == "2026-10-15T12:00:00"
    )


def test_finalizar_indisponibilidade_sem_fim(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, registro = preparar_indisponibilidade(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.patch(
        (
            f"{base_url}/api/indisponibilidades/"
            f"{registro['id']}/finalizar"
        ),
        headers=auth_headers,
        json={},
        timeout=10,
    )

    assert resposta.status_code == 400


def test_finalizar_indisponibilidade_fim_invalido(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, registro = preparar_indisponibilidade(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.patch(
        (
            f"{base_url}/api/indisponibilidades/"
            f"{registro['id']}/finalizar"
        ),
        headers=auth_headers,
        json={
            "fim":
                "2026-10-15T07:00:00"
        },
        timeout=10,
    )

    assert resposta.status_code == 400


def test_cancelar_indisponibilidade(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, registro = preparar_indisponibilidade(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    resposta = requests.patch(
        (
            f"{base_url}/api/indisponibilidades/"
            f"{registro['id']}/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 200

    assert (
        resposta.json()[
            "indisponibilidade"
        ]["status"]
        == "CANCELADA"
    )


def test_nao_editar_indisponibilidade_finalizada(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, registro = preparar_indisponibilidade(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    finalizar = requests.patch(
        (
            f"{base_url}/api/indisponibilidades/"
            f"{registro['id']}/finalizar"
        ),
        headers=auth_headers,
        json={
            "fim":
                "2026-10-15T12:00:00"
        },
        timeout=10,
    )

    assert finalizar.status_code == 200

    resposta = requests.put(
        (
            f"{base_url}/api/indisponibilidades/"
            f"{registro['id']}"
        ),
        headers=auth_headers,
        json={
            "motivo":
                "Não deve alterar"
        },
        timeout=10,
    )

    assert resposta.status_code == 400


def test_nao_editar_indisponibilidade_cancelada(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, registro = preparar_indisponibilidade(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    cancelar = requests.patch(
        (
            f"{base_url}/api/indisponibilidades/"
            f"{registro['id']}/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert cancelar.status_code == 200

    resposta = requests.put(
        (
            f"{base_url}/api/indisponibilidades/"
            f"{registro['id']}"
        ),
        headers=auth_headers,
        json={
            "motivo":
                "Não deve alterar"
        },
        timeout=10,
    )

    assert resposta.status_code == 400


def test_nao_cancelar_indisponibilidade_finalizada(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, registro = preparar_indisponibilidade(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    finalizar = requests.patch(
        (
            f"{base_url}/api/indisponibilidades/"
            f"{registro['id']}/finalizar"
        ),
        headers=auth_headers,
        json={
            "fim":
                "2026-10-15T12:00:00"
        },
        timeout=10,
    )

    assert finalizar.status_code == 200

    resposta = requests.patch(
        (
            f"{base_url}/api/indisponibilidades/"
            f"{registro['id']}/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert resposta.status_code == 400


def test_nao_finalizar_indisponibilidade_cancelada(
    base_url,
    auth_headers,
    codigo_unico,
    cleanup_registros_teste,
):
    _, registro = preparar_indisponibilidade(
        base_url,
        auth_headers,
        codigo_unico,
        cleanup_registros_teste,
    )

    cancelar = requests.patch(
        (
            f"{base_url}/api/indisponibilidades/"
            f"{registro['id']}/cancelar"
        ),
        headers=auth_headers,
        timeout=10,
    )

    assert cancelar.status_code == 200

    resposta = requests.patch(
        (
            f"{base_url}/api/indisponibilidades/"
            f"{registro['id']}/finalizar"
        ),
        headers=auth_headers,
        json={
            "fim":
                "2026-10-15T12:00:00"
        },
        timeout=10,
    )

    assert resposta.status_code == 400


def test_indisponibilidades_sem_token(
    base_url,
):
    resposta = requests.get(
        f"{base_url}/api/indisponibilidades/",
        timeout=10,
    )

    assert resposta.status_code == 401