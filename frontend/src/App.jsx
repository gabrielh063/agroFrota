import {
    Navigate,
    Route,
    Routes,
} from "react-router-dom";

import Login from "./pages/Login/Login";
import Home from "./pages/Home/Home";
import Maquinarios from "./pages/Maquinarios/Maquinarios";
import Equipamentos from "./pages/Equipamentos/Equipamentos";
import OrdensServico from "./pages/OrdensServico/OrdensServico";
import NovaOrdemServico from "./pages/NovaOrdemServico/NovaOrdemServico";
import DetalhesOrdemServico from "./pages/DetalhesOrdemServico/DetalhesOrdemServico";
import EditarOrdemServico from "./pages/EditarOrdemServico/EditarOrdemServico";
import Calendario from "./pages/Calendario/Calendario";
import AssistenteIA from "./pages/AssistenteIA/AssistenteIA";
import EquipePermissoes from "./pages/EquipePermissoes/EquipePermissoes";
import Cadastro from "./pages/Cadastro/Cadastro";

import AppLayout from "./layouts/AppLayout";
import ProtectedRoute from "./routes/ProtectedRoute";
import RequirePermission from "./routes/RequirePermission";
import { useAuth } from "./contexts/AuthContext";

function PaginaInicialAutorizada() {
    const { permissoes = [] } = useAuth();
    if (permissoes.includes("DASHBOARD.VISUALIZAR")) return <Home />;
    const caminhos = [
        ["MAQUINA_VISUALIZAR", "/maquinarios"],
        ["EQUIPAMENTO_VISUALIZAR", "/equipamentos"],
        ["OS.VISUALIZAR", "/ordens-servico"],
        ["USUARIO_VISUALIZAR", "/equipe-permissoes"],
    ];
    const primeiro = caminhos.find(([codigo]) => permissoes.includes(codigo));
    return primeiro ? <Navigate to={primeiro[1]} replace /> : <section className="permission-denied"><h1>Nenhuma página liberada</h1><p>Peça ao administrador para revisar seu perfil de acesso.</p></section>;
}

function App() {
    return (
        <Routes>

            <Route
                path="/login"
                element={
                    <Login />
                }
            />

            <Route path="/cadastro" element={<Cadastro />} />


            <Route
                element={
                    <ProtectedRoute>
                        <AppLayout />
                    </ProtectedRoute>
                }
            >

                <Route
                    path="/"
                    element={<PaginaInicialAutorizada />}
                />


                <Route
                    path="/calendario"
                    element={
                        <RequirePermission anyOf="OS.VISUALIZAR"><Calendario /></RequirePermission>
                    }
                />

                <Route
                    path="/assistente"
                    element={<RequirePermission anyOf="OS.VISUALIZAR"><AssistenteIA /></RequirePermission>}
                />

                <Route
                    path="/ordens-servico"
                    element={
                        <RequirePermission anyOf="OS.VISUALIZAR"><OrdensServico /></RequirePermission>
                    }
                />


                <Route
                    path="/ordens-servico/nova"
                    element={
                        <RequirePermission anyOf="OS.CRIAR"><NovaOrdemServico /></RequirePermission>
                    }
                />
                
                <Route
                    path="/ordens-servico/:id/editar"
                    element={
                        <RequirePermission anyOf="OS.EDITAR"><EditarOrdemServico /></RequirePermission>
                    }
                />

                <Route
                    path="/ordens-servico/:id"
                    element={
                        <RequirePermission anyOf="OS.VISUALIZAR"><DetalhesOrdemServico /></RequirePermission>
                    }
                />

                <Route
                    path="/maquinarios"
                    element={
                        <RequirePermission anyOf="MAQUINA_VISUALIZAR"><Maquinarios /></RequirePermission>
                    }
                />


                <Route
                    path="/equipamentos"
                    element={
                        <RequirePermission anyOf="EQUIPAMENTO_VISUALIZAR"><Equipamentos /></RequirePermission>
                    }
                />

                <Route
                    path="/equipe-permissoes"
                    element={<RequirePermission anyOf="USUARIO_VISUALIZAR"><EquipePermissoes /></RequirePermission>}
                />

            </Route>


            <Route
                path="*"
                element={
                    <Navigate
                        to="/"
                        replace
                    />
                }
            />

        </Routes>
    );
}


export default App;
