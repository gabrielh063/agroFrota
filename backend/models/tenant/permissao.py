from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import TenantBase


class Permissao(TenantBase):
    __tablename__ = "permissoes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    codigo: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    descricao: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )