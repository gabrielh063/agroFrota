import pytest
from config import Config
from conftest import DATABASE_NAME
from services.admin_policy import AdministracaoNegada, ContextoAdministrativo
from services.maquina_service import listar_maquinas, criar_maquina
from services.equipamento_service import listar_equipamentos
from test_matriz_escopo import sessao, contexto


@pytest.mark.parametrize('role', ['ADMIN_EMPRESA', 'DIRETORIA', 'GESTOR_FROTA',
                                 'ADMINISTRATIVO', 'MANUTENCAO', 'OPERADOR', 'AUDITOR'])
def test_ativos_leitura_e_escrita_matriz(base_url, role):
    session, _ = sessao()
    try:
        ctx = contexto(session, DATABASE_NAME, role)
    finally:
        session.close()
    assert isinstance(listar_maquinas(Config, DATABASE_NAME, contexto=ctx), list)
    assert isinstance(listar_equipamentos(Config, DATABASE_NAME, contexto=ctx), list)
    with pytest.raises(AdministracaoNegada):
        listar_maquinas(Config, DATABASE_NAME)
    with pytest.raises(AdministracaoNegada):
        listar_equipamentos(Config, DATABASE_NAME, contexto=ContextoAdministrativo(
            'agrofrota_test_outro', ctx.usuario_id, ctx.session_version))
    if role not in {'ADMIN_EMPRESA', 'GESTOR_FROTA'}:
        with pytest.raises(AdministracaoNegada):
            criar_maquina(Config, DATABASE_NAME, 'NEGADA', 'Teste', 'Teste', contexto=ctx)
