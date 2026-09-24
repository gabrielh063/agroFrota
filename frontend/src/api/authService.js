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