import {
    NavLink,
    useNavigate,
} from "react-router-dom";

import {
    useAuth,
} from "../../contexts/AuthContext";

import "./Sidebar.css";


function Sidebar() {
    const navigate = useNavigate();

    const {
        usuario,
        sair,
    } = useAuth();


    async function handleLogout() {
        try {
            await sair();
        } catch {
            window.alert("Não foi possível encerrar a sessão no servidor. Tente novamente.");
            return;
        }

        navigate(
            "/login",
            {
                replace: true,
            }
        );
    }


    const inicial =
        usuario?.nome
            ?.trim()
            ?.charAt(0)
            ?.toUpperCase()
        || "U";

    const operacional = [
        ["/", "bi-house-door", "Visão geral", true],
        ["/assistente", "bi-robot", "Assistente IA", true],
        ["/calendario", "bi-calendar3", "Calendário de serviços", true],
        ["/ordens-servico", "bi-clipboard-check", "Ordens de serviço", true],
        ["/maquinarios", "bi-truck-front", "Maquinários", true],
        ["/equipamentos", "bi-tools", "Equipamentos", true],
    ];


    return (
        <aside className="sidebar">

            <div className="sidebar-brand">

                <div className="sidebar-brand-icon">
                    <i className="bi bi-truck" />
                </div>

                <div className="sidebar-brand-text">
                    <strong>
                        AgroFrota
                    </strong>

                    <span>
                        Gestão de frota
                    </span>
                </div>

            </div>


            <nav className="sidebar-nav">
                <div className="sidebar-group">
                    <span className="sidebar-section-label">OPERACIONAL</span>
                    {operacional.map(([to, icon, label]) => <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}><i className={`bi ${icon}`} /><span>{label}</span></NavLink>)}
                </div>
                <div className="sidebar-group sidebar-management">
                    <span className="sidebar-section-label">GESTÃO</span>
                    <span className="sidebar-link sidebar-disabled" aria-disabled="true" title="Disponível em uma versão futura"><i className="bi bi-bar-chart-line" /><span>Relatórios e indicadores</span><small>Em breve</small></span>
                    <span className="sidebar-link sidebar-disabled" aria-disabled="true" title="Disponível em uma versão futura"><i className="bi bi-people" /><span>Equipe e recursos</span><small>Em breve</small></span>
                </div>
                {import.meta.env.VITE_AGROFROTA_DEMO === "true" && <div className="sidebar-demo"><strong><i /> Ambiente demonstrativo</strong><span>Informações fictícias para apresentação do AgroFrota.</span></div>}
            </nav>


            <div className="sidebar-footer">

                <div className="sidebar-user">

                    <div className="sidebar-avatar">
                        {inicial}
                    </div>

                    <div className="sidebar-user-info">

                        <strong>
                            {usuario?.nome
                                || "Usuário"}
                        </strong>

                        <span>
                            {usuario?.tenant_nome || usuario?.username || "Sessão autenticada"}
                        </span>

                    </div>

                </div>


                <button
                    className="sidebar-logout"
                    onClick={handleLogout}
                >
                    <i className="bi bi-box-arrow-left" />

                    <span>
                        Sair da demonstração
                    </span>
                </button>

            </div>

        </aside>
    );
}


export default Sidebar;
