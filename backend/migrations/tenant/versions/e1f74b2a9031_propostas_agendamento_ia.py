"""Persist one-time assistant scheduling proposals."""
from alembic import op
import sqlalchemy as sa

revision = "e1f74b2a9031"
down_revision = "c93ba4e1f632"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "propostas_agendamento_ia",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("database_name", sa.String(length=64), nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("session_version", sa.Integer(), nullable=False),
        sa.Column("ordem_id", sa.Integer(), sa.ForeignKey("ordens_servico.id"), nullable=False),
        sa.Column("inicio", sa.DateTime(), nullable=False),
        sa.Column("fim", sa.DateTime(), nullable=False),
        sa.Column("expira_em", sa.DateTime(), nullable=False),
        sa.Column("consumida_em", sa.DateTime(), nullable=True),
        sa.Column("criada_em", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("token_hash", name="uq_propostas_agendamento_ia_token_hash"),
        mysql_engine="InnoDB",
    )
    for name, column in (
        ("ix_propostas_agendamento_ia_tenant_id", "tenant_id"),
        ("ix_propostas_agendamento_ia_usuario_id", "usuario_id"),
        ("ix_propostas_agendamento_ia_ordem_id", "ordem_id"),
        ("ix_propostas_agendamento_ia_expira_em", "expira_em"),
    ):
        op.create_index(name, "propostas_agendamento_ia", [column])


def downgrade():
    raise RuntimeError("Propostas de agenda persistidas não podem ser removidas por downgrade.")
