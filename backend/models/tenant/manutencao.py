from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import TenantBase


class Manutencao(TenantBase):
    __tablename__ = "manutencoes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    ordem_servico_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ordens_servico.id"),
        nullable=False,
        index=True
    )

    responsavel_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=True
    )

    tipo: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    inicio: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    fim: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    descricao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    custo: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="EM_ANDAMENTO"
    )

    observacoes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
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

    ordem_servico = relationship(
        "OrdemServico",
        lazy="joined"
    )

    responsavel = relationship(
        "Usuario",
        lazy="joined"
    )

    def __repr__(self) -> str:
        return (
            f"<Manutencao "
            f"id={self.id} "
            f"ordem_servico_id={self.ordem_servico_id} "
            f"status='{self.status}'>"
        )