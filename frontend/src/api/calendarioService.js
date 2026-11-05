import { api } from "./api";


export async function listarAgendamentos() {
    const limite = 200;
    let offset = 0;
    const agendamentos = [];
    while (true) {
        const resposta = await api.get("/api/calendario/", { params: { limite, offset } });
        const pagina = resposta.data.agendamentos;
        agendamentos.push(...pagina);
        if (pagina.length < limite) break;
        offset += pagina.length;
    }
    return { agendamentos };
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