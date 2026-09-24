from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


TIPOS_MANUTENCAO = {
    "PREVENTIVA",
    "CORRETIVA",
    "PREDITIVA",
}


STATUS_MANUTENCAO = {
    "EM_ANDAMENTO",
    "CONCLUIDA",
    "CANCELADA",
}


class ManutencaoCriarSchema(BaseModel):
    ordem_servico_id: int = Field(gt=0)
    responsavel_id: int | None = Field(default=None, gt=0)

    tipo: str = Field(
        min_length=1,
        max_length=30
    )

    inicio: datetime

    fim: datetime | None = None

    descricao: str | None = None

    custo: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2
    )

    observacoes: str | None = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, valor: str) -> str:
        valor = valor.upper()

        if valor not in TIPOS_MANUTENCAO:
            raise ValueError(
                "Tipo de manutenção inválido. "
                "Use PREVENTIVA, CORRETIVA ou PREDITIVA."
            )

        return valor

    @field_validator("fim")
    @classmethod
    def validar_fim(cls, valor: datetime | None, info):
        inicio = info.data.get("inicio")

        if (
            valor is not None
            and inicio is not None
            and valor <= inicio
        ):
            raise ValueError(
                "A data/hora final deve ser posterior à inicial."
            )

        return valor


class ManutencaoAtualizarSchema(BaseModel):
    responsavel_id: int | None = Field(
        default=None,
        gt=0
    )

    tipo: str | None = Field(
        default=None,
        min_length=1,
        max_length=30
    )

    inicio: datetime | None = None

    fim: datetime | None = None

    descricao: str | None = None

    custo: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2
    )

    status: str | None = Field(
        default=None,
        min_length=1,
        max_length=30
    )

    observacoes: str | None = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, valor: str | None) -> str | None:
        if valor is None:
            return None

        valor = valor.upper()

        if valor not in TIPOS_MANUTENCAO:
            raise ValueError(
                "Tipo de manutenção inválido. "
                "Use PREVENTIVA, CORRETIVA ou PREDITIVA."
            )

        return valor

    @field_validator("status")
    @classmethod
    def validar_status(cls, valor: str | None) -> str | None:
        if valor is None:
            return None

        valor = valor.upper()

        if valor not in STATUS_MANUTENCAO:
            raise ValueError(
                "Status inválido. "
                "Use EM_ANDAMENTO, CONCLUIDA ou CANCELADA."
            )

        return valor


class ManutencaoRespostaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ordem_servico_id: int
    responsavel_id: int | None

    tipo: str

    inicio: datetime
    fim: datetime | None

    descricao: str | None

    custo: Decimal | None

    status: str

    observacoes: str | None