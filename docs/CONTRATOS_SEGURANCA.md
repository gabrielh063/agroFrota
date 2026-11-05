# Contratos de segurança — estado inicial

Base: `1711156`. Este documento distingue interfaces existentes de lacunas; não pressupõe que os serviços operacionais já apliquem escopo por objeto.

## Autenticação e sessão

`POST /api/auth/login` recebe JSON com `username`, `senha` e `database_name`. Em sucesso retorna `success`, `message` e `data` com `access_token`, `usuario` e `tenant`. Envie o token em `Authorization: Bearer <access_token>`. `POST /api/auth/logout` autenticado incrementa a versão persistente e revoga todas as sessões do usuário; descarte o token depois da confirmação. Não há refresh token. A versão atual usa bearer token, não cookie de sessão; não introduzimos transporte por cookie ou contrato CSRF.

O servidor resolve tenant e usuário a partir do token e consulta o estado atual do tenant, usuário, perfil e versão de sessão a cada requisição. Não aceite ator, tenant ou permissões enviados pelo cliente como autoridade. O perfil no token não é autoridade atual.

## Usuário e permissões

`GET /api/auth/me` autenticado retorna `success` e `data` com `usuario`, `tenant` e `permissoes` (lista ordenada de códigos atuais). O objeto do login é um retrato inicial, não uma fonte de autorização. Os códigos atualmente existentes e seus seeds estão em `backend/services/seed_service.py`; consulte-os antes de integrar. A matriz de sete perfis e escopos ainda não está implementada nesta base.

## Erros

As rotas existentes geralmente retornam JSON com `success: false` e `message`; validação pode acrescentar `errors`. Token inválido ou revogado normalmente retorna 401; ausência de permissão retorna 403. Há variações legadas de status, inclusive tenant inexistente 404 e tenant inativo 403; não dependa do texto da mensagem. Falhas inesperadas retornam 500.

## Integração de serviços

Nas rotas, a ordem existente é `@autenticar()`, `@resolver_tenant(Config)` e `@exigir_permissao(CODIGO)`. O contexto resolvido inclui `database_name`, `usuario_autenticado_id`, `usuario_perfil_id` atual e `tenant_session`. O decorador de permissão verifica o perfil ativo no banco. Ele verifica ação, não propriedade ou atribuição do objeto: serviços operacionais devem negar acesso fora do escopo autorizado. Ainda não há helper comum de escopo implementado; não tratar IDs de objeto fornecidos pelo cliente como prova de acesso. O contexto `ContextoAdministrativo` e `services.admin_policy.autorizar` são específicos das mutações administrativas, não um helper genérico de escopo.

A política administrativa e o bloqueio de último administrador estão em [POLITICA_ADMINISTRATIVA.md](POLITICA_ADMINISTRATIVA.md); cargos não concedem privilégios. Sessões estão descritas em [SESSOES.md](SESSOES.md).
