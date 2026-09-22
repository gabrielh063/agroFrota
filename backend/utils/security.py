from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


def gerar_hash_senha(senha: str) -> str:
    """
    Gera hash seguro para armazenamento da senha.
    """

    return generate_password_hash(
        senha,
        method="scrypt"
    )


def verificar_senha(
    senha: str,
    senha_hash: str
) -> bool:
    """
    Verifica se a senha informada corresponde ao hash.
    """

    return check_password_hash(
        senha_hash,
        senha
    )