import hashlib
import os
from datetime import date, datetime, timedelta

import requests
from sqlalchemy import select, update

from config import Config
from database.session import criar_sessao_tenant
from models.tenant.proposta_agendamento import PropostaAgendamento


def _criar_ordem(base_url, auth_headers, codigo_unico, cleanup):
    resposta = requests.post(
        f"{base_url}/api/maquinas/", headers=auth_headers,
        json={"identificacao": f"TEST-AI-{codigo_unico}", "modelo": "Modelo teste",
              "fabricante": "Fabricante teste", "status": "OPERANDO"}, timeout=10,
    )
    assert resposta.status_code == 201
    maquina = resposta.json()["data"]
    cleanup("maquinas", maquina["id"])
    resposta = requests.post(
        f"{base_url}/api/ordens-servico/", headers=auth_headers,
        json={"tipo": "MANUTENCAO", "titulo": "Revisão de teste",
              "maquina_id": maquina["id"], "prioridade": "MEDIA"}, timeout=10,
    )
    assert resposta.status_code == 201, resposta.text
    ordem = resposta.json()["ordem_servico"]
    cleanup("ordens_servico", ordem["id"])
    return ordem


def _pedido(base_url, auth_headers, numero):
    dia = (date.today() + timedelta(days=2)).strftime("%d/%m/%Y")
    resposta = requests.post(
        f"{base_url}/api/assistente/mensagem", headers=auth_headers,
        json={"mensagem": f"Agende a OS {numero} para {dia} às 14h por uma hora."}, timeout=10,
    )
    assert resposta.status_code == 200, resposta.text
    return resposta.json()


def _proposta_id(codigo):
    SessionTenant, engine = criar_sessao_tenant(Config, os.environ["AGROFROTA_TEST_DATABASE"])
    try:
        with SessionTenant() as session:
            return session.execute(select(PropostaAgendamento.id).where(
                PropostaAgendamento.token_hash == hashlib.sha256(codigo.encode()).hexdigest()
            )).scalar_one()
    finally:
        engine.dispose()


def test_agendamento_assistente_persistido_confirmado_e_uso_unico(
    base_url, auth_headers, codigo_unico, cleanup_registros_teste,
):
    ordem = _criar_ordem(base_url, auth_headers, codigo_unico, cleanup_registros_teste)
    proposta = _pedido(base_url, auth_headers, ordem["numero"])["proposta"]
    proposta_id = _proposta_id(proposta["codigo"])
    cleanup_registros_teste("propostas_agendamento_ia", proposta_id)

    confirmado = requests.post(
        f"{base_url}/api/assistente/confirmar", headers=auth_headers,
        json={"codigo": proposta["codigo"]}, timeout=10,
    )
    assert confirmado.status_code == 200, confirmado.text
    agendamento = confirmado.json()["agendamento"]
    cleanup_registros_teste("agendamentos", agendamento["id"])

    repetido = requests.post(
        f"{base_url}/api/assistente/confirmar", headers=auth_headers,
        json={"codigo": proposta["codigo"]}, timeout=10,
    )
    assert repetido.status_code == 200
    assert repetido.json()["agendamento"]["id"] == agendamento["id"]


def test_agendamento_assistente_proposta_expirada_e_rejeitada(
    base_url, auth_headers, codigo_unico, cleanup_registros_teste,
):
    ordem = _criar_ordem(base_url, auth_headers, codigo_unico, cleanup_registros_teste)
    proposta = _pedido(base_url, auth_headers, ordem["numero"])["proposta"]
    proposta_id = _proposta_id(proposta["codigo"])
    cleanup_registros_teste("propostas_agendamento_ia", proposta_id)

    SessionTenant, engine = criar_sessao_tenant(Config, os.environ["AGROFROTA_TEST_DATABASE"])
    try:
        with SessionTenant.begin() as session:
            session.execute(update(PropostaAgendamento).where(
                PropostaAgendamento.id == proposta_id
            ).values(expira_em=datetime.utcnow() - timedelta(seconds=1)))
    finally:
        engine.dispose()

    resposta = requests.post(
        f"{base_url}/api/assistente/confirmar", headers=auth_headers,
        json={"codigo": proposta["codigo"]}, timeout=10,
    )
    assert resposta.status_code == 409


def test_conversa_mantem_contexto_e_altera_horario_da_os_existente(
    base_url, auth_headers, codigo_unico, cleanup_registros_teste,
):
    ordem = _criar_ordem(base_url, auth_headers, codigo_unico, cleanup_registros_teste)
    first = _pedido(base_url, auth_headers, ordem["numero"])
    original = first["proposta"]
    original_id = _proposta_id(original["codigo"])
    cleanup_registros_teste("propostas_agendamento_ia", original_id)

    changed = requests.post(f"{base_url}/api/assistente/mensagem", headers=auth_headers,
        json={"conversation_id": first["conversation_id"], "mensagem": "Troca para as 9h"}, timeout=10)
    assert changed.status_code == 200, changed.text
    replacement = changed.json()["proposta"]
    assert replacement["dados"]["ordem_id"] == ordem["id"]
    assert replacement["inicio"].endswith("T09:00")
    cleanup_registros_teste("propostas_agendamento_ia", replacement["id"])

    old_confirm = requests.post(f"{base_url}/api/assistente/confirmar", headers=auth_headers,
        json={"proposta_id": original_id}, timeout=10)
    assert old_confirm.status_code == 409
    confirmed = requests.post(f"{base_url}/api/assistente/confirmar", headers=auth_headers,
        json={"proposta_id": replacement["id"], "conversation_id": first["conversation_id"]}, timeout=10)
    assert confirmed.status_code == 200, confirmed.text
    cleanup_registros_teste("agendamentos", confirmed.json()["agendamento"]["id"])


def test_agendamento_assistente_nao_propõe_os_com_conflito_existente(
    base_url, auth_headers, codigo_unico, cleanup_registros_teste,
):
    ordem = _criar_ordem(base_url, auth_headers, codigo_unico, cleanup_registros_teste)
    inicio = date.today() + timedelta(days=2)
    resposta = requests.post(
        f"{base_url}/api/calendario/", headers=auth_headers,
        json={"ordem_servico_id": ordem["id"],
              "inicio": f"{inicio.isoformat()}T14:00:00",
              "fim": f"{inicio.isoformat()}T15:00:00"}, timeout=10,
    )
    assert resposta.status_code == 201, resposta.text
    cleanup_registros_teste("agendamentos", resposta.json()["agendamento"]["id"])

    resposta = _pedido(base_url, auth_headers, ordem["numero"])
    assert resposta["proposta"] is None
    assert "Conflito" in resposta["resposta"]
