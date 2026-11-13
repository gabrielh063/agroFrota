"""Database-backed request limits; client forwarded-IP headers are not trusted."""
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import time

from sqlalchemy import case, delete, func, select
from sqlalchemy.dialects.mysql import insert as mysql_insert

from config import Config
from database.session import criar_sessao_central
from models.central.rate_limit import RateLimitCounter


def _opaque_key(bucket: str) -> str:
    secret = Config.SECRET_KEY.encode("utf-8")
    return hmac.new(secret, bucket.encode("utf-8"), hashlib.sha256).hexdigest()


def consumir_limite(bucket: str, *, limite: int, janela_segundos: int) -> tuple[bool, int]:
    """Atomically consume one slot; return (allowed, retry_after_seconds)."""
    if limite < 1 or janela_segundos < 1:
        raise ValueError("Rate limit configuration must be positive.")
    key = _opaque_key(bucket)
    now_epoch = time.time()
    now = datetime.fromtimestamp(now_epoch, UTC).replace(tzinfo=None)
    factory, _engine = criar_sessao_central(Config)

    cutoff = now - timedelta(seconds=janela_segundos)
    statement = mysql_insert(RateLimitCounter).values(
        key_hash=key, window_started_at=now, request_count=1,
    ).on_duplicate_key_update(
        request_count=case(
            (RateLimitCounter.window_started_at <= cutoff, 1),
            else_=func.least(RateLimitCounter.request_count + 1, limite + 1),
        ),
        window_started_at=case(
            (RateLimitCounter.window_started_at <= cutoff, now),
            else_=RateLimitCounter.window_started_at,
        ),
    )
    with factory() as session:
        session.execute(statement)
        row = session.execute(select(RateLimitCounter).where(
            RateLimitCounter.key_hash == key
        ).with_for_update()).scalar_one()
        elapsed = max(0, int((now - row.window_started_at).total_seconds()))
        allowed = row.request_count <= limite
        retry_after = 0 if allowed else max(1, janela_segundos - elapsed)
        session.commit()

    # Bound table growth without retaining request identities longer than one day.
    if int(now_epoch) % 257 == 0:
        with factory() as cleanup:
            cleanup.execute(delete(RateLimitCounter).where(
                RateLimitCounter.window_started_at < now - timedelta(days=1)
            ))
            cleanup.commit()
    return allowed, retry_after


def limpar_limite(bucket: str) -> None:
    """Clear an opaque bucket after successful authentication."""
    factory, _engine = criar_sessao_central(Config)
    with factory() as session:
        session.execute(delete(RateLimitCounter).where(
            RateLimitCounter.key_hash == _opaque_key(bucket)
        ))
        session.commit()
