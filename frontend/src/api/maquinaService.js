import { api } from "./api";


export async function listarMaquinas({
    incluirInativas = false,
} = {}) {
    const resposta = await api.get(
        "/api/maquinas/",
        {
            params: {
                incluir_inativas:
                    incluirInativas,
            },
        }
    );

    return resposta.data;
}

export async function criarMaquina(dados) {
    const resposta = await api.post(
        "/api/maquinas/",
        dados
    );

    return resposta.data;
}


export async function atualizarMaquina(
    maquinaId,
    dados
) {
    const resposta = await api.put(
        `/api/maquinas/${maquinaId}`,
        dados
    );

    return resposta.data;
}


export async function desativarMaquina(
    maquinaId
) {
    const resposta = await api.patch(
        `/api/maquinas/${maquinaId}/desativar`
    );

    return resposta.data;
}


export async function ativarMaquina(
    maquinaId
) {
    const resposta = await api.patch(
        `/api/maquinas/${maquinaId}/ativar`
    );

    return resposta.data;
}