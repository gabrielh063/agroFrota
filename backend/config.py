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