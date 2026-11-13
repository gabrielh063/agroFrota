from functools import wraps
import json
import logging
from time import perf_counter

from flask import jsonify
from flask_jwt_extended import get_jwt
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, DisconnectionError, InterfaceError, OperationalError, TimeoutError as PoolTimeout

from database.session import (
    criar_sessao_central,
    criar_sessao_tenant,
)
from models.central.tenant import Tenant
from models.tenant.usuario import Usuario
from models.tenant.perfil import Perfil
from services.admin_policy import ContextoAdministrativo


_logger = logging.getLogger(__name__)


def _erro_tecnico(erro):
    """Return a safe, stable error category without exception details."""
    if isinstance(erro, PoolTimeout):
        return "database_pool_timeout"
    if isinstance(erro, (DisconnectionError, InterfaceError, OperationalError)):
        return "database_unavailable"
    if isinstance(erro, DBAPIError):
        return "database_connection_error" if erro.connection_invalidated else "database_query_error"
    return "tenant_resolution_error"


def _registrar_metricas(etapa, metricas, erro=None):
    evento = {
        "event": "tenant_resolution",
        "stage": etapa,
        "timings_ms": {nome: round(valor, 2) for nome, valor in metricas.items()},
        "total_ms": round(metricas.get("request_total", sum(metricas.values())), 2),
    }
    if erro is not None:
        evento["error_category"] = _erro_tecnico(erro)
        evento["error_type"] = type(erro).__name__
        _logger.warning(json.dumps(evento, separators=(",", ":")))
    else:
        _logger.info(json.dumps(evento, separators=(",", ":")))


