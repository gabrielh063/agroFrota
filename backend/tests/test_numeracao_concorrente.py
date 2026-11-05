from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import select
from config import Config
from conftest import DATABASE_NAME, _exigir_ambiente_descartavel
from database.session import criar_sessao_tenant
from models.tenant.maquina import Maquina
from models.tenant.ordem_servico import OrdemServico
from models.tenant.operacao_lock import OperacaoLock
from services.ordem_servico_service import criar_ordem_servico, _proximo_numero_os


def test_os_concorrentes_numeros_distintos_e_rollback():
    _exigir_ambiente_descartavel()
    factory, _ = criar_sessao_tenant(Config, DATABASE_NAME)
    with factory() as session:
        maquina = Maquina(identificacao=uuid4().hex, modelo='Sintético', fabricante='Teste')
        session.add(maquina)
        session.commit()
        maquina_id = maquina.id
    barreira = Barrier(2, timeout=10)

    def criar(_):
        barreira.wait()
        return criar_ordem_servico(Config, DATABASE_NAME, 'SERVICO', 'Concorrência',
                                  maquina_id=maquina_id)

    with ThreadPoolExecutor(max_workers=2) as pool:
        ordens = list(pool.map(criar, range(2)))
    numeros = sorted(o.numero for o in ordens)
    assert numeros[1] == numeros[0] + 1
    with factory() as session:
        persistidas = session.scalars(select(OrdemServico).where(
            OrdemServico.id.in_([o.id for o in ordens]))).all()
        assert sorted(o.numero for o in persistidas) == numeros
        session.rollback()
        reservado = _proximo_numero_os(session)
        session.rollback()
    with factory() as session:
        assert session.get(OperacaoLock, 1).proximo_numero_os == reservado
        session.rollback()
        assert _proximo_numero_os(session) == reservado
        session.rollback()
