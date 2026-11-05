"""Persistent tenant operational serialization and OS sequence."""
from alembic import op
import sqlalchemy as sa

revision = 'b82a93d0e521'
down_revision = 'a71f82c9d410'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('operacao_lock',
                    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=False),
                    sa.Column('proximo_numero_os', sa.BigInteger(), nullable=False),
                    mysql_engine='InnoDB')
    op.execute('INSERT INTO operacao_lock (id, proximo_numero_os) '
               'SELECT 1, COALESCE(MAX(numero), 0) + 1 FROM ordens_servico')


def downgrade():
    raise RuntimeError('Restaure o backup validado; downgrade destrutivo não suportado.')
