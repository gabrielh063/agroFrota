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

import AppLayout from "./layouts/AppLayout";
import ProtectedRoute from "./routes/ProtectedRoute";
import RequirePermission from "./routes/RequirePermission";

function App() {
    return (
        <Routes>

            <Route
                path="/login"
                element={
                    <Login />
                }
            />


            <Route
                element={
                    <ProtectedRoute>
                        <AppLayout />
                    </ProtectedRoute>
                }
            >

                <Route
                    path="/"
                    element={
                        <RequirePermission anyOf="DASHBOARD.VISUALIZAR"><Home /></RequirePermission>
                    }
                />


                <Route
                    path="/calendario"
                    element={
                        <RequirePermission anyOf="OS.VISUALIZAR"><Calendario /></RequirePermission>
                    }
                />

                <Route
                    path="/assistente"
                    element={<RequirePermission anyOf="MAQUINA_VISUALIZAR"><AssistenteIA /></RequirePermission>}
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
