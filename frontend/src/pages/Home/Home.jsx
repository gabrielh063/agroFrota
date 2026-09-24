import {
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    useNavigate,
} from "react-router-dom";

import DashboardCard
    from "../../components/DashboardCard/DashboardCard";

import {
    buscarCapacidade,
} from "../../api/dashboardService";

import {
    listarOrdensServico,
} from "../../api/ordemServicoService";

import {
    listarMaquinas,
} from "../../api/maquinaService";

import {
    listarEquipamentos,
} from "../../api/equipamentoService";

import "./Home.css";


function Home() {
    const navigate =
        useNavigate();

    const [capacidade, setCapacidade] =
        useState(null);

    const [ordens, setOrdens] =
        useState([]);

    const [maquinas, setMaquinas] =
        useState([]);

    const [equipamentos, setEquipamentos] =
        useState([]);

    const [carregando, setCarregando] =
        useState(true);

    const [erro, setErro] =
        useState("");


    useEffect(() => {
        carregarDashboard();
    }, []);


    async function carregarDashboard() {
        try {
            setCarregando(true);
            setErro("");

            const [
                dadosCapacidade,
                dadosOrdens,
                dadosMaquinas,
                dadosEquipamentos,
            ] = await Promise.all([
                buscarCapacidade(),
                listarOrdensServico(),
                listarMaquinas(),
                listarEquipamentos(),
            ]);

            setCapacidade(
                dadosCapacidade.capacidade
            );

            setOrdens(
                dadosOrdens.ordens_servico
                || []
            );

            setMaquinas(
                dadosMaquinas.data
                || []
            );

            setEquipamentos(
                dadosEquipamentos.data
                || []
            );

        } catch (error) {
            console.error(
                "Erro ao carregar dashboard:",
                error
            );

            setErro(
                "Não foi possível carregar os dados do painel."
            );

        } finally {
            setCarregando(false);
        }
    }


    const ordensAbertas = useMemo(() => {
        const statusFinais = [
            "CONCLUIDA",
            "CANCELADA",
        ];

        return ordens
            .filter(
                (ordem) =>
                    ordem.ativo
                    &&
                    !statusFinais.includes(
                        ordem.status
                    )
            )
            .sort((a, b) => {
                if (!a.prazo) {
                    return 1;
                }

                if (!b.prazo) {
                    return -1;
                }

                return (
                    new Date(a.prazo)
                    -
                    new Date(b.prazo)
                );
            });

    }, [ordens]);


    function buscarNomeAtivo(ordem) {
        if (ordem.maquina_id) {
            const maquina =
                maquinas.find(
                    (item) =>
                        item.id
                        === ordem.maquina_id
                );

            if (maquina) {
                return (
                    `${maquina.fabricante} `
                    + `${maquina.modelo} · `
                    + `${maquina.identificacao}`
                );
            }
        }

        if (ordem.equipamento_id) {
            const equipamento =
                equipamentos.find(
                    (item) =>
                        item.id
                        === ordem.equipamento_id
                );

            if (equipamento) {
                return (
                    equipamento.identificacao
                    || equipamento.nome
                    || `Equipamento #${equipamento.id}`
                );
            }
        }

        return "Ativo não identificado";
    }


    function formatarPrazo(data) {
        if (!data) {
            return "Sem prazo";
        }

        return new Intl.DateTimeFormat(
            "pt-BR"
        ).format(
            new Date(data)
        );
    }


    function formatarTexto(valor) {
        if (!valor) {
            return "";
        }

        return valor
            .toLowerCase()
            .replaceAll("_", " ")
            .replace(
                /^\w/,
                (letra) =>
                    letra.toUpperCase()
            );
    }


    function classePrioridade(
        prioridade
    ) {
        switch (prioridade) {
            case "URGENTE":
                return "urgente";

            case "ALTA":
                return "alta";

            case "MEDIA":
                return "media";

            case "BAIXA":
                return "baixa";

            default:
                return "padrao";
        }
    }


    function textoAtivos() {
        if (!capacidade) {
            return "-";
        }

        return (
            `${capacidade.maquinas} ${
                capacidade.maquinas === 1
                    ? "máquina"
                    : "máquinas"
            } · ${capacidade.equipamentos} ${
                capacidade.equipamentos === 1
                    ? "equipamento"
                    : "equipamentos"
            }`
        );
    }


    function textoOperando() {
        if (!capacidade) {
            return "-";
        }

        return (
            `${capacidade.percentual_operando}% `
            + "da frota ativa"
        );
    }


    function textoManutencao() {
        if (!capacidade) {
            return "-";
        }

        return (
            `${capacidade.manutencao} em manutenção`
            + ` · ${capacidade.indisponivel} parados`
        );
    }


    return (
        <div className="home-page">

            <header className="home-header">

                <div>
                    <h1>
                        Painel de controle
                    </h1>

                    <p>
                        Visão geral da frota,
                        manutenções e ordens
                        de serviço.
                    </p>
                </div>


                <button
                    className="home-new-os"
                    onClick={() =>
                        navigate(
                            "/ordens-servico/nova"
                        )
                    }
                >
                    <i className="bi bi-plus-lg" />

                    Nova OS
                </button>

            </header>


            {erro && (
                <div className="home-error">

                    <i className="bi bi-exclamation-circle" />

                    <span>
                        {erro}
                    </span>

                    <button
                        onClick={
                            carregarDashboard
                        }
                    >
                        Tentar novamente
                    </button>

                </div>
            )}


            {carregando ? (

                <section className="dashboard-loading">

                    <div
                        className="
                            spinner-border
                            spinner-border-sm
                        "
                    />

                    <span>
                        Carregando indicadores...
                    </span>

                </section>

            ) : (

                <>
                    <section className="dashboard-cards">

                        <DashboardCard
                            titulo="Ativos totais"
                            valor={
                                capacidade
                                    ?.total_ativos
                                ?? 0
                            }
                            descricao={
                                textoAtivos()
                            }
                            icone="bi-truck-front"
                        />

                        <DashboardCard
                            titulo="Operando"
                            valor={
                                capacidade
                                    ?.operando
                                ?? 0
                            }
                            descricao={
                                textoOperando()
                            }
                            icone="bi-speedometer2"
                            variante="operando"
                        />

                        <DashboardCard
                            titulo="Em manutenção / parados"
                            valor={
                                (
                                    capacidade
                                        ?.manutencao
                                    ?? 0
                                )
                                +
                                (
                                    capacidade
                                        ?.indisponivel
                                    ?? 0
                                )
                            }
                            descricao={
                                textoManutencao()
                            }
                            icone="bi-tools"
                            variante="manutencao"
                        />

                        <DashboardCard
                            titulo="OS abertas"
                            valor={
                                ordensAbertas.length
                            }
                            descricao={
                                `${ordens.length} ${
                                    ordens.length === 1
                                        ? "ordem cadastrada"
                                        : "ordens cadastradas"
                                }`
                            }
                            icone="bi-clipboard-check"
                            variante="os"
                        />

                    </section>


                    <section className="open-orders">

                        <div className="open-orders-header">

                            <h2>
                                Ordens de serviço em aberto
                            </h2>

                            <button
                                onClick={() =>
                                    navigate(
                                        "/ordens-servico"
                                    )
                                }
                            >
                                Ver todas

                                <i className="bi bi-arrow-right" />
                            </button>

                        </div>


                        {ordensAbertas.length === 0 ? (

                            <div className="open-orders-empty">

                                <i className="bi bi-check-circle" />

                                <strong>
                                    Nenhuma OS em aberto
                                </strong>

                                <span>
                                    Não existem ordens pendentes no momento.
                                </span>

                            </div>

                        ) : (

                            <div className="open-orders-list">

                                {ordensAbertas
                                    .slice(0, 5)
                                    .map(
                                        (ordem) => (

                                            <button
                                                key={ordem.id}
                                                className="open-order-item"
                                                onClick={() =>
                                                    navigate(
                                                        `/ordens-servico/${ordem.id}`
                                                    )
                                                }
                                            >

                                                <div className="open-order-main">

                                                    <div className="open-order-top">

                                                        <span className="open-order-number">
                                                            OS #{ordem.numero}
                                                        </span>

                                                        <span
                                                            className={
                                                                `priority-badge ${
                                                                    classePrioridade(
                                                                        ordem.prioridade
                                                                    )
                                                                }`
                                                            }
                                                        >
                                                            {
                                                                formatarTexto(
                                                                    ordem.prioridade
                                                                )
                                                            }
                                                        </span>

                                                    </div>


                                                    <strong className="open-order-title">
                                                        {ordem.titulo}
                                                    </strong>


                                                    <span className="open-order-asset">
                                                        {
                                                            buscarNomeAtivo(
                                                                ordem
                                                            )
                                                        }
                                                    </span>

                                                </div>


                                                <div className="open-order-side">

                                                    <span className="status-badge">
                                                        {
                                                            formatarTexto(
                                                                ordem.status
                                                            )
                                                        }
                                                    </span>

                                                    <span className="open-order-date">
                                                        Prazo{" "}
                                                        {
                                                            formatarPrazo(
                                                                ordem.prazo
                                                            )
                                                        }
                                                    </span>

                                                </div>

                                            </button>

                                        )
                                    )}

                            </div>

                        )}

                    </section>

                </>

            )}

        </div>
    );
}


export default Home;