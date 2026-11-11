from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor
import json
import os
from threading import Barrier

import jwt
import requests
from services.admin_policy import ContextoAdministrativo
from services.assistente_operacoes_service import confirmar_por_id

from services.assistente_ia_service import responder_consulta_operacional
from services.assistente_conversa_service import iniciar_ou_continuar
from config import Config
from database.session import criar_sessao_tenant
from models.tenant.conversa_assistente import ConversaAssistente
from sqlalchemy import select


def test_prioridade_urgente_e_exata_e_exclui_concluidas():
    data = {
        "permissoes": ["OS.VISUALIZAR"],
        "ordens_servico": [
            {"id": 1, "numero": 101, "titulo": "Vazamento", "prioridade": "URGENTE", "status": "ABERTA", "ativo": True},
            {"id": 2, "numero": 102, "titulo": "Revisão", "prioridade": "ALTA", "status": "EM_ANDAMENTO", "ativo": True},
            {"id": 3, "numero": 103, "titulo": "Freios", "prioridade": "URGENTE", "status": "CONCLUIDA", "ativo": True},
        ],
    }
    answer = responder_consulta_operacional("Quais serviços estão com prioridade urgente?", data)
    assert "#101" in answer
    assert "#102" not in answer
    assert "#103" not in answer


def test_parser_reconhece_solicitacao_nova_de_os_com_agenda():
    _, action = iniciar_ou_continuar(
        "Agende uma colheita de silagem para 13/11/2026 às 8h por quatro horas, usando um trator disponível.", {}
    )
    assert action["tipo"] == "selecionar_recurso", action


def test_memoria_conversa_interpreta_continuacao_e_trator(
    base_url, auth_headers, codigo_unico, cleanup_registros_teste,
):
    response = requests.post(
        f"{base_url}/api/maquinas/", headers=auth_headers,
        json={"identificacao": f"CHAT-{codigo_unico}", "modelo": "Trator teste",
              "fabricante": "Fabricante", "categoria": "TRATOR", "status": "OPERANDO"}, timeout=10,
    )
    assert response.status_code == 201, response.text
    cleanup_registros_teste("maquinas", response.json()["data"]["id"])

    first = requests.post(f"{base_url}/api/assistente/mensagem", headers=auth_headers,
        json={"mensagem": "Agenda uma colheita de silo no dia 18 desse mês, vamos usar a máquina disponível."}, timeout=10)
    assert first.status_code == 200, first.text
    conversation_id = first.json()["conversation_id"]
    assert "tipo de recurso" in first.json()["resposta"].lower()

    second = requests.post(f"{base_url}/api/assistente/mensagem", headers=auth_headers,
        json={"conversation_id": conversation_id, "mensagem": "E trator?"}, timeout=10)
    assert second.status_code == 200, second.text
    assert "colheita" in second.json()["historico"][0]["texto"].lower()
    assert "horas" in second.json()["resposta"].lower() or "horário" in second.json()["resposta"].lower()

    loaded = requests.get(f"{base_url}/api/assistente/conversas/{conversation_id}", headers=auth_headers, timeout=10)
    assert loaded.status_code == 200
    assert len(loaded.json()["historico"]) >= 4


def test_disponibilidade_confere_agendamento_no_intervalo(
    base_url, auth_headers, codigo_unico, cleanup_registros_teste,
):
    machine_response = requests.post(f"{base_url}/api/maquinas/", headers=auth_headers,
        json={"identificacao": f"BUSY-{codigo_unico}", "modelo": "Trator teste",
              "fabricante": "Fabricante", "categoria": "TRATOR", "status": "OPERANDO"}, timeout=10)
    assert machine_response.status_code == 201, machine_response.text
    machine_id = machine_response.json()["data"]["id"]
    cleanup_registros_teste("maquinas", machine_id)
    order_response = requests.post(f"{base_url}/api/ordens-servico/", headers=auth_headers,
        json={"tipo": "SERVICO", "titulo": "Uso no intervalo", "maquina_id": machine_id}, timeout=10)
    assert order_response.status_code == 201, order_response.text
    order_id = order_response.json()["ordem_servico"]["id"]
    cleanup_registros_teste("ordens_servico", order_id)
    day = date.today() + timedelta(days=2)
    start = f"{day.isoformat()}T08:00:00"
    appointment = requests.post(f"{base_url}/api/calendario/", headers=auth_headers,
        json={"ordem_servico_id": order_id, "inicio": start, "fim": f"{day.isoformat()}T10:00:00"}, timeout=10)
    assert appointment.status_code == 201, appointment.text
    cleanup_registros_teste("agendamentos", appointment.json()["agendamento"]["id"])

    response = requests.post(f"{base_url}/api/assistente/mensagem", headers=auth_headers,
        json={"mensagem": f"Tem algum trator livre no dia {day:%d/%m/%Y} às 8h por duas horas?"}, timeout=10)
    assert response.status_code == 200, response.text
    assert response.json()["proposta"] is None
    assert "não encontrei trator livre" in response.json()["resposta"].lower()


