import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { login as loginApi, logout as logoutApi, obterSessaoAtual } from "../api/authService";
import { nomePerfil } from "../utils/perfilLabels";

const AuthContext = createContext(null);

function limparCredenciais() {
    sessionStorage.removeItem("agrofrota_token");
    sessionStorage.removeItem("agrofrota_usuario");
    sessionStorage.removeItem("agrofrota_tenant");
}

function statusDaFalha(error) {
    return error.response?.status === 403 ? "denied" : "temporary_error";
}

function mensagemDaFalha(error) {
    if (error.response?.status === 403) return "Sua conta está autenticada, mas não pode consultar as permissões agora.";
    return "Não foi possível validar suas permissões. Confira a conexão e tente novamente.";
}

export function AuthProvider({ children }) {
    const [token, setToken] = useState(() => sessionStorage.getItem("agrofrota_token"));
    const [usuario, setUsuario] = useState(null);
    const [tenant, setTenant] = useState(null);
    const [permissoes, setPermissoes] = useState([]);
    const [estadoValidacao, setEstadoValidacao] = useState(() =>
        sessionStorage.getItem("agrofrota_token") ? "loading" : "ready"
    );
    const [erroValidacao, setErroValidacao] = useState("");
    const [tentativa, setTentativa] = useState(0);
    const [sessaoExpirada, setSessaoExpirada] = useState(false);
    const requestId = useRef(0);
    const ultimaValidacao = useRef(0);

    const aceitarSessao = useCallback((sessao) => {
        const usuarioAtual = {
            ...sessao.usuario,
            perfil_nome: nomePerfil(sessao.usuario.perfil_nome),
            permissoes: sessao.permissoes || [],
        };
        setUsuario(usuarioAtual);
        setTenant(sessao.tenant);
        setPermissoes(usuarioAtual.permissoes);
        sessionStorage.setItem("agrofrota_usuario", JSON.stringify(usuarioAtual));
        sessionStorage.setItem("agrofrota_tenant", JSON.stringify(sessao.tenant));
        setErroValidacao("");
        setEstadoValidacao("ready");
    }, []);

    const invalidarSessao = useCallback(() => {
        requestId.current += 1;
        limparCredenciais();
        setToken(null);
        setUsuario(null);
        setTenant(null);
        setPermissoes([]);
        setEstadoValidacao("ready");
        setErroValidacao("");
        setSessaoExpirada(true);
    }, []);

    useEffect(() => {
        window.addEventListener("agrofrota:session-expired", invalidarSessao);
        return () => window.removeEventListener("agrofrota:session-expired", invalidarSessao);
    }, [invalidarSessao]);

    useEffect(() => {
        if (!token) return undefined;
        const id = ++requestId.current;
        let ativo = true;
        ultimaValidacao.current = Date.now();

        obterSessaoAtual()
            .then((sessao) => {
                if (ativo && requestId.current === id) aceitarSessao(sessao);
            })
            .catch((error) => {
                if (!ativo || requestId.current !== id) return;
                if (error.response?.status === 401) {
                    invalidarSessao();
                    return;
                }
                setPermissoes([]);
                setErroValidacao(mensagemDaFalha(error));
                setEstadoValidacao(statusDaFalha(error));
            });

        return () => { ativo = false; };
    }, [token, tentativa, aceitarSessao, invalidarSessao]);

    async function entrar(username, senha) {
        const dados = await loginApi({ username, senha });
        const accessToken = dados.data.access_token;
        requestId.current += 1;
        limparCredenciais();
        sessionStorage.setItem("agrofrota_token", accessToken);
        setUsuario(null);
        setTenant(null);
        setPermissoes([]);
        setSessaoExpirada(false);
        setEstadoValidacao("loading");
        setToken(accessToken);
        return dados;
    }

    async function sair() {
        const id = ++requestId.current;
        try {
            if (token) await logoutApi();
        } finally {
            // Logout local always wins over a slow /me or logout response.
            if (requestId.current === id) {
                limparCredenciais();
                setToken(null);
                setUsuario(null);
                setTenant(null);
                setPermissoes([]);
                setEstadoValidacao("ready");
                setErroValidacao("");
            }
        }
    }

    const tentarNovamente = useCallback(() => {
        setEstadoValidacao("loading");
        setErroValidacao("");
        setPermissoes([]);
        ultimaValidacao.current = Date.now();
        setTentativa((valor) => valor + 1);
    }, []);

    useEffect(() => {
        if (!token) return undefined;
        const validarSeVencida = () => {
            if (document.visibilityState === "hidden" || estadoValidacao !== "ready") return;
            if (Date.now() - ultimaValidacao.current < 10000) return;
            setEstadoValidacao("loading");
            setPermissoes([]);
            setErroValidacao("");
            setTentativa((valor) => valor + 1);
        };
        window.addEventListener("focus", validarSeVencida);
        document.addEventListener("visibilitychange", validarSeVencida);
        const timer = window.setInterval(validarSeVencida, 60000);
        return () => {
            window.removeEventListener("focus", validarSeVencida);
            document.removeEventListener("visibilitychange", validarSeVencida);
            window.clearInterval(timer);
        };
    }, [token, estadoValidacao]);

    return (
        <AuthContext.Provider value={{
            token, usuario, tenant, permissoes,
            carregandoPermissoes: estadoValidacao === "loading",
            estadoValidacao, erroValidacao, tentarNovamente,
            pode: (codigo) => permissoes.includes(codigo),
            autenticado: Boolean(token), sessaoExpirada, entrar, sair,
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const contexto = useContext(AuthContext);
    if (!contexto) throw new Error("useAuth deve ser usado dentro de AuthProvider.");
    return contexto;
}
