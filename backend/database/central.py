from sqlalchemy import create_engine
from sqlalchemy.engine import URL


def criar_engine_central(config):
    database_url = URL.create(
        drivername="mysql+pymysql",
        username=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT,
        database=config.DB_NAME,
        query={
            "charset": "utf8mb4"
        }
    )

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=280,
        future=True
    )

    return engine