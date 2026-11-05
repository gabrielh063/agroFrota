"""Bounded per-process runtime engines; provisioning uses separate engines."""
import os
import threading

from sqlalchemy.orm import sessionmaker

from database.central import criar_engine_central
from database.tenant import criar_engine_tenant

# Do not evict: callers can retain a session factory or an active session.
# Fail closed at the limit instead of disposing an engine still in use.
_MAX_ENGINES = 32
_lock = threading.Lock()
_engines = {}
_pid = os.getpid()


def _after_fork():
    global _pid, _engines, _lock
    _lock = threading.Lock()
    _engines = {}
    _pid = os.getpid()


if hasattr(os, "register_at_fork"):
    os.register_at_fork(after_in_child=_after_fork)


def _runtime_engine(config, database_name, central=False):
    global _pid, _engines, _lock
    if os.getpid() != _pid:
        # Gunicorn may fork after importing the module. Never share pools across forks.
        _lock = threading.Lock()
        _engines = {}
        _pid = os.getpid()
    key = (config.DB_HOST, config.DB_PORT, config.DB_USER, config.DB_PASSWORD, database_name)
    with _lock:
        if key not in _engines:
            if len(_engines) >= _MAX_ENGINES:
                raise RuntimeError('Limite de engines runtime atingido neste processo')
            engine = criar_engine_central(config) if central else criar_engine_tenant(config, database_name)
            _engines[key] = engine
        return _engines[key]


def _factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False), engine


def criar_sessao_central(config):
    return _factory(_runtime_engine(config, config.DB_NAME, central=True))


def criar_sessao_tenant(config, database_name):
    return _factory(_runtime_engine(config, database_name))
