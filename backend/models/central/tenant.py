from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import CentralBase


def utc_now():
    return datetime.now(UTC).replace(tzinfo=None)


class Tenant(CentralBase):

    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    nome: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    database_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now
    )

    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now
    )

    def __repr__(self) -> str:
        return (
            f"<Tenant "
            f"id={self.id} "
            f"nome='{self.nome}' "
            f"database='{self.database_name}'>"
        )