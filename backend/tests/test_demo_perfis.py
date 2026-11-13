"""Integração HTTP para demonstrar os sete perfis padrão em DB descartável."""

import secrets
import os
import uuid

import pytest
import requests

from services.matriz_acesso import MATRIZ


@pytest.fixture(scope="module")
def contas_por_perfil(base_url, auth_headers):
    profiles_response = requests.get(f"{base_url}/api/perfis/", headers=auth_headers, timeout=10)
    assert profiles_response.status_code == 200
    profile_ids = {item["nome"]: item["id"] for item in profiles_response.json()["data"]}

    manager_me = requests.get(f"{base_url}/api/auth/me", headers=auth_headers, timeout=10)
    assert manager_me.status_code == 200
    users = {"ADMIN_EMPRESA": {"id": manager_me.json()["data"]["usuario"]["id"],
                                "profile_id": profile_ids["ADMIN_EMPRESA"], "headers": auth_headers}}

    suffix = uuid.uuid4().hex[:12]
    for role in MATRIZ:
        if role == "ADMIN_EMPRESA":
            continue
        password = secrets.token_urlsafe(18)
        username = f"demo_{role.lower()}_{suffix}"
        created = requests.post(
            f"{base_url}/api/usuarios/",
            headers=auth_headers,
            json={"nome": f"Demo {role}", "username": username, "senha": password,
                  "perfil_id": profile_ids[role]},
            timeout=10,
        )
        assert created.status_code == 201
        logged_in = requests.post(
            f"{base_url}/api/auth/login",
            json={"username": username, "senha": password,
                  "database_name": os.environ["AGROFROTA_TEST_DATABASE"]},
            timeout=10,
        )
        assert logged_in.status_code == 200
        data = logged_in.json()["data"]
        users[role] = {"id": data["usuario"]["id"], "profile_id": profile_ids[role],
                       "username": username, "password": password,
                       "headers": {"Authorization": f"Bearer {data['access_token']}",
                                   "Content-Type": "application/json"}}

    assert set(users) == set(MATRIZ)
    return users


