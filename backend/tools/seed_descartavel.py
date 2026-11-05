"""Seed somente chamado pelo bootstrap descartável, depois das migrações."""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import Config
from database.session import criar_sessao_central
from models.central.tenant import Tenant
from sqlalchemy import text
from services.seed_service import criar_permissoes_padrao, criar_perfis_padrao, criar_usuario_gerente_padrao

if os.getenv('AGROFROTA_TEST_DISPOSABLE') != '1' or not Config.DB_NAME.startswith('agrofrota_test_'):
    raise RuntimeError('Seed restrito ao ambiente descartável')
Session, engine = criar_sessao_central(Config)
with Session.begin() as session:
    datadir, marker = session.execute(text("SELECT @@datadir, marker FROM disposable_marker")).one()
    expected = os.environ.get('AGROFROTA_TEST_DATADIR', '')
    if not expected.startswith('/tmp/agrofrota-db-') or Path(datadir).resolve() != Path(expected).resolve() or marker != os.environ.get('AGROFROTA_TEST_MARKER') or len(marker) < 32:
        raise RuntimeError('Identidade do ambiente descartável não confere')
    session.add_all([Tenant(id=4, nome='Teste A', database_name='agrofrota_test_a'), Tenant(id=5, nome='Teste B', database_name='agrofrota_test_b')])
engine.dispose()
for db, username, password in [('agrofrota_test_a', os.environ['AGROFROTA_TEST_USERNAME'], os.environ['AGROFROTA_TEST_PASSWORD']), ('agrofrota_test_b', os.environ['AGROFROTA_TEST_USERNAME_B'], os.environ['AGROFROTA_TEST_PASSWORD_B'])]:
    criar_permissoes_padrao(Config, db)
    criar_perfis_padrao(Config, db)
    criar_usuario_gerente_padrao(Config, db, 'Administrador de teste', username, password)
