from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import TenantBase


class OrdemServico(TenantBase):
    __tablename__ = "ordens_servico"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    numero: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True,
        index=True
    )

    tipo: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    titulo: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    descricao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    maquina_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("maquinas.id"),
        nullable=True
    )

    equipamento_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("equipamentos.id"),
        nullable=True
    )

    operador_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=True
    )

    responsavel_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=True
    )

    prioridade: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="MEDIA"
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="ABERTA"
    )

    prazo: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
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

    maquina = relationship(
        "Maquina",
        lazy="joined"
    )

    equipamento = relationship(
        "Equipamento",
        lazy="joined"
    )

    operador = relationship(
        "Usuario",
        foreign_keys=[operador_id],
        lazy="joined"
    )

    responsavel = relationship(
        "Usuario",
        foreign_keys=[responsavel_id],
        lazy="joined"
    )

    def __repr__(self) -> str:
        return (
            f"<OrdemServico "
            f"id={self.id} "
            f"numero={self.numero} "
            f"tipo='{self.tipo}' "
            f"status='{self.status}'>"
        )