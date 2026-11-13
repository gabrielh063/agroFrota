"""Persist conversational context and support OS/agenda proposals."""
from alembic import op
import sqlalchemy as sa

revision = "7b53d2a1c804"
down_revision = "e1f74b2a9031"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("maquinas", sa.Column("categoria", sa.String(60), nullable=True))
    with op.batch_alter_table("propostas_agendamento_ia") as batch:
        batch.alter_column("ordem_id", existing_type=sa.Integer(), nullable=True)
        batch.alter_column("inicio", existing_type=sa.DateTime(), nullable=True)
        batch.alter_column("fim", existing_type=sa.DateTime(), nullable=True)
        batch.add_column(sa.Column("operacao", sa.String(32), nullable=False, server_default="AGENDAR_OS"))
        batch.add_column(sa.Column("dados_json", sa.Text(), nullable=True))
        batch.add_column(sa.Column("chave_idempotencia", sa.String(64), nullable=True))
        batch.add_column(sa.Column("resultado_os_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("resultado_agendamento_id", sa.Integer(), nullable=True))
        batch.create_unique_constraint("uq_propostas_agendamento_ia_idempotencia", ["chave_idempotencia"])
        batch.create_foreign_key("fk_propostas_agendamento_ia_resultado_os", "ordens_servico", ["resultado_os_id"], ["id"])
        batch.create_foreign_key("fk_propostas_agendamento_ia_resultado_agendamento", "agendamentos", ["resultado_agendamento_id"], ["id"])

    op.create_table(
        "conversas_assistente_ia",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("database_name", sa.String(64), nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("session_version", sa.Integer(), nullable=False),
        sa.Column("estado_json", sa.Text(), nullable=False),
        sa.Column("mensagens_json", sa.Text(), nullable=False),
        sa.Column("expira_em", sa.DateTime(), nullable=False),
        sa.Column("criada_em", sa.DateTime(), nullable=False),
        sa.Column("atualizada_em", sa.DateTime(), nullable=False),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_conversas_assistente_ia_tenant_id", "conversas_assistente_ia", ["tenant_id"])
    op.create_index("ix_conversas_assistente_ia_usuario_id", "conversas_assistente_ia", ["usuario_id"])
    op.create_index("ix_conversas_assistente_ia_expira_em", "conversas_assistente_ia", ["expira_em"])


def downgrade():
    raise RuntimeError("Conversas e propostas operacionais não podem ser removidas por downgrade.")
