"""Classify legacy standard profiles without changing their permissions.

Revision ID: a71f82c9d410
Revises: 9b3b4b41d220
"""
from alembic import op
import sqlalchemy as sa

revision = 'a71f82c9d410'
down_revision = '9b3b4b41d220'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('perfis', sa.Column('politica_escopo', sa.String(32), nullable=True))
    # No associations or user assignments are added. Existing ADMIN_EMPRESA
    # names are not assumed to be the standard template.
    op.execute("UPDATE perfis SET politica_escopo='ADMIN_EMPRESA' WHERE nome='GERENTE'")
    op.execute("UPDATE perfis SET politica_escopo=nome WHERE nome IN ('OPERADOR','MANUTENCAO')")
    op.execute("UPDATE usuarios SET session_version=session_version+1 WHERE perfil_id IN (SELECT id FROM perfis WHERE politica_escopo IS NOT NULL)")


def downgrade():
    op.drop_column('perfis', 'politica_escopo')
