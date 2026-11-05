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

                <NavLink
                    to="/"
                    end
                    className={({ isActive }) =>
                        `sidebar-link ${
                            isActive
                                ? "active"
                                : ""
                        }`
                    }
                >
                    <i className="bi bi-house-door" />

                    <span>
                        Home
                    </span>
                </NavLink>


                <NavLink
                    to="/calendario"
                    className={({ isActive }) =>
                        `sidebar-link ${
                            isActive
                                ? "active"
                                : ""
                        }`
                    }
                >
                    <i className="bi bi-calendar3" />

                    <span>
                        Calendário de serviços
                    </span>
                </NavLink>


                <NavLink
                    to="/ordens-servico"
                    className={({ isActive }) =>
                        `sidebar-link ${
                            isActive
                                ? "active"
                                : ""
                        }`
                    }
                >
                    <i className="bi bi-clipboard-check" />

                    <span>
                        Ordens de serviço
                    </span>
                </NavLink>


                <NavLink
                    to="/maquinarios"
                    className={({ isActive }) =>
                        `sidebar-link ${
                            isActive
                                ? "active"
                                : ""
                        }`
                    }
                >
                    <i className="bi bi-truck-front" />

                    <span>
                        Maquinários
                    </span>
                </NavLink>


                <NavLink
                    to="/equipamentos"
                    className={({ isActive }) =>
                        `sidebar-link ${
                            isActive
                                ? "active"
                                : ""
                        }`
                    }
                >
                    <i className="bi bi-tools" />

                    <span>
                        Equipamentos
                    </span>
                </NavLink>

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
                            {usuario?.username
                                || ""}
                        </span>

                    </div>

                </div>


                <button
                    className="sidebar-logout"
                    onClick={handleLogout}
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