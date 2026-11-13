from uuid import uuid4
import pytest
from config import Config
from conftest import DATABASE_NAME
from services.admin_policy import AdministracaoNegada
from services.maquina_service import criar_maquina
from sqlalchemy import select, delete
from models.tenant.usuario import Usuario
from models.tenant.perfil import perfil_permissoes
from models.tenant.permissao import Permissao
from services.ordem_servico_service import (criar_ordem_servico, listar_ordens_servico,
    buscar_ordem_servico, atualizar_ordem_servico)
from test_matriz_escopo import sessao, contexto


def test_os_atribuicao_persistida_e_payload_nao_concede_acesso(base_url):
    session, _ = sessao()
    try:
        admin = contexto(session, DATABASE_NAME, 'ADMIN_EMPRESA')
        operador = contexto(session, DATABASE_NAME, 'OPERADOR')
        manutencao = contexto(session, DATABASE_NAME, 'MANUTENCAO')
    finally:
        session.close()
    maquina = criar_maquina(Config, DATABASE_NAME, uuid4().hex, 'Teste', 'Teste', contexto=admin)
    with pytest.raises(AdministracaoNegada):
        criar_ordem_servico(Config, DATABASE_NAME, 'SERVICO', 'Tentativa', maquina_id=maquina.id,
                            operador_id=operador.usuario_id, contexto=operador)
    atribuida = criar_ordem_servico(Config, DATABASE_NAME, 'SERVICO', 'Atribuição', maquina_id=maquina.id,
        operador_id=operador.usuario_id, responsavel_id=manutencao.usuario_id, contexto=admin)
    privada = criar_ordem_servico(Config, DATABASE_NAME, 'SERVICO', 'Restrita', maquina_id=maquina.id,
                                  contexto=admin)
    assert buscar_ordem_servico(Config, DATABASE_NAME, privada.id, contexto=operador) is None
    assert buscar_ordem_servico(Config, DATABASE_NAME, atribuida.id, contexto=operador).id == atribuida.id
    for ator in (operador, manutencao):
        ids = {o.id for o in listar_ordens_servico(Config, DATABASE_NAME, contexto=ator)}
        assert atribuida.id in ids and privada.id not in ids
    with pytest.raises(AdministracaoNegada):
        atualizar_ordem_servico(Config, DATABASE_NAME, atribuida.id,
                               responsavel_id=manutencao.usuario_id, contexto=manutencao)
    assert atualizar_ordem_servico(Config, DATABASE_NAME, atribuida.id,
        titulo='Execução autorizada', contexto=manutencao).titulo == 'Execução autorizada'
    criada = criar_ordem_servico(Config, DATABASE_NAME, 'SERVICO', 'Solicitação atribuída',
        maquina_id=maquina.id, operador_id=operador.usuario_id, contexto=operador)
    assert criada.operador_id == operador.usuario_id
    with pytest.raises(ValueError, match='não encontrada'):
        atualizar_ordem_servico(Config, DATABASE_NAME, privada.id, titulo='Negada', contexto=manutencao)
    session, _ = sessao()
    try:
        perfil_id = session.get(Usuario, manutencao.usuario_id).perfil_id
        permissao_id = session.scalar(select(Permissao.id).where(Permissao.codigo == 'OS.CONCLUIR'))
        session.execute(delete(perfil_permissoes).where(
            perfil_permissoes.c.perfil_id == perfil_id,
            perfil_permissoes.c.permissao_id == permissao_id))
        session.commit()
        try:
            with pytest.raises(AdministracaoNegada):
                atualizar_ordem_servico(Config, DATABASE_NAME, atribuida.id,
                                       status='concluida', contexto=manutencao)
            assert buscar_ordem_servico(Config, DATABASE_NAME, atribuida.id, contexto=admin).status == 'ABERTA'
        finally:
            session.execute(perfil_permissoes.insert().values(perfil_id=perfil_id, permissao_id=permissao_id))
            session.commit()
    finally:
        session.close()
