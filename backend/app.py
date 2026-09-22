from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from sqlalchemy import select

from config import Config

from database.central import criar_engine_central
from database.base import CentralBase

from models.central.tenant import Tenant
from models.tenant.usuario import Usuario

from services.tenant_service import criar_tenant

from routes.maquinas import maquinas_bp
from routes.equipamentos import equipamentos_bp

from middleware.auth import autenticar
from middleware.tenant import resolver_tenant

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    
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
    # --------------------------------------------------
    # BANCO CENTRAL
    # --------------------------------------------------

    engine_central = criar_engine_central(
        Config
    )

    try:
        CentralBase.metadata.create_all(
            engine_central
        )
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

    @app.get("/api/dev/protegida")
    @autenticar()
    @resolver_tenant(Config)
    def rota_protegida(
        usuario_id,
        tenant_id,
        perfil_id,
        tenant,
        database_name,
        tenant_session
    ):
        
        usuarios = tenant_session.execute(
            select(Usuario)
        ).scalars().all()

        return jsonify({
            "success": True,
            "message": "Acesso autorizado.",
            "usuario_id": usuario_id,
            "tenant_id": tenant_id,
            "perfil_id": perfil_id,
            "tenant_nome": tenant.nome,
            "database_name": database_name,
            "tenant_session": "ativa",
            "quantidade_usuarios": len(usuarios)
        })
    # --------------------------------------------------
    # ROTA TEMPORÁRIA DE DESENVOLVIMENTO
    # --------------------------------------------------

    @app.post("/api/dev/tenants")
    def criar_tenant_dev():

        from flask import request

        data = request.get_json(
            silent=True
        ) or {}

        nome = data.get("nome")

        if not nome:

            return jsonify({
                "success": False,
                "message": "Nome da empresa é obrigatório"
            }), 400

        tenant = criar_tenant(
            Config,
            nome
        )

        return jsonify({
            "success": True,
            "tenant": {
                "id": tenant.id,
                "nome": tenant.nome,
                "database_name": tenant.database_name,
                "ativo": tenant.ativo
            }
        }), 201

    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )