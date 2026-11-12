import { api } from "./api";


export async function login({
    username,
    senha,
}) {
    const databaseName =
        import.meta.env.VITE_TENANT_DATABASE;

    const resposta = await api.post(
        "/api/auth/login",
        {
            username,
            senha,
            database_name: databaseName,
        }
    );

    return resposta.data;
}

export async function logout() {
    await api.post("/api/auth/logout");
}

export async function obterSessaoAtual() {
    const resposta = await api.get("/api/auth/me");
    return resposta.data.data;
}
