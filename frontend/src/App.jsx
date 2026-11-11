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

import AppLayout from "./layouts/AppLayout";
import ProtectedRoute from "./routes/ProtectedRoute";

import PagePlaceholder
    from "./components/PagePlaceholder/PagePlaceholder";


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
                        <Home />
                    }
                />


                <Route
                    path="/calendario"
                    element={
                        <Calendario />
                    }
                />

                <Route
                    path="/assistente"
                    element={<AssistenteIA />}
                />

                <Route
                    path="/ordens-servico"
                    element={
                        <OrdensServico />
                    }
                />


                <Route
                    path="/ordens-servico/nova"
                    element={
                        <NovaOrdemServico />
                    }
                />
                
                <Route
                    path="/ordens-servico/:id/editar"
                    element={
                        <EditarOrdemServico />
                    }
                />

                <Route
                    path="/ordens-servico/:id"
                    element={
                        <DetalhesOrdemServico />
                    }
                />

                <Route
                    path="/maquinarios"
                    element={
                        <Maquinarios />
                    }
                />


                <Route
                    path="/equipamentos"
                    element={
                        <Equipamentos />
                    }
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