def test_sete_perfis_autorizacoes_efetivas_e_escopo(base_url, auth_headers, contas_por_perfil):
    users = contas_por_perfil
    for role, user in users.items():
        me = requests.get(f"{base_url}/api/auth/me", headers=user["headers"], timeout=10)
        assert me.status_code == 200
        assert set(me.json()["data"]["permissoes"]) == set(MATRIZ[role])
        assert requests.get(f"{base_url}/api/maquinas/", headers=user["headers"], timeout=10).status_code == 200

        users_response = requests.get(f"{base_url}/api/usuarios/", headers=user["headers"], timeout=10)
        assert users_response.status_code == (200 if "USUARIO_VISUALIZAR" in MATRIZ[role] else 403)

        audit_response = requests.get(f"{base_url}/api/auditoria/", headers=user["headers"], timeout=10)
        assert audit_response.status_code == (200 if "AUDITORIA.VISUALIZAR" in MATRIZ[role] else 403)

        profiles_response = requests.get(f"{base_url}/api/perfis/", headers=user["headers"], timeout=10)
        assert profiles_response.status_code == (200 if "PERFIL_VISUALIZAR" in MATRIZ[role] else 403)

        body = {"nome": "Usuário de negação", "username": f"deny_{role.lower()}_{uuid.uuid4().hex[:8]}",
                "senha": secrets.token_urlsafe(16),
                "perfil_id": users["ADMIN_EMPRESA"]["profile_id"]}
        create_user = requests.post(f"{base_url}/api/usuarios/", headers=user["headers"], json=body, timeout=10)
        assert create_user.status_code == (201 if role == "ADMIN_EMPRESA" else 403)

    audit = requests.get(f"{base_url}/api/auditoria/", headers=users["ADMIN_EMPRESA"]["headers"], timeout=10)
    assert audit.status_code == 200
    assert any(event["ator_id"] == users["ADMIN_EMPRESA"]["id"]
               and event["operacao"] == "criar_usuario"
               for event in audit.json()["data"])

    manager_headers = users["ADMIN_EMPRESA"]["headers"]
    suffix = uuid.uuid4().hex[:10].upper()
    machine_response = requests.post(
        f"{base_url}/api/maquinas/", headers=manager_headers,
        json={"identificacao": f"DEMO-RBAC-{suffix}", "modelo": "Modelo demonstrativo",
              "fabricante": "Fabricante fictício", "ano": 2025, "status": "OPERANDO",
              "controla_telemetria": False}, timeout=10,
    )
    assert machine_response.status_code == 201
    machine_id = machine_response.json()["data"]["id"]

    for role, user in users.items():
        update_response = requests.put(
            f"{base_url}/api/maquinas/{machine_id}", headers=user["headers"],
            json={"localizacao": f"Demo {role}"}, timeout=10,
        )
        assert update_response.status_code == (200 if "MAQUINA_EDITAR" in MATRIZ[role] else 403)

    def create_assigned_os(title, **assignment):
        response = requests.post(
            f"{base_url}/api/ordens-servico/", headers=manager_headers,
            json={"tipo": "SERVICO", "titulo": title, "maquina_id": machine_id, **assignment},
            timeout=10,
        )
        assert response.status_code == 201
        return response.json()["ordem_servico"]["id"]

    operator_os = create_assigned_os("OS fictícia vinculada ao Operador",
                                     operador_id=users["OPERADOR"]["id"])
    maintenance_os = create_assigned_os("OS fictícia atribuída à Manutenção",
                                         responsavel_id=users["MANUTENCAO"]["id"])

    for role, user in users.items():
        response = requests.get(f"{base_url}/api/ordens-servico/", headers=user["headers"], timeout=10)
        assert response.status_code == 200
        ids = {item["id"] for item in response.json()["ordens_servico"]}
        if role == "OPERADOR":
            assert operator_os in ids and maintenance_os not in ids
        elif role == "MANUTENCAO":
            assert maintenance_os in ids and operator_os not in ids
        else:
            assert {operator_os, maintenance_os} <= ids

    for role, user in users.items():
        payload = {"tipo": "SERVICO", "titulo": f"OS negada {role} {suffix}", "maquina_id": machine_id}
        if role == "OPERADOR":
            payload["operador_id"] = user["id"]
        response = requests.post(f"{base_url}/api/ordens-servico/", headers=user["headers"],
                                 json=payload, timeout=10)
        if role in {"ADMIN_EMPRESA", "GESTOR_FROTA", "OPERADOR"}:
            assert response.status_code == 201
        else:
            assert response.status_code == 403

    # The administration UI is backed by the same permission checks: only the
    # effective administrator may edit user records. Changing a profile also
    # revokes the target's existing session before its next request.
    operator = users["OPERADOR"]
    for role, user in users.items():
        response = requests.put(
            f"{base_url}/api/usuarios/{operator['id']}", headers=user["headers"],
            json={"nome": f"Operador atualizado por {role}"}, timeout=10,
        )
        assert response.status_code == (200 if role == "ADMIN_EMPRESA" else 403)

    stale_session = operator["headers"]
    change_profile = requests.put(
        f"{base_url}/api/usuarios/{operator['id']}", headers=manager_headers,
        json={"perfil_id": users["DIRETORIA"]["profile_id"]}, timeout=10,
    )
    assert change_profile.status_code == 200
    assert requests.get(f"{base_url}/api/auth/me", headers=stale_session, timeout=10).status_code == 401

    fresh_login = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": operator["username"], "senha": operator["password"],
              "database_name": os.environ["AGROFROTA_TEST_DATABASE"]},
        timeout=10,
    )
    assert fresh_login.status_code == 200
    fresh_token = fresh_login.json()["data"]["access_token"]
    fresh_headers = {"Authorization": f"Bearer {fresh_token}", "Content-Type": "application/json"}
    fresh_me = requests.get(f"{base_url}/api/auth/me", headers=fresh_headers, timeout=10)
    assert fresh_me.status_code == 200
    assert fresh_me.json()["data"]["usuario"]["perfil_nome"] == "DIRETORIA"
    assert set(fresh_me.json()["data"]["permissoes"]) == set(MATRIZ["DIRETORIA"])
