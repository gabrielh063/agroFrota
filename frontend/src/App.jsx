import {
    Navigate,
    Route,
    Routes,
} from "react-router-dom";

import Login from "./pages/Login/Login";
import Home from "./pages/Home/Home";

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
                        <PagePlaceholder
                            titulo="Calendário de serviços"
                        />
                    }
                />

                <Route
                    path="/ordens-servico"
                    element={
                        <PagePlaceholder
                            titulo="Ordens de serviço"
                        />
                    }
                />

                <Route
                    path="/ordens-servico/nova"
                    element={
                        <PagePlaceholder
                            titulo="Nova ordem de serviço"
                        />
                    }
                />

                <Route
                    path="/maquinarios"
                    element={
                        <PagePlaceholder
                            titulo="Maquinários"
                        />
                    }
                />

                <Route
                    path="/equipamentos"
                    element={
                        <PagePlaceholder
                            titulo="Equipamentos"
                        />
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