from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import TenantBase


class Maquina(TenantBase):
    __tablename__ = "maquinas"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    identificacao: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    modelo: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    fabricante: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    ano: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    localizacao: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="OPERANDO"
    )

    controla_telemetria: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<Maquina "
            f"id={self.id} "
            f"identificacao='{self.identificacao}' "
            f"modelo='{self.modelo}'>"
        )