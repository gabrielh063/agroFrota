import {
    useState,
} from "react";

import {
    useNavigate,
} from "react-router-dom";

import {
    useAuth,
} from "../../contexts/AuthContext";

import "./Login.css";


function Login() {
    const navigate = useNavigate();

    const {
        entrar,
        sessaoExpirada,
    } = useAuth();

    const [username, setUsername] =
        useState("");

    const [senha, setSenha] =
        useState("");

    const [erro, setErro] =
        useState("");

    const [carregando, setCarregando] =
        useState(false);


    async function handleSubmit(event) {
        event.preventDefault();

        setErro("");

        if (!username.trim()) {
            setErro(
                "Informe o usuário."
            );

            return;
        }

        if (!senha) {
            setErro(
                "Informe a senha."
            );

            return;
        }

        try {
            setCarregando(true);

            await entrar(
                username.trim(),
                senha
            );

            navigate(
                "/",
                {
                    replace: true,
                }
            );

        } catch (error) {
            console.error("Falha ao autenticar usuário:", error);
            setErro("Não foi possível entrar. Confira seus dados e tente novamente.");

        } finally {
            setCarregando(false);
        }
    }


    return (
        <div className="login-page">

            <section className="login-brand">

                <div className="login-logo">
                    <div className="login-logo-icon">
                        <i className="bi bi-truck" />
                    </div>

                    <span>
                        AgroFrota
                    </span>
                </div>


                <div className="login-brand-content">

                    <div className="login-brand-icon">
                        <i className="bi bi-gear-wide-connected" />
                    </div>

                    <h1>
                        Controle total da sua
                        frota e manutenções
                        agrícolas
                    </h1>

                    <p>
                        Tratores, colheitadeiras,
                        implementos e equipamentos
                        em um só lugar. Ordens de
                        serviço, calendário de
                        manutenção e status da frota
                        em tempo real.
                    </p>

                </div>


                <span className="login-copyright">
                    © 2026 AgroFrota
                </span>

                <div className="login-glow" />

            </section>


            <section className="login-form-area">

                <div className="login-form-container">

                    <header className="login-header">
                        <h2>
                            Entrar
                        </h2>

                        <p>
                            Acesse o painel de gestão
                            da frota.
                        </p>
                    </header>


                    <form
                        className="login-form"
                        onSubmit={handleSubmit}
                    >

                        <div className="form-field">
                            <label htmlFor="username">
                                Usuário
                            </label>

                            <input
                                id="username"
                                type="text"
                                value={username}
                                onChange={(event) =>
                                    setUsername(
                                        event.target.value
                                    )
                                }
                                placeholder="Digite seu usuário"
                                autoComplete="username"
                                disabled={carregando}
                            />
                        </div>


                        <div className="form-field">
                            <label htmlFor="senha">
                                Senha
                            </label>

                            <input
                                id="senha"
                                type="password"
                                value={senha}
                                onChange={(event) =>
                                    setSenha(
                                        event.target.value
                                    )
                                }
                                placeholder="Digite sua senha"
                                autoComplete="current-password"
                                disabled={carregando}
                            />
                        </div>


                        {(erro || sessaoExpirada) && (
                            <div
                                className="login-error"
                                role="alert"
                            >
                                <i className="bi bi-exclamation-circle" />

                                <span>
                                    {erro || "Sua sessão expirou ou foi revogada. Entre novamente."}
                                </span>
                            </div>
                        )}


                        <button
                            className="login-button"
                            type="submit"
                            disabled={carregando}
                        >
                            {carregando ? (
                                <>
                                    <span
                                        className="spinner-border spinner-border-sm"
                                    />

                                    Entrando...
                                </>
                            ) : (
                                "Entrar"
                            )}
                        </button>

                    </form>


                    <div className="login-info">
                        <i className="bi bi-shield-check" />

                        <span>
                            Ambiente seguro AgroFrota.
                            Utilize suas credenciais
                            para acessar o sistema.
                        </span>
                    </div>

                </div>

            </section>

        </div>
    );
}


export default Login;
