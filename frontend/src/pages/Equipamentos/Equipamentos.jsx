import {
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    ativarEquipamento,
    atualizarEquipamento,
    criarEquipamento,
    desativarEquipamento,
    listarEquipamentos,
} from "../../api/equipamentoService";

import EquipamentoFormModal
    from "../../components/EquipamentoFormModal/EquipamentoFormModal";

import "./Equipamentos.css";


function Equipamentos() {
    const [equipamentos, setEquipamentos] =
        useState([]);

    const [busca, setBusca] =
        useState("");

    const [status, setStatus] =
        useState("TODOS");

    const [situacao, setSituacao] =
        useState("ATIVOS");

    const [carregando, setCarregando] =
        useState(true);

    const [erro, setErro] =
        useState("");

    const [mensagem, setMensagem] =
        useState("");

    const [modalAberto, setModalAberto] =
        useState(false);

    const [
        equipamentoEditando,
        setEquipamentoEditando,
    ] = useState(null);

    const [salvando, setSalvando] =
        useState(false);

    const [
        erroFormulario,
        setErroFormulario,
    ] = useState("");

    const [menuAberto, setMenuAberto] =
        useState(null);


    useEffect(() => {
        carregarEquipamentos();
    }, []);


    async function carregarEquipamentos() {
        try {
            setCarregando(true);
            setErro("");

            const resposta =
                await listarEquipamentos({
                    incluirInativos: true,
                });

            setEquipamentos(
                resposta.data || []
            );

        } catch (error) {
            console.error(
                "Erro ao carregar equipamentos:",
                error
            );

            setErro(
                error.response?.data?.message
                || "Não foi possível carregar os equipamentos."
            );

        } finally {
            setCarregando(false);
        }
    }


    function abrirCadastro() {
        setEquipamentoEditando(null);
        setErroFormulario("");
        setModalAberto(true);
    }


    function abrirEdicao(
        equipamento
    ) {
        setEquipamentoEditando(
            equipamento
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
        setEquipamentoEditando(null);
        setErroFormulario("");
    }


    async function salvarEquipamento(
        dados
    ) {
        try {
            setSalvando(true);
            setErroFormulario("");

            let resposta;

            if (equipamentoEditando) {
                resposta =
                    await atualizarEquipamento(
                        equipamentoEditando.id,
                        dados
                    );

            } else {
                resposta =
                    await criarEquipamento(
                        dados
                    );
            }

            setModalAberto(false);
            setEquipamentoEditando(null);

            setMensagem(
                resposta.message
            );

            await carregarEquipamentos();

            setTimeout(
                () =>
                    setMensagem(""),
                3000
            );

        } catch (error) {
            console.error(
                "Erro ao salvar equipamento:",
                error
            );

            setErroFormulario(
                error.response?.data?.message
                || "Não foi possível salvar o equipamento."
            );

        } finally {
            setSalvando(false);
        }
    }


    async function alterarSituacao(
        equipamento
    ) {
        setMenuAberto(null);

        if (equipamento.ativo) {
            const confirmar =
                window.confirm(
                    `Deseja desativar "${equipamento.identificacao}"?`
                );

            if (!confirmar) {
                return;
            }
        }

        try {
            const resposta =
                equipamento.ativo
                    ? await desativarEquipamento(
                        equipamento.id
                    )
                    : await ativarEquipamento(
                        equipamento.id
                    );

            setMensagem(
                resposta.message
            );

            await carregarEquipamentos();

            setTimeout(
                () =>
                    setMensagem(""),
                3000
            );

        } catch (error) {
            setErro(
                error.response?.data?.message
                || "Não foi possível alterar o equipamento."
            );
        }
    }


    const equipamentosFiltrados =
        useMemo(() => {
            const termo =
                busca
                    .trim()
                    .toLowerCase();

            return equipamentos.filter(
                (equipamento) => {

                    const correspondeBusca =
                        !termo
                        ||
                        equipamento.identificacao
                            ?.toLowerCase()
                            .includes(termo)
                        ||
                        equipamento.nome
                            ?.toLowerCase()
                            .includes(termo)
                        ||
                        equipamento.tipo
                            ?.toLowerCase()
                            .includes(termo)
                        ||
                        equipamento.fabricante
                            ?.toLowerCase()
                            .includes(termo)
                        ||
                        equipamento.modelo
                            ?.toLowerCase()
                            .includes(termo);


                    const correspondeStatus =
                        status === "TODOS"
                        ||
                        equipamento.status
                            === status;


                    let correspondeSituacao =
                        true;

                    if (
                        situacao
                        === "ATIVOS"
                    ) {
                        correspondeSituacao =
                            equipamento.ativo;
                    }

                    if (
                        situacao
                        === "INATIVOS"
                    ) {
                        correspondeSituacao =
                            !equipamento.ativo;
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

        }, [
            equipamentos,
            busca,
            status,
            situacao,
        ]);


    function formatarStatus(
        valor
    ) {
        return valor
            ?.toLowerCase()
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
            case "DISPONIVEL":
                return "disponivel";

            case "EM_USO":
                return "em-uso";

            case "MANUTENCAO":
                return "manutencao";

            case "INATIVO":
                return "inativo";

            default:
                return "neutro";
        }
    }


    return (
        <div className="equipamentos-page">

            <header className="equipamentos-header">

                <div>
                    <h1>
                        Equipamentos
                    </h1>

                    <p>
                        Gerencie implementos e
                        equipamentos da frota.
                    </p>
                </div>


                <button
                    className="equipamentos-new"
                    onClick={abrirCadastro}
                >
                    <i className="bi bi-plus-lg" />

                    Novo equipamento
                </button>

            </header>


            {mensagem && (
                <div className="equipamentos-success">

                    <i className="bi bi-check-circle" />

                    {mensagem}

                </div>
            )}


            <section className="equipamentos-filters">

                <div className="equipamentos-search">

                    <i className="bi bi-search" />

                    <input
                        aria-label="Buscar equipamento"
                        value={busca}
                        onChange={(event) =>
                            setBusca(
                                event.target.value
                            )
                        }
                        placeholder="Buscar equipamento..."
                    />

                </div>


                <select
                    aria-label={`${({ TODOS: "Todos os status", DISPONIVEL: "Disponível", EM_USO: "Em uso", MANUTENCAO: "Manutenção", INATIVO: "Inativo" })[status]}, filtro de equipamentos`}
                    value={status}
                    onChange={(event) =>
                        setStatus(
                            event.target.value
                        )
                    }
                >
                    <option value="TODOS">
                        Todos os status
                    </option>

                    <option value="DISPONIVEL">
                        Disponível
                    </option>

                    <option value="EM_USO">
                        Em uso
                    </option>

                    <option value="MANUTENCAO">
                        Manutenção
                    </option>

                    <option value="INATIVO">
                        Inativo
                    </option>
                </select>


                <select
                    aria-label={`${({ ATIVOS: "Ativos", INATIVOS: "Inativos", TODOS: "Todos" })[situacao]}, filtro de situação`}
                    value={situacao}
                    onChange={(event) =>
                        setSituacao(
                            event.target.value
                        )
                    }
                >
                    <option value="ATIVOS">
                        Ativos
                    </option>

                    <option value="INATIVOS">
                        Inativos
                    </option>

                    <option value="TODOS">
                        Todos
                    </option>
                </select>

            </section>


            {erro && (
                <div className="equipamentos-error" role="alert">
                    {erro}
                </div>
            )}


            <section className="equipamentos-card">

                <div className="equipamentos-card-header">

                    <div>
                        <h2>
                            Equipamentos cadastrados
                        </h2>

                        <span>
                            {
                                equipamentosFiltrados
                                    .length
                            }{" "}
                            {
                                equipamentosFiltrados
                                    .length === 1
                                    ? "equipamento encontrado"
                                    : "equipamentos encontrados"
                            }
                        </span>
                    </div>

                </div>


                {carregando ? (

                    <div className="equipamentos-state">
                        Carregando equipamentos...
                    </div>

                ) : equipamentosFiltrados.length === 0 ? (

                    <div className="equipamentos-state">

                        <i className="bi bi-tools" />

                        <strong>
                            Nenhum equipamento encontrado
                        </strong>

                    </div>

                ) : (

                    <div className="equipamentos-table-wrapper" role="region" aria-label="Tabela de equipamentos" tabIndex={0}>

                        <table className="equipamentos-table">

                            <thead>
                                <tr>
                                    <th>Equipamento</th>
                                    <th>Tipo</th>
                                    <th>Ano</th>
                                    <th>Localização</th>
                                    <th>Status</th>
                                    <th>Situação</th>
                                    <th scope="col">Ações</th>
                                </tr>
                            </thead>


                            <tbody>

                                {equipamentosFiltrados.map(
                                    (equipamento) => (

                                        <tr
                                            key={
                                                equipamento.id
                                            }
                                        >

                                            <td>
                                                <div className="equipamento-info">

                                                    <div className="equipamento-icon">
                                                        <i className="bi bi-tools" />
                                                    </div>

                                                    <div>
                                                        <strong>
                                                            {
                                                                equipamento.identificacao
                                                            }
                                                        </strong>

                                                        <span>
                                                            {
                                                                equipamento.nome
                                                            }
                                                        </span>

                                                        <small>
                                                            {
                                                                [
                                                                    equipamento.fabricante,
                                                                    equipamento.modelo,
                                                                ]
                                                                    .filter(Boolean)
                                                                    .join(" ")
                                                            }
                                                        </small>
                                                    </div>

                                                </div>
                                            </td>


                                            <td>
                                                {equipamento.tipo}
                                            </td>


                                            <td>
                                                {equipamento.ano || "-"}
                                            </td>


                                            <td>
                                                {
                                                    equipamento.localizacao
                                                    || "-"
                                                }
                                            </td>


                                            <td>
                                                <span
                                                    className={
                                                        `equipamento-status ${
                                                            classeStatus(
                                                                equipamento.status
                                                            )
                                                        }`
                                                    }
                                                >
                                                    {
                                                        formatarStatus(
                                                            equipamento.status
                                                        )
                                                    }
                                                </span>
                                            </td>


                                            <td>
                                                <span
                                                    className={
                                                        equipamento.ativo
                                                            ? "equipamento-situacao ativo"
                                                            : "equipamento-situacao inativo"
                                                    }
                                                >
                                                    {
                                                        equipamento.ativo
                                                            ? "Ativo"
                                                            : "Inativo"
                                                    }
                                                </span>
                                            </td>


                                            <td className="equipamento-actions-cell">

                                                <button
                                                    className="equipamento-actions"
                                                    type="button"
                                                    aria-label={`Ações de ${equipamento.identificacao}`}
                                                    aria-haspopup="menu"
                                                    aria-expanded={menuAberto === equipamento.id}
                                                    onClick={() =>
                                                        setMenuAberto(
                                                            menuAberto
                                                                === equipamento.id
                                                                ? null
                                                                : equipamento.id
                                                        )
                                                    }
                                                >
                                                    <i className="bi bi-three-dots" />
                                                </button>


                                                {menuAberto === equipamento.id && (

                                                    <div className="equipamento-action-menu" role="menu">

                                                        <button
                                                            type="button"
                                                            role="menuitem"
                                                            onClick={() =>
                                                                abrirEdicao(
                                                                    equipamento
                                                                )
                                                            }
                                                        >
                                                            <i className="bi bi-pencil" />

                                                            Editar
                                                        </button>


                                                        <button
                                                            type="button"
                                                            role="menuitem"
                                                            className={
                                                                equipamento.ativo
                                                                    ? "danger"
                                                                    : ""
                                                            }
                                                            onClick={() =>
                                                                alterarSituacao(
                                                                    equipamento
                                                                )
                                                            }
                                                        >
                                                            <i
                                                                className={
                                                                    equipamento.ativo
                                                                        ? "bi bi-slash-circle"
                                                                        : "bi bi-check-circle"
                                                                }
                                                            />

                                                            {
                                                                equipamento.ativo
                                                                    ? "Desativar"
                                                                    : "Ativar"
                                                            }
                                                        </button>

                                                    </div>

                                                )}

                                            </td>

                                        </tr>

                                    )
                                )}

                            </tbody>

                        </table>

                    </div>

                )}

            </section>


            <EquipamentoFormModal
                aberto={modalAberto}
                equipamento={equipamentoEditando}
                salvando={salvando}
                erro={erroFormulario}
                onClose={fecharModal}
                onSubmit={salvarEquipamento}
            />

        </div>
    );
}


export default Equipamentos;
