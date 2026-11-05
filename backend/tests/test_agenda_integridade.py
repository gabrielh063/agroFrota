from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import select
from config import Config
from database.session import criar_sessao_tenant
from models.tenant.agendamento import Agendamento
from models.tenant.indisponibilidade import Indisponibilidade
from models.tenant.maquina import Maquina
from models.tenant.ordem_servico import OrdemServico
from services.calendario_service import criar_agendamento, cancelar_agendamento
from conftest import DATABASE_NAME, _exigir_ambiente_descartavel


@pytest.fixture
def banco():
    _exigir_ambiente_descartavel()
    factory, engine = criar_sessao_tenant(Config, DATABASE_NAME)
    with factory() as s:
        maquina = Maquina(identificacao=uuid4().hex, modelo='Teste', fabricante='Teste', ativo=True)
        s.add(maquina)
        s.flush()
        ordem = OrdemServico(numero=int(uuid4().int % 1000000000) + 1000000000,
                             tipo='SERVICO', titulo='Teste', maquina_id=maquina.id,
                             prioridade='MEDIA', status='ABERTA', ativo=True)
        s.add(ordem)
        s.commit()
        ids = maquina.id, ordem.id
    yield factory, ids
    engine.dispose()


def test_intervalos_indisponibilidade_e_cancelamento(banco):
    factory, (maquina, ordem) = banco
    inicio = datetime(2030, 1, 1, 8)
    with factory() as s:
        a = criar_agendamento(s, ordem, inicio, inicio + timedelta(hours=1))
        criar_agendamento(s, ordem, inicio + timedelta(hours=1), inicio + timedelta(hours=2))
        with pytest.raises(ValueError, match='Conflito'):
            criar_agendamento(s, ordem, inicio + timedelta(minutes=30), inicio + timedelta(hours=3))
        s.rollback()
        cancelar_agendamento(s, a.id)
        criar_agendamento(s, ordem, inicio, inicio + timedelta(hours=1))
        s.add(Indisponibilidade(maquina_id=maquina, inicio=inicio + timedelta(hours=3),
                               fim=inicio + timedelta(hours=4), motivo='Teste', tipo='QUEBRA', status='FINALIZADA'))
        s.commit()
        with pytest.raises(ValueError, match='indisponível'):
            criar_agendamento(s, ordem, inicio + timedelta(hours=3), inicio + timedelta(hours=4))
        s.rollback()
        assert len(s.scalars(select(Agendamento).where(Agendamento.ordem_servico_id == ordem)).all()) == 3


def test_concorrencia_duas_conexoes(banco):
    factory, (_, ordem) = banco
    inicio = datetime(2031, 1, 1, 8)
    barreira = Barrier(2, timeout=10)
    def reservar():
        with factory() as s:
            barreira.wait()
            try:
                criar_agendamento(s, ordem, inicio, inicio + timedelta(hours=1))
                return 'criado'
            except ValueError:
                s.rollback()
                return 'conflito'
    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados = list(pool.map(lambda _: reservar(), range(2)))
    assert sorted(resultados) == ['conflito', 'criado']
    with factory() as s:
        assert len(s.scalars(select(Agendamento).where(Agendamento.ordem_servico_id == ordem)).all()) == 1


def test_concorrencia_ordens_distintas_mesma_maquina(banco):
    factory, (maquina, ordem) = banco
    with factory() as s:
        outra = OrdemServico(numero=int(uuid4().int % 1000000000) + 1000000000,
                             tipo='SERVICO', titulo='Outra', maquina_id=maquina,
                             prioridade='MEDIA', status='ABERTA', ativo=True)
        s.add(outra)
        s.commit()
        outra_id = outra.id
    inicio = datetime(2032, 1, 1, 8)
    barreira = Barrier(2, timeout=10)
    def reservar(os_id):
        with factory() as s:
            barreira.wait()
            try:
                criar_agendamento(s, os_id, inicio, inicio + timedelta(hours=1))
                return 'criado'
            except ValueError:
                s.rollback()
                return 'conflito'
    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados = list(pool.map(reservar, [ordem, outra_id]))
    assert sorted(resultados) == ['conflito', 'criado']
    with factory() as s:
        assert len(s.scalars(select(Agendamento).where(Agendamento.ordem_servico_id.in_([ordem, outra_id]))).all()) == 1


def test_edicao_revalida_intervalo_e_transicao(banco):
    from services.calendario_service import atualizar_agendamento
    factory, (_, ordem) = banco
    inicio = datetime(2033, 1, 1, 8)
    with factory() as s:
        primeiro = criar_agendamento(s, ordem, inicio, inicio + timedelta(hours=1))
        segundo = criar_agendamento(s, ordem, inicio + timedelta(hours=1), inicio + timedelta(hours=2))
        primeiro_id, segundo_id = primeiro.id, segundo.id
        with pytest.raises(ValueError, match='Conflito'):
            atualizar_agendamento(s, segundo_id, inicio=inicio + timedelta(minutes=30))
        s.rollback()
        with pytest.raises(ValueError, match='Transição'):
            atualizar_agendamento(s, primeiro_id, status='CONCLUIDO')
        s.rollback()
        atualizar_agendamento(s, primeiro_id, status='EM_ANDAMENTO')
        atualizar_agendamento(s, primeiro_id, status='CONCLUIDO')
        s.expire_all()
        assert s.get(Agendamento, primeiro_id).status == 'CONCLUIDO'
        assert s.get(Agendamento, segundo_id).inicio == inicio + timedelta(hours=1)
