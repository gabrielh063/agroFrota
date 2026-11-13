from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import CentralBase


class RateLimitCounter(CentralBase):
    """Opaque fixed-window counters for cross-worker API throttling."""

    __tablename__ = "rate_limit_counters"

    key_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    window_started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, nullable=False)
