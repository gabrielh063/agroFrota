"""Ambiente MariaDB/HTTP descartável local; nunca reutiliza instalações existentes."""
import argparse
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

import pymysql
import requests

BACKEND = Path(__file__).resolve().parents[1]
PREFIX = 'agrofrota-db-'


def port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def metadata(path):
    p = Path(path).resolve()
    if not p.name.startswith(PREFIX) or not p.is_dir():
        raise ValueError('Diretório descartável inválido')
    st = p.stat()
    if st.st_uid != os.getuid() or st.st_mode & 0o077:
        raise ValueError('Diretório não é privado do usuário atual')
    state = json.loads((p / 'state.json').read_text())
    if state['directory'] != str(p) or len(state['marker']) < 32:
        raise ValueError('Identidade local inválida')
    return p, state


def connect(state):
    return pymysql.connect(host='127.0.0.1', port=state['db_port'], user=state['db_user'], password=state['db_password'], database='agrofrota_test_central', connect_timeout=2)


def verify(path):
    p, state = metadata(path)
    with connect(state) as db:
        with db.cursor() as cur:
            cur.execute('SELECT @@datadir, marker FROM disposable_marker')
            datadir, marker = cur.fetchone()
            if Path(datadir).resolve() != p / 'data' or marker != state['marker']:
                raise ValueError('Identidade do banco não confere')
            cur.execute('SELECT database_name FROM tenants ORDER BY id')
            if [x[0] for x in cur.fetchall()] != ['agrofrota_test_a', 'agrofrota_test_b']:
                raise ValueError('Tenants inesperados')
    for kind in ('db', 'api'):
        pid = state[kind + '_pid']
        args = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ').decode()
        expected = str(p / 'data') if kind == 'db' else str(state['api_port'])
        if expected not in args or ('mariadbd' if kind == 'db' else 'flask') not in args:
            raise ValueError('Identidade do processo não confere')
    return p, state


def env_for(p, state):
    env = os.environ.copy()
    env.update(DB_HOST='127.0.0.1', DB_PORT=str(state['db_port']), DB_USER=state['db_user'], DB_PASSWORD=state['db_password'], DB_NAME='agrofrota_test_central', AGROFROTA_ENV='testing', AGROFROTA_ENABLE_DEV_ROUTES='1', SECRET_KEY=state['secret'], JWT_SECRET_KEY=state['jwt_secret'], AGROFROTA_TEST_DISPOSABLE='1', AGROFROTA_TEST_DATADIR=str(p / 'data'), AGROFROTA_TEST_MARKER=state['marker'], AGROFROTA_BASE_URL=f"http://127.0.0.1:{state['api_port']}", AGROFROTA_TEST_DATABASE='agrofrota_test_a', AGROFROTA_TEST_DATABASE_B='agrofrota_test_b', AGROFROTA_TEST_USERNAME='admin_a', AGROFROTA_TEST_USERNAME_B='admin_b', AGROFROTA_TEST_PASSWORD=state['password_a'], AGROFROTA_TEST_PASSWORD_B=state['password_b'])
    return env


