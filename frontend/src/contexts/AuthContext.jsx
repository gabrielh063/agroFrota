import {
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";

import { login as loginApi, logout as logoutApi } from "../api/authService";


const AuthContext = createContext(null);


export function AuthProvider({
    children,
}) {
    const [token, setToken] = useState(
        () =>
            sessionStorage.getItem(
                "agrofrota_token"
            )
    );

    const [usuario, setUsuario] = useState(
        () => {
            const salvo =
                sessionStorage.getItem(
                    "agrofrota_usuario"
                );

            return salvo
                ? JSON.parse(salvo)
                : null;
        }
    );

    const [tenant, setTenant] = useState(
        () => {
            const salvo =
                sessionStorage.getItem(
                    "agrofrota_tenant"
                );

            return salvo
                ? JSON.parse(salvo)
                : null;
        }
    );


    const [sessaoExpirada, setSessaoExpirada] = useState(false);

    useEffect(() => {
        function expirarSessao() {
            sessionStorage.removeItem("agrofrota_token");
            sessionStorage.removeItem("agrofrota_usuario");
            sessionStorage.removeItem("agrofrota_tenant");
            setToken(null);
            setUsuario(null);
            setTenant(null);
            setSessaoExpirada(true);
        }
        window.addEventListener("agrofrota:session-expired", expirarSessao);
        return () => window.removeEventListener("agrofrota:session-expired", expirarSessao);
    }, []);

    async function entrar(
        username,
        senha
    ) {
        const dados = await loginApi({
            username,
            senha,
        });

        const accessToken =
            dados.data.access_token;

        const usuarioLogado =
            dados.data.usuario;

        const tenantLogado =
            dados.data.tenant;


        sessionStorage.setItem(
            "agrofrota_token",
            accessToken
        );

        sessionStorage.setItem(
            "agrofrota_usuario",
            JSON.stringify(
                usuarioLogado
            )
        );

        sessionStorage.setItem(
            "agrofrota_tenant",
            JSON.stringify(
                tenantLogado
            )
        );


        setSessaoExpirada(false);
        setToken(accessToken);
        setUsuario(usuarioLogado);
        setTenant(tenantLogado);

        return dados;
    }


    async function sair() {
        await logoutApi();
        sessionStorage.removeItem(
            "agrofrota_token"
        );

        sessionStorage.removeItem(
            "agrofrota_usuario"
        );

        sessionStorage.removeItem(
            "agrofrota_tenant"
        );

        setToken(null);
        setUsuario(null);
        setTenant(null);
    }


    return (
        <AuthContext.Provider
            value={{
                token,
                usuario,
                tenant,
                autenticado: Boolean(token),
                sessaoExpirada,
                entrar,
                sair,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}


export function useAuth() {
    const contexto =
        useContext(AuthContext);

    if (!contexto) {
        throw new Error(
            "useAuth deve ser usado dentro de AuthProvider."
        );
    }

    return contexto;
}