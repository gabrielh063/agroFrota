"""Safe failures in the assistant endpoint must roll back and hide internals."""
import logging
import re
from sqlalchemy.exc import OperationalError

import routes.assistente_ia as assistant_route


def _app():
    from app import create_app

    return create_app()


def test_ollama_indisponivel_retorna_503_sem_expor_excecao(monkeypatch, token, caplog):
    def indisponivel(*_args, **_kwargs):
        raise RuntimeError("http://127.0.0.1:11434/api/chat token=private-value")

    monkeypatch.setattr(assistant_route, "processar_mensagem", indisponivel)
    caplog.set_level(logging.WARNING, logger=assistant_route.__name__)
    response = _app().test_client().post(
        "/api/assistente/mensagem",
        headers={"Authorization": f"Bearer {token}"},
        json={"mensagem": "Resuma o estado operacional."},
    )

    assert response.status_code == 503
    assert "private-value" not in response.get_data(as_text=True)
    assert "private-value" not in caplog.text
    assert "RuntimeError" in caplog.text
    correlation_id = response.headers["X-Request-ID"]
    assert re.fullmatch(r"[0-9a-f]{32}", correlation_id)
    assert correlation_id in caplog.text
    assert "Resuma o estado operacional" not in caplog.text


def test_erro_interno_retorna_500_com_log_sanitizado(monkeypatch, token, caplog):
    def falha(*_args, **_kwargs):
        raise ValueError("SQL params include private-value")

    monkeypatch.setattr(assistant_route, "processar_mensagem", falha)
    caplog.set_level(logging.ERROR, logger=assistant_route.__name__)
    response = _app().test_client().post(
        "/api/assistente/mensagem",
        headers={"Authorization": f"Bearer {token}"},
        json={"mensagem": "Resuma o estado operacional."},
    )

    assert response.status_code == 500
    assert "private-value" not in response.get_data(as_text=True)
    assert "private-value" not in caplog.text
    assert "ValueError" in caplog.text
    correlation_id = response.headers["X-Request-ID"]
    assert re.fullmatch(r"[0-9a-f]{32}", correlation_id)
    assert correlation_id in caplog.text
    assert "SQL params" not in caplog.text


def test_falta_de_recursos_de_banco_retorna_503_sanitizado(monkeypatch, token, caplog):
    def sem_recursos(*_args, **_kwargs):
        raise OperationalError("SELECT secret SQL", {"password": "private-value"}, RuntimeError("private-value"))

    monkeypatch.setattr(assistant_route, "processar_mensagem", sem_recursos)
    caplog.set_level(logging.WARNING, logger=assistant_route.__name__)
    response = _app().test_client().post(
        "/api/assistente/mensagem",
        headers={"Authorization": f"Bearer {token}"},
        json={"mensagem": "Consulta sintética."},
    )

    assert response.status_code == 503
    assert "private-value" not in response.get_data(as_text=True)
    assert "private-value" not in caplog.text and "SELECT secret SQL" not in caplog.text
    assert re.fullmatch(r"[0-9a-f]{32}", response.headers["X-Request-ID"])
