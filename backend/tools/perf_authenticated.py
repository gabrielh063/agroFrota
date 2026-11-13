"""Sanitized functional/performance probe for the private persistent demo."""
import concurrent.futures
import json
import os
from pathlib import Path
import statistics
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE = os.environ.get("AGROFROTA_BASE_URL", "http://127.0.0.1:18088").rstrip("/")
CREDENTIALS = Path(os.environ.get(
    "AGROFROTA_DEMO_CREDENTIALS",
    Path.home() / ".config/agrofrota-infra-01/demo_credentials.json",
))
ACCOUNTS = (
    "admin_demo", "diretoria_demo", "gestor_frota_demo", "administrativo_demo",
    "manutencao_demo", "operador_demo", "auditor_demo",
)
READ_PATHS = (
    "/api/auth/me", "/api/dashboard/capacidade", "/api/maquinas/",
    "/api/ordens-servico/", "/api/calendario/", "/api/assistente/conversas",
    "/api/usuarios/",
)


def call(path, token=None, method="GET", payload=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode() if payload is not None else None
    request = Request(BASE + path, data=data, headers=headers, method=method)
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=25) as response:
            status = response.status
    except HTTPError as error:
        status = error.code
    except (URLError, TimeoutError):
        status = 0
    return status, (time.perf_counter() - started) * 1000


def login(username, password):
    request = Request(BASE + "/api/auth/login", data=json.dumps({
        "username": username, "senha": password, "database_name": "agrofrota_tenant",
    }).encode(), headers={"Content-Type": "application/json"}, method="POST")
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=25) as response:
            body = json.load(response)
            return response.status, (time.perf_counter() - started) * 1000, body["data"]["access_token"]
    except HTTPError as error:
        return error.code, (time.perf_counter() - started) * 1000, None
    except (URLError, TimeoutError):
        return 0, (time.perf_counter() - started) * 1000, None


def summary(samples):
    latencies = sorted(item[1] for item in samples)
    if not latencies:
        return {"requests": 0, "errors": 0}
    p95_index = max(0, int(0.95 * len(latencies) + 0.999999) - 1)
    errors = sum(item[0] >= 500 or item[0] == 0 for item in samples)
    return {
        "requests": len(samples), "errors": errors,
        "error_rate_percent": round(errors * 100 / len(samples), 2),
        "p50_ms": round(statistics.median(latencies), 2),
        "p95_ms": round(latencies[p95_index], 2),
        "max_ms": round(max(latencies), 2),
        "statuses": {str(code): sum(item[0] == code for item in samples) for code in sorted({item[0] for item in samples})},
    }


def main():
    credentials = json.loads(CREDENTIALS.read_text(encoding="utf-8"))
    result = {"base": BASE, "accounts": {}, "sequential": {}, "concurrent_me": {}, "authorization": {}}
    tokens = {}
    for username in ACCOUNTS:
        status, elapsed, token = login(username, credentials[username])
        record = {"login_status": status, "login_ms": round(elapsed, 2)}
        if status == 200:
            tokens[username] = token
            checks = {path: call(path, token) for path in READ_PATHS}
            record["read_statuses"] = {path: status for path, (status, _) in checks.items()}
            for path, sample in checks.items():
                result["sequential"].setdefault(path, []).append(sample)
        result["accounts"][username] = record

    if "admin_demo" in tokens:
        admin = tokens["admin_demo"]
        sequential = [call("/api/auth/me", admin) for _ in range(100)]
        result["sequential"]["/api/auth/me_100"] = sequential
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            result["concurrent_me"]["/api/auth/me"] = list(executor.map(lambda _: call("/api/auth/me", admin), range(100)))

    if "auditor_demo" in tokens:
        result["authorization"]["auditor_machine_create"] = call(
            "/api/maquinas/", tokens["auditor_demo"], method="POST", payload={}
        )[0]

    result["sequential"] = {key: summary(value) for key, value in result["sequential"].items()}
    result["concurrent_me"] = {key: summary(value) for key, value in result["concurrent_me"].items()}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
