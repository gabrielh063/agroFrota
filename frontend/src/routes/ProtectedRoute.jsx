import {
    Navigate,
} from "react-router-dom";

import {
    useAuth,
} from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";


function ProtectedRoute({
    children,
}) {
    const {
        autenticado,
        carregandoPermissoes,
        estadoValidacao,
        erroValidacao,
        tentarNovamente,
        sair,
    } = useAuth();
    const navigate = useNavigate();

    if (!autenticado) {
        return (
            <Navigate
                to="/login"
                replace
            />
        );
    }

    if (carregandoPermissoes || estadoValidacao !== "ready") {
        const sairDaSessao = async () => {
            try { await sair(); } catch { /* Credenciais locais são limpas mesmo sem rede. */ }
            navigate("/login", { replace: true });
        };
        if (carregandoPermissoes) {
            return <div className="route-loading" role="status" aria-live="polite">Carregando seu perfil e permissões…</div>;
        }
        return (
            <section className="permission-denied" role="alert">
                <h1>{estadoValidacao === "denied" ? "Acesso negado" : "Serviço temporariamente indisponível"}</h1>
                <p>{erroValidacao}</p>
                <div className="session-recovery-actions">
                    <button type="button" onClick={tentarNovamente}>Tentar novamente</button>
                    <button type="button" className="secondary" onClick={sairDaSessao}>Sair da conta</button>
                </div>
            </section>
        );
    }

    return children;
}


export default ProtectedRoute;
