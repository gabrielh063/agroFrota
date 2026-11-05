from types import SimpleNamespace

import pytest

from config import validar_configuracao


def config_segura():
    return SimpleNamespace(
        SECRET_KEY="aZ3!bm7K2#tx9Pq4Lw8R5uV6yD1hG0Fc",
        JWT_SECRET_KEY="kH8$zC5mN2qA6vW0yE3sD9pB7rT4fL1X",
        DB_USER="agrofrota_runtime", DB_PASSWORD="valor-de-teste",
        CORS_ORIGINS=["https://agrofrota.example"],
        JWT_ACCESS_TOKEN_EXPIRES=900,
    )


def test_producao_aceita_configuracao_basica_segura():
    validar_configuracao(config_segura(), "production")


@pytest.mark.parametrize("change", [
    {"SECRET_KEY": "chave-desenvolvimento"},
    {"DB_USER": "root"},
    {"DB_PASSWORD": ""},
    {"CORS_ORIGINS": ["*"]},
    {"JWT_ACCESS_TOKEN_EXPIRES": 7200},
])
def test_producao_rejeita_configuracao_insegura(change):
    config = config_segura()
    for name, value in change.items():
        setattr(config, name, value)
    with pytest.raises(RuntimeError, match="insegura"):
        validar_configuracao(config, "production")


def test_producao_rejeita_debug_e_rotas_dev():
    with pytest.raises(RuntimeError):
        validar_configuracao(config_segura(), "production", dev_routes=True)
    with pytest.raises(RuntimeError):
        validar_configuracao(config_segura(), "production", debug=True)
