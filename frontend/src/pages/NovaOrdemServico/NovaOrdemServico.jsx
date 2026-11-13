import {
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    useNavigate,
} from "react-router-dom";

import {
    criarOrdemServico,
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

import "./NovaOrdemServico.css";
import { useAuth } from "../../contexts/AuthContext";


const FORM_INICIAL = {
    tipo: "MANUTENCAO",
    titulo: "",
    descricao: "",

    tipoAtivo: "MAQUINA",
    ativoId: "",

    prioridade: "MEDIA",

    operadorId: "",
    responsavelId: "",

    prazo: "",
};


function NovaOrdemServico() {
    const navigate =
        useNavigate();
    const { pode, usuario } = useAuth();
    const podeAtribuirUsuarios = pode("USUARIO_VISUALIZAR");

    const [form, setForm] = useState(() => ({
        ...FORM_INICIAL,
        operadorId: podeAtribuirUsuarios ? "" : String(usuario?.id || ""),
    }));

    const [maquinas, setMaquinas] =
        useState([]);

    const [equipamentos, setEquipamentos] =
        useState([]);

    const [usuarios, setUsuarios] =
        useState([]);

    const [carregando, setCarregando] =
        useState(true);

    const [salvando, setSalvando] =
        useState(false);

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
                respostaMaquinas,
                respostaEquipamentos,
                respostaUsuarios,
            ] = await Promise.all([
                listarMaquinas(),
                listarEquipamentos(),
                podeAtribuirUsuarios ? listarUsuarios({ apenasAtivos: true }) : Promise.resolve({ data: [] }),
            ]);

            setMaquinas(
                respostaMaquinas.data
                || []
            );

            setEquipamentos(
                respostaEquipamentos.data
                || []
            );

            setUsuarios(
                respostaUsuarios.data
                || []
            );

        } catch (error) {
            console.error(
                "Erro ao carregar dados da OS:",
                error
            );

            setErro(
                error.response?.data?.message
                ||
                error.response?.data?.erro
                ||
                "Não foi possível carregar os dados necessários."
            );

        } finally {
            setCarregando(false);
        }
    }


    function atualizarCampo(
        campo,
        valor
    ) {
        setForm(
            (anterior) => ({
                ...anterior,
                [campo]: valor,
            })
        );
    }


    function alterarTipoAtivo(
        novoTipo
    ) {
        setForm(
            (anterior) => ({
                ...anterior,
                tipoAtivo: novoTipo,
                ativoId: "",
            })
        );
    }


    const ativosDisponiveis =
        useMemo(() => {
            if (
                form.tipoAtivo
                === "MAQUINA"
            ) {
                return maquinas;
            }

            return equipamentos;

        }, [
            form.tipoAtivo,
            maquinas,
            equipamentos,
        ]);


    function nomeAtivo(
        ativo
    ) {
        if (
            form.tipoAtivo
            === "MAQUINA"
        ) {
            return (
                `${ativo.identificacao} — `
                + `${ativo.fabricante} ${ativo.modelo}`
            );
        }

        const complemento = [
            ativo.fabricante,
            ativo.modelo,
        ]
            .filter(Boolean)
            .join(" ");

        return (
            `${ativo.identificacao} — `
            + `${ativo.nome}`
            + (
                complemento
                    ? ` · ${complemento}`
                    : ""
            )
        );
    }


    function nomeUsuario(
        usuario
    ) {
        if (usuario.nome) {
            return usuario.nome;
        }

        if (usuario.username) {
            return usuario.username;
        }

        return `Usuário #${usuario.id}`;
    }


    async function handleSubmit(
        event
    ) {
        event.preventDefault();

        if (!form.ativoId) {
            setErro(
                "Selecione uma máquina ou equipamento."
            );

            return;
        }

        try {
            setSalvando(true);
            setErro("");

            const dados = {
                tipo:
                    form.tipo,

                titulo:
                    form.titulo.trim(),

                descricao:
                    form.descricao.trim()
                    || null,

                maquina_id:
                    form.tipoAtivo
                    === "MAQUINA"
                        ? Number(
                            form.ativoId
                        )
                        : null,

                equipamento_id:
                    form.tipoAtivo
                    === "EQUIPAMENTO"
                        ? Number(
                            form.ativoId
                        )
                        : null,

                operador_id:
                    (podeAtribuirUsuarios ? form.operadorId : usuario?.id)
                        ? Number(
                            podeAtribuirUsuarios ? form.operadorId : usuario.id
                        )
                        : null,

                responsavel_id:
                    (podeAtribuirUsuarios ? form.responsavelId : "")
                        ? Number(
                            form.responsavelId
                        )
                        : null,

                prioridade:
                    form.prioridade,

                prazo:
                    form.prazo
                        || null,
            };


            await criarOrdemServico(
                dados
            );


            navigate(
                "/ordens-servico",
                {
                    replace: true,
                }
            );

        } catch (error) {
            console.error(
                "Erro ao criar OS:",
                error
            );

            const resposta =
                error.response?.data;

            if (
                resposta?.detalhes
                ?.length
            ) {
                setErro(
                    resposta.detalhes[0]
                        ?.msg
                    || "Dados inválidos."
                );

                return;
            }

            setErro(
                resposta?.erro
                ||
                resposta?.message
                ||
                "Não foi possível criar a ordem de serviço."
            );

        } finally {
            setSalvando(false);
        }
    }


    if (carregando) {
        return (
            <div className="nova-os-loading">

                <div className="spinner-border spinner-border-sm" />

                <span>
                    Carregando formulário...
                </span>

            </div>
        );
    }


    return (
        <div className="nova-os-page">

            <header className="nova-os-header">

                <div>

                    <button
                        className="nova-os-back"
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


                    <h1>
                        Nova ordem de serviço
                    </h1>

                    <p>
                        Cadastre um novo serviço
                        ou manutenção para a frota.
                    </p>

                </div>

            </header>


            <form
                className="nova-os-form"
                onSubmit={handleSubmit}
            >

                <section className="nova-os-card">

                    <div className="nova-os-card-header">
                        <div>
                            <h2>
                                Informações da ordem
                            </h2>

                            <p>
                                Dados principais da
                                ordem de serviço.
                            </p>
                        </div>
                    </div>


                    <div className="nova-os-card-body">

                        <div className="nova-os-grid">

                            {podeAtribuirUsuarios && <div className="nova-os-field">
                                <label htmlFor="tipo">
                                    Tipo *
                                </label>

                                <select
                                    id="tipo"
                                    value={
                                        form.tipo
                                    }
                                    onChange={
                                        (event) =>
                                            atualizarCampo(
                                                "tipo",
                                                event.target.value
                                            )
                                    }
                                >
                                    <option value="SERVICO">
                                        Serviço
                                    </option>

                                    <option value="MANUTENCAO">
                                        Manutenção
                                    </option>
                                </select>
                            </div>}


                            {podeAtribuirUsuarios && <div className="nova-os-field">
                                <label htmlFor="prioridade">
                                    Prioridade *
                                </label>

                                <select
                                    id="prioridade"
                                    value={
                                        form.prioridade
                                    }
                                    onChange={
                                        (event) =>
                                            atualizarCampo(
                                                "prioridade",
                                                event.target.value
                                            )
                                    }
                                >
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
                            </div>}


                            <div className="nova-os-field full">
                                <label htmlFor="titulo">
                                    Título *
                                </label>

                                <input
                                    id="titulo"
                                    type="text"
                                    required
                                    maxLength={150}
                                    value={
                                        form.titulo
                                    }
                                    onChange={
                                        (event) =>
                                            atualizarCampo(
                                                "titulo",
                                                event.target.value
                                            )
                                    }
                                    placeholder="Ex.: Manutenção preventiva do trator"
                                />
                            </div>


                            <div className="nova-os-field full">
                                <label htmlFor="descricao">
                                    Descrição
                                </label>

                                <textarea
                                    id="descricao"
                                    rows={4}
                                    value={
                                        form.descricao
                                    }
                                    onChange={
                                        (event) =>
                                            atualizarCampo(
                                                "descricao",
                                                event.target.value
                                            )
                                    }
                                    placeholder="Descreva o serviço que deverá ser realizado..."
                                />
                            </div>

                        </div>

                    </div>

                </section>


                <section className="nova-os-card">

                    <div className="nova-os-card-header">
                        <div>
                            <h2>
                                Ativo relacionado
                            </h2>

                            <p>
                                Selecione uma máquina
                                ou equipamento.
                            </p>
                        </div>
                    </div>


                    <div className="nova-os-card-body">

                        <div className="asset-type-selector">

                            <button
                                type="button"
                                className={
                                    form.tipoAtivo
                                    === "MAQUINA"
                                        ? "active"
                                        : ""
                                }
                                onClick={() =>
                                    alterarTipoAtivo(
                                        "MAQUINA"
                                    )
                                }
                            >
                                <i className="bi bi-truck-front" />

                                Máquina
                            </button>


                            <button
                                type="button"
                                className={
                                    form.tipoAtivo
                                    === "EQUIPAMENTO"
                                        ? "active"
                                        : ""
                                }
                                onClick={() =>
                                    alterarTipoAtivo(
                                        "EQUIPAMENTO"
                                    )
                                }
                            >
                                <i className="bi bi-tools" />

                                Equipamento
                            </button>

                        </div>


                        <div className="nova-os-field asset-select">

                            <label htmlFor="ativo">
                                {
                                    form.tipoAtivo
                                    === "MAQUINA"
                                        ? "Máquina *"
                                        : "Equipamento *"
                                }
                            </label>

                            <select
                                id="ativo"
                                required
                                value={
                                    form.ativoId
                                }
                                onChange={
                                    (event) =>
                                        atualizarCampo(
                                            "ativoId",
                                            event.target.value
                                        )
                                }
                            >
                                <option value="">
                                    Selecione...
                                </option>

                                {ativosDisponiveis.map(
                                    (ativo) => (
                                        <option
                                            key={
                                                ativo.id
                                            }
                                            value={
                                                ativo.id
                                            }
                                        >
                                            {
                                                nomeAtivo(
                                                    ativo
                                                )
                                            }
                                        </option>
                                    )
                                )}

                            </select>

                        </div>

                    </div>

                </section>


                <section className="nova-os-card">

                    <div className="nova-os-card-header">
                        <div>
                            <h2>
                                Responsáveis e prazo
                            </h2>

                            <p>
                                Informações opcionais
                                para acompanhamento.
                            </p>
                        </div>
                    </div>


                    <div className="nova-os-card-body">

                        <div className="nova-os-grid">

                            <div className="nova-os-field">
                                <label htmlFor="operador">
                                    Operador
                                </label>

                                <select
                                    id="operador"
                                    value={
                                        form.operadorId
                                    }
                                    onChange={
                                        (event) =>
                                            atualizarCampo(
                                                "operadorId",
                                                event.target.value
                                            )
                                    }
                                >
                                    <option value="">
                                        Não definido
                                    </option>

                                    {usuarios.map(
                                        (usuario) => (
                                            <option
                                                key={
                                                    usuario.id
                                                }
                                                value={
                                                    usuario.id
                                                }
                                            >
                                                {
                                                    nomeUsuario(
                                                        usuario
                                                    )
                                                }
                                            </option>
                                        )
                                    )}

                                </select>
                            </div>


                            <div className="nova-os-field">
                                <label htmlFor="responsavel">
                                    Responsável
                                </label>

                                <select
                                    id="responsavel"
                                    value={
                                        form.responsavelId
                                    }
                                    onChange={
                                        (event) =>
                                            atualizarCampo(
                                                "responsavelId",
                                                event.target.value
                                            )
                                    }
                                >
                                    <option value="">
                                        Não definido
                                    </option>

                                    {usuarios.map(
                                        (usuario) => (
                                            <option
                                                key={
                                                    usuario.id
                                                }
                                                value={
                                                    usuario.id
                                                }
                                            >
                                                {
                                                    nomeUsuario(
                                                        usuario
                                                    )
                                                }
                                            </option>
                                        )
                                    )}

                                </select>
                            </div>


                            <div className="nova-os-field full">
                                <label htmlFor="prazo">
                                    Prazo
                                </label>

                                <input
                                    id="prazo"
                                    type="datetime-local"
                                    value={
                                        form.prazo
                                    }
                                    onChange={
                                        (event) =>
                                            atualizarCampo(
                                                "prazo",
                                                event.target.value
                                            )
                                    }
                                />
                            </div>

                        </div>

                    </div>

                </section>


                {erro && (
                    <div className="nova-os-error" role="alert">

                        <i className="bi bi-exclamation-circle" />

                        {erro}

                    </div>
                )}


                <footer className="nova-os-footer">

                    <button
                        type="button"
                        className="nova-os-cancel"
                        onClick={() =>
                            navigate(
                                "/ordens-servico"
                            )
                        }
                        disabled={salvando}
                    >
                        Cancelar
                    </button>


                    <button
                        type="submit"
                        className="nova-os-submit"
                        disabled={salvando}
                    >
                        {
                            salvando
                                ? (
                                    <>
                                        <span className="spinner-border spinner-border-sm" />

                                        Criando...
                                    </>
                                )
                                : (
                                    <>
                                        <i className="bi bi-plus-lg" />

                                        Criar ordem de serviço
                                    </>
                                )
                        }
                    </button>

                </footer>

            </form>

        </div>
    );
}


export default NovaOrdemServico;
