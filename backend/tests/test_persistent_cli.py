import json
import os
import subprocess
import sys

sys.path.insert(0, str(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

import pytest

from deploy.persistent.agrofrota import ACCOUNT_NAMES, require_ready, restore_test, run_action, setup, validate_origin


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


def test_persistent_provision_invokes_seed_as_backend_module(tmp_path, monkeypatch):
    state = tmp_path / "private-state"
    setup(state, "https://agrofrota.example.ts.net")
    calls = []
    monkeypatch.setattr("deploy.persistent.agrofrota.require_tools", lambda: None)
    monkeypatch.setattr("deploy.persistent.agrofrota.compose", lambda directory, args: calls.append((directory, args)))

    class Args:
        action = "provision"
        state_dir = str(state)

    run_action(Args())

    assert calls == [(state, ["run", "--rm", "--no-deps", "backend", "python", "-m", "tools.provision_persistent_demo"])]


def test_restore_test_waits_for_isolated_database_health(tmp_path, monkeypatch):
    backup = tmp_path / "backup.sql"
    backup.write_text("-- sanitized fixture\n", encoding="utf-8")
    state = tmp_path / "private-state"
    setup(state, "https://agrofrota.example.ts.net")
    compose_calls = []
    run_calls = []

    def fake_compose(directory, args, **kwargs):
        compose_calls.append((args, kwargs))

    def fake_run(command, **kwargs):
        run_calls.append(command)
        if "SELECT CONCAT" in command[-1]:
            return subprocess.CompletedProcess(command, 0, stdout="2/1\n")
        return subprocess.CompletedProcess(command, 0, stdout="")

    monkeypatch.setattr("deploy.persistent.agrofrota.compose", fake_compose)
    monkeypatch.setattr("deploy.persistent.agrofrota.subprocess.run", fake_run)

    restore_test(state, backup)

    assert "--wait" in compose_calls[0][0]
    assert compose_calls[0][0][-1] == "database"
    assert len(run_calls) == 2
    assert compose_calls[-1][0][0] == "down"
