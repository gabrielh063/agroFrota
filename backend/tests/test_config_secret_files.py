import pytest

from config import _env_secret


def test_segredo_file_tem_precedencia_e_remove_quebra_de_linha(tmp_path, monkeypatch):
    secret_file = tmp_path / "secret"
    secret_file.write_text("s3nh@/com:caracteres\n", encoding="utf-8")
    monkeypatch.setenv("TEST_SECRET", "valor-do-ambiente")
    monkeypatch.setenv("TEST_SECRET_FILE", str(secret_file))

    assert _env_secret("TEST_SECRET") == "s3nh@/com:caracteres"


def test_segredo_file_falha_sem_expor_conteudo_do_caminho(monkeypatch):
    monkeypatch.delenv("TEST_SECRET", raising=False)
    monkeypatch.setenv("TEST_SECRET_FILE", "/caminho/ausente/secret")

    with pytest.raises(RuntimeError, match="arquivo de segredo TEST_SECRET") as error:
        _env_secret("TEST_SECRET")

    assert "/caminho/ausente" not in str(error.value)


def test_segredo_env_preserva_default(monkeypatch):
    monkeypatch.delenv("TEST_SECRET", raising=False)
    monkeypatch.delenv("TEST_SECRET_FILE", raising=False)

    assert _env_secret("TEST_SECRET", "somente-teste") == "somente-teste"
