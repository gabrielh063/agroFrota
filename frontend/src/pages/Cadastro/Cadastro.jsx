import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../../api/api";
import "./Cadastro.css";

function Cadastro() {
    const navigate = useNavigate();
    const [token] = useState(() => new URLSearchParams(window.location.hash.slice(1)).get("token") || "");
    const [convite, setConvite] = useState(null);
    const [form, setForm] = useState({ username: "", senha: "", confirmarSenha: "" });
    const [erro, setErro] = useState("");
    const [carregando, setCarregando] = useState(Boolean(token));
    const [salvando, setSalvando] = useState(false);

    useEffect(() => {
        window.history.replaceState({}, "", "/cadastro");
        let active = true;
        if (!token) {
            return () => { active = false; };
        }
        api.post("/api/convites/validar", { token })
            .then((response) => { if (active) setConvite(response.data.data); })
            .catch((error) => {
                if (active) setErro(error.response?.data?.message || "Este convite não está mais disponível.");
            })
            .finally(() => { if (active) setCarregando(false); });
        return () => { active = false; };
    }, [token]);

    async function cadastrar(event) {
        event.preventDefault();
        setErro("");
        if (form.senha !== form.confirmarSenha) {
            setErro("As senhas não coincidem.");
            return;
        }
        setSalvando(true);
        try {
            await api.post("/api/convites/registrar", {
                token, username: form.username.trim(), senha: form.senha,
            });
            navigate("/login", { replace: true, state: { mensagem: "Conta criada. Entre com seu usuário e senha." } });
        } catch (error) {
            setErro(error.response?.data?.message || "Não foi possível concluir o cadastro.");
        } finally {
            setSalvando(false);
        }
    }

    return (
        <main className="signup-page">
            <section className="signup-card" aria-labelledby="signup-title">
                <Link className="signup-brand" to="/login">AgroFrota</Link>
                <span className="signup-eyebrow">CONVITE DE ACESSO</span>
                <h1 id="signup-title">Criar sua conta</h1>
                {carregando ? <p role="status">Validando convite…</p> : (erro || !convite) ? (
                    <div className="signup-error" role="alert">{erro || "O link de convite está incompleto."}<p>Peça ao administrador da sua empresa um novo convite.</p></div>
                ) : (
                    <>
                        <p className="signup-intro">Este convite foi emitido para <strong>{convite?.nome}</strong>{convite?.email ? ` (${convite.email})` : ""}.</p>
                        {erro && <div className="signup-error" role="alert">{erro}</div>}
                        <form className="signup-form" onSubmit={cadastrar}>
                            <label htmlFor="signup-username">Usuário</label>
                            <input id="signup-username" required minLength={1} maxLength={80} autoComplete="username" value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} />
                            <label htmlFor="signup-password">Senha</label>
                            <input id="signup-password" required minLength={8} maxLength={128} type="password" autoComplete="new-password" value={form.senha} onChange={(event) => setForm({ ...form, senha: event.target.value })} />
                            <label htmlFor="signup-confirm">Confirmar senha</label>
                            <input id="signup-confirm" required minLength={8} maxLength={128} type="password" autoComplete="new-password" value={form.confirmarSenha} onChange={(event) => setForm({ ...form, confirmarSenha: event.target.value })} />
                            <button type="submit" disabled={salvando}>{salvando ? "Criando conta…" : "Criar conta"}</button>
                        </form>
                    </>
                )}
                <p className="signup-footer"><Link to="/login">Voltar ao login</Link></p>
            </section>
        </main>
    );
}

export default Cadastro;
