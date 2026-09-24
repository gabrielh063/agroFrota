import {
    useEffect,
    useState,
} from "react";

import "./EquipamentoFormModal.css";


const FORM_INICIAL = {
    identificacao: "",
    nome: "",
    tipo: "",
    fabricante: "",
    modelo: "",
    ano: "",
    localizacao: "",
    status: "DISPONIVEL",
};


function EquipamentoFormModal({
    aberto,
    equipamento,
    salvando,
    erro,
    onClose,
    onSubmit,
}) {
    const [form, setForm] =
        useState(FORM_INICIAL);


    const editando =
        Boolean(equipamento);


    useEffect(() => {
        if (!aberto) {
            return;
        }

        if (equipamento) {
            setForm({
                identificacao:
                    equipamento.identificacao
                    || "",

                nome:
                    equipamento.nome
                    || "",

                tipo:
                    equipamento.tipo
                    || "",

                fabricante:
                    equipamento.fabricante
                    || "",

                modelo:
                    equipamento.modelo
                    || "",

                ano:
                    equipamento.ano
                    ?? "",

                localizacao:
                    equipamento.localizacao
                    || "",

                status:
                    equipamento.status
                    || "DISPONIVEL",
            });

            return;
        }

        setForm(FORM_INICIAL);

    }, [
        aberto,
        equipamento,
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

            nome:
                form.nome.trim(),

            tipo:
                form.tipo.trim(),

            fabricante:
                form.fabricante.trim(),

            modelo:
                form.modelo.trim(),

            ano:
                form.ano === ""
                    ? null
                    : Number(form.ano),

            localizacao:
                form.localizacao.trim(),

            status:
                form.status,
        };

        onSubmit(dados);
    }


    if (!aberto) {
        return null;
    }


    return (
        <div
            className="equipamento-modal-overlay"
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

            <div className="equipamento-modal">

                <header className="equipamento-modal-header">

                    <div>
                        <h2>
                            {
                                editando
                                    ? "Editar equipamento"
                                    : "Novo equipamento"
                            }
                        </h2>

                        <p>
                            {
                                editando
                                    ? "Atualize os dados do equipamento."
                                    : "Cadastre um novo equipamento na frota."
                            }
                        </p>
                    </div>


                    <button
                        type="button"
                        className="equipamento-modal-close"
                        onClick={onClose}
                        disabled={salvando}
                    >
                        <i className="bi bi-x-lg" />
                    </button>

                </header>


                <form
                    className="equipamento-form"
                    onSubmit={handleSubmit}
                >

                    <div className="equipamento-form-grid">

                        <div className="equipamento-form-field">
                            <label>
                                Identificação *
                            </label>

                            <input
                                required
                                maxLength={100}
                                value={form.identificacao}
                                onChange={(event) =>
                                    atualizarCampo(
                                        "identificacao",
                                        event.target.value
                                    )
                                }
                                placeholder="Ex.: IMP-001"
                            />
                        </div>


                        <div className="equipamento-form-field">
                            <label>
                                Nome *
                            </label>

                            <input
                                required
                                maxLength={150}
                                value={form.nome}
                                onChange={(event) =>
                                    atualizarCampo(
                                        "nome",
                                        event.target.value
                                    )
                                }
                                placeholder="Ex.: Grade aradora"
                            />
                        </div>


                        <div className="equipamento-form-field full">
                            <label>
                                Tipo *
                            </label>

                            <input
                                required
                                maxLength={100}
                                value={form.tipo}
                                onChange={(event) =>
                                    atualizarCampo(
                                        "tipo",
                                        event.target.value
                                    )
                                }
                                placeholder="Ex.: Implemento agrícola"
                            />
                        </div>


                        <div className="equipamento-form-field">
                            <label>
                                Fabricante
                            </label>

                            <input
                                maxLength={100}
                                value={form.fabricante}
                                onChange={(event) =>
                                    atualizarCampo(
                                        "fabricante",
                                        event.target.value
                                    )
                                }
                                placeholder="Ex.: Baldan"
                            />
                        </div>


                        <div className="equipamento-form-field">
                            <label>
                                Modelo
                            </label>

                            <input
                                maxLength={150}
                                value={form.modelo}
                                onChange={(event) =>
                                    atualizarCampo(
                                        "modelo",
                                        event.target.value
                                    )
                                }
                                placeholder="Ex.: CRSG 20"
                            />
                        </div>


                        <div className="equipamento-form-field">
                            <label>
                                Ano
                            </label>

                            <input
                                type="number"
                                min="1900"
                                max="2100"
                                value={form.ano}
                                onChange={(event) =>
                                    atualizarCampo(
                                        "ano",
                                        event.target.value
                                    )
                                }
                                placeholder="2025"
                            />
                        </div>


                        <div className="equipamento-form-field">
                            <label>
                                Status
                            </label>

                            <select
                                value={form.status}
                                onChange={(event) =>
                                    atualizarCampo(
                                        "status",
                                        event.target.value
                                    )
                                }
                            >
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
                        </div>


                        <div className="equipamento-form-field full">
                            <label>
                                Localização
                            </label>

                            <input
                                maxLength={150}
                                value={form.localizacao}
                                onChange={(event) =>
                                    atualizarCampo(
                                        "localizacao",
                                        event.target.value
                                    )
                                }
                                placeholder="Ex.: Galpão de implementos"
                            />
                        </div>

                    </div>


                    {erro && (
                        <div className="equipamento-form-error">

                            <i className="bi bi-exclamation-circle" />

                            {erro}

                        </div>
                    )}


                    <footer className="equipamento-modal-footer">

                        <button
                            type="button"
                            className="equipamento-cancel"
                            onClick={onClose}
                            disabled={salvando}
                        >
                            Cancelar
                        </button>


                        <button
                            type="submit"
                            className="equipamento-save"
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


export default EquipamentoFormModal;