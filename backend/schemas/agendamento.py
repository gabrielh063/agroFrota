from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


STATUS_AGENDAMENTO = {
    "AGENDADO",
    "EM_ANDAMENTO",
    "CONCLUIDO",
    "CANCELADO",
}


class AgendamentoCriarSchema(BaseModel):
    ordem_servico_id: int = Field(gt=0)
    responsavel_id: int | None = Field(default=None, gt=0)
    inicio: datetime
    fim: datetime
    observacoes: str | None = None

    @field_validator("fim")
    @classmethod
    def validar_fim(cls, valor: datetime, info):
        inicio = info.data.get("inicio")

        if inicio is not None and valor <= inicio:
            raise ValueError(
                "A data/hora final deve ser posterior à inicial."
            )

        return valor


class AgendamentoAtualizarSchema(BaseModel):
    inicio: datetime | None = None
    fim: datetime | None = None
    responsavel_id: int | None = Field(default=None, gt=0)
    status: str | None = Field(
        default=None,
        min_length=1,
        max_length=30
    )
    observacoes: str | None = None

    @field_validator("status")
    @classmethod
    def validar_status(cls, valor: str | None) -> str | None:
        if valor is None:
            return None

        valor = valor.upper()

        if valor not in STATUS_AGENDAMENTO:
            raise ValueError(
                "Status inválido. Use AGENDADO, EM_ANDAMENTO, "
                "CONCLUIDO ou CANCELADO."
            )

        return valor


class AgendamentoRespostaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ordem_servico_id: int
    responsavel_id: int | None
    inicio: datetime
    fim: datetime
    status: str
    observacoes: str | None