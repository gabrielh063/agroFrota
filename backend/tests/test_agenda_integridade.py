from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier
from uuid import uuid4

import pytest
import requests
from sqlalchemy import select
from config import Config
from database.session import criar_sessao_tenant
from models.tenant.agendamento import Agendamento
from models.tenant.indisponibilidade import Indisponibilidade
from models.tenant.maquina import Maquina
from models.tenant.ordem_servico import OrdemServico
from services.calendario_service import criar_agendamento, cancelar_agendamento
from services.indisponibilidade_service import criar_indisponibilidade
from schemas.indisponibilidade import IndisponibilidadeCriarSchema
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


def test_concorrencia_agendamento_e_indisponibilidade_nao_cria_sobreposicao(banco):
    factory, (maquina, ordem) = banco
    inicio = datetime(2034, 1, 1, 8)
    barreira = Barrier(2, timeout=10)

    def reservar():
        with factory() as s:
            barreira.wait()
            try:
                criar_agendamento(s, ordem, inicio, inicio + timedelta(hours=2))
                return "agendamento"
            except ValueError:
                s.rollback()
                return "conflito"

    def bloquear():
        with factory() as s:
            barreira.wait()
            try:
                criar_indisponibilidade(s, IndisponibilidadeCriarSchema(
                    maquina_id=maquina, inicio=inicio,
                    fim=inicio + timedelta(hours=2), motivo="Quebra de teste",
                    tipo="QUEBRA",
                ))
                return "indisponibilidade"
            except ValueError:
                s.rollback()
                return "conflito"

    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados = list(pool.map(lambda fn: fn(), (reservar, bloquear)))

    assert resultados.count("conflito") == 1
    assert len(set(resultados) - {"conflito"}) == 1
    with factory() as s:
        agendamentos = s.scalars(select(Agendamento).where(
            Agendamento.ordem_servico_id == ordem,
        )).all()
        indisponibilidades = s.scalars(select(Indisponibilidade).where(
            Indisponibilidade.maquina_id == maquina,
        )).all()
        assert len(agendamentos) + len(indisponibilidades) == 1


def test_maquina_fora_de_operacao_nao_pode_ser_agendada(banco):
    factory, (maquina, ordem) = banco
    with factory() as s:
        item = s.get(Maquina, maquina)
        item.status = "MANUTENCAO"
        s.commit()
        with pytest.raises(ValueError, match="condição operacional"):
            criar_agendamento(s, ordem, datetime(2035, 1, 1, 8), datetime(2035, 1, 1, 10))
        s.rollback()
        assert s.scalars(select(Agendamento).where(Agendamento.ordem_servico_id == ordem)).all() == []


def test_recurso_com_agenda_pendente_nao_pode_ser_indisponibilizado(
    base_url, auth_headers, codigo_unico, cleanup_registros_teste,
):
    machine = requests.post(f"{base_url}/api/maquinas/", headers=auth_headers,
        json={"identificacao": f"LOCK-{codigo_unico}", "modelo": "Trator teste",
              "fabricante": "Fabricante", "categoria": "TRATOR", "status": "OPERANDO"}, timeout=10)
    assert machine.status_code == 201, machine.text
    machine_id = machine.json()["data"]["id"]
    cleanup_registros_teste("maquinas", machine_id)

    order = requests.post(f"{base_url}/api/ordens-servico/", headers=auth_headers,
        json={"tipo": "SERVICO", "titulo": "OS com agenda", "maquina_id": machine_id}, timeout=10)
    assert order.status_code == 201, order.text
    order_id = order.json()["ordem_servico"]["id"]
    cleanup_registros_teste("ordens_servico", order_id)

    start = "2036-01-01T08:00:00"
    appointment = requests.post(f"{base_url}/api/calendario/", headers=auth_headers,
        json={"ordem_servico_id": order_id, "inicio": start, "fim": "2036-01-01T10:00:00"}, timeout=10)
    assert appointment.status_code == 201, appointment.text
    cleanup_registros_teste("agendamentos", appointment.json()["agendamento"]["id"])

    update = requests.put(f"{base_url}/api/maquinas/{machine_id}", headers=auth_headers,
        json={"status": "MANUTENCAO"}, timeout=10)
    assert update.status_code == 400, update.text
    assert "Reagende ou cancele" in update.json()["message"]

    close = requests.patch(f"{base_url}/api/ordens-servico/{order_id}/cancelar",
        headers=auth_headers, timeout=10)
    assert close.status_code == 400, close.text
    assert "agendamentos pendentes" in close.json()["erro"]


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
