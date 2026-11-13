"""Record accepted invitation on its tenant user for safe retry.

Revision ID: f48d32ce17a1
Revises: e1f74b2a9031
"""
from alembic import op
import sqlalchemy as sa

revision = "f48d32ce17a1"
down_revision = "7b53d2a1c804"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("usuarios", sa.Column("convite_id", sa.String(length=36), nullable=True))
    op.create_unique_constraint("uq_usuarios_convite_id", "usuarios", ["convite_id"])


def downgrade():
    op.drop_constraint("uq_usuarios_convite_id", "usuarios", type_="unique")
    op.drop_column("usuarios", "convite_id")