def test_os_e_agendamento_atomicos_idempotentes_e_visiveis(
    base_url, auth_headers, token, codigo_unico, cleanup_registros_teste,
):
    machine_response = requests.post(f"{base_url}/api/maquinas/", headers=auth_headers,
        json={"identificacao": f"ATOM-{codigo_unico}", "modelo": "Trator teste",
              "fabricante": "Fabricante", "categoria": "TRATOR", "status": "OPERANDO"}, timeout=10)
    assert machine_response.status_code == 201, machine_response.text
    machine_id = machine_response.json()["data"]["id"]
    cleanup_registros_teste("maquinas", machine_id)

    day = date.today() + timedelta(days=2)
    start_text = f"{day:%d/%m/%Y} às 8h por quatro horas"
    first = requests.post(f"{base_url}/api/assistente/mensagem", headers=auth_headers,
        json={"mensagem": f"Agende uma colheita de silagem para {start_text}, usando um trator disponível."}, timeout=10)
    assert first.status_code == 200, first.text
    body = first.json()
    Session, engine = criar_sessao_tenant(Config, os.environ["AGROFROTA_TEST_DATABASE"])
    try:
        with Session() as db:
            stored = db.get(ConversaAssistente, body["conversation_id"])
            stored_state = json.loads(stored.estado_json)
    finally:
        engine.dispose()
    assert stored_state.get("operacao") == "CRIAR_OS_E_AGENDAR", {"state": stored_state, "response": body.get("resposta"), "sources": body.get("fontes")}
    if not body.get("proposta") and body.get("opcoes_recurso"):
        body_response = requests.post(f"{base_url}/api/assistente/mensagem", headers=auth_headers,
            json={"conversation_id": body["conversation_id"], "mensagem": "O primeiro recurso"}, timeout=10)
        assert body_response.status_code == 200, body_response.text
        body = body_response.json()
        repeat_text = "O primeiro recurso"
    else:
        repeat_text = f"Agende uma colheita de silagem para {start_text}, usando um trator disponível."
    assert body["proposta"], body
    assert body["proposta"]["operacao"] == "CRIAR_OS_E_AGENDAR"
    assert body["proposta"]["dados"]["recurso_id"] == machine_id
    assert "colheita" in body["proposta"]["dados"]["descricao"].lower()
    repeated = requests.post(f"{base_url}/api/assistente/mensagem", headers=auth_headers,
        json={"conversation_id": body["conversation_id"], "mensagem": repeat_text}, timeout=10)
    assert repeated.status_code == 200, repeated.text
    assert repeated.json()["proposta"]["id"] == body["proposta"]["id"]

    claims = jwt.decode(token, options={"verify_signature": False})
    context = ContextoAdministrativo(os.environ["AGROFROTA_TEST_DATABASE"],
        int(claims["sub"]), int(claims["session_version"]))
    kwargs = {"tenant_id": int(claims["tenant_id"]),
              "usuario_autenticado_id": int(claims["sub"]),
              "contexto_administrativo": context}
    barrier = Barrier(2)
    def confirm_concurrently(_):
        Session, engine = criar_sessao_tenant(Config, os.environ["AGROFROTA_TEST_DATABASE"])
        try:
            with Session() as db:
                barrier.wait(timeout=10)
                return confirmar_por_id(db, kwargs, body["proposta"]["id"], idempotent=True)
        finally:
            engine.dispose()
    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(confirm_concurrently, range(2)))
    assert all(item["status"] == 200 for item in outcomes), outcomes
    assert outcomes[0]["result"] == outcomes[1]["result"]
    result = outcomes[0]["result"]
    confirmed = requests.post(f"{base_url}/api/assistente/confirmar", headers=auth_headers,
        json={"proposta_id": body["proposta"]["id"], "conversation_id": body["conversation_id"]}, timeout=10)
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json()["resultado"]["os_id"] == result["os_id"]
    assert result["os_id"] and result["agendamento_id"]
    cleanup_registros_teste("ordens_servico", result["os_id"])
    cleanup_registros_teste("agendamentos", result["agendamento_id"])
    cleanup_registros_teste("propostas_agendamento_ia", body["proposta"]["id"])

    again = requests.post(f"{base_url}/api/assistente/confirmar", headers=auth_headers,
        json={"proposta_id": body["proposta"]["id"]}, timeout=10)
    assert again.status_code == 200, again.text
    assert again.json()["resultado"] == result

    listed = requests.get(f"{base_url}/api/ordens-servico/", headers=auth_headers, timeout=10)
    assert any(item["id"] == result["os_id"] for item in listed.json()["ordens_servico"])
    calendar = requests.get(f"{base_url}/api/calendario/", headers=auth_headers, timeout=10)
    assert any(item["id"] == result["agendamento_id"] for item in calendar.json()["agendamentos"])


