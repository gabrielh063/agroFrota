from unittest.mock import patch
from uuid import uuid4
import pytest
from sqlalchemy import func, select
from config import Config
from conftest import DATABASE_NAME
from models.tenant.auditoria import EventoAuditoria
from models.tenant.maquina import Maquina
from services.admin_policy import AdministracaoNegada
from services.auditoria_service import listar_eventos
from services.maquina_service import criar_maquina
from test_matriz_escopo import sessao, contexto


def test_auditoria_sucesso_rollback_e_leitura_restrita(base_url):
    session, _ = sessao()
    try:
        ctx = contexto(session, DATABASE_NAME, 'ADMIN_EMPRESA')
        operador = contexto(session, DATABASE_NAME, 'OPERADOR')
        auditor = contexto(session, DATABASE_NAME, 'AUDITOR')
        before = session.scalar(select(func.count()).select_from(EventoAuditoria))
        session.rollback()
        ident = uuid4().hex
        criar_maquina(Config, DATABASE_NAME, ident, 'Sintético', 'Teste', contexto=ctx)
        eventos = listar_eventos(session, auditor)
        assert eventos[0].operacao == 'criar_maquina'
        assert eventos[0].ator_id == ctx.usuario_id
        assert session.scalar(select(func.count()).select_from(EventoAuditoria)) == before + 1
        session.rollback()
        outra = uuid4().hex
        with patch('services.maquina_service.registrar_evento', side_effect=RuntimeError('falha sintética')):
            with pytest.raises(RuntimeError, match='falha sintética'):
                criar_maquina(Config, DATABASE_NAME, outra, 'Teste', 'Teste', contexto=ctx)
        assert session.scalar(select(Maquina.id).where(Maquina.identificacao == outra)) is None
        assert session.scalar(select(func.count()).select_from(EventoAuditoria)) == before + 1
        with pytest.raises(AdministracaoNegada):
            listar_eventos(session, operador)
        session.rollback()
        # Force a business transaction rollback after its audit row was added.
        with patch('sqlalchemy.orm.Session.commit', side_effect=RuntimeError('commit recusado')):
            with pytest.raises(RuntimeError, match='commit recusado'):
                criar_maquina(Config, DATABASE_NAME, outra, 'Teste', 'Teste', contexto=ctx)
        assert session.scalar(select(Maquina.id).where(Maquina.identificacao == outra)) is None
        assert session.scalar(select(func.count()).select_from(EventoAuditoria)) == before + 1
    finally:
        session.close()
