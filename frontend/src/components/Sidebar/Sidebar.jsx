import {
    NavLink,
    useNavigate,
} from "react-router-dom";
import { useState } from "react";

import {
    useAuth,
} from "../../contexts/AuthContext";

import "./Sidebar.css";


function Sidebar() {
    const navigate = useNavigate();
    const [menuAberto, setMenuAberto] = useState(false);

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
        setMenuAberto(false);
    }


    const inicial =
        usuario?.nome
            ?.trim()
            ?.charAt(0)
            ?.toUpperCase()
        || "U";

    const operacional = [
        ["/", "bi-house-door", "Visão geral", true],
        ["/assistente", "bi-chat-square-text", "Central de Operações", true],
        ["/calendario", "bi-calendar3", "Calendário de serviços", true],
        ["/ordens-servico", "bi-clipboard-check", "Ordens de serviço", true],
        ["/maquinarios", "bi-truck-front", "Maquinários", true],
        ["/equipamentos", "bi-tools", "Equipamentos", true],
    ];


    return (
        <aside className="sidebar">

            <div className="sidebar-mobile-bar">
                <div className="sidebar-mobile-brand">
                    <span className="sidebar-brand-icon"><i className="bi bi-truck" /></span>
                    <strong>AgroFrota</strong>
                </div>
                <button className="sidebar-menu-toggle" type="button" aria-expanded={menuAberto} aria-controls="sidebar-navigation" aria-label={menuAberto ? "Fechar menu" : "Abrir menu"} onClick={() => setMenuAberto((aberto) => !aberto)}>
                    <i className={`bi ${menuAberto ? "bi-x-lg" : "bi-list"}`} />
                </button>
            </div>

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


            <nav id="sidebar-navigation" className={`sidebar-nav ${menuAberto ? "sidebar-nav-open" : ""}`}>
                <div className="sidebar-group">
                    <span className="sidebar-section-label">OPERAÇÕES</span>
                    {operacional.map(([to, icon, label]) => <NavLink key={to} to={to} end={to === "/"} onClick={() => setMenuAberto(false)} className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}><i className={`bi ${icon}`} /><span>{label}</span></NavLink>)}
                </div>
                <div className="sidebar-group sidebar-management">
                    <span className="sidebar-section-label">GESTÃO</span>
                    <span className="sidebar-link sidebar-disabled" aria-disabled="true" title="Disponível em uma versão futura"><i className="bi bi-bar-chart-line" /><span>Relatórios e indicadores</span><small>Em breve</small></span>
                    <span className="sidebar-link sidebar-disabled" aria-disabled="true" title="Disponível em uma versão futura"><i className="bi bi-people" /><span>Equipe e recursos</span><small>Em breve</small></span>
                </div>
                {import.meta.env.VITE_AGROFROTA_DEMO === "true" && <div className="sidebar-demo"><strong><i /> Ambiente demonstrativo</strong><span>Informações fictícias para apresentação do AgroFrota.</span></div>}
            </nav>


            <div className="sidebar-footer">

                <span className="sidebar-section-label sidebar-account-label">CONTA</span>

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
                    type="button"
                >
                    <i className="bi bi-box-arrow-left" />

                    <span>
                        Sair
                    </span>
                </button>

            </div>

        </aside>
    );
}


export default Sidebar;