def start():
    for command in ('mariadb-install-db', 'mariadbd'):
        if not shutil.which(command):
            raise RuntimeError(f'{command} não encontrado')
    db_port = port()
    api_port = port()
    while api_port == db_port:
        api_port = port()
    p = Path(tempfile.mkdtemp(prefix=PREFIX)).resolve()
    state = dict(directory=str(p), marker=secrets.token_hex(32), db_port=db_port, api_port=api_port, db_user='af_test', db_password=secrets.token_hex(24), password_a=secrets.token_urlsafe(24), password_b=secrets.token_urlsafe(24), secret=secrets.token_urlsafe(48), jwt_secret=secrets.token_urlsafe(48))
    try:
        subprocess.run(['mariadb-install-db', '--no-defaults', f'--datadir={p / "data"}', '--auth-root-authentication-method=socket', '--skip-test-db'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log = (p / 'mariadb.log').open('ab')
        dbproc = subprocess.Popen(['mariadbd', '--no-defaults', f'--datadir={p / "data"}', f'--socket={p / "mysql.sock"}', f'--pid-file={p / "mysql.pid"}', '--bind-address=127.0.0.1', f'--port={state["db_port"]}'], stdout=log, stderr=log, start_new_session=True)
        state['db_pid'] = dbproc.pid
        for _ in range(100):
            try:
                admin = pymysql.connect(unix_socket=str(p / 'mysql.sock'), user=getpass.getuser(), connect_timeout=1, autocommit=True)
                break
            except pymysql.Error:
                if dbproc.poll() is not None:
                    raise RuntimeError('MariaDB descartável não iniciou; consulte o log privado')
                time.sleep(.1)
        else:
            raise RuntimeError('Timeout ao iniciar MariaDB descartável')
        with admin:
            with admin.cursor() as cur:
                cur.execute('SELECT @@datadir')
                if Path(cur.fetchone()[0]).resolve() != p / 'data':
                    raise ValueError('Datadir inesperado')
                for db in ('agrofrota_test_central', 'agrofrota_test_a', 'agrofrota_test_b'):
                    cur.execute(f'CREATE DATABASE `{db}`')
                cur.execute("CREATE USER 'af_test'@'127.0.0.1' IDENTIFIED BY %s", (state['db_password'],))
                for db in ('agrofrota_test_central', 'agrofrota_test_a', 'agrofrota_test_b'):
                    cur.execute(f"GRANT ALL PRIVILEGES ON `{db}`.* TO 'af_test'@'127.0.0.1'")
                cur.execute('CREATE TABLE agrofrota_test_central.disposable_marker (marker VARCHAR(128) NOT NULL)')
                cur.execute('INSERT INTO agrofrota_test_central.disposable_marker VALUES (%s)', (state['marker'],))
        env = env_for(p, state)
        def alembic(ini, db=None):
            e = env.copy()
            if db:
                e['AGROFROTA_TENANT_DB'] = db
            subprocess.run([sys.executable, '-m', 'alembic', '-c', ini, 'upgrade', 'head'], cwd=BACKEND, env=e, check=True)
        alembic('alembic-central.ini')
        for db in ('agrofrota_test_a', 'agrofrota_test_b'):
            alembic('alembic-tenant.ini', db)
        seed = BACKEND / 'tools' / 'seed_descartavel.py'
        subprocess.run([sys.executable, str(seed)], cwd=BACKEND, env=env, check=True)
        apilog = (p / 'api.log').open('ab')
        api = subprocess.Popen([sys.executable, '-m', 'flask', '--app', 'app', 'run', '--host', '127.0.0.1', '--port', str(state['api_port']), '--with-threads'], cwd=BACKEND, env=env, stdout=apilog, stderr=apilog, start_new_session=True)
        state['api_pid'] = api.pid
        (p / 'state.json').write_text(json.dumps(state))
        os.chmod(p / 'state.json', 0o600)
        for _ in range(100):
            try:
                if requests.get(env['AGROFROTA_BASE_URL'] + '/api/health', timeout=.3).status_code == 200:
                    break
            except requests.RequestException:
                pass
            if api.poll() is not None:
                raise RuntimeError('API descartável não iniciou; consulte o log privado')
            time.sleep(.1)
        else:
            raise RuntimeError('Timeout ao iniciar API descartável')
        verify(p)
        print(f'Ambiente descartável: {p}')
    except Exception:
        print(f'Preparação incompleta em {p}; recursos não foram removidos automaticamente.', file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['start', 'test', 'stop'])
    parser.add_argument('directory', nargs='?')
    parser.add_argument('tests', nargs='*')
    args = parser.parse_args()
    if args.command == 'start':
        if args.directory or args.tests:
            parser.error('start não aceita diretório ou testes')
        start()
        return
    if not args.directory:
        parser.error('informe o diretório retornado por start')
    p, state = verify(args.directory)
    if args.command == 'test':
        tests = args.tests or ['tests/test_auth.py', 'tests/test_security.py', 'tests/test_multitenant.py', 'tests/test_permissoes_rf08.py', 'tests/test_revogacao_acesso.py', 'tests/test_admin_transacional.py']
        raise SystemExit(subprocess.call([sys.executable, '-m', 'pytest', '-q', *tests], cwd=BACKEND, env=env_for(p, state)))
    if args.tests:
        parser.error('stop não aceita testes')
    # Verify both process identities and the server marker immediately before stopping.
    for kind in ('api', 'db'):
        os.kill(state[kind + '_pid'], signal.SIGTERM)
    for _ in range(100):
        alive = [pid for pid in (state['api_pid'], state['db_pid']) if Path(f'/proc/{pid}').exists() and Path(f'/proc/{pid}/cmdline').read_bytes()]
        if not alive:
            break
        time.sleep(.1)
    else:
        raise RuntimeError('Processos ainda ativos; diretório preservado')
    shutil.rmtree(p)
    print('Recursos descartáveis encerrados e removidos.')


if __name__ == '__main__':
    main()
