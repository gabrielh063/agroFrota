import {
    useEffect,
    useState,
} from "react";

import "./AgendamentoDetalhesModal.css";


function dataParaInput(valor) {
    if (!valor) {
        return "";
    }

    return valor.slice(0, 16);
}


function formatarData(valor) {
    if (!valor) {
        return "-";
    }

    return new Intl.DateTimeFormat(
        "pt-BR",
        {
            dateStyle: "long",
            timeStyle: "short",
        }
    ).format(
        new Date(valor)
    );
}


function formatarStatus(status) {
    const mapa = {
        AGENDADO: "Agendado",
        EM_ANDAMENTO: "Em andamento",
        CONCLUIDO: "Concluído",
        CANCELADO: "Cancelado",
    };

    return mapa[status] || status;
}


function AgendamentoDetalhesModal({
    agendamento,
    ordem,
    usuarios,
    aberto,
    salvando,
    erro,
    onClose,
    onSalvar,
    onCancelar,
    onVerOS,
}) {
    const [editando, setEditando] =
        useState(false);

    const [form, setForm] =
        useState({
            inicio: "",
            fim: "",
            responsavelId: "",
            status: "AGENDADO",
            observacoes: "",
        });


    useEffect(() => {
        if (!agendamento) {
            return;
        }

        setEditando(false);

        setForm({
            inicio:
                dataParaInput(
                    agendamento.inicio
                ),

            fim:
                dataParaInput(
                    agendamento.fim
                ),

            responsavelId:
                agendamento.responsavel_id
                    ? String(
                        agendamento.responsavel_id
                    )
                    : "",

            status:
                agendamento.status,

            observacoes:
                agendamento.observacoes
                || "",
        });

    }, [agendamento]);


    if (
        !aberto
        ||
        !agendamento
    ) {
        return null;
    }


    const finalizado =
        agendamento.status
        === "CONCLUIDO"
        ||
        agendamento.status
        === "CANCELADO";


    const responsavel =
        usuarios.find(
            (usuario) =>
                usuario.id
                === agendamento.responsavel_id
        );


    const usuariosDisponiveis =
        usuarios.filter(
            (usuario) =>
                usuario.ativo
                ||
                usuario.id
                === agendamento.responsavel_id
        );


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


    function enviarEdicao(
        event
    ) {
        event.preventDefault();

        const dados = {};


        if (
            form.inicio
            !== dataParaInput(
                agendamento.inicio
            )
        ) {
            dados.inicio =
                form.inicio;
        }


        if (
            form.fim
            !== dataParaInput(
                agendamento.fim
            )
        ) {
            dados.fim =
                form.fim;
        }


        const responsavelNovo =
            form.responsavelId
                ? Number(
                    form.responsavelId
                )
                : null;


        if (
            responsavelNovo
            !== (
                agendamento.responsavel_id
                ?? null
            )
        ) {
            dados.responsavel_id =
                responsavelNovo;
        }


        if (
            form.status
            !== agendamento.status
        ) {
            dados.status =
                form.status;
        }


        const observacoesNovas =
            form.observacoes.trim()
            || null;


        if (
            observacoesNovas
            !== (
                agendamento.observacoes
                || null
            )
        ) {
            dados.observacoes =
                observacoesNovas;
        }


        onSalvar(
            agendamento.id,
            dados
        );
    }


    return (
        <div
            className="agd-detail-overlay"
            onMouseDown={(event) => {
                if (
                    event.target
                    === event.currentTarget
                    &&
                    !salvando
                ) {
                    onClose();
                }
            }}
        >

            <div className="agd-detail-modal">

                <header className="agd-detail-header">

                    <div>

                        <span className="agd-detail-number">
                            Agendamento #{agendamento.id}
                        </span>

                        <h2>
                            {
                                ordem
                                    ? ordem.titulo
                                    : "Agendamento"
                            }
                        </h2>

                        {
                            ordem
                            && (
                                <p>
                                    OS #{ordem.numero}
                                </p>
                            )
                        }

                    </div>


                    <div className="agd-detail-header-right">

                        <span
                            className={
                                `agd-status ${agendamento.status.toLowerCase()}`
                            }
                        >
                            {
                                formatarStatus(
                                    agendamento.status
                                )
                            }
                        </span>


                        <button
                            type="button"
                            className="agd-close"
                            onClick={onClose}
                            disabled={salvando}
                        >
                            <i className="bi bi-x-lg" />
                        </button>

                    </div>

                </header>


                {!editando ? (

                    <div className="agd-detail-content">

                        <div className="agd-detail-grid">

                            <div className="agd-info">

                                <span>
                                    <i className="bi bi-calendar-event" />

                                    Início
                                </span>

                                <strong>
                                    {
                                        formatarData(
                                            agendamento.inicio
                                        )
                                    }
                                </strong>

                            </div>


                            <div className="agd-info">

                                <span>
                                    <i className="bi bi-calendar-check" />

                                    Fim
                                </span>

                                <strong>
                                    {
                                        formatarData(
                                            agendamento.fim
                                        )
                                    }
                                </strong>

                            </div>


                            <div className="agd-info">

                                <span>
                                    <i className="bi bi-person" />

                                    Responsável
                                </span>

                                <strong>
                                    {
                                        responsavel?.nome
                                        ||
                                        responsavel?.username
                                        ||
                                        "Não definido"
                                    }
                                </strong>

                            </div>


                            <div className="agd-info">

                                <span>
                                    <i className="bi bi-activity" />

                                    Status
                                </span>

                                <strong>
                                    {
                                        formatarStatus(
                                            agendamento.status
                                        )
                                    }
                                </strong>

                            </div>

                        </div>


                        <div className="agd-observacoes">

                            <span>
                                Observações
                            </span>

                            <p>
                                {
                                    agendamento.observacoes
                                    ||
                                    "Nenhuma observação informada."
                                }
                            </p>

                        </div>


                        {erro && (
                            <div className="agd-error">
                                <i className="bi bi-exclamation-circle" />

                                {erro}
                            </div>
                        )}


                        <footer className="agd-actions">

                            <button
                                type="button"
                                className="agd-secondary"
                                onClick={onVerOS}
                            >
                                <i className="bi bi-box-arrow-up-right" />

                                Ver OS
                            </button>


                            {!finalizado && (
                                <>
                                    <button
                                        type="button"
                                        className="agd-edit"
                                        onClick={() =>
                                            setEditando(
                                                true
                                            )
                                        }
                                    >
                                        <i className="bi bi-pencil" />

                                        Editar
                                    </button>


                                    <button
                                        type="button"
                                        className="agd-danger"
                                        onClick={onCancelar}
                                        disabled={salvando}
                                    >
                                        <i className="bi bi-x-circle" />

                                        Cancelar agendamento
                                    </button>
                                </>
                            )}

                        </footer>

                    </div>

                ) : (

                    <form
                        className="agd-edit-form"
                        onSubmit={enviarEdicao}
                    >

                        <div className="agd-form-grid">

                            <div className="agd-field">

                                <label>
                                    Início *
                                </label>

                                <input
                                    type="datetime-local"
                                    required
                                    value={
                                        form.inicio
                                    }
                                    onChange={(event) =>
                                        atualizarCampo(
                                            "inicio",
                                            event.target.value
                                        )
                                    }
                                />

                            </div>


                            <div className="agd-field">

                                <label>
                                    Fim *
                                </label>

                                <input
                                    type="datetime-local"
                                    required
                                    value={
                                        form.fim
                                    }
                                    onChange={(event) =>
                                        atualizarCampo(
                                            "fim",
                                            event.target.value
                                        )
                                    }
                                />

                            </div>


                            <div className="agd-field">

                                <label>
                                    Responsável
                                </label>

                                <select
                                    value={
                                        form.responsavelId
                                    }
                                    onChange={(event) =>
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
                                                    usuario.nome
                                                    ||
                                                    usuario.username
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


                            <div className="agd-field">

                                <label>
                                    Status
                                </label>

                                <select
                                    value={
                                        form.status
                                    }
                                    onChange={(event) =>
                                        atualizarCampo(
                                            "status",
                                            event.target.value
                                        )
                                    }
                                >
                                    <option value="AGENDADO">
                                        Agendado
                                    </option>

                                    <option value="EM_ANDAMENTO">
                                        Em andamento
                                    </option>

                                    <option value="CONCLUIDO">
                                        Concluído
                                    </option>
                                </select>

                            </div>


                            <div className="agd-field full">

                                <label>
                                    Observações
                                </label>

                                <textarea
                                    rows={4}
                                    value={
                                        form.observacoes
                                    }
                                    onChange={(event) =>
                                        atualizarCampo(
                                            "observacoes",
                                            event.target.value
                                        )
                                    }
                                />

                            </div>

                        </div>


                        {erro && (
                            <div className="agd-error">

                                <i className="bi bi-exclamation-circle" />

                                {erro}

                            </div>
                        )}


                        <footer className="agd-actions">

                            <button
                                type="button"
                                className="agd-secondary"
                                onClick={() =>
                                    setEditando(
                                        false
                                    )
                                }
                                disabled={salvando}
                            >
                                Voltar
                            </button>


                            <button
                                type="submit"
                                className="agd-save"
                                disabled={salvando}
                            >
                                {
                                    salvando
                                        ? "Salvando..."
                                        : "Salvar alterações"
                                }
                            </button>

                        </footer>

                    </form>

                )}

            </div>

        </div>
    );
}


export default AgendamentoDetalhesModal;