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
import { useAuth } from "../../contexts/AuthContext";


function Maquinarios() {
    const { pode } = useAuth();
    const podeCriar = pode("MAQUINA_CRIAR");
    const podeEditar = pode("MAQUINA_EDITAR");
    const podeDesativar = pode("MAQUINA_DESATIVAR");
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

    const maquinasAtivas = maquinas.filter((maquina) => maquina.ativo);
    const maquinasOperando = maquinasAtivas.filter((maquina) => maquina.status === "OPERANDO").length;
    const maquinasAtencao = maquinasAtivas.filter((maquina) => ["MANUTENCAO", "PARADA"].includes(maquina.status)).length;


    return (
        <div className="maquinarios-page">

            <header className="maquinarios-header">

                <div className="maquinarios-heading-copy">
                    <span className="maquinarios-eyebrow"><i className="bi bi-truck-front" /> GESTÃO DE ATIVOS</span>
                    <div className="maquinarios-title-row">
                        <h1>Maquinários</h1>
                        <span className="maquinarios-total"><strong>{carregando ? "—" : maquinas.length}</strong> cadastrados</span>
                    </div>
                    <p>Consulte a frota, acompanhe a condição dos ativos e mantenha os cadastros atualizados.</p>
                </div>


                {podeCriar && <button
                    className="maquinarios-new"
                    type="button"
                    onClick={abrirCadastro}
                >
                    <i className="bi bi-plus-lg" />

                    Novo maquinário
                </button>}

            </header>

            {!carregando && !erro && <section className="maquinarios-summary" aria-label="Resumo da frota">
                <div className="maquinarios-summary-item"><span className="summary-icon"><i className="bi bi-truck-front" /></span><span><small>Ativos na frota</small><strong>{maquinasAtivas.length}</strong></span></div>
                <div className="maquinarios-summary-item"><span className="summary-icon summary-operando"><i className="bi bi-check2-circle" /></span><span><small>Em operação</small><strong>{maquinasOperando}</strong></span></div>
                <div className="maquinarios-summary-item"><span className="summary-icon summary-atencao"><i className="bi bi-wrench-adjustable" /></span><span><small>Precisam de atenção</small><strong>{maquinasAtencao}</strong></span></div>
            </section>}


            {mensagem && (
                <div className="maquinarios-success">

                    <i className="bi bi-check-circle" />

                    {mensagem}

                </div>
            )}


            <section className="maquinarios-filters" aria-label="Filtros de maquinários">

                <div className="maquinarios-search">

                    <i className="bi bi-search" />

                    <input
                        type="text"
                        aria-label="Buscar maquinários"
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


                <label className="maquinarios-select"><span>Status operacional</span><select
                    aria-label="Filtrar por status operacional"
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

                </select></label>


                <label className="maquinarios-select"><span>Situação do cadastro</span><select
                    aria-label="Filtrar por situação do cadastro"
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
                </select></label>

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
                                    <th scope="col">Maquinário</th>
                                    <th scope="col">Ano</th>
                                    <th scope="col">Localização</th>
                                    <th scope="col">Status</th>
                                    <th scope="col">Telemetria</th>
                                    <th scope="col">Cadastro</th>
                                    <th scope="col"><span className="visually-hidden">Ações</span></th>
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

                                            <td data-label="Maquinário">
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

                                                        <span className="maquina-modelo">
                                                            {
                                                                maquina.fabricante
                                                            }{" "}
                                                            {
                                                                maquina.modelo
                                                            }
                                                        </span>
                                                        <small className={`maquina-categoria ${maquina.categoria ? "" : "sem-categoria"}`}>
                                                            <i className="bi bi-tag" /> {maquina.categoria || "Categoria não definida"}
                                                        </small>
                                                    </div>

                                                </div>
                                            </td>


                                            <td data-label="Ano">
                                                {
                                                    maquina.ano
                                                    || "-"
                                                }
                                            </td>


                                            <td data-label="Localização">
                                                {
                                                    maquina.localizacao
                                                    || "-"
                                                }
                                            </td>


                                            <td data-label="Status">
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


                                            <td data-label="Telemetria">
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


                                            <td data-label="Cadastro">
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

                                                {(podeEditar || podeDesativar) && <button
                                                    className="maquina-actions"
                                                    type="button"
                                                    aria-label={`Ações de ${maquina.identificacao}`}
                                                    aria-haspopup="menu"
                                                    aria-expanded={menuAberto === maquina.id}
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
                                                </button>}


                                                {
                                                    menuAberto
                                                    === maquina.id
                                                    && (
                                                        <div className="maquina-action-menu" role="menu">

                                                            {podeEditar && <button
                                                                type="button"
                                                                role="menuitem"
                                                                onClick={() =>
                                                                    abrirEdicao(
                                                                        maquina
                                                                    )
                                                                }
                                                            >
                                                                <i className="bi bi-pencil" />

                                                                Editar
                                                            </button>}


                                                            {podeDesativar && <button
                                                                type="button"
                                                                role="menuitem"
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
                                                            </button>}

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
