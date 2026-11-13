"""Add tenant-bound account invitations.

Revision ID: 8c4a2d91f630
Revises: d54b3417f6ae
"""
from alembic import op
import sqlalchemy as sa

revision = "8c4a2d91f630"
down_revision = "d54b3417f6ae"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "convites",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=True),
        sa.Column("cargo_id", sa.Integer(), nullable=True),
        sa.Column("perfil_id", sa.Integer(), nullable=False),
        sa.Column("criado_por", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("expira_em", sa.DateTime(), nullable=False),
        sa.Column("consumido_em", sa.DateTime(), nullable=True),
        sa.Column("revogado_em", sa.DateTime(), nullable=True),
        sa.Column("revogado_por", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_convites_tenant_id", "convites", ["tenant_id"])


def downgrade():
    op.drop_index("ix_convites_tenant_id", table_name="convites")
    op.drop_table("convites")
