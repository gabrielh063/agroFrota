from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column
from database.base import TenantBase


class OperacaoLock(TenantBase):
    __tablename__ = 'operacao_lock'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    proximo_numero_os: Mapped[int] = mapped_column(BigInteger, nullable=False)
