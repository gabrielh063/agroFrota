import { api } from "./api";


export async function listarOrdensServico({
    apenasAtivas = false,
} = {}) {
    const resposta = await api.get(
        "/api/ordens-servico/",
        {
            params: {
                apenas_ativas:
                    apenasAtivas,
            },
        }
    );

    return resposta.data;
}


export async function buscarOrdemServico(
    ordemId
) {
    const resposta = await api.get(
        `/api/ordens-servico/${ordemId}`
    );

    return resposta.data;
}


export async function criarOrdemServico(
    dados
) {
    const resposta = await api.post(
        "/api/ordens-servico/",
        dados
    );

    return resposta.data;
}


export async function atualizarOrdemServico(
    ordemId,
    dados
) {
    const resposta = await api.put(
        `/api/ordens-servico/${ordemId}`,
        dados
    );

    return resposta.data;
}


export async function concluirOrdemServico(
    ordemId
) {
    const resposta = await api.patch(
        `/api/ordens-servico/${ordemId}/concluir`
    );

    return resposta.data;
}


export async function cancelarOrdemServico(
    ordemId
) {
    const resposta = await api.patch(
        `/api/ordens-servico/${ordemId}/cancelar`
    );

    return resposta.data;
}