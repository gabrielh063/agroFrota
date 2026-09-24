from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


TIPOS_INDISPONIBILIDADE = {
    "MANUTENCAO",
    "QUEBRA",
    "FALTA_OPERADOR",
    "FALTA_PECA",
    "AGUARDANDO_SERVICO",
    "OUTRO",
}

STATUS_INDISPONIBILIDADE = {
    "ATIVA",
    "FINALIZADA",
    "CANCELADA",
}


class IndisponibilidadeCriarSchema(BaseModel):
    maquina_id: int | None = Field(default=None, gt=0)
    equipamento_id: int | None = Field(default=None, gt=0)
    manutencao_id: int | None = Field(default=None, gt=0)

    inicio: datetime
    fim: datetime | None = None

    motivo: str = Field(min_length=1, max_length=100)
    tipo: str = Field(min_length=1, max_length=30)

    observacoes: str | None = None

    @model_validator(mode="after")
    def validar_dados(self):
        if self.maquina_id is None and self.equipamento_id is None:
            raise ValueError(
                "Informe uma máquina ou um equipamento."
            )

        if self.maquina_id is not None and self.equipamento_id is not None:
            raise ValueError(
                "Informe apenas uma máquina ou um equipamento."
            )

        if self.fim is not None and self.fim <= self.inicio:
            raise ValueError(
                "O fim deve ser posterior ao início."
            )

        if self.tipo not in TIPOS_INDISPONIBILIDADE:
            raise ValueError(
                f"Tipo de indisponibilidade inválido. "
                f"Permitidos: {', '.join(sorted(TIPOS_INDISPONIBILIDADE))}."
            )

        return self


class IndisponibilidadeAtualizarSchema(BaseModel):
    maquina_id: int | None = Field(default=None, gt=0)
    equipamento_id: int | None = Field(default=None, gt=0)
    manutencao_id: int | None = Field(default=None, gt=0)

    inicio: datetime | None = None
    fim: datetime | None = None

    motivo: str | None = Field(default=None, min_length=1, max_length=100)
    tipo: str | None = Field(default=None, min_length=1, max_length=30)

    observacoes: str | None = None
    status: str | None = None

    @model_validator(mode="after")
    def validar_dados(self):
        if self.maquina_id is not None and self.equipamento_id is not None:
            raise ValueError(
                "Informe apenas uma máquina ou um equipamento."
            )

        if self.inicio is not None and self.fim is not None:
            if self.fim <= self.inicio:
                raise ValueError(
                    "O fim deve ser posterior ao início."
                )

        if self.tipo is not None and self.tipo not in TIPOS_INDISPONIBILIDADE:
            raise ValueError(
                f"Tipo de indisponibilidade inválido. "
                f"Permitidos: {', '.join(sorted(TIPOS_INDISPONIBILIDADE))}."
            )

        if (
            self.status is not None
            and self.status not in STATUS_INDISPONIBILIDADE
        ):
            raise ValueError(
                f"Status inválido. "
                f"Permitidos: {', '.join(sorted(STATUS_INDISPONIBILIDADE))}."
            )

        return self


class IndisponibilidadeRespostaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    maquina_id: int | None
    equipamento_id: int | None
    manutencao_id: int | None

    inicio: datetime
    fim: datetime | None

    motivo: str
    tipo: str
    observacoes: str | None
    status: str

    criado_em: datetime
    atualizado_em: datetime