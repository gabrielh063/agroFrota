import {
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";

import { login as loginApi, logout as logoutApi, obterSessaoAtual } from "../api/authService";
import { nomePerfil } from "../utils/perfilLabels";


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

    const [permissoes, setPermissoes] = useState([]);
    const [carregandoPermissoes, setCarregandoPermissoes] = useState(
        () => Boolean(sessionStorage.getItem("agrofrota_token"))
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
            setPermissoes([]);
            setCarregandoPermissoes(false);
            setSessaoExpirada(true);
        }
        window.addEventListener("agrofrota:session-expired", expirarSessao);
        return () => window.removeEventListener("agrofrota:session-expired", expirarSessao);
    }, []);

    useEffect(() => {
        let ativo = true;
        if (!token) {
            return () => { ativo = false; };
        }

        obterSessaoAtual()
            .then((sessao) => {
                if (!ativo) return;
                const usuarioAtual = sessao.usuario;
                const tenantAtual = sessao.tenant;
                usuarioAtual.perfil_nome = nomePerfil(usuarioAtual.perfil_nome);
                usuarioAtual.permissoes = sessao.permissoes || [];
                setUsuario(usuarioAtual);
                setTenant(tenantAtual);
                setPermissoes(usuarioAtual.permissoes);
                sessionStorage.setItem("agrofrota_usuario", JSON.stringify(usuarioAtual));
                sessionStorage.setItem("agrofrota_tenant", JSON.stringify(tenantAtual));
            })
            .catch(() => {
                if (!ativo) return;
                sessionStorage.removeItem("agrofrota_token");
                sessionStorage.removeItem("agrofrota_usuario");
                sessionStorage.removeItem("agrofrota_tenant");
                setToken(null);
                setUsuario(null);
                setTenant(null);
                setPermissoes([]);
            })
            .finally(() => {
                if (ativo) setCarregandoPermissoes(false);
            });

        return () => { ativo = false; };
    }, [token]);

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
        sessionStorage.setItem(
            "agrofrota_token",
            accessToken
        );

        try {
            const sessao = await obterSessaoAtual();
            const usuarioLogado = { ...sessao.usuario, perfil_nome: nomePerfil(sessao.usuario.perfil_nome), permissoes: sessao.permissoes || [] };
            sessionStorage.setItem("agrofrota_usuario", JSON.stringify(usuarioLogado));
            sessionStorage.setItem("agrofrota_tenant", JSON.stringify(sessao.tenant));
            setPermissoes(usuarioLogado.permissoes);
            setUsuario(usuarioLogado);
            setTenant(sessao.tenant);
            setSessaoExpirada(false);
            setCarregandoPermissoes(false);
            setToken(accessToken);
        } catch (error) {
            sessionStorage.removeItem("agrofrota_token");
            throw error;
        }

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
        setPermissoes([]);
    }


    return (
        <AuthContext.Provider
            value={{
                token,
                usuario,
                tenant,
                permissoes,
                carregandoPermissoes,
                pode: (codigo) => permissoes.includes(codigo),
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
