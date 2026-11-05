from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from database.base import TenantBase


class EventoAuditoria(TenantBase):
    __tablename__ = 'eventos_auditoria'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ator_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    operacao: Mapped[str] = mapped_column(String(80), nullable=False)
    ocorrido_em: Mapped[datetime] = mapped_column(DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
