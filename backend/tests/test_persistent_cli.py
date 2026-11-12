import json
import os
import sys

sys.path.insert(0, str(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

import pytest

from deploy.persistent.agrofrota import ACCOUNT_NAMES, require_ready, setup, validate_origin


def test_persistent_setup_creates_unique_private_secrets_and_demo_accounts(tmp_path, capsys):
    state = tmp_path / "private-state"
    setup(state, "https://agrofrota.example.ts.net")

    assert state.stat().st_mode & 0o777 == 0o700
    for filename in (
        ".env", "db_password", "db_root_password", "flask_secret_key",
        "jwt_secret_key", "demo_credentials.json",
    ):
        path = state / filename
        assert path.stat().st_mode & 0o777 == 0o600
    credentials = json.loads((state / "demo_credentials.json").read_text(encoding="utf-8"))
    assert require_ready(state) == state / ".env"
    assert set(credentials) == set(ACCOUNT_NAMES)
    assert len(set(credentials.values())) == len(ACCOUNT_NAMES)
    assert all(len(value) >= 32 for value in credentials.values())
    assert all(value not in (state / ".env").read_text(encoding="utf-8") for value in credentials.values())
    output = capsys.readouterr().out
    assert all(name in output for name in ACCOUNT_NAMES)


def test_persistent_setup_never_overwrites_existing_secret(tmp_path):
    state = tmp_path / "private-state"
    setup(state, "https://agrofrota.example.ts.net")
    original = (state / "db_password").read_bytes()

    with pytest.raises(RuntimeError, match="Nada foi sobrescrito"):
        setup(state, "https://other.example.ts.net")

    assert (state / "db_password").read_bytes() == original


@pytest.mark.parametrize("origin", [
    "http://agrofrota.example.ts.net",
    "https://agrofrota.example.ts.net/extra",
    "https://user:pass@agrofrota.example.ts.net",
])
def test_persistent_setup_rejects_noncanonical_origin(origin):
    with pytest.raises(ValueError):
        validate_origin(origin)


def test_persistent_setup_refuses_existing_public_state_directory(tmp_path):
    state = tmp_path / "state"
    state.mkdir(mode=0o755)
    os.chmod(state, 0o755)

    with pytest.raises(RuntimeError, match="modo privado"):
        setup(state, "https://agrofrota.example.ts.net")

    assert list(state.iterdir()) == []
