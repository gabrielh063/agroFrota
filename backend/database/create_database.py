from sqlalchemy import text

from database.central import criar_engine_central


def criar_database_tenant(config, database_name):
    engine = criar_engine_central(config)

    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    f"CREATE DATABASE `{database_name}` "
                    "CHARACTER SET utf8mb4 "
                    "COLLATE utf8mb4_unicode_ci"
                )
            )
    finally:
        engine.dispose()