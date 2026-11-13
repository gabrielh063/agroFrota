from datetime import datetime

from flask import Blueprint, jsonify, request

from config import Config
from middleware.auth import autenticar
from middleware.permissions import exigir_permissao
from middleware.tenant import resolver_tenant

from services.dashboard_service import (
    obter_dashboard_indisponibilidade,
    obter_capacidade_patio,
    obter_atividade_servicos,
)


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard"
)


def _parse_datetime(valor: str | None):
    if not valor:
        return None

    try:
        return datetime.fromisoformat(valor)
    except ValueError:
        raise ValueError(
            "Data inválida. Use o formato "
            "YYYY-MM-DDTHH:MM:SS."
        )


@dashboard_bp.get("/indisponibilidade")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.VISUALIZAR")
def dashboard_indisponibilidade(**kwargs):
    tenant_session = kwargs["tenant_session"]

    try:
        inicio_periodo = _parse_datetime(
            request.args.get("inicio")
        )

        fim_periodo = _parse_datetime(
            request.args.get("fim")
        )

        if (
            inicio_periodo is not None
            and fim_periodo is not None
            and fim_periodo <= inicio_periodo
        ):
            return jsonify({
                "success": False,
                "message": (
                    "O fim do período deve ser "
                    "posterior ao início."
                )
            }), 400

        dashboard = obter_dashboard_indisponibilidade(
            session=tenant_session,
            inicio_periodo=inicio_periodo,
            fim_periodo=fim_periodo,
        )

        return jsonify({
            "success": True,
            "dashboard": dashboard,
        })

    except ValueError as erro:
        return jsonify({
            "success": False,
            "message": str(erro),
        }), 400

    except Exception:
        return jsonify({
            "success": False,
            "message": (
                "Erro interno ao carregar "
                "dashboard de indisponibilidade."
            ),
        }), 500
        
@dashboard_bp.get("/capacidade")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.VISUALIZAR")
def dashboard_capacidade(**kwargs):
    tenant_session = kwargs["tenant_session"]

    try:
        capacidade = obter_capacidade_patio(
            session=tenant_session
        )

        return jsonify({
            "success": True,
            "capacidade": capacidade,
        })

    except Exception:
        return jsonify({
            "success": False,
            "message": (
                "Erro interno ao carregar "
                "capacidade do pátio."
            ),
        }), 500


@dashboard_bp.get("/atividade")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("OS.VISUALIZAR")
def dashboard_atividade(**kwargs):
    try:
        meses = max(1, min(int(request.args.get("meses", 12)), 12))
        atividade = obter_atividade_servicos(
            kwargs["tenant_session"], kwargs["contexto_administrativo"], meses
        )
        return jsonify({"success": True, "atividade": atividade})
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Período inválido."}), 400
    except Exception:
        return jsonify({"success": False, "message": "Erro ao carregar atividade de serviços."}), 500
