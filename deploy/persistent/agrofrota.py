#!/usr/bin/env python3
"""Operator CLI for the explicitly named persistent Compose project."""
import argparse
import json
import os
from pathlib import Path
import secrets
import shutil
import stat
import subprocess
import sys
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[2]
COMPOSE = ROOT / "deploy/persistent/compose.yaml"
PROJECT = "agrofrota-infra-01"
ACCOUNT_NAMES = (
    "admin_demo", "diretoria_demo", "gestor_frota_demo", "administrativo_demo",
    "manutencao_demo", "operador_demo", "auditor_demo",
)


def state_directory(value):
    return Path(value).expanduser() if value else Path.home() / ".config/agrofrota-infra-01"


def write_private(path, content):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise


def validate_origin(value):
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.path or parsed.query or parsed.fragment or parsed.username:
        raise ValueError("Origem deve ser a URL HTTPS MagicDNS exata, sem caminho ou credenciais.")
    return value.rstrip("/")


def env_file(directory):
    validate_state_directory(directory)
    path = directory / ".env"
    if not path.is_file() or path.is_symlink() or path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077:
        raise RuntimeError("Configuração ausente ou permissões inseguras; execute setup.")
    return path


def validate_state_directory(directory):
    if directory.is_symlink() or not directory.is_dir():
        raise RuntimeError("Diretório de estado não é uma pasta local válida.")
    info = directory.stat()
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
        raise RuntimeError("Diretório de estado deve pertencer ao operador e ter modo privado.")


def compose(directory, args, *, project=PROJECT, extra_env=None, check=True):
    env_path = env_file(directory)
    command = ["docker", "compose", "--project-name", project, "--file", str(COMPOSE), "--env-file", str(env_path), *args]
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    return subprocess.run(command, cwd=ROOT, env=env, check=check)


def require_tools():
    for binary in ("docker",):
        if not shutil.which(binary):
            raise RuntimeError(f"Dependência ausente: {binary}.")
    subprocess.run(["docker", "compose", "version"], check=True)


def setup(directory, origin):
    origin = validate_origin(origin)
    created = not directory.exists()
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if created:
        os.chmod(directory, 0o700)
    validate_state_directory(directory)
    files = (
        "db_password", "db_root_password", "flask_secret_key", "jwt_secret_key",
        "demo_credentials.json", ".env",
    )
    if any((directory / name).exists() for name in files):
        raise RuntimeError("Já existem arquivos de instalação. Nada foi sobrescrito; use credentials para consultar as contas.")
    credentials = {name: secrets.token_urlsafe(36) for name in ACCOUNT_NAMES}
    secret_values = {
        "db_password": secrets.token_urlsafe(48),
        "db_root_password": secrets.token_urlsafe(48),
        "flask_secret_key": secrets.token_urlsafe(64),
        "jwt_secret_key": secrets.token_urlsafe(64),
        "demo_credentials.json": json.dumps(credentials, ensure_ascii=False, indent=2) + "\n",
    }
    try:
        for name, value in secret_values.items():
            write_private(directory / name, value)
        env = "\n".join((
            f"AGROFROTA_SECRETS_DIR={directory.resolve()}",
            f"AGROFROTA_ORIGIN={origin}",
            "AGROFROTA_HTTP_BIND=127.0.0.1",
            "AGROFROTA_HTTP_PORT=18088",
            f"AGROFROTA_CONTAINER_UID={os.getuid()}",
            f"AGROFROTA_CONTAINER_GID={os.getgid()}",
            "AGROFROTA_VOLUME_NAME=agrofrota-infra-01-mariadb",
            "AGROFROTA_NETWORK_NAME=agrofrota-infra-01-private",
            "",
        ))
        write_private(directory / ".env", env)
    except Exception:
        # Preserve any partial secrets for manual review; never delete security material automatically.
        raise

    print(f"Segredos gravados com modo 0600 em {directory.resolve()}")
    print("Contas de demonstração (guardar em local privado):")
    for username, password in credentials.items():
        print(f"{username}: {password}")
    print("As senhas também ficam somente no arquivo privado demo_credentials.json para recuperação.")


def require_ready(directory):
    env_path = env_file(directory)
    expected = {"db_password", "db_root_password", "flask_secret_key", "jwt_secret_key", "demo_credentials.json"}
    for name in expected:
        path = directory / name
        if not path.is_file() or path.is_symlink() or path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077:
            raise RuntimeError(f"Arquivo protegido ausente ou com permissões inseguras: {name}.")
    return env_path


