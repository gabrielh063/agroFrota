import {
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    ativarMaquina,
    atualizarMaquina,
    criarMaquina,
    desativarMaquina,
    listarMaquinas,
} from "../../api/maquinaService";

import MaquinaFormModal
    from "../../components/MaquinaFormModal/MaquinaFormModal";

import "./Maquinarios.css";


function Maquinarios() {
    const [maquinas, setMaquinas] =
        useState([]);

    const [busca, setBusca] =
        useState("");

    const [status, setStatus] =
        useState("TODOS");

    const [situacao, setSituacao] =
        useState("ATIVAS");

    const [carregando, setCarregando] =
        useState(true);

    const [erro, setErro] =
        useState("");

    const [mensagem, setMensagem] =
        useState("");

    const [
        modalAberto,
        setModalAberto,
    ] = useState(false);

    const [
        maquinaEditando,
        setMaquinaEditando,
    ] = useState(null);

    const [
        salvando,
        setSalvando,
    ] = useState(false);

    const [
        erroFormulario,
        setErroFormulario,
    ] = useState("");

    const [
        menuAberto,
        setMenuAberto,
    ] = useState(null);


    useEffect(() => {
        carregarMaquinas();
    }, []);


    async function carregarMaquinas() {
        try {
            setCarregando(true);
            setErro("");

            const resposta =
                await listarMaquinas({
                incluirInativas: true,
                });

            setMaquinas(
                resposta.data || []
            );

        } catch (error) {
            console.error(
                "Erro ao listar máquinas:",
                error
            );

            setErro(
                error.response?.data?.message
                || "Não foi possível carregar os maquinários."
            );

        } finally {
            setCarregando(false);
        }
    }


    function abrirCadastro() {
        setMaquinaEditando(null);
        setErroFormulario("");
        setModalAberto(true);
    }


    function abrirEdicao(
        maquina
    ) {
        setMaquinaEditando(
            maquina
        );

        setErroFormulario("");
        setMenuAberto(null);
        setModalAberto(true);
    }


    function fecharModal() {
        if (salvando) {
            return;
        }

        setModalAberto(false);
        setMaquinaEditando(null);
        setErroFormulario("");
    }


    async function salvarMaquina(
        dados
    ) {
        try {
            setSalvando(true);
            setErroFormulario("");

            let resposta;

            if (maquinaEditando) {
                resposta =
                    await atualizarMaquina(
                        maquinaEditando.id,
                        dados
                    );

            } else {
                resposta =
                    await criarMaquina(
                        dados
                    );
            }

            fecharModal();

            setMensagem(
                resposta.message
            );

            await carregarMaquinas();

            setTimeout(
                () =>
                    setMensagem(""),
                3000
            );

        } catch (error) {
            console.error(
                "Erro ao salvar máquina:",
                error
            );

            setErroFormulario(
                error.response?.data?.message
                || "Não foi possível salvar o maquinário."
            );

        } finally {
            setSalvando(false);
        }
    }


    async function alterarSituacao(
        maquina
    ) {
        setMenuAberto(null);

        if (maquina.ativo) {
            const confirmar =
                window.confirm(
                    `Deseja desativar o maquinário "${maquina.identificacao}"?`
                );

            if (!confirmar) {
                return;
            }
        }

        try {
            setErro("");

            const resposta =
                maquina.ativo
                    ? await desativarMaquina(
                        maquina.id
                    )
                    : await ativarMaquina(
                        maquina.id
                    );

            setMensagem(
                resposta.message
            );

            await carregarMaquinas();

            setTimeout(
                () =>
                    setMensagem(""),
                3000
            );

        } catch (error) {
            console.error(
                "Erro ao alterar situação:",
                error
            );

            setErro(
                error.response?.data?.message
                || "Não foi possível alterar a situação do maquinário."
            );
        }
    }


    const statusDisponiveis = useMemo(
        () => [
            "OPERANDO",
            "PARADA",
            "MANUTENCAO",
            "INATIVA",
        ],
        []
    );


    const maquinasFiltradas = useMemo(
        () => {
            const termo =
                busca
                    .trim()
                    .toLowerCase();

            return maquinas.filter(
                (maquina) => {
                    const correspondeBusca =
                        !termo
                        ||
                        maquina.identificacao
                            ?.toLowerCase()
                            .includes(termo)
                        ||
                        maquina.fabricante
                            ?.toLowerCase()
                            .includes(termo)
                        ||
                        maquina.modelo
                            ?.toLowerCase()
                            .includes(termo)
                        ||
                        maquina.localizacao
                            ?.toLowerCase()
                            .includes(termo);


                    const correspondeStatus =
                        status === "TODOS"
                        ||
                        maquina.status
                            === status;


                    let correspondeSituacao =
                        true;

                    if (
                        situacao
                        === "ATIVAS"
                    ) {
                        correspondeSituacao =
                            maquina.ativo;
                    }

                    if (
                        situacao
                        === "INATIVAS"
                    ) {
                        correspondeSituacao =
                            !maquina.ativo;
                    }


                    return (
                        correspondeBusca
                        &&
                        correspondeStatus
                        &&
                        correspondeSituacao
                    );
                }
            );
        },
        [
            maquinas,
            busca,
            status,
            situacao,
        ]
    );


    function formatarStatus(
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


    function classeStatus(
        valor
    ) {
        switch (valor) {
            case "OPERANDO":
                return "operando";

            case "MANUTENCAO":
                return "manutencao";

            case "PARADA":
                return "indisponivel";

            case "INATIVA":
                return "inativa";

            default:
                return "neutro";
        }
    }


    return (
        <div className="maquinarios-page">

            <header className="maquinarios-header">

                <div>
                    <h1>
                        Maquinários
                    </h1>

                    <p>
                        Gerencie os maquinários
                        cadastrados na frota.
                    </p>
                </div>


                <button
                    className="maquinarios-new"
                    type="button"
                    onClick={abrirCadastro}
                >
                    <i className="bi bi-plus-lg" />

                    Novo maquinário
                </button>

            </header>


            {mensagem && (
                <div className="maquinarios-success">

                    <i className="bi bi-check-circle" />

                    {mensagem}

                </div>
            )}


            <section className="maquinarios-filters">

                <div className="maquinarios-search">

                    <i className="bi bi-search" />

                    <input
                        type="text"
                        placeholder="Buscar por identificação, fabricante, modelo..."
                        value={busca}
                        onChange={
                            (event) =>
                                setBusca(
                                    event.target.value
                                )
                        }
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

                    {statusDisponiveis.map(
                        (item) => (
                            <option
                                key={item}
                                value={item}
                            >
                                {
                                    formatarStatus(
                                        item
                                    )
                                }
                            </option>
                        )
                    )}

                </select>


                <select
                    value={situacao}
                    onChange={
                        (event) =>
                            setSituacao(
                                event.target.value
                            )
                    }
                >
                    <option value="ATIVAS">
                        Ativos
                    </option>

                    <option value="INATIVAS">
                        Inativos
                    </option>

                    <option value="TODAS">
                        Todos
                    </option>
                </select>

            </section>


            {erro && (
                <div className="maquinarios-error">

                    <i className="bi bi-exclamation-circle" />

                    <span>
                        {erro}
                    </span>

                    <button
                        onClick={
                            carregarMaquinas
                        }
                    >
                        Tentar novamente
                    </button>

                </div>
            )}


            <section className="maquinarios-card">

                <div className="maquinarios-card-header">

                    <div>
                        <h2>
                            Frota cadastrada
                        </h2>

                        <span>
                            {
                                maquinasFiltradas
                                    .length
                            }{" "}
                            {
                                maquinasFiltradas
                                    .length === 1
                                    ? "maquinário encontrado"
                                    : "maquinários encontrados"
                            }
                        </span>
                    </div>

                </div>


                {carregando ? (

                    <div className="maquinarios-state">

                        <div className="spinner-border spinner-border-sm" />

                        <span>
                            Carregando maquinários...
                        </span>

                    </div>

                ) : maquinasFiltradas.length === 0 ? (

                    <div className="maquinarios-state">

                        <i className="bi bi-truck-front" />

                        <strong>
                            Nenhum maquinário encontrado
                        </strong>

                        <span>
                            Ajuste os filtros ou
                            cadastre um novo maquinário.
                        </span>

                    </div>

                ) : (

                    <div className="maquinarios-table-wrapper">

                        <table className="maquinarios-table">

                            <thead>
                                <tr>
                                    <th>Maquinário</th>
                                    <th>Ano</th>
                                    <th>Localização</th>
                                    <th>Status</th>
                                    <th>Telemetria</th>
                                    <th>Situação</th>
                                    <th />
                                </tr>
                            </thead>


                            <tbody>

                                {maquinasFiltradas.map(
                                    (maquina) => (

                                        <tr
                                            key={
                                                maquina.id
                                            }
                                        >

                                            <td>
                                                <div className="maquina-identificacao">

                                                    <div className="maquina-icon">
                                                        <i className="bi bi-truck-front" />
                                                    </div>

                                                    <div>
                                                        <strong>
                                                            {
                                                                maquina.identificacao
                                                            }
                                                        </strong>

                                                        <span>
                                                            {
                                                                maquina.fabricante
                                                            }{" "}
                                                            {
                                                                maquina.modelo
                                                            }
                                                        </span>
                                                    </div>

                                                </div>
                                            </td>


                                            <td>
                                                {
                                                    maquina.ano
                                                    || "-"
                                                }
                                            </td>


                                            <td>
                                                {
                                                    maquina.localizacao
                                                    || "-"
                                                }
                                            </td>


                                            <td>
                                                <span
                                                    className={
                                                        `maquina-status ${
                                                            classeStatus(
                                                                maquina.status
                                                            )
                                                        }`
                                                    }
                                                >
                                                    {
                                                        formatarStatus(
                                                            maquina.status
                                                        )
                                                    }
                                                </span>
                                            </td>


                                            <td>
                                                <span
                                                    className={
                                                        maquina.controla_telemetria
                                                            ? "telemetria ativa"
                                                            : "telemetria"
                                                    }
                                                >
                                                    <i
                                                        className={
                                                            maquina.controla_telemetria
                                                                ? "bi bi-broadcast"
                                                                : "bi bi-broadcast-pin"
                                                        }
                                                    />

                                                    {
                                                        maquina.controla_telemetria
                                                            ? "Sim"
                                                            : "Não"
                                                    }
                                                </span>
                                            </td>


                                            <td>
                                                <span
                                                    className={
                                                        maquina.ativo
                                                            ? "situacao ativo"
                                                            : "situacao inativo"
                                                    }
                                                >
                                                    {
                                                        maquina.ativo
                                                            ? "Ativo"
                                                            : "Inativo"
                                                    }
                                                </span>
                                            </td>


                                            <td className="actions-cell">

                                                <button
                                                    className="maquina-actions"
                                                    type="button"
                                                    title="Ações"
                                                    onClick={() =>
                                                        setMenuAberto(
                                                            menuAberto
                                                                === maquina.id
                                                                ? null
                                                                : maquina.id
                                                        )
                                                    }
                                                >
                                                    <i className="bi bi-three-dots" />
                                                </button>


                                                {
                                                    menuAberto
                                                    === maquina.id
                                                    && (
                                                        <div className="maquina-action-menu">

                                                            <button
                                                                type="button"
                                                                onClick={() =>
                                                                    abrirEdicao(
                                                                        maquina
                                                                    )
                                                                }
                                                            >
                                                                <i className="bi bi-pencil" />

                                                                Editar
                                                            </button>


                                                            <button
                                                                type="button"
                                                                className={
                                                                    maquina.ativo
                                                                        ? "danger"
                                                                        : ""
                                                                }
                                                                onClick={() =>
                                                                    alterarSituacao(
                                                                        maquina
                                                                    )
                                                                }
                                                            >
                                                                <i
                                                                    className={
                                                                        maquina.ativo
                                                                            ? "bi bi-slash-circle"
                                                                            : "bi bi-check-circle"
                                                                    }
                                                                />

                                                                {
                                                                    maquina.ativo
                                                                        ? "Desativar"
                                                                        : "Ativar"
                                                                }
                                                            </button>

                                                        </div>
                                                    )
                                                }

                                            </td>

                                        </tr>

                                    )
                                )}

                            </tbody>

                        </table>

                    </div>

                )}

            </section>


            <MaquinaFormModal
                aberto={modalAberto}
                maquina={maquinaEditando}
                salvando={salvando}
                erro={erroFormulario}
                onClose={fecharModal}
                onSubmit={salvarMaquina}
            />

        </div>
    );
}


export default Maquinarios;