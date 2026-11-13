from pydantic import BaseModel, ConfigDict, Field


class MaquinaCriarSchema(BaseModel):
    identificacao: str = Field(
        min_length=1,
        max_length=100
    )

    modelo: str = Field(
        min_length=1,
        max_length=150
    )

    fabricante: str = Field(
        min_length=1,
        max_length=100
    )

    categoria: str | None = Field(default=None, max_length=60)

    ano: int | None = Field(
        default=None,
        ge=1900,
        le=2100
    )

    localizacao: str | None = Field(
        default=None,
        max_length=150
    )

    status: str = Field(
        default="OPERANDO",
        pattern="^(OPERANDO|PARADA|MANUTENCAO|INATIVA)$"
    )

    controla_telemetria: bool = False


class MaquinaAtualizarSchema(BaseModel):
    identificacao: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    modelo: str | None = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    fabricante: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    categoria: str | None = Field(default=None, max_length=60)

    ano: int | None = Field(
        default=None,
        ge=1900,
        le=2100
    )

    localizacao: str | None = Field(
        default=None,
        max_length=150
    )

    status: str | None = Field(
        default=None,
        pattern="^(OPERANDO|PARADA|MANUTENCAO|INATIVA)$"
    )

    controla_telemetria: bool | None = None

    ativo: bool | None = None


class MaquinaRespostaSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    identificacao: str
    modelo: str
    fabricante: str
    categoria: str | None = None
    ano: int | None
    localizacao: str | None
    status: str
    controla_telemetria: bool
    ativo: bool
