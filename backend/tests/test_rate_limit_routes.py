"""Route-level rate limits fail closed and ignore client-supplied proxy headers."""
import routes.auth as auth_route
import routes.convites as invite_route


def _app():
    from flask import Flask
    from routes.auth import auth_bp
    from routes.convites import convites_bp

    app = Flask(__name__)
    app.register_blueprint(auth_bp)
    app.register_blueprint(convites_bp)
    return app


def test_validar_convite_responde_429_e_nao_confia_em_x_forwarded_for(monkeypatch):
    buckets = []

    def limited(bucket, **_kwargs):
        buckets.append(bucket)
        return False, 37

    monkeypatch.setattr(invite_route, "consumir_limite", limited)
    response = _app().test_client().post(
        "/api/convites/validar", headers={"X-Forwarded-For": "198.51.100.77"},
        json={"token": "synthetic"},
    )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "37"
    assert buckets == ["invite-validate-peer:127.0.0.1"]
    assert "198.51.100.77" not in buckets[0]


def test_login_responde_429_antes_de_validar_credenciais(monkeypatch):
    buckets = []

    def limited(bucket, **_kwargs):
        buckets.append(bucket)
        return False, 19

    monkeypatch.setattr(auth_route, "consumir_limite", limited)
    response = _app().test_client().post(
        "/api/auth/login", headers={"X-Forwarded-For": "203.0.113.44"}, json={},
    )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "19"
    assert buckets == ["login-peer:127.0.0.1"]
    assert "203.0.113.44" not in buckets[0]
