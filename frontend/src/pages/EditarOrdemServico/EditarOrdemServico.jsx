import {
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    useNavigate,
    useParams,
} from "react-router-dom";

import {
    atualizarOrdemServico,
    buscarOrdemServico,
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

/*
 * Reaproveitamos o mesmo visual
 * utilizado na criação da OS.
 */
import "../NovaOrdemServico/NovaOrdemServico.css";


function dataParaInput(valor) {
    if (!valor) {
        return "";
    }

    /*
     * O backend retorna algo parecido com:
     *
     * 2026-09-30T08:00:00
     *
     * datetime-local precisa de:
     *
     * 2026-09-30T08:00
     */
    return valor.slice(0, 16);
}


function EditarOrdemServico() {
    const navigate =
        useNavigate();

    const {
        id,
    } = useParams();


    const [ordem, setOrdem] =
        useState(null);

    const [form, setForm] =
        useState(null);

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

    const [mensagem, setMensagem] =
        useState("");


    useEffect(() => {
        carregarDados();
    }, [id]);


    async function carregarDados() {
        try {
            setCarregando(true);
            setErro("");

            const [
                respostaOrdem,
                respostaMaquinas,
                respostaEquipamentos,
                respostaUsuarios,
            ] = await Promise.all([
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


            const ordemCarregada =
                respostaOrdem.ordem_servico;


            /*
             * Segurança também no frontend.
             */
            if (
                ordemCarregada.status
                === "CONCLUIDA"
                ||
                ordemCarregada.status
                === "CANCELADA"
            ) {
                setErro(
                    "Esta ordem de serviço não pode mais ser editada."
                );

                setOrdem(
                    ordemCarregada
                );

                return;
            }


            setOrdem(
                ordemCarregada
            );

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


            const tipoAtivo =
                ordemCarregada.maquina_id
                    ? "MAQUINA"
                    : "EQUIPAMENTO";


            setForm({
                tipo:
                    ordemCarregada.tipo,

                titulo:
                    ordemCarregada.titulo,

                descricao:
                    ordemCarregada.descricao
                    || "",

                tipoAtivo,

                ativoId:
                    String(
                        ordemCarregada.maquina_id
                        ??
                        ordemCarregada.equipamento_id
                        ??
                        ""
                    ),

                prioridade:
                    ordemCarregada.prioridade,

                operadorId:
                    ordemCarregada.operador_id
                        ? String(
                            ordemCarregada.operador_id
                        )
                        : "",

                responsavelId:
                    ordemCarregada.responsavel_id
                        ? String(
                            ordemCarregada.responsavel_id
                        )
                        : "",

                prazo:
                    dataParaInput(
                        ordemCarregada.prazo
                    ),
            });

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


    function atualizarCampo(
        campo,
        valor
    ) {
        setMensagem("");

        setForm(
            (anterior) => ({
                ...anterior,
                [campo]: valor,
            })
        );
    }


    function alterarTipoAtivo(
        tipoAtivo
    ) {
        setMensagem("");

        setForm(
            (anterior) => ({
                ...anterior,
                tipoAtivo,
                ativoId: "",
            })
        );
    }


    const maquinasDisponiveis =
        useMemo(() => {
            if (!ordem) {
                return [];
            }

            return maquinas.filter(
                (maquina) => {
                    if (maquina.ativo) {
                        return true;
                    }

                    /*
                     * Mantém visível a máquina
                     * atualmente vinculada, mesmo
                     * se ela foi desativada depois.
                     */
                    return (
                        ordem.maquina_id
                        === maquina.id
                    );
                }
            );

        }, [
            maquinas,
            ordem,
        ]);


    const equipamentosDisponiveis =
        useMemo(() => {
            if (!ordem) {
                return [];
            }

            return equipamentos.filter(
                (equipamento) => {
                    if (equipamento.ativo) {
                        return true;
                    }

                    return (
                        ordem.equipamento_id
                        === equipamento.id
                    );
                }
            );

        }, [
            equipamentos,
            ordem,
        ]);


    const usuariosDisponiveis =
        useMemo(() => {
            if (!ordem) {
                return [];
            }

            return usuarios.filter(
                (usuario) => {
                    if (usuario.ativo) {
                        return true;
                    }

                    return (
                        usuario.id
                        === ordem.operador_id
                        ||
                        usuario.id
                        === ordem.responsavel_id
                    );
                }
            );

        }, [
            usuarios,
            ordem,
        ]);


    function nomeMaquina(
        maquina
    ) {
        return (
            `${maquina.identificacao} — `
            + `${maquina.fabricante} ${maquina.modelo}`
            + (
                maquina.ativo
                    ? ""
                    : " · Inativa"
            )
        );
    }


    function nomeEquipamento(
        equipamento
    ) {
        const detalhe = [
            equipamento.fabricante,
            equipamento.modelo,
        ]
            .filter(Boolean)
            .join(" ");

        return (
            `${equipamento.identificacao} — `
            + `${equipamento.nome}`
            + (
                detalhe
                    ? ` · ${detalhe}`
                    : ""
            )
            + (
                equipamento.ativo
                    ? ""
                    : " · Inativo"
            )
        );
    }


    function nomeUsuario(
        usuario
    ) {
        return (
            usuario.nome
            ||
            usuario.username
            ||
            `Usuário #${usuario.id}`
        );
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


        const dados = {};


        /*
         * CAMPOS SIMPLES
         */

        const titulo =
            form.titulo.trim();

        const descricao =
            form.descricao.trim()
            || null;


        if (
            form.tipo
            !== ordem.tipo
        ) {
            dados.tipo =
                form.tipo;
        }


        if (
            titulo
            !== ordem.titulo
        ) {
            dados.titulo =
                titulo;
        }


        if (
            descricao
            !== (
                ordem.descricao
                || null
            )
        ) {
            dados.descricao =
                descricao;
        }


        if (
            form.prioridade
            !== ordem.prioridade
        ) {
            dados.prioridade =
                form.prioridade;
        }


        /*
         * ATIVO
         */

        const tipoAtivoOriginal =
            ordem.maquina_id
                ? "MAQUINA"
                : "EQUIPAMENTO";


        const ativoIdOriginal =
            String(
                ordem.maquina_id
                ??
                ordem.equipamento_id
            );


        const ativoAlterado =
            form.tipoAtivo
                !== tipoAtivoOriginal
            ||
            form.ativoId
                !== ativoIdOriginal;


        if (ativoAlterado) {
            if (
                form.tipoAtivo
                === "MAQUINA"
            ) {
                dados.maquina_id =
                    Number(
                        form.ativoId
                    );

                dados.equipamento_id =
                    null;

            } else {
                dados.maquina_id =
                    null;

                dados.equipamento_id =
                    Number(
                        form.ativoId
                    );
            }
        }


        /*
         * OPERADOR
         */

        const operadorNovo =
            form.operadorId
                ? Number(
                    form.operadorId
                )
                : null;


        if (
            operadorNovo
            !== (
                ordem.operador_id
                ?? null
            )
        ) {
            dados.operador_id =
                operadorNovo;
        }


        /*
         * RESPONSÁVEL
         */

        const responsavelNovo =
            form.responsavelId
                ? Number(
                    form.responsavelId
                )
                : null;


        if (
            responsavelNovo
            !== (
                ordem.responsavel_id
                ?? null
            )
        ) {
            dados.responsavel_id =
                responsavelNovo;
        }


        /*
         * PRAZO
         */

        const prazoOriginal =
            dataParaInput(
                ordem.prazo
            );

        const prazoNovo =
            form.prazo
            || null;


        if (
            form.prazo
            !== prazoOriginal
        ) {
            dados.prazo =
                prazoNovo;
        }


        /*
         * Nenhuma alteração.
         */

        if (
            Object.keys(
                dados
            ).length === 0
        ) {
            setMensagem(
                "Nenhuma alteração foi realizada."
            );

            return;
        }


        try {
            setSalvando(true);
            setErro("");
            setMensagem("");


            await atualizarOrdemServico(
                ordem.id,
                dados
            );


            navigate(
                `/ordens-servico/${ordem.id}`,
                {
                    replace: true,
                }
            );

        } catch (error) {
            console.error(
                "Erro ao atualizar OS:",
                error
            );

            const resposta =
                error.response?.data;


            if (
                resposta?.detalhes
                ?.length
            ) {
                setErro(
                    resposta
                        .detalhes[0]
                        ?.msg
                    ||
                    "Dados inválidos."
                );

                return;
            }


            setErro(
                resposta?.erro
                ||
                resposta?.message
                ||
                "Não foi possível atualizar a ordem de serviço."
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
                    Carregando ordem de serviço...
                </span>

            </div>
        );
    }


    if (
        erro
        &&
        !form
    ) {
        return (
            <div className="nova-os-page">

                <button
                    className="nova-os-back"
                    onClick={() =>
                        navigate(
                            `/ordens-servico/${id}`
                        )
                    }
                >
                    <i className="bi bi-arrow-left" />

                    Voltar
                </button>


                <div className="nova-os-error">

                    <i className="bi bi-exclamation-circle" />

                    {erro}

                </div>

            </div>
        );
    }


    if (!form) {
        return null;
    }


    const ativosDisponiveis =
        form.tipoAtivo
        === "MAQUINA"
            ? maquinasDisponiveis
            : equipamentosDisponiveis;


    return (
        <div className="nova-os-page">

            <header className="nova-os-header">

                <div>

                    <button
                        className="nova-os-back"
                        type="button"
                        onClick={() =>
                            navigate(
                                `/ordens-servico/${ordem.id}`
                            )
                        }
                    >
                        <i className="bi bi-arrow-left" />

                        OS #{ordem.numero}
                    </button>


                    <h1>
                        Editar ordem de serviço
                    </h1>

                    <p>
                        Atualize as informações
                        da ordem de serviço.
                    </p>

                </div>

            </header>


            <form
                className="nova-os-form"
                onSubmit={
                    handleSubmit
                }
            >

                <section className="nova-os-card">

                    <div className="nova-os-card-header">

                        <div>
                            <h2>
                                Informações da ordem
                            </h2>

                            <p>
                                Dados principais da OS.
                            </p>
                        </div>

                    </div>


                    <div className="nova-os-card-body">

                        <div className="nova-os-grid">

                            <div className="nova-os-field">

                                <label>
                                    Tipo *
                                </label>

                                <select
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

                            </div>


                            <div className="nova-os-field">

                                <label>
                                    Prioridade *
                                </label>

                                <select
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

                            </div>


                            <div className="nova-os-field full">

                                <label>
                                    Título *
                                </label>

                                <input
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
                                />

                            </div>


                            <div className="nova-os-field full">

                                <label>
                                    Descrição
                                </label>

                                <textarea
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
                                Altere a máquina ou
                                equipamento relacionado.
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


                        <div className="nova-os-field">

                            <label>
                                {
                                    form.tipoAtivo
                                    === "MAQUINA"
                                        ? "Máquina *"
                                        : "Equipamento *"
                                }
                            </label>

                            <select
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
                                                form.tipoAtivo
                                                === "MAQUINA"
                                                    ? nomeMaquina(
                                                        ativo
                                                    )
                                                    : nomeEquipamento(
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
                                Operador, responsável
                                e prazo da ordem.
                            </p>
                        </div>

                    </div>


                    <div className="nova-os-card-body">

                        <div className="nova-os-grid">

                            <div className="nova-os-field">

                                <label>
                                    Operador
                                </label>

                                <select
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

                                    {usuariosDisponiveis.map(
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
                                                {
                                                    usuario.ativo
                                                        ? ""
                                                        : " · Inativo"
                                                }
                                            </option>
                                        )
                                    )}

                                </select>

                            </div>


                            <div className="nova-os-field">

                                <label>
                                    Responsável
                                </label>

                                <select
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

                                    {usuariosDisponiveis.map(
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
                                                {
                                                    usuario.ativo
                                                        ? ""
                                                        : " · Inativo"
                                                }
                                            </option>
                                        )
                                    )}

                                </select>

                            </div>


                            <div className="nova-os-field full">

                                <label>
                                    Prazo
                                </label>

                                <input
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


                {mensagem && (
                    <div className="detalhes-os-success">

                        <i className="bi bi-info-circle" />

                        {mensagem}

                    </div>
                )}


                {erro && (
                    <div className="nova-os-error">

                        <i className="bi bi-exclamation-circle" />

                        {erro}

                    </div>
                )}


                <footer className="nova-os-footer">

                    <button
                        type="button"
                        className="nova-os-cancel"
                        disabled={salvando}
                        onClick={() =>
                            navigate(
                                `/ordens-servico/${ordem.id}`
                            )
                        }
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

                                        Salvando...
                                    </>
                                )
                                : (
                                    <>
                                        <i className="bi bi-check-lg" />

                                        Salvar alterações
                                    </>
                                )
                        }
                    </button>

                </footer>

            </form>

        </div>
    );
}


export default EditarOrdemServico;