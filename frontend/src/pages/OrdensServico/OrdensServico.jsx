import {
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    useNavigate,
} from "react-router-dom";

import {
    listarOrdensServico,
} from "../../api/ordemServicoService";

import {
    listarMaquinas,
} from "../../api/maquinaService";

import {
    listarEquipamentos,
} from "../../api/equipamentoService";

import "./OrdensServico.css";


const STATUS_FINAIS = [
    "CONCLUIDA",
    "CANCELADA",
];


function OrdensServico() {
    const navigate =
        useNavigate();

    const [ordens, setOrdens] =
        useState([]);

    const [maquinas, setMaquinas] =
        useState([]);

    const [equipamentos, setEquipamentos] =
        useState([]);

    const [busca, setBusca] =
        useState("");

    const [status, setStatus] =
        useState("TODOS");

    const [prioridade, setPrioridade] =
        useState("TODAS");

    const [tipo, setTipo] =
        useState("TODOS");

    const [carregando, setCarregando] =
        useState(true);

    const [erro, setErro] =
        useState("");


    useEffect(() => {
        carregarDados();
    }, []);


    async function carregarDados() {
        try {
            setCarregando(true);
            setErro("");

            const [
                respostaOrdens,
                respostaMaquinas,
                respostaEquipamentos,
            ] = await Promise.all([
                listarOrdensServico(),
                listarMaquinas({
                    incluirInativas: true,
                }),
                listarEquipamentos({
                    incluirInativos: true,
                }),
            ]);

            setOrdens(
                respostaOrdens
                    .ordens_servico
                || []
            );

            setMaquinas(
                respostaMaquinas.data
                || []
            );

            setEquipamentos(
                respostaEquipamentos.data
                || []
            );

        } catch (error) {
            console.error(
                "Erro ao carregar OS:",
                error
            );

            setErro(
                error.response?.data?.erro
                ||
                error.response?.data?.message
                ||
                "Não foi possível carregar as ordens de serviço."
            );

        } finally {
            setCarregando(false);
        }
    }


    function buscarAtivo(
        ordem
    ) {
        if (ordem.maquina_id) {
            const maquina =
                maquinas.find(
                    (item) =>
                        item.id
                        === ordem.maquina_id
                );

            if (!maquina) {
                return {
                    nome:
                        `Máquina #${ordem.maquina_id}`,
                    detalhe: "",
                    tipo: "Máquina",
                };
            }

            return {
                nome:
                    maquina.identificacao,

                detalhe:
                    `${maquina.fabricante} ${maquina.modelo}`,

                tipo:
                    "Máquina",
            };
        }


        if (ordem.equipamento_id) {
            const equipamento =
                equipamentos.find(
                    (item) =>
                        item.id
                        === ordem.equipamento_id
                );

            if (!equipamento) {
                return {
                    nome:
                        `Equipamento #${ordem.equipamento_id}`,
                    detalhe: "",
                    tipo: "Equipamento",
                };
            }

            return {
                nome:
                    equipamento.identificacao,

                detalhe:
                    equipamento.nome,

                tipo:
                    "Equipamento",
            };
        }


        return {
            nome:
                "Ativo não identificado",

            detalhe: "",

            tipo: "-",
        };
    }


    function formatarTexto(
        valor
    ) {
        if (!valor) {
            return "-";
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


    function formatarData(
        valor
    ) {
        if (!valor) {
            return "Sem prazo";
        }

        return new Intl.DateTimeFormat(
            "pt-BR"
        ).format(
            new Date(valor)
        );
    }


    function classeStatus(
        valor
    ) {
        switch (valor) {
            case "ABERTA":
                return "aberta";

            case "EM_ANDAMENTO":
                return "andamento";

            case "CONCLUIDA":
                return "concluida";

            case "CANCELADA":
                return "cancelada";

            default:
                return "";
        }
    }


    function classePrioridade(
        valor
    ) {
        switch (valor) {
            case "URGENTE":
                return "urgente";

            case "ALTA":
                return "alta";

            case "MEDIA":
                return "media";

            case "BAIXA":
                return "baixa";

            default:
                return "";
        }
    }


    const ordensFiltradas =
        useMemo(() => {
            const termo =
                busca
                    .trim()
                    .toLowerCase();

            return ordens.filter(
                (ordem) => {

                    const ativo =
                        buscarAtivo(
                            ordem
                        );


                    const correspondeBusca =
                        !termo
                        ||
                        ordem.titulo
                            ?.toLowerCase()
                            .includes(termo)
                        ||
                        String(
                            ordem.numero
                        ).includes(termo)
                        ||
                        ativo.nome
                            ?.toLowerCase()
                            .includes(termo)
                        ||
                        ativo.detalhe
                            ?.toLowerCase()
                            .includes(termo);


                    const correspondeStatus =
                        status === "TODOS"
                        ||
                        ordem.status
                            === status;


                    const correspondePrioridade =
                        prioridade
                            === "TODAS"
                        ||
                        ordem.prioridade
                            === prioridade;


                    const correspondeTipo =
                        tipo === "TODOS"
                        ||
                        ordem.tipo
                            === tipo;


                    return (
                        correspondeBusca
                        &&
                        correspondeStatus
                        &&
                        correspondePrioridade
                        &&
                        correspondeTipo
                    );
                }
            );

        }, [
            ordens,
            maquinas,
            equipamentos,
            busca,
            status,
            prioridade,
            tipo,
        ]);


    const quantidadeAbertas =
        ordens.filter(
            (ordem) =>
                !STATUS_FINAIS.includes(
                    ordem.status
                )
        ).length;


    return (
        <div className="os-page">

            <header className="os-header">

                <div>
                    <h1>
                        Ordens de serviço
                    </h1>

                    <p>
                        Gerencie serviços,
                        manutenções e atividades
                        da frota.
                    </p>
                </div>


                <button
                    className="os-new"
                    type="button"
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


            <section className="os-summary">

                <div>
                    <span>
                        Total
                    </span>

                    <strong>
                        {ordens.length}
                    </strong>
                </div>


                <div>
                    <span>
                        Em aberto
                    </span>

                    <strong>
                        {
                            quantidadeAbertas
                        }
                    </strong>
                </div>


                <div>
                    <span>
                        Concluídas
                    </span>

                    <strong>
                        {
                            ordens.filter(
                                (ordem) =>
                                    ordem.status
                                    === "CONCLUIDA"
                            ).length
                        }
                    </strong>
                </div>


                <div>
                    <span>
                        Canceladas
                    </span>

                    <strong>
                        {
                            ordens.filter(
                                (ordem) =>
                                    ordem.status
                                    === "CANCELADA"
                            ).length
                        }
                    </strong>
                </div>

            </section>


            <section className="os-filters">

                <div className="os-search">

                    <i className="bi bi-search" />

                    <input
                        type="text"
                        value={busca}
                        onChange={
                            (event) =>
                                setBusca(
                                    event.target.value
                                )
                        }
                        placeholder="Buscar por OS, título ou ativo..."
                    />

                </div>


                <select
                    value={status}
                    onChange={
                        (event) =>
                            setStatus(
                                event.target.value
                            )
                    }
                >
                    <option value="TODOS">
                        Todos os status
                    </option>

                    <option value="ABERTA">
                        Aberta
                    </option>

                    <option value="EM_ANDAMENTO">
                        Em andamento
                    </option>

                    <option value="CONCLUIDA">
                        Concluída
                    </option>

                    <option value="CANCELADA">
                        Cancelada
                    </option>
                </select>


                <select
                    value={prioridade}
                    onChange={
                        (event) =>
                            setPrioridade(
                                event.target.value
                            )
                    }
                >
                    <option value="TODAS">
                        Prioridades
                    </option>

                    <option value="BAIXA">
                        Baixa
                    </option>

                    <option value="MEDIA">
                        Média
                    </option>

                    <option value="ALTA">
                        Alta
                    </option>

                    <option value="URGENTE">
                        Urgente
                    </option>
                </select>


                <select
                    value={tipo}
                    onChange={
                        (event) =>
                            setTipo(
                                event.target.value
                            )
                    }
                >
                    <option value="TODOS">
                        Todos os tipos
                    </option>

                    <option value="SERVICO">
                        Serviço
                    </option>

                    <option value="MANUTENCAO">
                        Manutenção
                    </option>
                </select>

            </section>


            {erro && (
                <div className="os-error">

                    <i className="bi bi-exclamation-circle" />

                    <span>
                        {erro}
                    </span>

                    <button
                        onClick={
                            carregarDados
                        }
                    >
                        Tentar novamente
                    </button>

                </div>
            )}


            <section className="os-card">

                <div className="os-card-header">

                    <div>
                        <h2>
                            Ordens cadastradas
                        </h2>

                        <span>
                            {
                                ordensFiltradas
                                    .length
                            }{" "}
                            {
                                ordensFiltradas
                                    .length === 1
                                    ? "ordem encontrada"
                                    : "ordens encontradas"
                            }
                        </span>
                    </div>

                </div>


                {carregando ? (

                    <div className="os-state">

                        <div className="spinner-border spinner-border-sm" />

                        <span>
                            Carregando ordens...
                        </span>

                    </div>

                ) : ordensFiltradas.length === 0 ? (

                    <div className="os-state">

                        <i className="bi bi-clipboard-check" />

                        <strong>
                            Nenhuma ordem encontrada
                        </strong>

                        <span>
                            Ajuste os filtros ou
                            crie uma nova ordem.
                        </span>

                    </div>

                ) : (

                    <div className="os-table-wrapper">

                        <table className="os-table">

                            <thead>
                                <tr>
                                    <th>OS</th>
                                    <th>Ativo</th>
                                    <th>Tipo</th>
                                    <th>Prioridade</th>
                                    <th>Status</th>
                                    <th>Prazo</th>
                                    <th />
                                </tr>
                            </thead>


                            <tbody>

                                {ordensFiltradas.map(
                                    (ordem) => {

                                        const ativo =
                                            buscarAtivo(
                                                ordem
                                            );

                                        return (
                                            <tr
                                                key={
                                                    ordem.id
                                                }
                                                onClick={() =>
                                                    navigate(
                                                        `/ordens-servico/${ordem.id}`
                                                    )
                                                }
                                            >

                                                <td>
                                                    <div className="os-info">

                                                        <span className="os-number">
                                                            OS #{ordem.numero}
                                                        </span>

                                                        <strong>
                                                            {
                                                                ordem.titulo
                                                            }
                                                        </strong>

                                                    </div>
                                                </td>


                                                <td>
                                                    <div className="os-asset">

                                                        <strong>
                                                            {
                                                                ativo.nome
                                                            }
                                                        </strong>

                                                        <span>
                                                            {
                                                                ativo.detalhe
                                                            }
                                                        </span>

                                                    </div>
                                                </td>


                                                <td>
                                                    {
                                                        formatarTexto(
                                                            ordem.tipo
                                                        )
                                                    }
                                                </td>


                                                <td>
                                                    <span
                                                        className={
                                                            `os-priority ${
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
                                                </td>


                                                <td>
                                                    <span
                                                        className={
                                                            `os-status ${
                                                                classeStatus(
                                                                    ordem.status
                                                                )
                                                            }`
                                                        }
                                                    >
                                                        {
                                                            formatarTexto(
                                                                ordem.status
                                                            )
                                                        }
                                                    </span>
                                                </td>


                                                <td>
                                                    <span className="os-deadline">
                                                        {
                                                            formatarData(
                                                                ordem.prazo
                                                            )
                                                        }
                                                    </span>
                                                </td>


                                                <td>
                                                    <i className="bi bi-chevron-right os-chevron" />
                                                </td>

                                            </tr>
                                        );
                                    }
                                )}

                            </tbody>

                        </table>

                    </div>

                )}

            </section>

        </div>
    );
}


export default OrdensServico;