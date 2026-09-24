import {
    useEffect,
    useState,
} from "react";

import "./AgendamentoModal.css";


function AgendamentoModal({
    aberto,
    ordens,
    usuarios,
    salvando,
    erro,
    onClose,
    onSubmit,
}) {
    const [form, setForm] =
        useState({
            ordemServicoId: "",
            responsavelId: "",
            inicio: "",
            fim: "",
            observacoes: "",
        });


    useEffect(() => {
        if (!aberto) {
            return;
        }

        setForm({
            ordemServicoId: "",
            responsavelId: "",
            inicio: "",
            fim: "",
            observacoes: "",
        });

    }, [aberto]);


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


    function enviar(
        event
    ) {
        event.preventDefault();

        if (
            new Date(form.fim)
            <= new Date(form.inicio)
        ) {
            return;
        }


        onSubmit({
            ordem_servico_id:
                Number(
                    form.ordemServicoId
                ),

            responsavel_id:
                form.responsavelId
                    ? Number(
                        form.responsavelId
                    )
                    : null,

            inicio:
                form.inicio,

            fim:
                form.fim,

            observacoes:
                form.observacoes.trim()
                || null,
        });
    }


    if (!aberto) {
        return null;
    }


    return (
        <div
            className="agendamento-overlay"
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

            <div className="agendamento-modal">

                <header className="agendamento-modal-header">

                    <div>
                        <h2>
                            Agendar serviço
                        </h2>

                        <p>
                            Vincule uma ordem de serviço
                            ao calendário.
                        </p>
                    </div>


                    <button
                        type="button"
                        onClick={onClose}
                        disabled={salvando}
                    >
                        <i className="bi bi-x-lg" />
                    </button>

                </header>


                <form
                    onSubmit={enviar}
                    className="agendamento-form"
                >

                    <div className="agendamento-field full">

                        <label>
                            Ordem de serviço *
                        </label>

                        <select
                            required
                            value={
                                form.ordemServicoId
                            }
                            onChange={(event) =>
                                atualizarCampo(
                                    "ordemServicoId",
                                    event.target.value
                                )
                            }
                        >
                            <option value="">
                                Selecione uma OS...
                            </option>

                            {ordens.map(
                                (ordem) => (
                                    <option
                                        key={ordem.id}
                                        value={ordem.id}
                                    >
                                        OS #{ordem.numero}
                                        {" — "}
                                        {ordem.titulo}
                                    </option>
                                )
                            )}

                        </select>

                    </div>


                    <div className="agendamento-grid">

                        <div className="agendamento-field">

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


                        <div className="agendamento-field">

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

                    </div>


                    <div className="agendamento-field full">

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

                            {usuarios.map(
                                (usuario) => (
                                    <option
                                        key={usuario.id}
                                        value={usuario.id}
                                    >
                                        {
                                            usuario.nome
                                            ||
                                            usuario.username
                                        }
                                    </option>
                                )
                            )}

                        </select>

                    </div>


                    <div className="agendamento-field full">

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
                            placeholder="Informações adicionais sobre o serviço..."
                        />

                    </div>


                    {erro && (
                        <div className="agendamento-error">

                            <i className="bi bi-exclamation-circle" />

                            {erro}

                        </div>
                    )}


                    <footer className="agendamento-footer">

                        <button
                            type="button"
                            className="agendamento-cancel"
                            onClick={onClose}
                            disabled={salvando}
                        >
                            Cancelar
                        </button>


                        <button
                            type="submit"
                            className="agendamento-submit"
                            disabled={salvando}
                        >
                            {
                                salvando
                                    ? "Agendando..."
                                    : "Criar agendamento"
                            }
                        </button>

                    </footer>

                </form>

            </div>

        </div>
    );
}


export default AgendamentoModal;