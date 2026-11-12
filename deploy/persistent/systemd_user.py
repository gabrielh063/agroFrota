#!/usr/bin/env python3
"""Install/remove only this repository's per-user systemd unit."""
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "deploy/persistent/agrofrota.py"
MARKER = "# Managed-by: AgroFrota infra-01"
UNIT_NAME = "agrofrota-infra-01.service"


def systemd_quote(value):
    return '"' + str(value).replace("%", "%%").replace("\\", "\\\\").replace('"', '\\"') + '"'


def unit_text(state_dir):
    user = os.environ.get("USER") or str(os.getuid())
    start = " ".join(systemd_quote(part) for part in (
        "python3", str(CLI), "--state-dir", str(state_dir), "up"
    ))
    stop = " ".join(systemd_quote(part) for part in (
        "python3", str(CLI), "--state-dir", str(state_dir), "stop"
    ))
    return f"""{MARKER}
[Unit]
Description=AgroFrota persistente (Tailscale privado)
After=network-online.target docker.service tailscaled.service
Wants=network-online.target
Requires=docker.service
ConditionPathExists={systemd_quote(state_dir / '.env')}

[Service]
Type=oneshot
RemainAfterExit=yes
User={systemd_quote(user)}
WorkingDirectory={systemd_quote(ROOT)}
ExecStart={start}
ExecStop={stop}
TimeoutStartSec=15min
TimeoutStopSec=90s
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=read-only

[Install]
WantedBy=default.target
"""


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"install", "remove"}:
        raise SystemExit("uso: systemd_user.py install|remove")
    unit_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "systemd/user"
    unit_path = unit_dir / UNIT_NAME
    if sys.argv[1] == "install":
        state_dir = Path(os.environ.get("AGROFROTA_STATE_DIR", Path.home() / ".config/agrofrota-infra-01")).expanduser().resolve()
        if not (state_dir / ".env").is_file():
            raise SystemExit("Estado persistente ainda não foi inicializado; rode setup primeiro.")
        if unit_path.exists() and MARKER not in unit_path.read_text(encoding="utf-8"):
            raise SystemExit(f"Unidade preexistente não gerenciada pelo AgroFrota: {unit_path}")
        unit_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        temp = unit_path.with_suffix(".service.tmp")
        temp.write_text(unit_text(state_dir), encoding="utf-8")
        os.chmod(temp, 0o600)
        temp.replace(unit_path)
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        print(f"Unidade preparada: {unit_path}. Para ativá-la, use systemctl --user enable --now {UNIT_NAME}.")
        return

    if not unit_path.is_file() or MARKER not in unit_path.read_text(encoding="utf-8"):
        raise SystemExit("Unidade ausente ou não identificada como AgroFrota; nada foi removido.")
    subprocess.run(["systemctl", "--user", "disable", "--now", UNIT_NAME], check=True)
    unit_path.unlink()
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    print("Somente a unidade do AgroFrota foi removida; volume de dados e segredos foram preservados.")


if __name__ == "__main__":
    main()
