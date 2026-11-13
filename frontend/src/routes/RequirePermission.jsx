import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "./RequirePermission.css";

export default function RequirePermission({ anyOf, children }) {
    const { pode, usuario, carregandoPermissoes, permissoes } = useAuth();
    const required = Array.isArray(anyOf) ? anyOf : [anyOf];

    if (carregandoPermissoes) {
        return <div className="route-loading" role="status" aria-live="polite">Carregando seu perfil e permissões…</div>;
    }

    if (!required.some((code) => pode(code))) {
        const destinos = [
            ["DASHBOARD.VISUALIZAR", "/", "Visão geral"],
            ["MAQUINA_VISUALIZAR", "/maquinarios", "Maquinários"],
            ["EQUIPAMENTO_VISUALIZAR", "/equipamentos", "Equipamentos"],
            ["OS.VISUALIZAR", "/ordens-servico", "Ordens de serviço"],
            ["USUARIO_VISUALIZAR", "/equipe-permissoes", "Equipe e Permissões"],
        ];
        const destinoAutorizado = destinos.find(([code]) => permissoes.includes(code));
        return (
            <section className="permission-denied" role="alert">
                <span className="permission-denied-icon" aria-hidden="true"><i className="bi bi-shield-lock" /></span>
                <p className="permission-denied-eyebrow">ACESSO RESTRITO</p>
                <h1>Você não tem permissão para esta página</h1>
                <p>Seu perfil atual é <strong>{usuario?.perfil_nome || "não identificado"}</strong>. Peça ao administrador da empresa se precisar acessar esta área.</p>
                {destinoAutorizado && <Link to={destinoAutorizado[1]} className="permission-denied-link">Ir para {destinoAutorizado[2]}</Link>}
            </section>
        );
    }

    return children;
}
