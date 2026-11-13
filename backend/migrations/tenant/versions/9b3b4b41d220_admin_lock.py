"""Serialize administrative mutations within each tenant.

Revision ID: 9b3b4b41d220
Revises: 58a724c498ce
"""
from alembic import op
import sqlalchemy as sa

revision = '9b3b4b41d220'
down_revision = '58a724c498ce'
branch_labels = None
depends_on = None


def upgrade():
    tables = ('usuarios', 'perfis', 'permissoes', 'perfil_permissoes')
    rows = op.get_bind().execute(sa.text(
        "SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN "
        "('usuarios','perfis','permissoes','perfil_permissoes')"
    )).all()
    engines = {name: engine for name, engine in rows}
    if any((engines.get(name) or '').lower() != 'innodb' for name in tables):
        raise RuntimeError('Autorização administrativa exige tabelas transacionais InnoDB.')
    op.create_table('administracao_lock',
                    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=False),
                    sa.CheckConstraint('id = 1', name='ck_administracao_lock_singleton'),
                    mysql_engine='InnoDB')
    op.execute('INSERT INTO administracao_lock (id) VALUES (1)')


def downgrade():
    op.drop_table('administracao_lock')
