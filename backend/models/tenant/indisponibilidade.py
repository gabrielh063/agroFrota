from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import TenantBase


class Indisponibilidade(TenantBase):
    __tablename__ = "indisponibilidades"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    maquina_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("maquinas.id"),
        nullable=True,
        index=True
    )

    equipamento_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("equipamentos.id"),
        nullable=True,
        index=True
    )

    manutencao_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("manutencoes.id"),
        nullable=True,
        index=True
    )

    inicio: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    fim: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    motivo: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    tipo: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    observacoes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="ATIVA"
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

    maquina = relationship(
        "Maquina",
        lazy="joined"
    )

    equipamento = relationship(
        "Equipamento",
        lazy="joined"
    )

    manutencao = relationship(
        "Manutencao",
        lazy="joined"
    )

    def __repr__(self) -> str:
        return (
            f"<Indisponibilidade "
            f"id={self.id} "
            f"tipo='{self.tipo}' "
            f"status='{self.status}'>"
        )