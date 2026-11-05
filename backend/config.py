import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Configurações principais da aplicação.
    """

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "chave-desenvolvimento"
    )

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "chave-jwt-desenvolvimento"
    )

    # ------------------------------------------------------
    # BANCO CENTRAL
    # ------------------------------------------------------

    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "fazenda_saas")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://"
        f"{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}"
        f"/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ------------------------------------------------------
    # JWT
    # ------------------------------------------------------

    JWT_ACCESS_TOKEN_EXPIRES = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600")
    )

    # ------------------------------------------------------
    # CORS
    # ------------------------------------------------------

    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]

def validar_configuracao(config, ambiente, debug=False, dev_routes=False):
    """Reject unsafe production settings before any database access."""
    if ambiente not in {"development", "testing", "production"}:
        raise RuntimeError("AGROFROTA_ENV deve ser development, testing ou production.")
    if ambiente != "production":
        return
    problemas = []
    if debug or dev_routes:
        problemas.append("debug e rotas dev devem estar desativados")
    for nome in ("SECRET_KEY", "JWT_SECRET_KEY"):
        valor = getattr(config, nome, "")
        if not isinstance(valor, str) or len(valor) < 32 or valor in {
            "chave-desenvolvimento", "chave-jwt-desenvolvimento",
            "preencha_com_valor_aleatorio_local", "preencha_com_outro_valor_aleatorio_local",
        } or len(set(valor)) < 12:
            problemas.append(f"{nome} deve ser um segredo aleatório de pelo menos 32 caracteres")
    if config.SECRET_KEY == config.JWT_SECRET_KEY:
        problemas.append("SECRET_KEY e JWT_SECRET_KEY devem ser diferentes")
    if not config.DB_PASSWORD or config.DB_USER.lower() in {"root", "admin"}:
        problemas.append("banco exige usuário runtime dedicado e senha")
    if any(origin == "*" or not origin.startswith("https://") for origin in config.CORS_ORIGINS):
        problemas.append("CORS em produção aceita somente origens HTTPS explícitas")
    if not 60 <= config.JWT_ACCESS_TOKEN_EXPIRES <= 3600:
        problemas.append("JWT_ACCESS_TOKEN_EXPIRES deve estar entre 60 e 3600 segundos")
    if problemas:
        raise RuntimeError("Configuração de produção insegura: " + "; ".join(problemas))
