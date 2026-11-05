# Contratos de segurança — estado inicial

Base: `1711156`. Este documento distingue interfaces existentes de lacunas; não pressupõe que os serviços operacionais já apliquem escopo por objeto.

## Autenticação e sessão

`POST /api/auth/login` recebe JSON com `username`, `senha` e `database_name`. Em sucesso retorna `success`, `message` e `data` com `access_token`, `usuario` e `tenant`. Envie o token em `Authorization: Bearer <access_token>`. `POST /api/auth/logout` autenticado incrementa a versão persistente e revoga todas as sessões do usuário; descarte o token depois da confirmação. Não há refresh token. A versão atual usa bearer token, não cookie de sessão; não introduzimos transporte por cookie ou contrato CSRF.

O servidor resolve tenant e usuário a partir do token e consulta o estado atual do tenant, usuário, perfil e versão de sessão a cada requisição. Não aceite ator, tenant ou permissões enviados pelo cliente como autoridade. O perfil no token não é autoridade atual.

## Usuário e permissões

`GET /api/auth/me` autenticado retorna `success` e `data` com `usuario`, `tenant` e `permissoes` (lista ordenada de códigos atuais). O objeto do login é um retrato inicial, não uma fonte de autorização. Os códigos atualmente existentes e seus seeds estão em `backend/services/seed_service.py`; consulte-os antes de integrar. A matriz fechada e seus escopos estão descritos abaixo.

## Erros

As rotas existentes geralmente retornam JSON com `success: false` e `message`; validação pode acrescentar `errors`. Token inválido ou revogado normalmente retorna 401; ausência de permissão retorna 403. Há variações legadas de status, inclusive tenant inexistente 404 e tenant inativo 403; não dependa do texto da mensagem. Falhas inesperadas retornam 500.

## Integração de serviços

Nas rotas, a ordem existente é `@autenticar()`, `@resolver_tenant(Config)` e `@exigir_permissao(CODIGO)`. O contexto resolvido inclui `database_name`, `usuario_autenticado_id`, `usuario_perfil_id` atual e `tenant_session`. O decorador de permissão verifica o perfil ativo no banco. Ele verifica ação, não propriedade ou atribuição do objeto: serviços operacionais devem negar acesso fora do escopo autorizado. Use o helper comum de escopo descrito abaixo; não tratar IDs fornecidos pelo cliente como prova de acesso. O contexto `ContextoAdministrativo` e `services.admin_policy.autorizar` são específicos das mutações administrativas, não um helper genérico de escopo.

A política administrativa e o bloqueio de último administrador estão em [POLITICA_ADMINISTRATIVA.md](POLITICA_ADMINISTRATIVA.md); cargos não concedem privilégios. Sessões estão descritas em [SESSOES.md](SESSOES.md).

## Matriz e helper de escopo — contrato para integração

O contrato de ação e escopo está definido em `backend/services/matriz_acesso.py` (`MATRIZ`): cada entrada associa um código de permissão a `empresa`, `proprio` ou `atribuicao`. A ausência da ação significa negação. A permissão efetiva do perfil é obrigatória além da matriz. Os sete perfis padrão são `ADMIN_EMPRESA`, `DIRETORIA`, `GESTOR_FROTA`, `ADMINISTRATIVO`, `MANUTENCAO`, `OPERADOR` e `AUDITOR`. Cargo, nome editável e dados do corpo não atribuem escopo. Perfis personalizados sem política reconhecida não recebem escopo operacional automaticamente. Administradores efetivos personalizados mantêm acesso administrativo de empresa somente quando possuem todas as capacidades administrativas e a permissão da operação.

O serviço chama `consultar_autorizado(session, contexto, codigo, consulta, proprio=coluna, atribuicao=coluna)`, importado de `services.escopo`, tanto para lista quanto para detalhe. `session` é a sessão do banco do tenant criado pelo servidor e `contexto` é `kwargs['contexto_administrativo']` de `@resolver_tenant`; não construa contexto com payload. O helper confere banco, usuário, versão e perfil e produz uma consulta SQL filtrada. Permissão ou contexto inválido lança `AdministracaoNegada` (403); falta de coluna exigida pelo escopo produz filtro falso. Para detalhe adicione `where(Modelo.id == id)` **antes ou depois** do helper e responda 404 quando não houver linha. Para atribuição, passe uma coluna que represente vínculo já validado e persistido no banco, nunca um ID do corpo. Relações mais complexas podem ser passadas como expressão SQL booleana comparável ao ator somente após adaptação pelo serviço; o contrato atual recebe coluna escalar de usuário. A base é um banco por tenant: IDs iguais em tenants distintos identificam registros locais. Para escrita, faça a seleção autorizada e a alteração na mesma transação e trate concorrência no serviço.

```python
from sqlalchemy import select
from services.escopo import consultar_autorizado
consulta = consultar_autorizado(session, contexto, 'OS.VISUALIZAR',
    select(OrdemServico), atribuicao=OrdemServico.responsavel_id)
lista = session.execute(consulta).scalars().all()
item = session.execute(consulta.where(OrdemServico.id == ordem_id)).scalar_one_or_none()
# Para registro próprio: codigo USUARIO_PROPRIO_VISUALIZAR, proprio=Usuario.id.
```

A revisão tenant `a71f82c9d410` sucede `9b3b4b41d220`; identifica explicitamente os legados `GERENTE`, `MANUTENCAO` e `OPERADOR`, sem acrescentar permissões ou reatribuir usuários e revoga suas sessões. Um perfil personalizado que coincida com esses nomes recebe no máximo a interseção entre permissões atuais e matriz. Os demais perfis existentes permanecem sem política de escopo; não são concedidos privilégios ao atualizar. O seed cria somente perfis ausentes e não modifica associações de perfis existentes. Para primeiro provisionamento novo usa `ADMIN_EMPRESA`.

A matriz ainda não está aplicada aos serviços operacionais: B deve integrar e testar cada rota, incluindo sua fonte de atribuição. O helper não determina se uma atribuição foi criada legitimamente, nem valida dados enviados na criação; isso pertence ao serviço operacional.
