from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCriarSchema(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    username: str = Field(min_length=1, max_length=80)
    senha: str = Field(min_length=6, max_length=128)
    email: EmailStr | None = None
    cargo_id: int | None = Field(default=None, gt=0)
    perfil_id: int = Field(gt=0)


class UsuarioAtualizarSchema(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=150)
    username: str | None = Field(default=None, min_length=1, max_length=80)
    email: EmailStr | None = None
    cargo_id: int | None = Field(default=None, gt=0)
    perfil_id: int | None = Field(default=None, gt=0)
    ativo: bool | None = None


class UsuarioRespostaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    username: str
    email: str | None
    cargo_id: int | None
    perfil_id: int
    ativo: bool
    
class UsuarioAlterarSenhaSchema(BaseModel):
    senha_atual: str = Field(
        min_length=1,
        max_length=128
    )

    nova_senha: str = Field(
        min_length=6,
        max_length=128
    )   