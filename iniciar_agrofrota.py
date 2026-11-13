#!/usr/bin/env python3
"""AgroFrota: sessão local descartável com MariaDB, Flask, Vite e Ollama.

Uso (na raiz do repositório, ao lado das pastas backend/ e frontend/):
    python3 iniciar_agrofrota.py
    python3 iniciar_agrofrota.py --modelo llama3.2:3b
    python3 iniciar_agrofrota.py --sem-dados

Ctrl+C: encerra os serviços desta sessão e apaga apenas seu MariaDB temporário.
Não executa git pull, não troca branch e não mexe em bancos existentes.

A arquitetura do AgroFrota exige dois schemas lógicos no MESMO MariaDB:
    agrofrota_demo_central (tenants)
    agrofrota_demo_tenant  (empresa, máquinas, OS etc.)
"""

from __future__ import annotations

import argparse
import fcntl
import getpass
import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
CENTRAL_DB = "agrofrota_demo_central"
TENANT_DB = "agrofrota_demo_tenant"
LOGIN = "admin_demo"
PREFIX = "agrofrota-sessao-"
DEMO_PROFILES = (
    ("ADMIN_EMPRESA", "Administrador/Gerente", LOGIN),
    ("DIRETORIA", "Diretoria", "diretoria_demo"),
    ("GESTOR_FROTA", "Gestor de Frota", "gestor_frota_demo"),
    ("ADMINISTRATIVO", "Administrativo", "administrativo_demo"),
    ("MANUTENCAO", "Manutenção", "manutencao_demo"),
    ("OPERADOR", "Operador", "operador_demo"),
    ("AUDITOR", "Auditor", "auditor_demo"),
)


def echo(msg=""):
    print(msg, flush=True)


def must_exist():
    for p in (BACKEND / "app.py", BACKEND / "alembic-central.ini", BACKEND / "alembic-tenant.ini", FRONTEND / "package.json"):
        if not p.is_file():
            raise RuntimeError(f"Arquivo do projeto não encontrado: {p}")
    for command in ("mariadb-install-db", "mariadbd", "npm"):
        if shutil.which(command) is None:
            raise RuntimeError(f"'{command}' não está instalado ou não está no PATH.")


def ensure_venv():
    launch_dir = Path(os.environ["AGROFROTA_LAUNCH_DIR"]).resolve()
    VENV = launch_dir / "venv"
    target = VENV / "bin" / "python"
    if Path(sys.prefix).resolve() != VENV.resolve():
        if not target.is_file():
            echo("[preparação] Criando ambiente virtual Python...")
            subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
        os.execv(str(target), [str(target), str(Path(__file__).resolve()), *sys.argv[1:]])


