from types import SimpleNamespace

import pytest

from database import session as runtime


def test_reuse_and_limit_without_disposing_active_engines(monkeypatch):
    monkeypatch.setattr(runtime, '_engines', {})
    monkeypatch.setattr(runtime, '_MAX_ENGINES', 2)
    created = []
    monkeypatch.setattr(runtime, 'criar_engine_tenant', lambda config, name: created.append(object()) or created[-1])
    config = SimpleNamespace(DB_HOST='localhost', DB_PORT=3306, DB_USER='runtime', DB_PASSWORD='secret')
    first = runtime._runtime_engine(config, 'a')
    assert runtime._runtime_engine(config, 'a') is first
    assert runtime._runtime_engine(config, 'b') is not first
    with pytest.raises(RuntimeError, match='Limite'):
        runtime._runtime_engine(config, 'c')
    assert runtime._runtime_engine(config, 'a') is first
    assert len(created) == 2