def test_falha_de_agenda_reverte_os_e_contador(
    base_url, auth_headers, codigo_unico, cleanup_registros_teste,
):
    machine_response = requests.post(f"{base_url}/api/maquinas/", headers=auth_headers,
        json={"identificacao": f"ROLL-{codigo_unico}", "modelo": "Trator teste",
              "fabricante": "Fabricante", "categoria": "TRATOR", "status": "OPERANDO"}, timeout=10)
    assert machine_response.status_code == 201, machine_response.text
    machine_id = machine_response.json()["data"]["id"]
    cleanup_registros_teste("maquinas", machine_id)

    day = date.today() + timedelta(days=3)
    message = f"Agende colheita de silagem dia {day:%d/%m/%Y} às 8h por duas horas usando trator disponível"
    response = requests.post(f"{base_url}/api/assistente/mensagem", headers=auth_headers,
        json={"mensagem": message}, timeout=10)
    assert response.status_code == 200, response.text
    proposal = response.json()["proposta"]
    if not proposal and response.json().get("opcoes_recurso"):
        response = requests.post(f"{base_url}/api/assistente/mensagem", headers=auth_headers,
            json={"conversation_id": response.json()["conversation_id"], "mensagem": "O primeiro recurso"}, timeout=10)
        assert response.status_code == 200, response.text
        proposal = response.json()["proposta"]
    assert proposal, response.json()
    cleanup_registros_teste("propostas_agendamento_ia", proposal["id"])
    # Introduce a legitimate calendar conflict after proposal time-of-check.
    other = requests.post(f"{base_url}/api/ordens-servico/", headers=auth_headers,
        json={"tipo": "SERVICO", "titulo": "Conflito de teste", "maquina_id": machine_id}, timeout=10)
    assert other.status_code == 201, other.text
    other_os = other.json()["ordem_servico"]
    cleanup_registros_teste("ordens_servico", other_os["id"])
    conflict = requests.post(f"{base_url}/api/calendario/", headers=auth_headers,
        json={"ordem_servico_id": other_os["id"], "inicio": proposal["inicio"], "fim": proposal["fim"]}, timeout=10)
    assert conflict.status_code == 201, conflict.text
    cleanup_registros_teste("agendamentos", conflict.json()["agendamento"]["id"])

    failed = requests.post(f"{base_url}/api/assistente/confirmar", headers=auth_headers,
        json={"proposta_id": proposal["id"]}, timeout=10)
    assert failed.status_code == 409, failed.text
    orders = requests.get(f"{base_url}/api/ordens-servico/", headers=auth_headers, timeout=10).json()["ordens_servico"]
    assert not any(item["titulo"] == "Colheita de silagem" and item["maquina_id"] == machine_id for item in orders)
