from datetime import datetime

import pytest
from pydantic import ValidationError

from schemas.indisponibilidade import (
    IndisponibilidadeCriarSchema,
)


def test_criar_indisponibilidade_valida():

    dados = IndisponibilidadeCriarSchema(
        maquina_id=1,
        inicio=datetime(
            2026,
            9,
            25,
            8,
            0
        ),
        fim=datetime(
            2026,
            9,
            25,
            12,
            0
        ),
        motivo="Manutenção preventiva",
        tipo="MANUTENCAO",
    )

    assert dados.maquina_id == 1
    assert dados.tipo == "MANUTENCAO"


def test_exigir_maquina_ou_equipamento():

    with pytest.raises(
        ValidationError
    ):

        IndisponibilidadeCriarSchema(
            inicio=datetime.now(),
            motivo="Teste",
            tipo="MANUTENCAO",
        )


def test_nao_permitir_maquina_e_equipamento():

    with pytest.raises(
        ValidationError
    ):

        IndisponibilidadeCriarSchema(
            maquina_id=1,
            equipamento_id=1,
            inicio=datetime.now(),
            motivo="Teste",
            tipo="MANUTENCAO",
        )


def test_fim_deve_ser_posterior_inicio():

    with pytest.raises(
        ValidationError
    ):

        IndisponibilidadeCriarSchema(
            maquina_id=1,

            inicio=datetime(
                2026,
                9,
                25,
                12,
                0
            ),

            fim=datetime(
                2026,
                9,
                25,
                8,
                0
            ),

            motivo="Teste",

            tipo="MANUTENCAO",
        )


def test_tipo_indisponibilidade_invalido():

    with pytest.raises(
        ValidationError
    ):

        IndisponibilidadeCriarSchema(
            maquina_id=1,
            inicio=datetime.now(),
            motivo="Teste",
            tipo="TIPO_INEXISTENTE",
        )