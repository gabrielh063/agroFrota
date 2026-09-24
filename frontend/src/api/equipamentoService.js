import { api } from "./api";


export async function listarEquipamentos() {
    const resposta = await api.get(
        "/api/equipamentos/"
    );

    return resposta.data;
}