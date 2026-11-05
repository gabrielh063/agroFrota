from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from schemas.agendamento import AgendamentoAtualizarSchema
from services.calendario_service import atualizar_agendamento


def agendamento():
    return SimpleNamespace(
        inicio=datetime(2026, 11, 6, 8), fim=datetime(2026, 11, 6, 9),
        status="AGENDADO", responsavel_id=7, observacoes="existente",
    )


def test_campos_omitidos_sao_preservados_e_null_remove_valores():
    item = agendamento()
    session = Mock()
    dados = AgendamentoAtualizarSchema.model_validate(
        {"responsavel_id": None, "observacoes": None}
    ).model_dump(exclude_unset=True)
    with patch("services.calendario_service.buscar_agendamento", return_value=item):
        atualizar_agendamento(session, 1, **dados)
    assert item.responsavel_id is None
    assert item.observacoes is None
    assert item.status == "AGENDADO"
    assert item.inicio == datetime(2026, 11, 6, 8)
    session.commit.assert_called_once()


def test_responsavel_inativo_nao_deve_gravar_alteracoes():
    item = agendamento()
    session = Mock()
    session.execute.return_value.scalar_one_or_none.return_value = SimpleNamespace(ativo=False)
    with patch("services.calendario_service.buscar_agendamento", return_value=item):
        with pytest.raises(ValueError, match="inativo"):
            atualizar_agendamento(session, 1, status="EM_ANDAMENTO", responsavel_id=8)
    assert item.status == "AGENDADO"
    session.commit.assert_not_called()
