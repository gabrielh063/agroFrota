import { api } from "./api";


export async function listarOrdensServico() {
    const resposta = await api.get(
        "/api/ordens-servico/"
    );

    return resposta.data;
}