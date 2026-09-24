from pydantic import BaseModel, Field


class PerfilPermissaoSchema(BaseModel):

    permissao_id: int = Field(
        gt=0
    )