def run_action(args):
    directory = state_directory(args.state_dir)
    require_ready(directory)
    if args.action == "credentials":
        data = json.loads((directory / "demo_credentials.json").read_text(encoding="utf-8"))
        for username in ACCOUNT_NAMES:
            print(f"{username}: {data[username]}")
        return
    require_tools()
    if args.action == "up":
        compose(directory, ["up", "--detach", "--build"])
    elif args.action == "stop":
        compose(directory, ["stop"])
    elif args.action == "restart":
        compose(directory, ["restart"])
    elif args.action == "status":
        compose(directory, ["ps"])
    elif args.action == "logs":
        compose(directory, ["logs", "--tail", "100"])
    elif args.action == "provision":
        compose(directory, ["run", "--rm", "--no-deps", "backend", "python", "-m", "tools.provision_persistent_demo"])
    elif args.action == "backup":
        backup(directory, args.output)
    elif args.action == "restore-test":
        restore_test(directory, args.backup)


def backup(directory, output):
    destination = Path(output).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(destination, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            env_path = env_file(directory)
            command = ["docker", "compose", "--project-name", PROJECT, "--file", str(COMPOSE), "--env-file", str(env_path), "exec", "-T", "database", "sh", "-ec", "export MYSQL_PWD=\"$(cat /run/secrets/db_root_password)\"; exec mariadb-dump -uroot --single-transaction --routines --events --databases agrofrota_central agrofrota_tenant"]
            result = subprocess.run(command, cwd=ROOT, stdout=stream, check=False)
            if result.returncode:
                raise subprocess.CalledProcessError(result.returncode, command)
            stream.flush()
            os.fsync(stream.fileno())
        print(f"Backup criado com modo 0600: {destination}")
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def restore_test(directory, backup_path):
    source = Path(backup_path).expanduser().resolve(strict=True)
    if not source.is_file() or source.stat().st_size == 0:
        raise ValueError("Backup inexistente ou vazio.")
    suffix = secrets.token_hex(5)
    project = f"agro-restore-{suffix}"
    volume = f"{project}-db"
    network = f"{project}-net"
    overrides = {"AGROFROTA_VOLUME_NAME": volume, "AGROFROTA_NETWORK_NAME": network}
    started = True
    try:
        compose(directory, ["up", "--detach", "--wait", "database"], project=project, extra_env=overrides)
        command = ["docker", "compose", "--project-name", project, "--file", str(COMPOSE), "--env-file", str(directory / ".env"), "exec", "-T", "database", "sh", "-ec", "export MYSQL_PWD=\"$(cat /run/secrets/db_root_password)\"; exec mariadb -uroot"]
        with source.open("rb") as dump:
            subprocess.run(command, cwd=ROOT, stdin=dump, check=True)
        verify = ["docker", "compose", "--project-name", project, "--file", str(COMPOSE), "--env-file", str(directory / ".env"), "exec", "-T", "database", "sh", "-ec", "export MYSQL_PWD=\"$(cat /run/secrets/db_root_password)\"; exec mariadb -uroot -Nse \"SELECT CONCAT((SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name IN ('agrofrota_central','agrofrota_tenant')),'/',(SELECT COUNT(*) FROM agrofrota_tenant.alembic_version))\""]
        result = subprocess.run(verify, cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE)
        if result.stdout.strip() != "2/1":
            raise RuntimeError("Validação do backup restaurado falhou; a instância temporária será limpa após o teste.")
        print("Restauração isolada validada: dois schemas e tabela de versão Alembic presentes.")
    finally:
        if started:
            # Unique per-run project and volume names are verified before cleanup.
            if project.startswith("agro-restore-") and volume == f"{project}-db":
                compose(directory, ["down", "--volumes", "--remove-orphans"], project=project, extra_env=overrides, check=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", help="Diretório local protegido (padrão: ~/.config/agrofrota-infra-01).")
    sub = parser.add_subparsers(dest="action", required=True)
    setup_parser = sub.add_parser("setup", help="Criar segredos locais; não inicia serviços.")
    setup_parser.add_argument("--origin", required=True, help="Origem HTTPS MagicDNS confirmada na tailnet.")
    sub.add_parser("up")
    sub.add_parser("stop")
    sub.add_parser("restart")
    sub.add_parser("status")
    sub.add_parser("logs")
    sub.add_parser("provision")
    sub.add_parser("credentials")
    backup_parser = sub.add_parser("backup")
    backup_parser.add_argument("--output", required=True)
    restore_parser = sub.add_parser("restore-test")
    restore_parser.add_argument("--backup", required=True)
    args = parser.parse_args()
    directory = state_directory(args.state_dir)
    try:
        if args.action == "setup":
            setup(directory, args.origin)
        else:
            run_action(args)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Operação interrompida: {error}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
