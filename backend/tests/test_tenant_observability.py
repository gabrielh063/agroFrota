import logging

from sqlalchemy.exc import OperationalError, TimeoutError as PoolTimeout

from middleware.tenant import _erro_tecnico, _registrar_metricas


def test_tenant_errors_have_safe_database_categories(caplog):
    pool_error = PoolTimeout("pool timed out")
    connection_error = OperationalError("SELECT secret", {"password": "never-log-this"}, Exception("connection refused"))

    assert _erro_tecnico(pool_error) == "database_pool_timeout"
    assert _erro_tecnico(connection_error) == "database_unavailable"

    with caplog.at_level(logging.WARNING, logger="middleware.tenant"):
        _registrar_metricas("tenant_connect", {"tenant_connect": 12.5, "request_total": 14.0}, connection_error)

    assert '"error_category":"database_unavailable"' in caplog.text
    assert '"error_type":"OperationalError"' in caplog.text
    assert '"tenant_connect":12.5' in caplog.text
    assert "never-log-this" not in caplog.text
    assert "connection refused" not in caplog.text
