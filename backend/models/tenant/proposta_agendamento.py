from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import TenantBase


class PropostaAgendamento(TenantBase):
    """Proposta temporária e de uso único para agenda do assistente."""

    __tablename__ = "propostas_agendamento_ia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    tenant_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    database_name: Mapped[str] = mapped_column(String(64), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    session_version: Mapped[int] = mapped_column(Integer, nullable=False)
    # Legacy proposals reference an existing OS. New proposals may create one.
    ordem_id: Mapped[int | None] = mapped_column(ForeignKey("ordens_servico.id"), nullable=True, index=True)
    inicio: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fim: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    operacao: Mapped[str] = mapped_column(String(32), nullable=False, default="AGENDAR_OS")
    dados_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    chave_idempotencia: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    resultado_os_id: Mapped[int | None] = mapped_column(ForeignKey("ordens_servico.id"), nullable=True)
    resultado_agendamento_id: Mapped[int | None] = mapped_column(ForeignKey("agendamentos.id"), nullable=True)
    expira_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    consumida_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
