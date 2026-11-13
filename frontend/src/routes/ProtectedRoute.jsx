import {
    Navigate,
} from "react-router-dom";

import {
    useAuth,
} from "../contexts/AuthContext";


function ProtectedRoute({
    children,
}) {
    const {
        autenticado,
        carregandoPermissoes,
    } = useAuth();

    if (!autenticado) {
        return (
            <Navigate
                to="/login"
                replace
            />
        );
    }

    if (carregandoPermissoes) {
        return <div className="route-loading" role="status" aria-live="polite">Carregando seu perfil e permissões…</div>;
    }

    return children;
}


export default ProtectedRoute;
