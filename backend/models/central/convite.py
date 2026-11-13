from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import CentralBase


def utc_now():
    return datetime.now(UTC).replace(tzinfo=None)


class Convite(CentralBase):
    __tablename__ = "convites"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    cargo_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    perfil_id: Mapped[int] = mapped_column(Integer, nullable=False)
    criado_por: Mapped[int] = mapped_column(Integer, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    expira_em: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    consumido_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    revogado_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    revogado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
