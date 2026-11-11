import database  # Initialize the package before importing tenant model modules.

from services.assistente_ia_service import responder_consulta_operacional


def test_consulta_multiparta_lista_ativos_parados_e_os_abertas():
    dados = {
        "total_maquinas": 2,
        "total_equipamentos": 0,
        "maquinas": [
            {"identificacao": "TR-01", "status": "MANUTENCAO", "ativo": True},
            {"identificacao": "TR-02", "status": "OPERANDO", "ativo": True},
        ],
        "equipamentos": [],
        "permissoes": ["OS.VISUALIZAR"],
        "ordens_servico": [
            {"numero": 12, "titulo": "Revisão hidráulica", "status": "ABERTA", "ativo": True},
        ],
    }
    resposta = responder_consulta_operacional(
        "Quais máquinas estão paradas e quais OS estão abertas?", dados
    )
    assert "TR-01" in resposta
    assert "OS #12" in resposta


def test_consulta_operacional_sem_registros_nao_inventa():
    dados = {
        "total_maquinas": 0,
        "total_equipamentos": 0,
        "maquinas": [],
        "equipamentos": [],
        "permissoes": ["OS.VISUALIZAR"],
        "ordens_servico": [],
    }
    resposta = responder_consulta_operacional(
        "Quais máquinas estão paradas e quais OS estão abertas?", dados
    )
    assert "Não encontrei" in resposta
    assert "OS #" not in resposta
