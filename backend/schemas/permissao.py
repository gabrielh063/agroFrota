from pydantic import BaseModel, ConfigDict, Field


class PermissaoCriarSchema(BaseModel):
    codigo: str = Field(
        min_length=1,
        max_length=100
    )

    descricao: str | None = Field(
        default=None,
        max_length=255
    )


class PermissaoAtualizarSchema(BaseModel):
    codigo: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    descricao: str | None = Field(
        default=None,
        max_length=255
    )


class PermissaoRespostaSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    codigo: str
    descricao: str | None