def resolver_tenant(config):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            inicio_requisicao = perf_counter()
            tenant_session = None
            metricas = {}
            etapa = "claims"
            inicio = inicio_requisicao

            tenant_id = kwargs.get(
                "tenant_id"
            )

            usuario_id = kwargs.get(
                "usuario_autenticado_id"
            )

            # ------------------------------------------
            # DADOS OBRIGATÓRIOS VINDOS DO JWT
            # ------------------------------------------

            if tenant_id is None:
                return jsonify({
                    "success": False,
                    "message": "Tenant não identificado.",
                }), 401

            if usuario_id is None:
                return jsonify({
                    "success": False,
                    "message": "Usuário não identificado.",
                }), 401

            try:

                # --------------------------------------
                # BUSCA O TENANT NO BANCO CENTRAL
                # --------------------------------------

                etapa = "central_connect"
                inicio = perf_counter()
                SessionCentral, _ = (
                    criar_sessao_central(
                        config
                    )
                )

                central_session = (
                    SessionCentral()
                )

                try:
                    central_session.connection()
                    metricas["central_connect"] = (perf_counter() - inicio) * 1000
                    etapa = "tenant_lookup"
                    inicio = perf_counter()
                    tenant = (
                        central_session.execute(
                            select(Tenant).where(
                                Tenant.id
                                == tenant_id
                            )
                        )
                        .scalar_one_or_none()
                    )
                    metricas["tenant_lookup"] = (perf_counter() - inicio) * 1000

                finally:
                    central_session.close()

                # --------------------------------------
                # VALIDA TENANT
                # --------------------------------------

                if tenant is None:
                    return jsonify({
                        "success": False,
                        "message":
                            "Tenant não encontrado.",
                    }), 404

                if not tenant.ativo:
                    return jsonify({
                        "success": False,
                        "message":
                            "Tenant está inativo.",
                    }), 403

                # --------------------------------------
                # ABRE O BANCO DO TENANT
                # --------------------------------------

                etapa = "tenant_connect"
                inicio = perf_counter()
                SessionTenant, _ = (
                    criar_sessao_tenant(
                        config,
                        tenant.database_name,
                    )
                )

                tenant_session = (
                    SessionTenant()
                )
                tenant_session.connection()
                metricas["tenant_connect"] = (perf_counter() - inicio) * 1000

                # --------------------------------------
                # VALIDA O USUÁRIO ATUAL
                # --------------------------------------
                #
                # Não confia apenas no JWT.
                #
                # O usuário precisa:
                # - continuar existindo
                # - continuar ativo
                #
                # --------------------------------------

                etapa = "user_lookup"
                inicio = perf_counter()
                usuario = (
                    tenant_session.execute(
                        select(Usuario).where(
                            Usuario.id
                            == usuario_id
                        )
                    )
                    .scalar_one_or_none()
                )
                metricas["user_lookup"] = (perf_counter() - inicio) * 1000

                if usuario is None:

                    tenant_session.close()
                    tenant_session = None

                    return jsonify({
                        "success": False,
                        "message":
                            "Usuário não encontrado.",
                    }), 401

                if not usuario.ativo:

                    tenant_session.close()
                    tenant_session = None

                    return jsonify({
                        "success": False,
                        "message":
                            "Usuário está inativo.",
                    }), 401

                versao = get_jwt().get("session_version")
                if type(versao) is not int or versao != usuario.session_version:
                    tenant_session.close()
                    tenant_session = None
                    return jsonify({"success": False, "message": "Sessão revogada."}), 401

                # --------------------------------------
                # PERFIL ATUAL DO USUÁRIO
                # --------------------------------------
                #
                # Ignora o perfil antigo presente
                # no JWT.
                #
                # Se o usuário era GERENTE quando
                # recebeu o token e depois virou
                # OPERADOR, usamos OPERADOR.
                #
                # --------------------------------------

                perfil_id_atual = (
                    usuario.perfil_id
                )

                if perfil_id_atual is None:

                    tenant_session.close()
                    tenant_session = None

                    return jsonify({
                        "success": False,
                        "message":
                            "Perfil do usuário "
                            "não identificado.",
                    }), 403

                etapa = "profile_lookup"
                inicio = perf_counter()
                perfil_ativo = tenant_session.execute(
                    select(Perfil.id).where(
                        Perfil.id == perfil_id_atual,
                        Perfil.ativo.is_(True),
                    )
                ).scalar_one_or_none()
                metricas["profile_lookup"] = (perf_counter() - inicio) * 1000
                if perfil_ativo is None:
                    tenant_session.close()
                    tenant_session = None
                    return jsonify({"success": False, "message": "Perfil não encontrado ou inativo."}), 403

            except Exception as erro:

                if tenant_session is not None:
                    try:
                        tenant_session.rollback()
                    except Exception:
                        pass
                    finally:
                        try:
                            tenant_session.close()
                        except Exception:
                            _logger.warning('{"event":"tenant_session_close","error_category":"session_close_error"}')
                        tenant_session = None

                metricas.setdefault(etapa, (perf_counter() - inicio) * 1000)
                metricas["request_total"] = (perf_counter() - inicio_requisicao) * 1000

                _registrar_metricas(etapa, metricas, erro)

                # Keep the response generic; never expose connection details.

                indisponivel = _erro_tecnico(erro) in {"database_pool_timeout", "database_unavailable"}
                return jsonify({
                    "success": False,
                    "message":
                        "O serviço está temporariamente indisponível. Tente novamente."
                        if indisponivel else "Não foi possível resolver o tenant.",
                }), 503 if indisponivel else 500

            # ------------------------------------------
            # CONTEXTO DA REQUISIÇÃO
            # ------------------------------------------

            kwargs["contexto_administrativo"] = ContextoAdministrativo(
                tenant.database_name, usuario_id, versao
            )
            kwargs["tenant"] = tenant

            kwargs["database_name"] = (
                tenant.database_name
            )

            kwargs["tenant_session"] = (
                tenant_session
            )

            # IMPORTANTE:
            #
            # sobrescreve o perfil que veio do JWT
            # pelo perfil ATUAL salvo no banco.
            kwargs["usuario_perfil_id"] = (
                perfil_id_atual
            )

            # ------------------------------------------
            # EXECUTA A ROTA
            # ------------------------------------------

            try:
                return func(
                    *args,
                    **kwargs,
                )

            except Exception:

                tenant_session.rollback()

                raise

            finally:
                metricas["request_total"] = (perf_counter() - inicio_requisicao) * 1000
                _registrar_metricas("resolved", metricas)
                try:
                    tenant_session.close()
                except Exception:
                    _logger.warning('{"event":"tenant_session_close","error_category":"session_close_error"}')

        return wrapper

    return decorator
