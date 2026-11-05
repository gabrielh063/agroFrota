import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from sqlalchemy import select

from config import Config, validar_configuracao

from database.central import criar_engine_central
from database.base import CentralBase

from models.central.tenant import Tenant
from models.tenant.usuario import Usuario

from services.tenant_service import criar_tenant
from services.admin_policy import AdministracaoNegada

from routes.maquinas import maquinas_bp
from routes.equipamentos import equipamentos_bp
from routes.cargos import cargos_bp
from routes.permissoes import permissoes_bp
from routes.perfis import perfis_bp
from routes.perfil_permissoes import perfil_permissoes_bp
from routes.auth import auth_bp
from routes.usuarios import usuarios_bp
from routes.ordens_servico import ordens_servico_bp
from routes.calendario import calendario_bp
from routes.manutencoes import manutencoes_bp
from routes.indisponibilidades import indisponibilidades_bp
from routes.dashboard import dashboard_bp
from routes.auditoria import auditoria_bp

from middleware.auth import autenticar
from middleware.tenant import resolver_tenant
from middleware.permissions import exigir_permissao

def create_app():

    app = Flask(__name__)

    @app.errorhandler(AdministracaoNegada)
    def administracao_negada(_erro):
        return jsonify({"success": False, "message": str(_erro)}), 403
    app.config.from_object(Config)
    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

    ambiente = os.getenv("AGROFROTA_ENV", "development").lower()
    dev_routes = os.getenv("AGROFROTA_ENABLE_DEV_ROUTES") == "1"
    validar_configuracao(Config, ambiente, debug=os.getenv("FLASK_DEBUG", "0") != "0", dev_routes=dev_routes)


    jwt = JWTManager(app)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["CORS_ORIGINS"]
            }
        }
    )

    app.register_blueprint(maquinas_bp)
    app.register_blueprint(equipamentos_bp)
    app.register_blueprint(cargos_bp)
    app.register_blueprint(permissoes_bp)
    app.register_blueprint(perfis_bp)
    app.register_blueprint(perfil_permissoes_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(ordens_servico_bp)
    app.register_blueprint(calendario_bp)
    app.register_blueprint(manutencoes_bp)
    app.register_blueprint(indisponibilidades_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auditoria_bp)

    # --------------------------------------------------
    # BANCO CENTRAL
    # --------------------------------------------------

    if ambiente != "production":
        engine_central = criar_engine_central(Config)
        try:
            CentralBase.metadata.create_all(engine_central)
        finally:
            engine_central.dispose()

    # --------------------------------------------------
    # ROTAS
    # --------------------------------------------------

    @app.get("/")
    def index():

        return jsonify({
            "success": True,
            "message": "API AgroFrota funcionando"
        })

    @app.get("/api/health")
    def health():

        return jsonify({
            "success": True,
            "status": "online"
        })

    if os.getenv("AGROFROTA_ENABLE_DEV_ROUTES") == "1":
        @app.get("/api/dev/protegida")
        @autenticar()
        @resolver_tenant(Config)
        def rota_protegida(**kwargs):
            tenant_session = kwargs["tenant_session"]
            tenant = kwargs["tenant"]

            usuarios = tenant_session.execute(
                select(Usuario)
            ).scalars().all()

            return jsonify({
                "success": True,
                "message": "Acesso autorizado.",
                "usuario_id": kwargs["usuario_autenticado_id"],
                "tenant_id": kwargs["tenant_id"],
                "perfil_id": kwargs["usuario_perfil_id"],
                "tenant_nome": tenant.nome,
                "database_name": kwargs["database_name"],
                "tenant_session": "ativa",
                "quantidade_usuarios": len(usuarios)
            })
        # --------------------------------------------------
        # ROTA TEMPORÁRIA DE DESENVOLVIMENTO
        # --------------------------------------------------

        @app.get("/api/dev/teste-permissao")
        @autenticar()
        @resolver_tenant(Config)
        @exigir_permissao("OS.CRIAR")
        def teste_permissao(**kwargs):
            return jsonify({
                "success": True,
                "message": "Permissão OS.CRIAR validada com sucesso."
            })

    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False
    )
