from pydantic import BaseModel, ConfigDict, Field


class EquipamentoCriarSchema(BaseModel):
    identificacao: str = Field(
        min_length=1,
        max_length=100
    )

    nome: str = Field(
        min_length=1,
        max_length=150
    )

    tipo: str = Field(
        min_length=1,
        max_length=100
    )

    fabricante: str | None = Field(
        default=None,
        max_length=100
    )

    modelo: str | None = Field(
        default=None,
        max_length=150
    )

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
        default="DISPONIVEL",
        pattern="^(DISPONIVEL|EM_USO|MANUTENCAO|INATIVO)$"
    )


class EquipamentoAtualizarSchema(BaseModel):
    identificacao: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    nome: str | None = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    tipo: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    fabricante: str | None = Field(
        default=None,
        max_length=100
    )

    modelo: str | None = Field(
        default=None,
        max_length=150
    )

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
        pattern="^(DISPONIVEL|EM_USO|MANUTENCAO|INATIVO)$"
    )

    ativo: bool | None = None


class EquipamentoRespostaSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    identificacao: str
    nome: str
    tipo: str
    fabricante: str | None
    modelo: str | None
    ano: int | None
    localizacao: str | None
    status: str
    ativo: bool