from pydantic import BaseModel, ConfigDict, Field


class PerfilCriarSchema(BaseModel):
    nome: str = Field(
        min_length=1,
        max_length=100
    )

    descricao: str | None = Field(
        default=None,
        max_length=255
    )


class PerfilAtualizarSchema(BaseModel):
    nome: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    descricao: str | None = Field(
        default=None,
        max_length=255
    )

    ativo: bool | None = None


class PerfilRespostaSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    nome: str
    descricao: str | None
    ativo: bool