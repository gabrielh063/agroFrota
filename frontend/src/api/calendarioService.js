import { api } from "./api";


export async function listarAgendamentos() {
    const resposta = await api.get(
        "/api/calendario/"
    );

    return resposta.data;
}


export async function buscarAgendamento(
    agendamentoId
) {
    const resposta = await api.get(
        `/api/calendario/${agendamentoId}`
    );

    return resposta.data;
}


export async function criarAgendamento(
    dados
) {
    const resposta = await api.post(
        "/api/calendario/",
        dados
    );

    return resposta.data;
}


export async function atualizarAgendamento(
    agendamentoId,
    dados
) {
    const resposta = await api.put(
        `/api/calendario/${agendamentoId}`,
        dados
    );

    return resposta.data;
}


export async function cancelarAgendamento(
    agendamentoId
) {
    const resposta = await api.patch(
        `/api/calendario/${agendamentoId}/cancelar`
    );

    return resposta.data;
}