"""Tenant-bound account invitations with one-time, hashed tokens."""
from datetime import UTC, datetime, timedelta
import hashlib
import secrets
import uuid

from flask import Blueprint, jsonify, request
from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator
from sqlalchemy import select

from config import Config
from database.session import criar_sessao_central, criar_sessao_tenant
from middleware.auth import autenticar
from middleware.permissions import exigir_permissao
from middleware.tenant import resolver_tenant
from models.central.convite import Convite
from models.central.tenant import Tenant
from models.tenant.auditoria import EventoAuditoria
from models.tenant.cargo import Cargo
from models.tenant.perfil import Perfil
from models.tenant.usuario import Usuario
from services.admin_policy import AdministracaoNegada, ContextoAdministrativo, autorizar, perfil_delegavel
from services.rate_limit_service import consumir_limite
from utils.security import gerar_hash_senha, verificar_senha


convites_bp = Blueprint("convites", __name__, url_prefix="/api/convites")
_TOKEN_PATTERN_LENGTH = 43
_INVITE_LIFETIME = timedelta(hours=72)


class ConviteCriarSchema(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    email: EmailStr | None = Field(default=None, max_length=150)
    cargo_id: int | None = Field(default=None, gt=0)
    perfil_id: int = Field(gt=0)

    @field_validator("nome")
    @classmethod
    def limpar_nome(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Nome obrigatório.")
        return value


class ConviteRegistrarSchema(BaseModel):
    token: str = Field(min_length=_TOKEN_PATTERN_LENGTH, max_length=64)
    username: str = Field(min_length=1, max_length=80)
    senha: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def limpar_username(cls, value):
        value = value.strip()
        if not value or any(ch.isspace() for ch in value):
            raise ValueError("Username inválido.")
        return value


def _agora():
    return datetime.now(UTC).replace(tzinfo=None)


def _hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _convite_ativo(convite, agora):
    return (convite is not None and convite.revogado_em is None
            and convite.consumido_em is None and convite.expira_em > agora)


def _erro_convidado():
    return jsonify({"success": False, "message": "Convite inválido, expirado, revogado ou já utilizado."}), 400


def _limite(bucket, limite, janela):
    try:
        allowed, retry_after = consumir_limite(bucket, limite=limite, janela_segundos=janela)
    except Exception:
        return jsonify({"success": False, "message": "Serviço temporariamente indisponível."}), 503
    if not allowed:
        return jsonify({"success": False, "message": "Muitas tentativas. Aguarde e tente novamente."}), 429, {
            "Retry-After": str(retry_after),
        }
    return None


def _peer():
    # request.remote_addr is the direct peer; X-Forwarded-For is deliberately ignored.
    return request.remote_addr or "unknown"


@convites_bp.get("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("USUARIO_CRIAR")
def listar(**kwargs):
    session_factory, _engine = criar_sessao_central(Config)
    tenant_factory, _tenant_engine = criar_sessao_tenant(Config, kwargs["database_name"])
    with tenant_factory() as tenant_session, session_factory() as session:
        try:
            autorizar(tenant_session, kwargs["database_name"],
                      kwargs["contexto_administrativo"], "USUARIO_CRIAR")
        except AdministracaoNegada:
            return jsonify({"success": False, "message": "Ação não autorizada."}), 403
        rows = session.scalars(select(Convite).where(
            Convite.tenant_id == kwargs["tenant_id"]
        ).order_by(Convite.criado_em.desc()).limit(100)).all()
        now = _agora()
        return jsonify({"success": True, "data": [{
            "id": row.id,
            "nome": row.nome,
            "email": row.email,
            "perfil_id": row.perfil_id,
            "criado_em": row.criado_em.isoformat(),
            "expira_em": row.expira_em.isoformat(),
            "status": ("revogado" if row.revogado_em else
                       "utilizado" if row.consumido_em else
                       "expirado" if row.expira_em <= now else "pendente"),
        } for row in rows]})


@convites_bp.post("/")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("USUARIO_CRIAR")
def criar(**kwargs):
    limited = _limite(
        f"invite-create:{kwargs['database_name']}:{kwargs['usuario_autenticado_id']}", 30, 3600,
    )
    if limited:
        return limited
    try:
        body = ConviteCriarSchema.model_validate(request.get_json(silent=True) or {})
    except ValidationError as error:
        return jsonify({"success": False, "message": "Dados inválidos.",
                        "errors": error.errors(include_input=False, include_url=False)}), 400

    tenant_factory, _tenant_engine = criar_sessao_tenant(Config, kwargs["database_name"])
    central_factory, _central_engine = criar_sessao_central(Config)
    try:
        with tenant_factory() as tenant_session, central_factory() as central_session:
            try:
                _, permissions = autorizar(tenant_session, kwargs["database_name"],
                                           kwargs["contexto_administrativo"], "USUARIO_CRIAR")
                perfil_delegavel(tenant_session, body.perfil_id, permissions)
                if body.cargo_id is not None:
                    cargo = tenant_session.get(Cargo, body.cargo_id)
                    if cargo is None or not cargo.ativo:
                        return jsonify({"success": False, "message": "Cargo inexistente ou inativo."}), 400

                tenant = central_session.execute(select(Tenant).where(
                    Tenant.id == kwargs["tenant_id"],
                    Tenant.database_name == kwargs["database_name"],
                    Tenant.ativo.is_(True),
                )).scalar_one_or_none()
                if tenant is None:
                    tenant_session.rollback()
                    return jsonify({"success": False, "message": "Tenant indisponível."}), 404

                token = secrets.token_urlsafe(32)
                now = _agora()
                invite = Convite(
                    id=str(uuid.uuid4()), tenant_id=tenant.id, token_hash=_hash_token(token),
                    nome=body.nome, email=str(body.email) if body.email else None,
                    cargo_id=body.cargo_id, perfil_id=body.perfil_id,
                    criado_por=kwargs["usuario_autenticado_id"], criado_em=now,
                    expira_em=now + _INVITE_LIFETIME,
                )
                central_session.add(invite)
                tenant_session.commit()
                central_session.commit()
                return jsonify({"success": True, "data": {
                    "id": invite.id, "token": token,
                    "expira_em": invite.expira_em.isoformat(),
                }}), 201
            except AdministracaoNegada:
                tenant_session.rollback()
                central_session.rollback()
                return jsonify({"success": False, "message": "Ação não autorizada."}), 403
            except Exception:
                tenant_session.rollback()
                central_session.rollback()
                raise
    finally:
        pass


@convites_bp.patch("/<string:convite_id>/revogar")
@autenticar()
@resolver_tenant(Config)
@exigir_permissao("USUARIO_CRIAR")
def revogar(convite_id, **kwargs):
    try:
        uuid.UUID(convite_id)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Convite não encontrado."}), 404

    tenant_factory, _tenant_engine = criar_sessao_tenant(Config, kwargs["database_name"])
    central_factory, _central_engine = criar_sessao_central(Config)
    with tenant_factory() as tenant_session, central_factory() as session:
        # Lock the central invitation before taking the tenant AdminLock. The
        # registration route uses the same central -> tenant lock order; keeping
        # it consistent prevents a register/revoke deadlock on MariaDB.
        invite = session.execute(select(Convite).where(
            Convite.id == convite_id,
            Convite.tenant_id == kwargs["tenant_id"],
        ).with_for_update()).scalar_one_or_none()
        if invite is None:
            return jsonify({"success": False, "message": "Convite não encontrado."}), 404
        try:
            autorizar(tenant_session, kwargs["database_name"],
                      kwargs["contexto_administrativo"], "USUARIO_CRIAR")
        except AdministracaoNegada:
            return jsonify({"success": False, "message": "Ação não autorizada."}), 403
        if invite.consumido_em is not None:
            return jsonify({"success": False, "message": "Convite já utilizado."}), 409
        if invite.revogado_em is None:
            invite.revogado_em = _agora()
            invite.revogado_por = kwargs["usuario_autenticado_id"]
            session.commit()
            tenant_session.commit()
        return jsonify({"success": True, "message": "Convite revogado."})


@convites_bp.post("/validar")
def validar():
    limited = _limite(f"invite-validate-peer:{_peer()}", 120, 60)
    if limited:
        return limited
    body = request.get_json(silent=True)
    token = body.get("token", "") if isinstance(body, dict) else ""
    if (not isinstance(token, str) or len(token) != _TOKEN_PATTERN_LENGTH
            or not all(ch.isalnum() or ch in "_-" for ch in token)):
        return _erro_convidado()
    central_factory, _engine = criar_sessao_central(Config)
    with central_factory() as session:
        invite = session.execute(select(Convite).where(
            Convite.token_hash == _hash_token(token)
        )).scalar_one_or_none()
        if not _convite_ativo(invite, _agora()):
            return _erro_convidado()
        return jsonify({"success": True, "data": {
            "nome": invite.nome, "email": invite.email,
            "expira_em": invite.expira_em.isoformat(),
        }})


@convites_bp.post("/registrar")
def registrar():
    limited = _limite(f"invite-register-peer:{_peer()}", 20, 900)
    if limited:
        return limited
    request_body = request.get_json(silent=True)
    if not isinstance(request_body, dict):
        request_body = {}
    submitted_token = request_body.get("token")
    if isinstance(submitted_token, str):
        limited = _limite(f"invite-register-token:{submitted_token}", 5, 900)
        if limited:
            return limited
    try:
        body = ConviteRegistrarSchema.model_validate(request_body)
    except ValidationError as error:
        return jsonify({"success": False, "message": "Dados inválidos.",
                        "errors": error.errors(include_input=False, include_url=False)}), 400
    if len(body.token) != _TOKEN_PATTERN_LENGTH or not all(
        ch.isalnum() or ch in "_-" for ch in body.token
    ):
        return _erro_convidado()

    central_factory, _central_engine = criar_sessao_central(Config)
    try:
        with central_factory() as central_session:
            invite = central_session.execute(select(Convite).where(
                Convite.token_hash == _hash_token(body.token)
            ).with_for_update()).scalar_one_or_none()
            now = _agora()
            if not _convite_ativo(invite, now):
                return _erro_convidado()
            tenant = central_session.execute(select(Tenant).where(
                Tenant.id == invite.tenant_id, Tenant.ativo.is_(True)
            )).scalar_one_or_none()
            if tenant is None:
                return _erro_convidado()

            tenant_factory, _tenant_engine = criar_sessao_tenant(Config, tenant.database_name)
            with tenant_factory() as tenant_session:
                try:
                    existing = tenant_session.execute(select(Usuario).where(
                        Usuario.convite_id == invite.id
                    ).with_for_update()).scalar_one_or_none()
                    if existing is not None:
                        if existing.username != body.username or not verificar_senha(body.senha, existing.senha_hash):
                            tenant_session.rollback()
                            return _erro_convidado()
                        tenant_session.rollback()
                    else:
                        issuer = tenant_session.get(Usuario, invite.criado_por)
                        if issuer is None:
                            return _erro_convidado()
                        # Recheck current authority at acceptance. Build context with
                        # the current version so a normal logout does not cancel an invite.
                        issuer_context = ContextoAdministrativo(
                            tenant.database_name, issuer.id, issuer.session_version,
                        )
                        try:
                            _, issuer_permissions = autorizar(
                                tenant_session, tenant.database_name, issuer_context, "USUARIO_CRIAR",
                            )
                            perfil_delegavel(
                                tenant_session, invite.perfil_id, issuer_permissions,
                            )
                        except AdministracaoNegada:
                            tenant_session.rollback()
                            return _erro_convidado()
                        if tenant_session.execute(select(Usuario.id).where(
                            Usuario.username == body.username
                        )).scalar_one_or_none() is not None:
                            return jsonify({"success": False, "message": "Username indisponível."}), 409
                        if invite.email and tenant_session.execute(select(Usuario.id).where(
                            Usuario.email == invite.email
                        )).scalar_one_or_none() is not None:
                            return jsonify({"success": False, "message": "E-mail já associado a uma conta."}), 409
                        profile = tenant_session.get(Perfil, invite.perfil_id)
                        cargo = tenant_session.get(Cargo, invite.cargo_id) if invite.cargo_id else None
                        if profile is None or not profile.ativo or (invite.cargo_id and (cargo is None or not cargo.ativo)):
                            return jsonify({"success": False, "message": "O perfil ou cargo do convite não está mais ativo."}), 409
                        user = Usuario(
                            nome=invite.nome, username=body.username,
                            email=invite.email, senha_hash=gerar_hash_senha(body.senha),
                            cargo_id=invite.cargo_id, perfil_id=invite.perfil_id,
                            ativo=True, convite_id=invite.id,
                        )
                        tenant_session.add(user)
                        tenant_session.add(EventoAuditoria(
                            ator_id=invite.criado_por, operacao="aceitar_convite",
                        ))
                        tenant_session.commit()
                except Exception:
                    tenant_session.rollback()
                    raise
            invite.consumido_em = _agora()
            central_session.commit()
            return jsonify({"success": True, "message": "Conta criada. Você já pode entrar."}), 201
    except Exception:
        return jsonify({"success": False, "message": "Não foi possível concluir o cadastro. Tente novamente."}), 503
