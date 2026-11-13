from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import TenantBase


class Usuario(TenantBase):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    nome: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    username: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
        index=True
    )

    email: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        unique=True
    )

    senha_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    cargo_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("cargos.id"),
        nullable=True
    )

    perfil_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("perfis.id"),
        nullable=False
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    session_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    ultimo_login: Mapped[datetime | None] = mapped_column(
        DateTime,
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

    cargo = relationship(
        "Cargo",
        lazy="joined"
    )

    perfil = relationship(
        "Perfil",
        lazy="joined"
    )