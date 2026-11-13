"""Invitation acceptance, authorization and concurrency against disposable MariaDB."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import os
import secrets
import uuid

import requests
from sqlalchemy import select

from config import Config
from database.session import criar_sessao_central, criar_sessao_tenant
from models.central.convite import Convite
from models.tenant.usuario import Usuario


def _criar_convite(base_url, headers, profile_id, *, email=None):
    return requests.post(
        f"{base_url}/api/convites/", headers=headers,
        json={"nome": "Pessoa Convidada", "email": email, "perfil_id": profile_id}, timeout=10,
    )


def _perfil(base_url, headers, name):
    response = requests.get(f"{base_url}/api/perfis/", headers=headers, timeout=10)
    assert response.status_code == 200
    return next(profile["id"] for profile in response.json()["data"] if profile["nome"] == name)


def _registrar(base_url, token, username, password=None):
    return requests.post(
        f"{base_url}/api/convites/registrar",
        json={"token": token, "username": username,
              "senha": password or secrets.token_urlsafe(18)}, timeout=15,
    )


def test_convite_cadastra_conta_no_tenant_e_token_nao_reaparece(base_url, auth_headers):
    profile_id = _perfil(base_url, auth_headers, "OPERADOR")
    email = f"invite-{uuid.uuid4().hex[:12]}@example.com"
    created = _criar_convite(base_url, auth_headers, profile_id, email=email)
    assert created.status_code == 201, created.text
    invite = created.json()["data"]
    assert len(invite["token"]) == 43

    listed = requests.get(f"{base_url}/api/convites/", headers=auth_headers, timeout=10)
    assert listed.status_code == 200
    public_entry = next(row for row in listed.json()["data"] if row["id"] == invite["id"])
    assert public_entry["status"] == "pendente"
    assert "token" not in public_entry and invite["token"] not in listed.text

    checked = requests.post(f"{base_url}/api/convites/validar", json={"token": invite["token"]}, timeout=10)
    assert checked.status_code == 200
    assert checked.json()["data"]["email"] == email
    username = f"invite_{uuid.uuid4().hex[:12]}"
    password = secrets.token_urlsafe(18)
    registered = _registrar(base_url, invite["token"], username, password)
    assert registered.status_code == 201
    assert "token" not in registered.text and "database_name" not in registered.text

    repeated = _registrar(base_url, invite["token"], username, password)
    assert repeated.status_code == 400
    database = os.environ["AGROFROTA_TEST_DATABASE"]
    factory, _ = criar_sessao_tenant(Config, database)
    with factory() as session:
        user = session.execute(select(Usuario).where(Usuario.username == username)).scalar_one()
        assert user.convite_id == invite["id"]
        assert user.email == email and user.perfil_id == profile_id
    logged_in = requests.post(f"{base_url}/api/auth/login", json={
        "username": username, "senha": password, "database_name": database,
    }, timeout=10)
    assert logged_in.status_code == 200


def test_convite_revogado_expirado_e_tenant_isolado(base_url, auth_headers):
    profile_id = _perfil(base_url, auth_headers, "OPERADOR")
    created = _criar_convite(base_url, auth_headers, profile_id)
    assert created.status_code == 201
    invite = created.json()["data"]
    revoked = requests.patch(
        f"{base_url}/api/convites/{invite['id']}/revogar", headers=auth_headers, timeout=10,
    )
    assert revoked.status_code == 200
    assert _registrar(base_url, invite["token"], f"revoked_{uuid.uuid4().hex[:8]}").status_code == 400

    expiring = _criar_convite(base_url, auth_headers, profile_id)
    assert expiring.status_code == 201
    expiring_data = expiring.json()["data"]
    central_factory, _ = criar_sessao_central(Config)
    with central_factory() as session:
        row = session.get(Convite, expiring_data["id"])
        row.expira_em = row.criado_em - timedelta(seconds=1)
        session.commit()
    checked = requests.post(f"{base_url}/api/convites/validar", json={"token": expiring_data["token"]}, timeout=10)
    assert checked.status_code == 400

    other_database = os.environ["AGROFROTA_TEST_DATABASE_B"]
    other_login = requests.post(f"{base_url}/api/auth/login", json={
        "username": os.environ["AGROFROTA_TEST_USERNAME_B"],
        "senha": os.environ["AGROFROTA_TEST_PASSWORD_B"],
        "database_name": other_database,
    }, timeout=10)
    assert other_login.status_code == 200
    other_headers = {"Authorization": f"Bearer {other_login.json()['data']['access_token']}"}
    denied = requests.patch(
        f"{base_url}/api/convites/{expiring_data['id']}/revogar", headers=other_headers, timeout=10,
    )
    assert denied.status_code == 404


def test_convite_e_de_uso_unico_sob_requisicoes_concorrentes(base_url, auth_headers):
    profile_id = _perfil(base_url, auth_headers, "OPERADOR")
    created = _criar_convite(base_url, auth_headers, profile_id)
    assert created.status_code == 201
    token = created.json()["data"]["token"]
    names = [f"race_{uuid.uuid4().hex[:12]}" for _ in range(2)]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda username: _registrar(base_url, token, username), names))
    assert sorted(response.status_code for response in results) == [201, 400]

    factory, _ = criar_sessao_tenant(Config, os.environ["AGROFROTA_TEST_DATABASE"])
    with factory() as session:
        users = session.scalars(select(Usuario).where(Usuario.convite_id == created.json()["data"]["id"])).all()
        assert len(users) == 1


def test_perfil_sem_permissao_nao_emite_convite(base_url, auth_headers):
    operator_id = _perfil(base_url, auth_headers, "OPERADOR")
    username = f"no_invite_{uuid.uuid4().hex[:12]}"
    password = secrets.token_urlsafe(18)
    created_user = requests.post(f"{base_url}/api/usuarios/", headers=auth_headers, json={
        "nome": "Operador de teste", "username": username,
        "senha": password, "perfil_id": operator_id,
    }, timeout=10)
    assert created_user.status_code == 201
    logged_in = requests.post(f"{base_url}/api/auth/login", json={
        "username": username, "senha": password,
        "database_name": os.environ["AGROFROTA_TEST_DATABASE"],
    }, timeout=10)
    assert logged_in.status_code == 200
    headers = {"Authorization": f"Bearer {logged_in.json()['data']['access_token']}"}
    denied = _criar_convite(base_url, headers, operator_id)
    assert denied.status_code == 403
