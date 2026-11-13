# AGRO-FINAL-08 — Correção da aba Ordens de Serviço

**Data:** 13/11/2026  
**Base:** PR #11, `def9aafb94effaffd94b0be0be7b9c50d9975d02`  
**Estado:** em validação de publicação e atualização privada

## Causa raiz

Os logs do container `agrofrota-infra-01-backend-1` registraram a requisição Safari autenticada `GET /api/ordens-servico/?apenas_ativas=false` com HTTP 500 às 14:59:34. A exceção foi `sqlalchemy.exc.TimeoutError: QueuePool limit of size 2 overflow 0 reached, connection timed out, timeout 5.00`.

O resolvedor de tenant mantinha uma conexão aberta durante toda a view. O middleware de permissão usava essa sessão, mas as consultas de OS e de permissões abriam outra sessão do mesmo engine por meio dos serviços. Com as três chamadas concorrentes da tela de OS, a conexão de validação ficava ocupada junto da conexão do serviço; o pool tenant tinha duas conexões por worker e sem overflow. Os logs também registraram 500 de `/api/perfis/<id>/permissoes` pela mesma exceção de pool. Foi uma causa comum de contenção de sessões, reproduzida em duas rotas distintas.

O código da instalação correspondeu ao publicado: o hash de `backend/middleware/permissions.py` no container foi igual ao arquivo do HEAD do PR (`92652e8f…`) e `backend/services/ordem_servico_service.py` também (`bd3559cf…`). A imagem ativa era `sha256:0a0705f…`, do projeto Compose privado `agrofrota-infra-01`.

## Correção e regressão

Após a permissão autorizada, o middleware fecha a sessão usada para resolver tenant/perfil antes de executar a view. A sessão continua reutilizável pelas rotas que recebem `tenant_session`; serviços com sessão própria já não competem com uma conexão de autorização retida. Nenhuma política de escopo, permissão, tenant ou pool foi alterada.

O servidor MariaDB descartável da suíte agora aceita requests concorrentes. O novo teste cria uma máquina e três OS fictícias, reproduz em paralelo os GETs de OS, máquinas e equipamentos feitos por `OrdensServico.jsx`, valida as três OS na listagem e exercita chamadas simultâneas de permissões de perfis. Nenhum dado da instalação persistente é usado pelo teste.

## Integridade anterior à atualização

Backup pré-deploy privado criado em `/home/gabriel/.config/agrofrota-infra-01/agro-final-08-predeploy.sql`, fora do repositório, com modo `0600`. SHA-256: `f2206465c08443135d7c9f8eac7b624df5fb3a9f5a476242d5091c84ee91a45f`; tamanho: 30.341 bytes.

Readback agregado anterior à atualização: 1 tenant, 7 usuários, 3 máquinas e 3 ordens de serviço. A comparação pós-deploy será registrada abaixo.

## Validações

- Backend em MariaDB descartável: **267 aprovados**, 74 avisos de depreciação preexistentes.
- Build frontend: **passou** (`npm --prefix frontend run build`).
- Escopo das OS por sete perfis e matriz RBAC: incluído na suíte completa; aprovação pós-correção.
- Calendário e viewport 390×844: pendentes de confirmação pós-deploy.
- CI GitHub, HTTPS Tailscale e leitura pós-deploy: pendentes.

## Publicação e instalação privada

Esta correção será publicada na branch `fix/agro-final-07-mobile-tenant-rbac`, na PR #11. Não haverá merge automático.
