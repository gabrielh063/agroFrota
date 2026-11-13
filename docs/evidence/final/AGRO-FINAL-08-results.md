# AGRO-FINAL-08 — Correção da aba Ordens de Serviço

**Data:** 13/11/2026  
**Base:** PR #11, `def9aafb94effaffd94b0be0be7b9c50d9975d02`  
**Estado:** `AGRO_FINAL_08_READY`

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
- GitHub Actions para o commit `2ba406f92a8215816a79c97441085cc84eb89655`: backend MariaDB e frontend **SUCCESS** ([run 43450159162](https://github.com/gabrielh063/agroFrota/actions/runs/43450159162)). Lint concluiu com avisos conhecidos; exit code 0.
- HTTPS Tailscale pós-deploy: `/api/health` respondeu HTTP 200 com `status=online`.
- Smoke autenticado pós-deploy, sem registrar tokens/senhas: sete perfis receberam HTTP 200 em Ordens de Serviço e Calendário. Admin Empresa, Diretoria, Gestor de Frota, Administrativo e Auditor viram 3 OS; Manutenção e Operador viram 1 OS cada. Foram conferidos os IDs de atribuição dos perfis limitados.
- Consulta concorrente de permissões de todos os sete perfis: **7/7 HTTP 200**.
- Readback de dados pós-deploy: 1 tenant, 7 usuários, 3 máquinas e 3 OS — mesmas contagens anteriores. O container MariaDB e seu volume não foram recriados; somente o container backend foi atualizado.
- Chrome headless autenticado em emulação **390×844**: a página carregou 3 linhas, sem erro e sem overflow horizontal da página (largura 390 px). Captura: [`ordens-servico-390x844.png`](agro-final-08/ordens-servico-390x844.png).
- O Calendário retornou HTTP 200 para os sete perfis após o deploy. Nenhum 500 ocorreu nos cenários pós-deploy reproduzidos.
- O Safari físico do iPhone não foi novamente controlado após a atualização. A captura do viewport é Chrome headless; o tráfego Safari registrado antes do deploy forneceu a reprodução original da falha.

## Publicação e instalação privada

Commit `2ba406f92a8215816a79c97441085cc84eb89655` publicado na branch `fix/agro-final-07-mobile-tenant-rbac`, PR #11 ([aberta, sem merge](https://github.com/gabrielh063/agroFrota/pull/11)).

Imagem do backend pós-deploy: `sha256:9e0295242e8f835d6bb89b1f1e767623ade1a2a33112e346f45c0a9763384002`; o SHA-256 do módulo de permissões dentro do container coincide com o commit publicado (`362c369005304f70e8b97e131468f0a5dad44c18dba4b6d2a1d565ccf82b7d79`). Backend ficou `healthy`; imagem frontend e configuração HTTPS/Tailscale não foram alteradas.
