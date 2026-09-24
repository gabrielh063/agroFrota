import { api } from "./api";


export async function listarUsuarios({
    apenasAtivos = false,
} = {}) {
    const resposta = await api.get(
        "/api/usuarios/",
        {
            params: {
                apenas_ativos:
                    apenasAtivos,
            },
        }
    );

    return resposta.data;
}