def ensure_deps():
    try:
        import alembic  # noqa: F401
        import pymysql  # noqa: F401
        import flask  # noqa: F401
        import flask_cors  # noqa: F401
        import sqlalchemy  # noqa: F401
    except ImportError:
        echo("[preparação] Instalando dependências do backend...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(BACKEND / "requirements.txt")], check=True)
    if not (FRONTEND / "node_modules" / ".bin" / "vite").is_file():
        echo("[preparação] Instalando dependências do frontend...")
        subprocess.run(["npm", "ci"], cwd=FRONTEND, check=True)


def free_port(preferred=None, avoid=()):
    candidates = ([preferred] if preferred else []) + [0]
    for candidate in candidates:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", candidate))
                port = sock.getsockname()[1]
                if port not in avoid:
                    return port
            except OSError:
                pass
    raise RuntimeError("Não encontrei porta livre.")


def http_status(url, timeout=1.0, method="GET", headers=None):
    try:
        request = Request(url, method=method, headers=headers or {})
        with urlopen(request, timeout=timeout) as response:
            return response.status, dict(response.headers)
    except HTTPError as exc:
        return exc.code, dict(exc.headers)
    except (OSError, URLError):
        return None, {}


SEED_CODE = r'''
from datetime import datetime, timedelta
from sqlalchemy import select
from config import Config
from database.session import criar_sessao_central, criar_sessao_tenant
from models.central.tenant import Tenant
from models.tenant.maquina import Maquina
from models.tenant.equipamento import Equipamento
from models.tenant.ordem_servico import OrdemServico
from models.tenant.agendamento import Agendamento
from models.tenant.operacao_lock import OperacaoLock
from models.tenant.perfil import Perfil
from models.tenant.usuario import Usuario
from services.seed_service import (criar_permissoes_padrao, criar_perfis_padrao,
                                   criar_usuario_gerente_padrao)
from utils.security import gerar_hash_senha
import os
import json

central = os.environ["DB_NAME"]
tenant = os.environ["AGROFROTA_TENANT_DB"]
SessionCentral, _ = criar_sessao_central(Config)
with SessionCentral.begin() as session:
    session.add(Tenant(nome="AgroFrota Demonstracao", database_name=tenant, ativo=True))

criar_permissoes_padrao(Config, tenant)
criar_perfis_padrao(Config, tenant)
criar_usuario_gerente_padrao(Config, tenant, "Administrador Demo",
                            os.environ["AGRO_DEMO_USER"], os.environ["AGRO_DEMO_PASSWORD"])

demo_credentials = json.loads(os.environ["AGRO_DEMO_PROFILE_CREDENTIALS"])
SessionTenant, _ = criar_sessao_tenant(Config, tenant)
with SessionTenant.begin() as session:
    profiles = {profile.nome: profile for profile in session.execute(select(Perfil)).scalars()}
    demo_user_ids = {}
    for credential in demo_credentials:
        profile = profiles.get(credential["profile"])
        if profile is None or not profile.ativo:
            raise RuntimeError("Perfil demonstrativo não foi provisionado pelas migrations/seed")
        if credential["profile"] == "ADMIN_EMPRESA":
            usuario = session.execute(select(Usuario).where(
                Usuario.username == credential["username"]
            )).scalar_one()
        else:
            usuario = Usuario(
                nome=f"Demo — {credential['label']}",
                username=credential["username"],
                senha_hash=gerar_hash_senha(credential["password"]),
                perfil_id=profile.id,
                ativo=True,
            )
            session.add(usuario)
            session.flush()
        demo_user_ids[credential["profile"]] = usuario.id

if os.environ.get("AGRO_DEMO_SEED_DATA") == "1":
    SessionTenant, _ = criar_sessao_tenant(Config, tenant)
    with SessionTenant.begin() as session:
        m = [
            Maquina(identificacao="DEMO-TR-01", modelo="6110J", fabricante="John Deere", categoria="TRATOR", ano=2021, status="OPERANDO", ativo=True, localizacao="Fazenda demonstrativa"),
            Maquina(identificacao="DEMO-TR-02", modelo="MF 6713", fabricante="Massey Ferguson", categoria="TRATOR", ano=2022, status="OPERANDO", ativo=True, localizacao="Fazenda demonstrativa"),
            Maquina(identificacao="DEMO-TR-03", modelo="A114", fabricante="Valtra", categoria="TRATOR", ano=2019, status="MANUTENCAO", ativo=True, localizacao="Oficina"),
            Maquina(identificacao="DEMO-CO-01", modelo="TC5.80", fabricante="New Holland", categoria="COLHEITADEIRA", ano=2020, status="OPERANDO", ativo=True, localizacao="Fazenda demonstrativa"),
            Maquina(identificacao="DEMO-PU-01", modelo="Uniport 3030", fabricante="Jacto", categoria="PULVERIZADOR", ano=2018, status="PARADA", ativo=True, localizacao="Galpão"),
        ]
        e = [
            Equipamento(identificacao="DEMO-IM-01", nome="Grade aradora 28 discos", tipo="GRADE", status="DISPONIVEL", ativo=True),
            Equipamento(identificacao="DEMO-IM-02", nome="Carreta graneleira", tipo="CARRETA", status="DISPONIVEL", ativo=True),
            Equipamento(identificacao="DEMO-IM-03", nome="Distribuidor de adubo", tipo="DISTRIBUIDOR", status="MANUTENCAO", ativo=True),
        ]
        session.add_all([*m, *e])
        session.flush()
        lock = session.get(OperacaoLock, 1)
        if lock is None:
            raise RuntimeError("operacao_lock não inicializado pelas migrations")
        start = lock.proximo_numero_os
        os_rows = [
            OrdemServico(numero=start, tipo="MANUTENCAO", titulo="Revisão preventiva do trator", descricao="OS fictícia atribuída à equipe de manutenção", maquina_id=m[0].id, responsavel_id=demo_user_ids["MANUTENCAO"], prioridade="MEDIA", status="ABERTA", ativo=True),
            OrdemServico(numero=start + 1, tipo="MANUTENCAO", titulo="Troca de filtros hidráulicos", descricao="OS fictícia atribuída ao operador", maquina_id=m[2].id, operador_id=demo_user_ids["OPERADOR"], prioridade="ALTA", status="EM_ANDAMENTO", ativo=True),
            OrdemServico(numero=start + 2, tipo="MANUTENCAO", titulo="Inspeção da colheitadeira", maquina_id=m[3].id, prioridade="URGENTE", status="ABERTA", ativo=True),
            OrdemServico(numero=start + 3, tipo="MANUTENCAO", titulo="Ajuste de grade aradora", equipamento_id=e[0].id, prioridade="MEDIA", status="ABERTA", ativo=True),
            OrdemServico(numero=start + 4, tipo="MANUTENCAO", titulo="Teste elétrico de partida", maquina_id=m[0].id, prioridade="ALTA", status="CONCLUIDA", ativo=True),
            OrdemServico(numero=start + 5, tipo="MANUTENCAO", titulo="Inspeção de bomba pulverizadora", maquina_id=m[4].id, prioridade="URGENTE", status="EM_ANDAMENTO", ativo=True),
        ]
        session.add_all(os_rows)
        lock.proximo_numero_os = start + len(os_rows)
        session.flush()
        day = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        session.add(Agendamento(ordem_servico_id=os_rows[0].id, inicio=day,
                                fim=day + timedelta(hours=2), status="AGENDADO",
                                observacoes="Agenda fictícia de demonstração"))
print("Seed inicial concluído: administrador e dados demonstrativos.")
'''


class Session:
    def __init__(self, model: str, sem_dados: bool):
        self.model = model
        self.sem_dados = sem_dados
        self.dir: Path | None = None
        self.children: dict[str, subprocess.Popen] = {}
        self.logs = {}
        self.state = {}
        self.env = {}
        self.owned_ollama = False

    def log(self, name):
        f = (self.dir / f"{name}.log").open("ab")
        self.logs[name] = f
        return f

    def run_logged(self, argv, *, cwd=None, env=None, logfile="preparacao"):
        description = "seed de demonstração" if "-c" in argv else " ".join(str(x) for x in argv[:4])
        echo("[preparação] " + description + " ...")
        with (self.dir / f"{logfile}.log").open("ab") as output:
            subprocess.run(argv, cwd=cwd, env=env, stdout=output, stderr=subprocess.STDOUT, check=True)

    def launch(self, name, argv, *, cwd=None, env=None):
        proc = subprocess.Popen(argv, cwd=cwd, env=env,
                                stdout=self.log(name), stderr=subprocess.STDOUT,
                                start_new_session=True)
        self.children[name] = proc
        return proc

    def wait_for(self, name, url, attempts=120, headers=None):
        for _ in range(attempts):
            proc = self.children.get(name)
            if proc is not None and proc.poll() is not None:
                raise RuntimeError(f"Processo '{name}' encerrou inesperadamente. Veja os logs.")
            code, _ = http_status(url, timeout=0.3, headers=headers)
            if code == 200:
                return
            time.sleep(0.25)
        raise RuntimeError(f"Serviço '{name}' não iniciou: {url}")

    def start(self):
        import pymysql
        self.dir = Path(os.environ["AGROFROTA_LAUNCH_DIR"]).resolve()
        if self.dir.parent != Path(tempfile.gettempdir()).resolve() or not self.dir.name.startswith(PREFIX):
            raise RuntimeError("Diretório temporário da sessão não passou na validação de identidade.")
        self.state = {
            "session_id": secrets.token_hex(16),
            "db_port": free_port(),
            "api_port": None,
            "frontend_port": None,
            "db_user": "af_demo",
            "db_password": secrets.token_urlsafe(32),
            "app_user": LOGIN,
            "app_password": secrets.token_urlsafe(16),
            "secret_key": secrets.token_urlsafe(48),
            "jwt_secret_key": secrets.token_urlsafe(48),
            "central_db": CENTRAL_DB,
            "tenant_db": TENANT_DB,
        }
        self.state["demo_profiles"] = [
            {
                "profile": role,
                "label": label,
                "username": username,
                "password": self.state["app_password"] if role == "ADMIN_EMPRESA" else secrets.token_urlsafe(18),
            }
            for role, label, username in DEMO_PROFILES
        ]
        self.state["api_port"] = free_port(avoid={self.state["db_port"]})
        self.state["frontend_port"] = free_port(preferred=5173, avoid={self.state["db_port"], self.state["api_port"]})
        s = self.state
        self.env = os.environ.copy()
        self.env.update({
            "DB_HOST": "127.0.0.1", "DB_PORT": str(s["db_port"]),
            "DB_USER": s["db_user"], "DB_PASSWORD": s["db_password"],
            "DB_NAME": CENTRAL_DB,
            "AGROFROTA_TENANT_DB": TENANT_DB,
            "AGROFROTA_ENV": "development", "AGROFROTA_ENABLE_DEV_ROUTES": "0",
            "SECRET_KEY": s["secret_key"], "JWT_SECRET_KEY": s["jwt_secret_key"],
            "FLASK_DEBUG": "0",
            "CORS_ORIGINS": f"http://127.0.0.1:{s['frontend_port']},http://localhost:{s['frontend_port']}",
            "AGRO_AI_MODEL": self.model,
            "AGRO_AI_OLLAMA_URL": "http://127.0.0.1:11434",
            "AGRO_AI_TIMEZONE": "America/Sao_Paulo",
            "AGRO_AI_INDEX_PATH": str(self.dir / "vault.sqlite3"),
            "AGRO_DEMO_SEED_DATA": "0" if self.sem_dados else "1",
            "VITE_API_URL": f"http://127.0.0.1:{s['api_port']}",
            "VITE_TENANT_DATABASE": TENANT_DB,
            "VITE_AGROFROTA_DEMO": "true",
        })
        (self.dir / "state.json").write_text(json.dumps(s, indent=2))
        os.chmod(self.dir / "state.json", 0o600)

        echo("[1/5] Criando uma instância MariaDB temporária...")
        self.run_logged([
            "mariadb-install-db", "--no-defaults", f"--datadir={self.dir / 'data'}",
            "--auth-root-authentication-method=socket", "--skip-test-db",
        ])
        db = self.launch("mariadb", [
            "mariadbd", "--no-defaults", f"--datadir={self.dir / 'data'}",
            f"--socket={self.dir / 'mysql.sock'}", f"--pid-file={self.dir / 'mysql.pid'}",
            "--bind-address=127.0.0.1", f"--port={s['db_port']}",
        ])
        for _ in range(120):
            if db.poll() is not None:
                raise RuntimeError("MariaDB encerrou inesperadamente.")
            try:
                admin = pymysql.connect(unix_socket=str(self.dir / "mysql.sock"),
                                        user=getpass.getuser(), connect_timeout=1, autocommit=True)
                break
            except pymysql.Error:
                time.sleep(0.25)
        else:
            raise RuntimeError("MariaDB não ficou disponível.")

        with admin:
            with admin.cursor() as cur:
                cur.execute("SELECT @@datadir")
                if Path(cur.fetchone()[0]).resolve() != (self.dir / "data").resolve():
                    raise RuntimeError("O servidor MariaDB não pertence a esta sessão.")
                for name in (CENTRAL_DB, TENANT_DB):
                    cur.execute(f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                cur.execute("CREATE USER 'af_demo'@'127.0.0.1' IDENTIFIED BY %s", (s["db_password"],))
                for name in (CENTRAL_DB, TENANT_DB):
                    cur.execute(f"GRANT ALL PRIVILEGES ON `{name}`.* TO 'af_demo'@'127.0.0.1'")

        echo("[2/5] Aplicando migrations e criando usuário administrador...")
        for ini, dbname in (("alembic-central.ini", CENTRAL_DB), ("alembic-tenant.ini", TENANT_DB)):
            env = dict(self.env, AGROFROTA_TENANT_DB=dbname)
            self.run_logged([sys.executable, "-m", "alembic", "-c", ini, "upgrade", "head"],
                            cwd=BACKEND, env=env)
        seed_env = dict(self.env, AGRO_DEMO_USER=s["app_user"],
                        AGRO_DEMO_PASSWORD=s["app_password"],
                        AGRO_DEMO_PROFILE_CREDENTIALS=json.dumps(s["demo_profiles"]))
        self.run_logged([sys.executable, "-c", SEED_CODE], cwd=BACKEND, env=seed_env)

        echo("[3/5] Verificando o Ollama...")
        ollama_up, _ = http_status("http://127.0.0.1:11434/api/tags", timeout=1.2)
        if ollama_up != 200:
            if shutil.which("ollama"):
                self.launch("ollama", ["ollama", "serve"])
                self.owned_ollama = True
                try:
                    self.wait_for("ollama", "http://127.0.0.1:11434/api/tags", attempts=80)
                except RuntimeError:
                    echo("[aviso] Ollama não iniciou; o restante do sistema poderá funcionar sem IA.")
            else:
                echo("[aviso] Ollama não instalado: a IA não estará disponível.")

        echo("[4/5] Iniciando Flask com a branch atualmente selecionada...")
        self.launch("flask", [
            sys.executable, "-m", "flask", "--app", "app", "run",
            "--host", "127.0.0.1", "--port", str(s["api_port"]), "--without-threads",
        ], cwd=BACKEND, env=self.env)
        self.wait_for("flask", f"http://127.0.0.1:{s['api_port']}/api/health")
        options_url = f"http://127.0.0.1:{s['api_port']}/api/assistente/conversas"
        status, cors_headers = http_status(options_url, method="OPTIONS", headers={
            "Origin": f"http://127.0.0.1:{s['frontend_port']}",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        })
        if status != 200:
            raise RuntimeError(f"A rota da IA não respondeu ao preflight (HTTP {status}). Verifique se está na branch AGRO-IA-02.")
        allow_origin = cors_headers.get("Access-Control-Allow-Origin")
        if allow_origin not in (f"http://127.0.0.1:{s['frontend_port']}", "*"):
            raise RuntimeError("O preflight da API não autorizou a origem do frontend.")

        login_request = Request(
            f"http://127.0.0.1:{s['api_port']}/api/auth/login",
            data=json.dumps({"username": s["app_user"], "senha": s["app_password"],
                             "database_name": TENANT_DB}).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(login_request, timeout=4) as response:
                login_data = json.loads(response.read())
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            raise RuntimeError(f"Login demonstrativo não passou no smoke test ({type(exc).__name__}).") from exc
        token = login_data.get("data", {}).get("access_token") if login_data.get("success") else None
        if not token:
            raise RuntimeError("A API não retornou sessão para o usuário demonstrativo.")
        auth_headers = {"Authorization": f"Bearer {token}"}
        for path in ("/api/auth/me", "/api/dashboard/capacidade", "/api/assistente/conversas"):
            status, _ = http_status(f"http://127.0.0.1:{s['api_port']}{path}", headers=auth_headers)
            if status != 200:
                raise RuntimeError(f"Smoke test autenticado falhou em {path} (HTTP {status}).")

        echo("[5/5] Iniciando frontend React/Vite...")
        self.launch("vite", ["npm", "--prefix", str(FRONTEND), "run", "dev", "--",
                              "--host", "127.0.0.1", "--port", str(s["frontend_port"]), "--strictPort"],
                    cwd=ROOT, env=self.env)
        self.wait_for("vite", f"http://127.0.0.1:{s['frontend_port']}/", attempts=120)
        self.show_info()

    def show_info(self):
        s = self.state
        echo("\n" + "=" * 66)
        echo("  AGROFROTA INICIADO — AMBIENTE TEMPORÁRIO / DADOS FICTÍCIOS")
        echo("=" * 66)
        echo(f"  Tela de login:  http://127.0.0.1:{s['frontend_port']}/login")
        echo(f"  Dashboard:      http://127.0.0.1:{s['frontend_port']}/")
        echo(f"  Assistente IA:  http://127.0.0.1:{s['frontend_port']}/assistente")
        echo(f"  API Flask:      http://127.0.0.1:{s['api_port']}")
        echo(f"  Ollama:         http://127.0.0.1:11434  (modelo: {self.model})")
        echo("-" * 66)
        echo("  CONTAS TEMPORÁRIAS DE DEMONSTRAÇÃO (credenciais válidas somente nesta sessão):")
        for profile in s["demo_profiles"]:
            echo(f"  {profile['label']:<24} usuário: {profile['username']}  senha: {profile['password']}")
        echo(f"  Empresa/tenant: {s['tenant_db']}")
        echo("-" * 66)
        echo(f"  Banco central:  {s['central_db']}")
        echo(f"  Banco empresa:  {s['tenant_db']}")
        echo(f"  MariaDB host:   127.0.0.1")
        echo(f"  MariaDB porta:  {s['db_port']}")
        echo(f"  MariaDB user:   {s['db_user']}")
        echo(f"  MariaDB senha:  {s['db_password']}")
        echo("-" * 66)
        echo(f"  Logs privados:  {self.dir}")
        echo("  Encerrar:       Ctrl+C NESTE terminal")
        echo("  ATENÇÃO: Banco, propostas e dados serão APAGADOS ao encerrar.")
        echo("=" * 66 + "\n")

    def print_error_logs(self):
        if not self.dir:
            return
        for name in ("preparacao", "mariadb", "flask", "vite", "ollama"):
            p = self.dir / f"{name}.log"
            if p.is_file():
                text = p.read_text(errors="replace").splitlines()[-12:]
                if text:
                    message = "\n".join(text)
                    for key in ("db_password", "app_password", "secret_key", "jwt_secret_key"):
                        if self.state.get(key):
                            message = message.replace(self.state[key], "[oculto]")
                    echo(f"\n--- {name}: últimas linhas ---\n{message}")

    def stop(self):
        echo("\n[encerrando] Finalizando apenas os processos desta sessão...")
        for name in ("vite", "flask", "ollama", "mariadb"):
            proc = self.children.get(name)
            if not proc or proc.poll() is not None:
                continue
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait(timeout=5)
        for logfile in self.logs.values():
            logfile.close()
        if self.dir:
            expected_root = Path(tempfile.gettempdir()).resolve()
            if (self.dir.parent == expected_root and self.dir.name.startswith(PREFIX)
                    and self.dir.is_dir() and self.dir.stat().st_uid == os.getuid()
                    and all((p.poll() is not None) for p in self.children.values())):
                shutil.rmtree(self.dir)
                echo("[concluído] Banco MariaDB temporário e logs desta sessão removidos.")
            else:
                echo(f"[aviso] Não foi possível garantir limpeza segura: {self.dir}")


def main():
    parser = argparse.ArgumentParser(description="Inicia AgroFrota em MariaDB temporário; Ctrl+C apaga o banco.")
    parser.add_argument("--modelo", default="llama3.1:8b", help="Modelo Ollama local já instalado")
    parser.add_argument("--sem-dados", action="store_true", help="Não cria dados fictícios, apenas usuário de login")
    args = parser.parse_args()
    must_exist()
    existing_launch_dir = os.environ.get("AGROFROTA_LAUNCH_DIR")
    if existing_launch_dir:
        launch_dir = Path(existing_launch_dir).resolve()
        if (launch_dir.parent != Path(tempfile.gettempdir()).resolve()
                or not launch_dir.name.startswith(PREFIX)
                or not launch_dir.is_dir() or launch_dir.stat().st_uid != os.getuid()):
            raise RuntimeError("Diretório temporário recebido na reexecução não passou na validação.")
    else:
        launch_dir = Path(tempfile.mkdtemp(prefix=PREFIX)).resolve()
        os.chmod(launch_dir, 0o700)
        os.environ["AGROFROTA_LAUNCH_DIR"] = str(launch_dir)

    lock_file = Path(tempfile.gettempdir()) / f"agrofrota-launcher-{os.getuid()}.lock"
    with lock_file.open("a+") as lock:
        os.chmod(lock_file, 0o600)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("Este inicializador já está executando outra sessão. Encerre-a com Ctrl+C primeiro.")
        run = None
        def on_term(_signum, _frame):
            raise KeyboardInterrupt
        signal.signal(signal.SIGTERM, on_term)
        if hasattr(signal, "SIGHUP"):
            signal.signal(signal.SIGHUP, on_term)
        try:
            ensure_venv()
            ensure_deps()
            run = Session(args.modelo, args.sem_dados)
            run.start()
            while True:
                for name in ("mariadb", "flask", "vite"):
                    child = run.children.get(name)
                    if child and child.poll() is not None:
                        raise RuntimeError(f"O processo '{name}' encerrou (código {child.returncode}).")
                time.sleep(1)
        except KeyboardInterrupt:
            echo("\nSolicitação de parada recebida.")
        except Exception:
            echo("\n[erro] O ambiente não conseguiu iniciar ou um serviço parou.")
            if run:
                run.print_error_logs()
            raise
        finally:
            if run:
                run.stop()
            elif launch_dir.is_dir() and launch_dir.parent == Path(tempfile.gettempdir()).resolve():
                shutil.rmtree(launch_dir)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        echo(f"ERRO: {type(exc).__name__}: {exc}")
        sys.exit(1)
