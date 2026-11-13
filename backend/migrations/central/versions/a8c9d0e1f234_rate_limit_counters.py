"""Persist opaque fixed-window API rate limits.

Revision ID: a8c9d0e1f234
Revises: 8c4a2d91f630
"""
from alembic import op
import sqlalchemy as sa


revision = "a8c9d0e1f234"
down_revision = "8c4a2d91f630"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rate_limit_counters",
        sa.Column("key_hash", sa.String(length=64), nullable=False),
        sa.Column("window_started_at", sa.DateTime(), nullable=False),
        sa.Column("request_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("key_hash"),
        mysql_engine="InnoDB",
    )


def downgrade():
    op.drop_table("rate_limit_counters")
