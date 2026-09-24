import {
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    useNavigate,
} from "react-router-dom";

import {
    criarAgendamento,
    listarAgendamentos,
} from "../../api/calendarioService";

import {
    listarOrdensServico,
} from "../../api/ordemServicoService";

import {
    listarUsuarios,
} from "../../api/usuarioService";

import AgendamentoModal
    from "../../components/AgendamentoModal/AgendamentoModal";

import "./Calendario.css";


const MESES = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
];


const DIAS_SEMANA = [
    "Dom",
    "Seg",
    "Ter",
    "Qua",
    "Qui",
    "Sex",
    "Sáb",
];


function Calendario() {
    const navigate =
        useNavigate();

    const hoje =
        new Date();

    const [mesAtual, setMesAtual] =
        useState(
            new Date(
                hoje.getFullYear(),
                hoje.getMonth(),
                1
            )
        );

    const [
        agendamentos,
        setAgendamentos,
    ] = useState([]);

    const [ordens, setOrdens] =
        useState([]);

    const [usuarios, setUsuarios] =
        useState([]);

    const [carregando, setCarregando] =
        useState(true);

    const [modalAberto, setModalAberto] =
        useState(false);

    const [salvando, setSalvando] =
        useState(false);

    const [erro, setErro] =
        useState("");

    const [
        erroFormulario,
        setErroFormulario,
    ] = useState("");


    useEffect(() => {
        carregarDados();
    }, []);


    async function carregarDados() {
        try {
            setCarregando(true);
            setErro("");

            const [
                respostaAgendamentos,
                respostaOrdens,
                respostaUsuarios,
            ] = await Promise.all([
                listarAgendamentos(),

                listarOrdensServico(),

                listarUsuarios({
                    apenasAtivos: true,
                }),
            ]);


            setAgendamentos(
                respostaAgendamentos
                    .agendamentos
                || []
            );

            setOrdens(
                respostaOrdens
                    .ordens_servico
                || []
            );

            setUsuarios(
                respostaUsuarios
                    .data
                || []
            );

        } catch (error) {
            console.error(
                "Erro ao carregar calendário:",
                error
            );

            setErro(
                error.response?.data?.message
                ||
                error.response?.data?.erro
                ||
                "Não foi possível carregar o calendário."
            );

        } finally {
            setCarregando(false);
        }
    }


    const ordensAgendaveis =
        useMemo(() => {
            return ordens.filter(
                (ordem) =>
                    ordem.ativo
                    &&
                    ordem.status
                        !== "CONCLUIDA"
                    &&
                    ordem.status
                        !== "CANCELADA"
            );
        }, [ordens]);


    function buscarOrdem(
        ordemServicoId
    ) {
        return ordens.find(
            (ordem) =>
                ordem.id
                === ordemServicoId
        );
    }


    function buscarUsuario(
        usuarioId
    ) {
        return usuarios.find(
            (usuario) =>
                usuario.id
                === usuarioId
        );
    }


    async function salvarAgendamento(
        dados
    ) {
        try {
            setSalvando(true);
            setErroFormulario("");

            await criarAgendamento(
                dados
            );

            setModalAberto(false);

            await carregarDados();

        } catch (error) {
            console.error(
                "Erro ao criar agendamento:",
                error
            );

            setErroFormulario(
                error.response?.data?.message
                ||
                "Não foi possível criar o agendamento."
            );

        } finally {
            setSalvando(false);
        }
    }


    function mesAnterior() {
        setMesAtual(
            (anterior) =>
                new Date(
                    anterior.getFullYear(),
                    anterior.getMonth() - 1,
                    1
                )
        );
    }


    function proximoMes() {
        setMesAtual(
            (anterior) =>
                new Date(
                    anterior.getFullYear(),
                    anterior.getMonth() + 1,
                    1
                )
        );
    }


    function irParaHoje() {
        setMesAtual(
            new Date(
                hoje.getFullYear(),
                hoje.getMonth(),
                1
            )
        );
    }


    function mesmoDia(
        dataA,
        dataB
    ) {
        return (
            dataA.getFullYear()
                === dataB.getFullYear()
            &&
            dataA.getMonth()
                === dataB.getMonth()
            &&
            dataA.getDate()
                === dataB.getDate()
        );
    }


    function agendamentosDoDia(
        dia
    ) {
        const inicioDia =
            new Date(
                dia.getFullYear(),
                dia.getMonth(),
                dia.getDate(),
                0,
                0,
                0
            );

        const fimDia =
            new Date(
                dia.getFullYear(),
                dia.getMonth(),
                dia.getDate(),
                23,
                59,
                59
            );


        return agendamentos.filter(
            (agendamento) => {
                if (
                    agendamento.status
                    === "CANCELADO"
                ) {
                    return false;
                }

                const inicio =
                    new Date(
                        agendamento.inicio
                    );

                const fim =
                    new Date(
                        agendamento.fim
                    );

                return (
                    inicio <= fimDia
                    &&
                    fim >= inicioDia
                );
            }
        );
    }


    function gerarDias() {
        const ano =
            mesAtual.getFullYear();

        const mes =
            mesAtual.getMonth();

        const primeiroDia =
            new Date(
                ano,
                mes,
                1
            );

        const inicio =
            new Date(
                ano,
                mes,
                1 - primeiroDia.getDay()
            );


        return Array.from(
            {
                length: 42,
            },
            (_, indice) => {
                const dia =
                    new Date(inicio);

                dia.setDate(
                    inicio.getDate()
                    + indice
                );

                return dia;
            }
        );
    }


    const dias =
        gerarDias();


    const proximos =
        useMemo(() => {
            const agora =
                new Date();

            return [...agendamentos]
                .filter(
                    (agendamento) =>
                        agendamento.status
                            !== "CANCELADO"
                        &&
                        new Date(
                            agendamento.fim
                        ) >= agora
                )
                .sort(
                    (a, b) =>
                        new Date(a.inicio)
                        -
                        new Date(b.inicio)
                )
                .slice(0, 6);

        }, [agendamentos]);


    function formatarHora(
        valor
    ) {
        return new Intl.DateTimeFormat(
            "pt-BR",
            {
                hour: "2-digit",
                minute: "2-digit",
            }
        ).format(
            new Date(valor)
        );
    }


    function formatarData(
        valor
    ) {
        return new Intl.DateTimeFormat(
            "pt-BR",
            {
                day: "2-digit",
                month: "2-digit",
            }
        ).format(
            new Date(valor)
        );
    }


    function classeStatus(
        status
    ) {
        switch (status) {
            case "AGENDADO":
                return "agendado";

            case "EM_ANDAMENTO":
                return "andamento";

            case "CONCLUIDO":
                return "concluido";

            default:
                return "";
        }
    }


    return (
        <div className="calendario-page">

            <header className="calendario-header">

                <div>
                    <h1>
                        Calendário de serviços
                    </h1>

                    <p>
                        Acompanhe serviços e
                        manutenções programadas.
                    </p>
                </div>


                <button
                    className="calendario-new"
                    onClick={() => {
                        setErroFormulario("");
                        setModalAberto(true);
                    }}
                >
                    <i className="bi bi-plus-lg" />

                    Agendar serviço
                </button>

            </header>


            {erro && (
                <div className="calendario-error">
                    {erro}
                </div>
            )}


            <div className="calendario-layout">

                <section className="calendar-card">

                    <div className="calendar-toolbar">

                        <div className="calendar-navigation">

                            <button
                                onClick={
                                    mesAnterior
                                }
                            >
                                <i className="bi bi-chevron-left" />
                            </button>


                            <h2>
                                {
                                    MESES[
                                        mesAtual.getMonth()
                                    ]
                                }{" "}
                                {
                                    mesAtual.getFullYear()
                                }
                            </h2>


                            <button
                                onClick={
                                    proximoMes
                                }
                            >
                                <i className="bi bi-chevron-right" />
                            </button>

                        </div>


                        <button
                            className="calendar-today"
                            onClick={
                                irParaHoje
                            }
                        >
                            Hoje
                        </button>

                    </div>


                    {carregando ? (

                        <div className="calendar-loading">

                            <div className="spinner-border spinner-border-sm" />

                            Carregando calendário...

                        </div>

                    ) : (

                        <div className="calendar-grid">

                            {DIAS_SEMANA.map(
                                (dia) => (
                                    <div
                                        key={dia}
                                        className="calendar-weekday"
                                    >
                                        {dia}
                                    </div>
                                )
                            )}


                            {dias.map(
                                (dia) => {

                                    const eventos =
                                        agendamentosDoDia(
                                            dia
                                        );

                                    const foraMes =
                                        dia.getMonth()
                                        !== mesAtual.getMonth();

                                    return (
                                        <div
                                            key={
                                                dia.toISOString()
                                            }
                                            className={
                                                `calendar-day ${
                                                    foraMes
                                                        ? "outside"
                                                        : ""
                                                } ${
                                                    mesmoDia(
                                                        dia,
                                                        hoje
                                                    )
                                                        ? "today"
                                                        : ""
                                                }`
                                            }
                                        >

                                            <span className="calendar-day-number">
                                                {
                                                    dia.getDate()
                                                }
                                            </span>


                                            <div className="calendar-events">

                                                {eventos
                                                    .slice(0, 3)
                                                    .map(
                                                        (agendamento) => {

                                                            const ordem =
                                                                buscarOrdem(
                                                                    agendamento.ordem_servico_id
                                                                );

                                                            return (
                                                                <button
                                                                    key={
                                                                        agendamento.id
                                                                    }
                                                                    className={
                                                                        `calendar-event ${
                                                                            classeStatus(
                                                                                agendamento.status
                                                                            )
                                                                        }`
                                                                    }
                                                                    title={
                                                                        ordem?.titulo
                                                                        || "Agendamento"
                                                                    }
                                                                    onClick={() => {
                                                                        if (ordem) {
                                                                            navigate(
                                                                                `/ordens-servico/${ordem.id}`
                                                                            );
                                                                        }
                                                                    }}
                                                                >
                                                                    <span>
                                                                        {
                                                                            formatarHora(
                                                                                agendamento.inicio
                                                                            )
                                                                        }
                                                                    </span>

                                                                    {
                                                                        ordem
                                                                            ? `OS #${ordem.numero} ${ordem.titulo}`
                                                                            : `Agendamento #${agendamento.id}`
                                                                    }
                                                                </button>
                                                            );
                                                        }
                                                    )}


                                                {
                                                    eventos.length > 3
                                                    && (
                                                        <small>
                                                            +{
                                                                eventos.length
                                                                - 3
                                                            } mais
                                                        </small>
                                                    )
                                                }

                                            </div>

                                        </div>
                                    );
                                }
                            )}

                        </div>

                    )}

                </section>


                <aside className="calendar-upcoming">

                    <div className="calendar-upcoming-header">

                        <h2>
                            Próximos serviços
                        </h2>

                        <span>
                            {
                                proximos.length
                            }
                        </span>

                    </div>


                    {proximos.length === 0 ? (

                        <div className="calendar-empty">

                            <i className="bi bi-calendar-check" />

                            <strong>
                                Nenhum serviço agendado
                            </strong>

                            <span>
                                Os próximos serviços
                                aparecerão aqui.
                            </span>

                        </div>

                    ) : (

                        <div className="calendar-upcoming-list">

                            {proximos.map(
                                (agendamento) => {

                                    const ordem =
                                        buscarOrdem(
                                            agendamento.ordem_servico_id
                                        );

                                    const responsavel =
                                        buscarUsuario(
                                            agendamento.responsavel_id
                                        );

                                    return (
                                        <button
                                            key={
                                                agendamento.id
                                            }
                                            onClick={() => {
                                                if (ordem) {
                                                    navigate(
                                                        `/ordens-servico/${ordem.id}`
                                                    );
                                                }
                                            }}
                                        >

                                            <div className="upcoming-date">

                                                <strong>
                                                    {
                                                        formatarData(
                                                            agendamento.inicio
                                                        )
                                                    }
                                                </strong>

                                                <span>
                                                    {
                                                        formatarHora(
                                                            agendamento.inicio
                                                        )
                                                    }
                                                </span>

                                            </div>


                                            <div className="upcoming-info">

                                                <strong>
                                                    {
                                                        ordem
                                                            ? `OS #${ordem.numero} · ${ordem.titulo}`
                                                            : `Agendamento #${agendamento.id}`
                                                    }
                                                </strong>

                                                <span>
                                                    {
                                                        responsavel?.nome
                                                        ||
                                                        "Sem responsável"
                                                    }
                                                </span>

                                            </div>

                                        </button>
                                    );
                                }
                            )}

                        </div>

                    )}

                </aside>

            </div>


            <AgendamentoModal
                aberto={modalAberto}
                ordens={ordensAgendaveis}
                usuarios={usuarios}
                salvando={salvando}
                erro={erroFormulario}
                onClose={() =>
                    setModalAberto(false)
                }
                onSubmit={
                    salvarAgendamento
                }
            />

        </div>
    );
}


export default Calendario;