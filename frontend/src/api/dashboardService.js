import { api } from "./api";


export async function buscarCapacidade() {
    const resposta = await api.get(
        "/api/dashboard/capacidade"
    );

    return resposta.data;
}


export async function buscarIndisponibilidade() {
    const resposta = await api.get(
        "/api/dashboard/indisponibilidade"
    );

    return resposta.data;
}