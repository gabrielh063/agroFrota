import {
    useEffect,
    useState,
} from "react";

import {
    useNavigate,
    useParams,
} from "react-router-dom";

import {
    atualizarOrdemServico,
    buscarOrdemServico,
    cancelarOrdemServico,
    concluirOrdemServico,
} from "../../api/ordemServicoService";

import {
    listarMaquinas,
} from "../../api/maquinaService";

import {
    listarEquipamentos,
} from "../../api/equipamentoService";

import {
    listarUsuarios,
} from "../../api/usuarioService";

import "./DetalhesOrdemServico.css";


function DetalhesOrdemServico() {
    const navigate =
        useNavigate();

    const {
        id,
    } = useParams();


    const [ordem, setOrdem] =
        useState(null);

    const [maquinas, setMaquinas] =
        useState([]);

    const [equipamentos, setEquipamentos] =
        useState([]);

    const [usuarios, setUsuarios] =
        useState([]);

    const [carregando, setCarregando] =
        useState(true);

    const [acaoCarregando, setAcaoCarregando] =
        useState("");

    const [erro, setErro] =
        useState("");

    const [mensagem, setMensagem] =
        useState("");


    useEffect(() => {
        carregarDados();
    }, [id]);


    async function carregarDados() {
        try {
            setCarregando(true);
            setErro("");

            const resultados =
                await Promise.allSettled([
                    buscarOrdemServico(id),

                    listarMaquinas({
                        incluirInativas: true,
                    }),

                    listarEquipamentos({
                        incluirInativos: true,
                    }),

                    listarUsuarios({
                        apenasAtivos: false,
                    }),
                ]);


            const [
                resultadoOrdem,
                resultadoMaquinas,
                resultadoEquipamentos,
                resultadoUsuarios,
            ] = resultados;


            if (
                resultadoOrdem.status
                === "rejected"
            ) {
                throw resultadoOrdem.reason;
            }


            setOrdem(
                resultadoOrdem
                    .value
                    .ordem_servico
            );


            if (
                resultadoMaquinas.status
                === "fulfilled"
            ) {
                setMaquinas(
                    resultadoMaquinas
                        .value
                        .data
                    || []
                );
            }


            if (
                resultadoEquipamentos.status
                === "fulfilled"
            ) {
                setEquipamentos(
                    resultadoEquipamentos
                        .value
                        .data
                    || []
                );
            }


            if (
                resultadoUsuarios.status
                === "fulfilled"
            ) {
                setUsuarios(
                    resultadoUsuarios
                        .value
                        .data
                    || []
                );
            }

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
                "Não foi possível carregar a ordem de serviço."
            );

        } finally {
            setCarregando(false);
        }
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
            return "Não definido";
        }

        const data =
            new Date(valor);

        if (
            Number.isNaN(
                data.getTime()
            )
        ) {
            return valor;
        }

        return new Intl.DateTimeFormat(
            "pt-BR",
            {
                dateStyle: "medium",
                timeStyle: "short",
            }
        ).format(data);
    }


    function buscarUsuario(
        usuarioId
    ) {
        if (!usuarioId) {
            return "Não definido";
        }

        const usuario =
            usuarios.find(
                (item) =>
                    item.id
                    === usuarioId
            );

        if (!usuario) {
            return (
                `Usuário #${usuarioId}`
            );
        }

        return (
            usuario.nome
            ||
            usuario.username
            ||
            `Usuário #${usuarioId}`
        );
    }


    function buscarAtivo() {
        if (!ordem) {
            return null;
        }


        if (ordem.maquina_id) {
            const maquina =
                maquinas.find(
                    (item) =>
                        item.id
                        === ordem.maquina_id
                );

            if (!maquina) {
                return {
                    tipo: "Máquina",

                    identificacao:
                        `Máquina #${ordem.maquina_id}`,

                    nome:
                        "Dados do ativo indisponíveis",

                    localizacao:
                        null,

                    ativo:
                        null,
                };
            }

            return {
                tipo:
                    "Máquina",

                identificacao:
                    maquina.identificacao,

                nome:
                    `${maquina.fabricante} ${maquina.modelo}`,

                localizacao:
                    maquina.localizacao,

                ativo:
                    maquina.ativo,
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
                    tipo:
                        "Equipamento",

                    identificacao:
                        `Equipamento #${ordem.equipamento_id}`,

                    nome:
                        "Dados do ativo indisponíveis",

                    localizacao:
                        null,

                    ativo:
                        null,
                };
            }

            const fabricanteModelo = [
                equipamento.fabricante,
                equipamento.modelo,
            ]
                .filter(Boolean)
                .join(" ");

            return {
                tipo:
                    "Equipamento",

                identificacao:
                    equipamento.identificacao,

                nome:
                    equipamento.nome,

                complemento:
                    fabricanteModelo,

                localizacao:
                    equipamento.localizacao,

                ativo:
                    equipamento.ativo,
            };
        }


        return {
            tipo: "-",
            identificacao:
                "Ativo não identificado",
            nome: "",
            localizacao: null,
            ativo: null,
        };
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


    async function iniciarOrdem() {
        const confirmar =
            window.confirm(
                "Deseja iniciar esta ordem de serviço?"
            );

        if (!confirmar) {
            return;
        }


        try {
            setAcaoCarregando(
                "INICIAR"
            );

            setErro("");
            setMensagem("");


            const resposta =
                await atualizarOrdemServico(
                    ordem.id,
                    {
                        status:
                            "EM_ANDAMENTO",
                    }
                );


            setOrdem(
                resposta.ordem_servico
            );

            setMensagem(
                "Ordem de serviço iniciada."
            );

        } catch (error) {
            console.error(
                "Erro ao iniciar OS:",
                error
            );

            setErro(
                error.response?.data?.erro
                ||
                error.response?.data?.message
                ||
                "Não foi possível iniciar a ordem de serviço."
            );

        } finally {
            setAcaoCarregando("");
        }
    }


    async function concluirOrdem() {
        const confirmar =
            window.confirm(
                "Deseja concluir esta ordem de serviço?"
            );

        if (!confirmar) {
            return;
        }


        try {
            setAcaoCarregando(
                "CONCLUIR"
            );

            setErro("");
            setMensagem("");


            const resposta =
                await concluirOrdemServico(
                    ordem.id
                );


            setOrdem(
                resposta.ordem_servico
            );

            setMensagem(
                resposta.mensagem
                ||
                "Ordem de serviço concluída."
            );

        } catch (error) {
            console.error(
                "Erro ao concluir OS:",
                error
            );

            setErro(
                error.response?.data?.erro
                ||
                error.response?.data?.message
                ||
                "Não foi possível concluir a ordem de serviço."
            );

        } finally {
            setAcaoCarregando("");
        }
    }


    async function cancelarOrdem() {
        const confirmar =
            window.confirm(
                "Deseja realmente cancelar esta ordem de serviço?"
            );

        if (!confirmar) {
            return;
        }


        try {
            setAcaoCarregando(
                "CANCELAR"
            );

            setErro("");
            setMensagem("");


            const resposta =
                await cancelarOrdemServico(
                    ordem.id
                );


            setOrdem(
                resposta.ordem_servico
            );

            setMensagem(
                resposta.mensagem
                ||
                "Ordem de serviço cancelada."
            );

        } catch (error) {
            console.error(
                "Erro ao cancelar OS:",
                error
            );

            setErro(
                error.response?.data?.erro
                ||
                error.response?.data?.message
                ||
                "Não foi possível cancelar a ordem de serviço."
            );

        } finally {
            setAcaoCarregando("");
        }
    }


    if (carregando) {
        return (
            <div className="detalhes-os-loading">

                <div className="spinner-border spinner-border-sm" />

                <span>
                    Carregando ordem de serviço...
                </span>

            </div>
        );
    }


    if (
        erro
        &&
        !ordem
    ) {
        return (
            <div className="detalhes-os-page">

                <button
                    className="detalhes-os-back"
                    onClick={() =>
                        navigate(
                            "/ordens-servico"
                        )
                    }
                >
                    <i className="bi bi-arrow-left" />

                    Ordens de serviço
                </button>


                <div className="detalhes-os-error">

                    <i className="bi bi-exclamation-circle" />

                    {erro}

                </div>

            </div>
        );
    }


    if (!ordem) {
        return null;
    }


    const ativo =
        buscarAtivo();

    const finalizada =
        ordem.status
        === "CONCLUIDA"
        ||
        ordem.status
        === "CANCELADA";


    return (
        <div className="detalhes-os-page">

            <button
                className="detalhes-os-back"
                type="button"
                onClick={() =>
                    navigate(
                        "/ordens-servico"
                    )
                }
            >
                <i className="bi bi-arrow-left" />

                Ordens de serviço
            </button>


            <header className="detalhes-os-header">

                <div>

                    <div className="detalhes-os-number">
                        OS #{ordem.numero}
                    </div>

                    <h1>
                        {ordem.titulo}
                    </h1>


                    <div className="detalhes-os-meta">

                        <span>
                            {
                                formatarTexto(
                                    ordem.tipo
                                )
                            }
                        </span>

                        <span className="meta-divider">
                            •
                        </span>

                        <span
                            className={
                                `detalhes-prioridade ${
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

                </div>


                <span
                    className={
                        `detalhes-status ${
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

            </header>


            {mensagem && (
                <div className="detalhes-os-success">

                    <i className="bi bi-check-circle" />

                    {mensagem}

                </div>
            )}


            {erro && (
                <div className="detalhes-os-error">

                    <i className="bi bi-exclamation-circle" />

                    {erro}

                </div>
            )}


            <div className="detalhes-os-grid">

                <main className="detalhes-os-main">

                    <section className="detalhes-card">

                        <div className="detalhes-card-header">

                            <h2>
                                Ativo relacionado
                            </h2>

                        </div>


                        <div className="detalhes-card-body">

                            <div className="detalhes-ativo">

                                <div className="detalhes-ativo-icon">

                                    <i
                                        className={
                                            ativo.tipo
                                            === "Máquina"
                                                ? "bi bi-truck-front"
                                                : "bi bi-tools"
                                        }
                                    />

                                </div>


                                <div className="detalhes-ativo-info">

                                    <span>
                                        {ativo.tipo}
                                    </span>

                                    <strong>
                                        {
                                            ativo.identificacao
                                        }
                                    </strong>

                                    <p>
                                        {ativo.nome}
                                    </p>


                                    {
                                        ativo.complemento
                                        && (
                                            <small>
                                                {
                                                    ativo.complemento
                                                }
                                            </small>
                                        )
                                    }


                                    {
                                        ativo.localizacao
                                        && (
                                            <small>
                                                <i className="bi bi-geo-alt" />

                                                {
                                                    ativo.localizacao
                                                }
                                            </small>
                                        )
                                    }

                                </div>

                            </div>

                        </div>

                    </section>


                    <section className="detalhes-card">

                        <div className="detalhes-card-header">

                            <h2>
                                Descrição
                            </h2>

                        </div>


                        <div className="detalhes-card-body">

                            <p className="detalhes-description">

                                {
                                    ordem.descricao
                                    ||
                                    "Nenhuma descrição informada."
                                }

                            </p>

                        </div>

                    </section>

                </main>


                <aside className="detalhes-os-sidebar">

                    <section className="detalhes-card">

                        <div className="detalhes-card-header">

                            <h2>
                                Informações
                            </h2>

                        </div>


                        <div className="detalhes-info-list">

                            <div className="detalhes-info-item">

                                <span>
                                    <i className="bi bi-calendar3" />

                                    Prazo
                                </span>

                                <strong>
                                    {
                                        formatarData(
                                            ordem.prazo
                                        )
                                    }
                                </strong>

                            </div>


                            <div className="detalhes-info-item">

                                <span>
                                    <i className="bi bi-person" />

                                    Responsável
                                </span>

                                <strong>
                                    {
                                        buscarUsuario(
                                            ordem.responsavel_id
                                        )
                                    }
                                </strong>

                            </div>


                            <div className="detalhes-info-item">

                                <span>
                                    <i className="bi bi-person-gear" />

                                    Operador
                                </span>

                                <strong>
                                    {
                                        buscarUsuario(
                                            ordem.operador_id
                                        )
                                    }
                                </strong>

                            </div>


                            <div className="detalhes-info-item">

                                <span>
                                    <i className="bi bi-tag" />

                                    Tipo
                                </span>

                                <strong>
                                    {
                                        formatarTexto(
                                            ordem.tipo
                                        )
                                    }
                                </strong>

                            </div>

                        </div>

                    </section>

                </aside>

            </div>


            <section className="detalhes-actions">

                {finalizada ? (

                    <div className="detalhes-finalizada">

                        <i className="bi bi-lock" />

                        Esta ordem está {
                            ordem.status
                            === "CONCLUIDA"
                                ? "concluída"
                                : "cancelada"
                        } e não pode mais ser alterada.

                    </div>

                ) : (

                    <div className="detalhes-actions-buttons">

                        <button
                            type="button"
                            className="os-action-edit"
                            onClick={() =>
                                navigate(
                                    `/ordens-servico/${ordem.id}/editar`
                                )
                            }
                            disabled={
                                Boolean(
                                    acaoCarregando
                                )
                            }
                        >
                            <i className="bi bi-pencil" />

                            Editar
                        </button>

                        {
                            ordem.status
                            === "ABERTA"
                            && (
                                <button
                                    type="button"
                                    className="os-action-start"
                                    onClick={
                                        iniciarOrdem
                                    }
                                    disabled={
                                        Boolean(
                                            acaoCarregando
                                        )
                                    }
                                >
                                    <i className="bi bi-play-fill" />

                                    {
                                        acaoCarregando
                                        === "INICIAR"
                                            ? "Iniciando..."
                                            : "Iniciar OS"
                                    }
                                </button>
                            )
                        }


                        <button
                            type="button"
                            className="os-action-complete"
                            onClick={
                                concluirOrdem
                            }
                            disabled={
                                Boolean(
                                    acaoCarregando
                                )
                            }
                        >
                            <i className="bi bi-check-lg" />

                            {
                                acaoCarregando
                                === "CONCLUIR"
                                    ? "Concluindo..."
                                    : "Concluir"
                            }
                        </button>


                        <button
                            type="button"
                            className="os-action-cancel"
                            onClick={
                                cancelarOrdem
                            }
                            disabled={
                                Boolean(
                                    acaoCarregando
                                )
                            }
                        >
                            <i className="bi bi-x-lg" />

                            {
                                acaoCarregando
                                === "CANCELAR"
                                    ? "Cancelando..."
                                    : "Cancelar OS"
                            }
                        </button>

                    </div>

                )}

            </section>

        </div>
    );
}


export default DetalhesOrdemServico;