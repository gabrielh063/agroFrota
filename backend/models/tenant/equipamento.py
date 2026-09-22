from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import TenantBase


class Equipamento(TenantBase):
    __tablename__ = "equipamentos"

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

    nome: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    tipo: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    fabricante: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    modelo: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
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
        default="DISPONIVEL"
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
            f"<Equipamento "
            f"id={self.id} "
            f"identificacao='{self.identificacao}' "
            f"nome='{self.nome}'>"
        )