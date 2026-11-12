import pytest

from routes.assistente_ia import _enabled
from services import assistente_ia_service


def test_central_permanece_desabilitada_em_producao_sem_flag(monkeypatch):
    monkeypatch.setenv("AGROFROTA_ENV", "production")
    monkeypatch.delenv("AGROFROTA_ENABLE_ASSISTANT", raising=False)

    assert _enabled() is False


def test_central_existente_pode_ser_habilitada_explicitamente_em_producao(monkeypatch):
    monkeypatch.setenv("AGROFROTA_ENV", "production")
    monkeypatch.setenv("AGROFROTA_ENABLE_ASSISTANT", "1")
    monkeypatch.delenv("AGROFROTA_ENABLE_DEV_ROUTES", raising=False)

    assert _enabled() is True


def test_flag_da_central_nao_habilita_rotas_de_desenvolvimento(monkeypatch):
    monkeypatch.setenv("AGROFROTA_ENV", "production")
    monkeypatch.setenv("AGROFROTA_ENABLE_ASSISTANT", "1")
    monkeypatch.delenv("AGROFROTA_ENABLE_DEV_ROUTES", raising=False)

    import config
    monkeypatch.setattr(config.Config, "SECRET_KEY", "jX4rT2mP8vN6cQ1wY5hK9bF3dL7sA0eG")
    monkeypatch.setattr(config.Config, "JWT_SECRET_KEY", "pB9yW3nH6fR1vK8zM2qD5sC7aE4tL0xG")
    monkeypatch.setattr(config.Config, "DB_USER", "agrofrota_runtime")
    monkeypatch.setattr(config.Config, "DB_PASSWORD", "senha-runtime-de-teste")
    monkeypatch.setattr(config.Config, "CORS_ORIGINS", ["https://agrofrota.example.ts.net"])

    from app import create_app

    app = create_app()
    assert "/api/dev/protegida" not in {rule.rule for rule in app.url_map.iter_rules()}


def test_consulta_dependente_do_modelo_exibe_erro_explicito_quando_ollama_indisponivel(monkeypatch):
    monkeypatch.setenv("AGRO_AI_OLLAMA_URL", "http://127.0.0.1:11434")
    monkeypatch.setattr(assistente_ia_service, "recuperar", lambda _pergunta: [])

    def indisponivel(*_args, **_kwargs):
        raise assistente_ia_service.requests.ConnectionError("falha sintética de conexão")

    monkeypatch.setattr(assistente_ia_service.requests, "get", indisponivel)
    monkeypatch.setattr(assistente_ia_service.requests, "post", indisponivel)

    with pytest.raises(RuntimeError, match="Não foi possível consultar o Ollama"):
        assistente_ia_service.chamar_ollama("pergunta demonstrativa", {})
