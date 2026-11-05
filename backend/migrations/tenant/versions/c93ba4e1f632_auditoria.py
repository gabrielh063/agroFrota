"""Persistent audit metadata; intentionally excludes business payloads and secrets."""
from alembic import op
import sqlalchemy as sa
revision = 'c93ba4e1f632'
down_revision = 'b82a93d0e521'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('eventos_auditoria',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('ator_id', sa.Integer(), nullable=False),
        sa.Column('operacao', sa.String(80), nullable=False),
        sa.Column('ocorrido_em', sa.DateTime(), nullable=False), mysql_engine='InnoDB')
    op.create_index('ix_eventos_auditoria_ator_id', 'eventos_auditoria', ['ator_id'])


def downgrade():
    raise RuntimeError('Auditoria persistente não pode ser removida por downgrade.')
