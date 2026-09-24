from utils.security import (
    gerar_hash_senha,
    verificar_senha,
)


def test_gerar_hash_senha():

    senha = "SenhaTeste@123"

    senha_hash = gerar_hash_senha(
        senha
    )

    assert senha_hash is not None

    assert senha_hash != senha

    assert len(senha_hash) > len(senha)


def test_verificar_senha_correta():

    senha = "SenhaTeste@123"

    senha_hash = gerar_hash_senha(
        senha
    )

    assert verificar_senha(
        senha,
        senha_hash
    ) is True


def test_rejeitar_senha_incorreta():

    senha_hash = gerar_hash_senha(
        "SenhaCorreta@123"
    )

    assert verificar_senha(
        "SenhaErrada",
        senha_hash
    ) is False