import {
    useEffect,
    useState,
} from "react";

import "./MaquinaFormModal.css";


const FORM_INICIAL = {
    identificacao: "",
    fabricante: "",
    modelo: "",
    categoria: "",
    ano: "",
    localizacao: "",
    status: "OPERANDO",
    controla_telemetria: false,
};


function MaquinaFormModal({
    aberto,
    maquina,
    salvando,
    erro,
    onClose,
    onSubmit,
}) {
    const [form, setForm] =
        useState(FORM_INICIAL);


    const editando =
        Boolean(maquina);


    useEffect(() => {
        if (!aberto) {
            return;
        }

        if (maquina) {
            setForm({
                identificacao:
                    maquina.identificacao
                    || "",

                fabricante:
                    maquina.fabricante
                    || "",

                modelo:
                    maquina.modelo
                    || "",

                categoria:
                    maquina.categoria
                    || "",

                ano:
                    maquina.ano
                    ?? "",

                localizacao:
                    maquina.localizacao
                    || "",

                status:
                    maquina.status
                    || "OPERANDO",

                controla_telemetria:
                    Boolean(
                        maquina.controla_telemetria
                    ),
            });

            return;
        }

        setForm(
            FORM_INICIAL
        );

    }, [
        aberto,
        maquina,
    ]);


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


    function handleSubmit(
        event
    ) {
        event.preventDefault();

        const dados = {
            identificacao:
                form.identificacao.trim(),

            fabricante:
                form.fabricante.trim(),

            modelo:
                form.modelo.trim(),

            categoria:
                form.categoria.trim() || null,

            ano:
                form.ano === ""
                    ? null
                    : Number(form.ano),

            localizacao:
                form.localizacao
                    .trim()
                    || null,

            status:
                form.status,

            controla_telemetria:
                form.controla_telemetria,
        };

        onSubmit(dados);
    }


    if (!aberto) {
        return null;
    }


    return (
        <div
            className="modal-overlay"
            onMouseDown={
                (event) => {
                    if (
                        event.target
                        === event.currentTarget
                        &&
                        !salvando
                    ) {
                        onClose();
                    }
                }
            }
        >
            <div className="maquina-modal">

                <header className="maquina-modal-header">

                    <div>
                        <h2>
                            {
                                editando
                                    ? "Editar maquinário"
                                    : "Novo maquinário"
                            }
                        </h2>

                        <p>
                            {
                                editando
                                    ? "Atualize os dados do maquinário."
                                    : "Cadastre um novo maquinário na frota."
                            }
                        </p>
                    </div>


                    <button
                        type="button"
                        className="modal-close"
                        onClick={onClose}
                        disabled={salvando}
                    >
                        <i className="bi bi-x-lg" />
                    </button>

                </header>


                <form
                    onSubmit={handleSubmit}
                    className="maquina-form"
                >

                    <div className="maquina-form-grid">

                        <div className="maquina-form-field full">
                            <label htmlFor="identificacao">
                                Identificação *
                            </label>

                            <input
                                id="identificacao"
                                type="text"
                                maxLength={100}
                                required
                                value={
                                    form.identificacao
                                }
                                onChange={
                                    (event) =>
                                        atualizarCampo(
                                            "identificacao",
                                            event.target.value
                                        )
                                }
                                placeholder="Ex.: TR-001"
                                disabled={salvando}
                            />
                        </div>


                        <div className="maquina-form-field">
                            <label htmlFor="fabricante">
                                Fabricante *
                            </label>

                            <input
                                id="fabricante"
                                type="text"
                                maxLength={100}
                                required
                                value={
                                    form.fabricante
                                }
                                onChange={
                                    (event) =>
                                        atualizarCampo(
                                            "fabricante",
                                            event.target.value
                                        )
                                }
                                placeholder="Ex.: John Deere"
                                disabled={salvando}
                            />
                        </div>


                        <div className="maquina-form-field">
                            <label htmlFor="modelo">
                                Modelo *
                            </label>

                            <input
                                id="modelo"
                                type="text"
                                maxLength={150}
                                required
                                value={
                                    form.modelo
                                }
                                onChange={
                                    (event) =>
                                        atualizarCampo(
                                            "modelo",
                                            event.target.value
                                        )
                                }
                                placeholder="Ex.: 6110J"
                                disabled={salvando}
                            />
                        </div>

                        <div className="maquina-form-field full">
                            <label htmlFor="categoria">Categoria operacional</label>
                            <select id="categoria" value={form.categoria}
                                onChange={(event) => atualizarCampo("categoria", event.target.value)}
                                disabled={salvando}>
                                <option value="">Não classificada</option>
                                <option value="TRATOR">Trator</option>
                                <option value="COLHEITADEIRA">Colheitadeira</option>
                                <option value="PULVERIZADOR">Pulverizador</option>
                                <option value="CAMINHAO">Caminhão</option>
                                <option value="OUTRA">Outra máquina</option>
                            </select>
                            <small>Usada para filtrar recursos; cadastros antigos podem ser classificados ao editar.</small>
                        </div>


                        <div className="maquina-form-field">
                            <label htmlFor="ano">
                                Ano
                            </label>

                            <input
                                id="ano"
                                type="number"
                                min="1900"
                                max="2100"
                                value={
                                    form.ano
                                }
                                onChange={
                                    (event) =>
                                        atualizarCampo(
                                            "ano",
                                            event.target.value
                                        )
                                }
                                placeholder="2026"
                                disabled={salvando}
                            />
                        </div>


                        <div className="maquina-form-field">
                            <label htmlFor="status">
                                Status *
                            </label>

                            <select
                                id="status"
                                value={
                                    form.status
                                }
                                onChange={
                                    (event) =>
                                        atualizarCampo(
                                            "status",
                                            event.target.value
                                        )
                                }
                                disabled={salvando}
                            >
                                <option value="OPERANDO">
                                    Operando
                                </option>

                                <option value="PARADA">
                                    Parada
                                </option>

                                <option value="MANUTENCAO">
                                    Manutenção
                                </option>

                                <option value="INATIVA">
                                    Inativa
                                </option>
                            </select>
                        </div>


                        <div className="maquina-form-field full">
                            <label htmlFor="localizacao">
                                Localização
                            </label>

                            <input
                                id="localizacao"
                                type="text"
                                maxLength={150}
                                value={
                                    form.localizacao
                                }
                                onChange={
                                    (event) =>
                                        atualizarCampo(
                                            "localizacao",
                                            event.target.value
                                        )
                                }
                                placeholder="Ex.: Pátio Norte"
                                disabled={salvando}
                            />
                        </div>


                        <label className="telemetria-check full">

                            <input
                                type="checkbox"
                                checked={
                                    form.controla_telemetria
                                }
                                onChange={
                                    (event) =>
                                        atualizarCampo(
                                            "controla_telemetria",
                                            event.target.checked
                                        )
                                }
                                disabled={salvando}
                            />

                            <span className="telemetria-check-box">
                                <i className="bi bi-check-lg" />
                            </span>

                            <div>
                                <strong>
                                    Controla telemetria
                                </strong>

                                <span>
                                    Marque se este maquinário
                                    possui monitoramento de
                                    telemetria.
                                </span>
                            </div>

                        </label>

                    </div>


                    {erro && (
                        <div className="maquina-form-error">

                            <i className="bi bi-exclamation-circle" />

                            {erro}

                        </div>
                    )}


                    <footer className="maquina-modal-footer">

                        <button
                            type="button"
                            className="modal-cancel"
                            onClick={onClose}
                            disabled={salvando}
                        >
                            Cancelar
                        </button>


                        <button
                            type="submit"
                            className="modal-save"
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

                                            {
                                                editando
                                                    ? "Salvar alterações"
                                                    : "Cadastrar"
                                            }
                                        </>
                                    )
                            }
                        </button>

                    </footer>

                </form>

            </div>
        </div>
    );
}


export default MaquinaFormModal;
