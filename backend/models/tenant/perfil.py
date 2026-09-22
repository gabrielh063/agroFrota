from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import TenantBase


perfil_permissoes = Table(
    "perfil_permissoes",
    TenantBase.metadata,

    Column(
        "perfil_id",
        Integer,
        ForeignKey("perfis.id"),
        primary_key=True
    ),

    Column(
        "permissao_id",
        Integer,
        ForeignKey("permissoes.id"),
        primary_key=True
    )
)


class Perfil(TenantBase):
    __tablename__ = "perfis"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    descricao: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    permissoes = relationship(
        "Permissao",
        secondary=perfil_permissoes,
        lazy="selectin"
    )