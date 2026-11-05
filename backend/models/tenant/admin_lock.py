from sqlalchemy import CheckConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column
from database.base import TenantBase


class AdminLock(TenantBase):
    __tablename__ = 'administracao_lock'
    __table_args__ = (CheckConstraint('id = 1', name='ck_administracao_lock_singleton'), {'mysql_engine': 'InnoDB'})
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
