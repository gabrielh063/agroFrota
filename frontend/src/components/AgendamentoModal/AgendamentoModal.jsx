import {
    useEffect,
    useRef,
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
    const dialogRef = useRef(null);
    const closeRef = useRef(onClose);
    const savingRef = useRef(salvando);

    useEffect(() => {
        closeRef.current = onClose;
        savingRef.current = salvando;
    }, [onClose, salvando]);

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

    useEffect(() => {
        if (!aberto) {
            return;
        }

        const dialog = dialogRef.current;
        const previous = document.activeElement;
        const focusable = () => [...dialog.querySelectorAll(
            'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])'
        )];

        requestAnimationFrame(() => focusable()[0]?.focus());

        function handleKeyDown(event) {
            if (event.key === "Escape" && !savingRef.current) {
                event.preventDefault();
                closeRef.current();
                return;
            }

            if (event.key !== "Tab") {
                return;
            }

            const items = focusable();
            const first = items[0];
            const last = items[items.length - 1];

            if (!first || !last) {
                event.preventDefault();
            } else if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        }

        document.addEventListener("keydown", handleKeyDown);
        return () => {
            document.removeEventListener("keydown", handleKeyDown);
            previous?.focus?.();
        };
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

            <div
                className="agendamento-modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="agendamento-modal-title"
                ref={dialogRef}
                tabIndex={-1}
            >

                <header className="agendamento-modal-header">

                    <div>
                        <h2 id="agendamento-modal-title">
                            Agendar serviço
                        </h2>

                        <p>
                            Vincule uma ordem de serviço
                            ao calendário.
                        </p>
                    </div>


                    <button
                        type="button"
                        aria-label="Fechar agendamento"
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

                        <label htmlFor="agendamento-os">
                            Ordem de serviço *
                        </label>

                        <select
                            id="agendamento-os"
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

                            <label htmlFor="agendamento-inicio">
                                Início *
                            </label>

                            <input
                                id="agendamento-inicio"
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

                            <label htmlFor="agendamento-fim">
                                Fim *
                            </label>

                            <input
                                id="agendamento-fim"
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

                        <label htmlFor="agendamento-responsavel">
                            Responsável
                        </label>

                        <select
                            id="agendamento-responsavel"
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

                        <label htmlFor="agendamento-observacoes">
                            Observações
                        </label>

                        <textarea
                            id="agendamento-observacoes"
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
                        <div className="agendamento-error" role="alert">

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
