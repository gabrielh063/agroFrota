from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import TenantBase


class ConversaAssistente(TenantBase):
    __tablename__ = "conversas_assistente_ia"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    database_name: Mapped[str] = mapped_column(String(64), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    session_version: Mapped[int] = mapped_column(Integer, nullable=False)
    estado_json: Mapped[str] = mapped_column(Text, nullable=False)
    mensagens_json: Mapped[str] = mapped_column(Text, nullable=False)
    expira_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    atualizada_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
