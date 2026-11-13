import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api/api";
import "./Cadastro.css";

function Cadastro() {
    const [token, setToken] = useState(() => new URLSearchParams(window.location.hash.slice(1)).get("token") || "");
    const [convite, setConvite] = useState(null);
    const [form, setForm] = useState({ username: "", senha: "", confirmarSenha: "" });
    const [erroConvite, setErroConvite] = useState("");
    const [erroFormulario, setErroFormulario] = useState("");
    const [carregando, setCarregando] = useState(Boolean(token));
    const [salvando, setSalvando] = useState(false);
    const [concluido, setConcluido] = useState(false);
    const envioEmAndamento = useRef(false);

    useEffect(() => {
        window.history.replaceState({}, "", "/cadastro");
        let active = true;
        if (!token) {
            return () => { active = false; };
        }
        api.post("/api/convites/validar", { token })
            .then((response) => { if (active) setConvite(response.data.data); })
            .catch((error) => {
                if (active) setErroConvite(error.response?.data?.message || "Este convite não está mais disponível.");
            })
            .finally(() => { if (active) setCarregando(false); });
        return () => { active = false; };
    }, [token]);

    async function cadastrar(event) {
        event.preventDefault();
        if (envioEmAndamento.current || !convite || concluido) return;
        setErroFormulario("");
        if (form.senha !== form.confirmarSenha) {
            setErroFormulario("As senhas não coincidem.");
            return;
        }
        envioEmAndamento.current = true;
        setSalvando(true);
        try {
            await api.post("/api/convites/registrar", {
                token, username: form.username.trim(), senha: form.senha,
            });
            setConcluido(true);
            setToken("");
            setForm({ username: "", senha: "", confirmarSenha: "" });
        } catch (error) {
            const message = error.response?.data?.message;
            if (error.response?.status === 400 && message?.startsWith("Convite inválido,")) {
                setErroConvite(message);
                setConvite(null);
                setForm({ username: "", senha: "", confirmarSenha: "" });
            } else {
                setErroFormulario(message || "Não foi possível concluir o cadastro. Confira sua conexão e tente novamente.");
            }
        } finally {
            envioEmAndamento.current = false;
            setSalvando(false);
        }
    }

    return (
        <main className="signup-page">
            <section className="signup-card" aria-labelledby="signup-title">
                <Link className="signup-brand" to="/login">AgroFrota</Link>
                <span className="signup-eyebrow">CONVITE DE ACESSO</span>
                <h1 id="signup-title">Criar sua conta</h1>
                {carregando ? <p role="status">Validando convite…</p> : concluido ? (
                    <div className="signup-complete" role="status">
                        <p>Conta criada. Você já pode entrar.</p>
                        <Link className="signup-login-link" to="/login" state={{ mensagem: "Conta criada. Entre com seu usuário e senha." }}>Ir para o login</Link>
                    </div>
                ) : (erroConvite || !convite) ? (
                    <div className="signup-error" role="alert">{erroConvite || "O link de convite está incompleto."}<p>Peça ao administrador da sua empresa um novo convite.</p></div>
                ) : (
                    <>
                        <p className="signup-intro">Este convite foi emitido para <strong>{convite?.nome}</strong>{convite?.email ? ` (${convite.email})` : ""}.</p>
                        {erroFormulario && <div className="signup-error" role="alert">{erroFormulario}</div>}
                        <form className="signup-form" onSubmit={cadastrar}>
                            <label htmlFor="signup-username">Usuário</label>
                            <input id="signup-username" required minLength={1} maxLength={80} autoComplete="username" value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} />
                            <label htmlFor="signup-password">Senha</label>
                            <input id="signup-password" required minLength={8} maxLength={128} type="password" autoComplete="new-password" value={form.senha} onChange={(event) => setForm({ ...form, senha: event.target.value })} />
                            <label htmlFor="signup-confirm">Confirmar senha</label>
                            <input id="signup-confirm" required minLength={8} maxLength={128} type="password" autoComplete="new-password" value={form.confirmarSenha} onChange={(event) => setForm({ ...form, confirmarSenha: event.target.value })} />
                            <button type="submit" disabled={salvando || concluido}>{salvando ? "Criando conta…" : "Criar conta"}</button>
                        </form>
                    </>
                )}
                <p className="signup-footer"><Link to="/login">Voltar ao login</Link></p>
            </section>
        </main>
    );
}

export default Cadastro;
