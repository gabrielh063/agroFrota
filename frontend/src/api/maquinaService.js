import { api } from "./api";


export async function listarMaquinas() {
    const resposta = await api.get(
        "/api/maquinas/"
    );

    return resposta.data;
}