from flask import Blueprint, jsonify, request
from config import Config
from middleware.auth import autenticar
from middleware.tenant import resolver_tenant
from services.auditoria_service import listar_eventos

auditoria_bp = Blueprint('auditoria', __name__, url_prefix='/api/auditoria')


@auditoria_bp.get('/')
@autenticar()
@resolver_tenant(Config)
def listar(**kwargs):
    try:
        eventos = listar_eventos(kwargs['tenant_session'], kwargs['contexto_administrativo'],
                                int(request.args.get('limite', 100)), int(request.args.get('offset', 0)))
    except ValueError:
        return jsonify(success=False, message='Paginação inválida.'), 400
    return jsonify(success=True, data=[dict(id=e.id, ator_id=e.ator_id,
        operacao=e.operacao, ocorrido_em=e.ocorrido_em.isoformat() + 'Z') for e in eventos])
