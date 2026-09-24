import { api } from "./api";


export async function listarEquipamentos({
    incluirInativos = false,
} = {}) {
    const resposta = await api.get(
        "/api/equipamentos/",
        {
            params: {
                incluir_inativos:
                    incluirInativos,
            },
        }
    );

    return resposta.data;
}


export async function criarEquipamento(
    dados
) {
    const resposta = await api.post(
        "/api/equipamentos/",
        dados
    );

    return resposta.data;
}


export async function atualizarEquipamento(
    equipamentoId,
    dados
) {
    const resposta = await api.put(
        `/api/equipamentos/${equipamentoId}`,
        dados
    );

    return resposta.data;
}


export async function desativarEquipamento(
    equipamentoId
) {
    const resposta = await api.patch(
        `/api/equipamentos/${equipamentoId}/desativar`
    );

    return resposta.data;
}


export async function ativarEquipamento(
    equipamentoId
) {
    const resposta = await api.patch(
        `/api/equipamentos/${equipamentoId}/ativar`
    );

    return resposta.data;
}