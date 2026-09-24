from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


TIPOS_OS = {
    "SERVICO",
    "MANUTENCAO",
}

PRIORIDADES_OS = {
    "BAIXA",
    "MEDIA",
    "ALTA",
    "URGENTE",
}

STATUS_OS = {
    "ABERTA",
    "EM_ANDAMENTO",
    "CONCLUIDA",
    "CANCELADA",
}


class OrdemServicoCriarSchema(BaseModel):

    tipo: str = Field(
        min_length=1,
        max_length=30
    )

    titulo: str = Field(
        min_length=1,
        max_length=150
    )

    descricao: str | None = None

    maquina_id: int | None = Field(
        default=None,
        gt=0
    )

    equipamento_id: int | None = Field(
        default=None,
        gt=0
    )

    operador_id: int | None = Field(
        default=None,
        gt=0
    )

    responsavel_id: int | None = Field(
        default=None,
        gt=0
    )

    prioridade: str = Field(
        default="MEDIA",
        min_length=1,
        max_length=30
    )

    prazo: datetime | None = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, valor: str) -> str:

        valor = valor.upper()

        if valor not in TIPOS_OS:
            raise ValueError(
                "Tipo de OS inválido. "
                "Use SERVICO ou MANUTENCAO."
            )

        return valor

    @field_validator("prioridade")
    @classmethod
    def validar_prioridade(cls, valor: str) -> str:

        valor = valor.upper()

        if valor not in PRIORIDADES_OS:
            raise ValueError(
                "Prioridade inválida. "
                "Use BAIXA, MEDIA, ALTA ou URGENTE."
            )

        return valor


class OrdemServicoAtualizarSchema(BaseModel):

    tipo: str | None = Field(
        default=None,
        min_length=1,
        max_length=30
    )

    titulo: str | None = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    descricao: str | None = None

    maquina_id: int | None = Field(
        default=None,
        gt=0
    )

    equipamento_id: int | None = Field(
        default=None,
        gt=0
    )

    operador_id: int | None = Field(
        default=None,
        gt=0
    )

    responsavel_id: int | None = Field(
        default=None,
        gt=0
    )

    prioridade: str | None = Field(
        default=None,
        min_length=1,
        max_length=30
    )

    status: str | None = Field(
        default=None,
        min_length=1,
        max_length=30
    )

    prazo: datetime | None = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, valor: str | None) -> str | None:

        if valor is None:
            return valor

        valor = valor.upper()

        if valor not in TIPOS_OS:
            raise ValueError(
                "Tipo de OS inválido. "
                "Use SERVICO ou MANUTENCAO."
            )

        return valor

    @field_validator("prioridade")
    @classmethod
    def validar_prioridade(cls, valor: str | None) -> str | None:

        if valor is None:
            return valor

        valor = valor.upper()

        if valor not in PRIORIDADES_OS:
            raise ValueError(
                "Prioridade inválida. "
                "Use BAIXA, MEDIA, ALTA ou URGENTE."
            )

        return valor

    @field_validator("status")
    @classmethod
    def validar_status(cls, valor: str | None) -> str | None:

        if valor is None:
            return valor

        valor = valor.upper()

        if valor not in STATUS_OS:
            raise ValueError(
                "Status de OS inválido."
            )

        return valor


class OrdemServicoRespostaSchema(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    numero: int
    tipo: str
    titulo: str
    descricao: str | None
    maquina_id: int | None
    equipamento_id: int | None
    operador_id: int | None
    responsavel_id: int | None
    prioridade: str
    status: str
    prazo: datetime | None
    ativo: bool