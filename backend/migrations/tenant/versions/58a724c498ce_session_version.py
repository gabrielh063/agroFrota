"""Invalidate sessions persistently on logout or password change.

Revision ID: 58a724c498ce
Revises: 287674a77e77
"""
from alembic import op
import sqlalchemy as sa

revision = '58a724c498ce'
down_revision = '287674a77e77'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('usuarios', sa.Column('session_version', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('usuarios', 'session_version')
