# AGRO-FINAL-07 — resultados

**Data:** 13/11/2026  
**Host:** Linux Mint, Docker Compose, MariaDB, Gunicorn, Nginx e Tailscale Serve  
**Worktree:** `.worktrees/agro-final-07`  
**Base:** PR #10, `88cc9127d932c3986e5187ff35338b4c58e09403`  
**Classificação deste incremento:** `AGRO_FINAL_07_READY` para código, regressão local e deploy privado.  
**MVP global:** permanece `AGRO_MVP_FINAL_PARTIAL` por pendências históricas independentes de acessibilidade e avaliação dos registros legados.

## Causa raiz e correção do tenant

O middleware anterior convertia exceções diferentes em HTTP 500 genérico, sem distinguir indisponibilidade do MariaDB, falha de conexão, timeout do pool e erro de resolução. A instrumentação sanitizada registrou tempos separados para conexão central, lookup do tenant, lookup do usuário, validação do perfil e duração total, além de categorias técnicas sem dados de credencial ou detalhes internos no corpo da resposta.

Sob carga realista no browser ocorreram dois eventos `database_pool_timeout`, cada um após espera de 5 segundos para adquirir conexão tenant. As conexões centrais e o lookup do tenant levaram poucos milissegundos. A configuração permitia 4 threads em cada worker Gunicorn, enquanto cada engine tenant tinha pool de 2 conexões e `max_overflow=0`. Isso produzia contenção de pool por worker; a antiga mensagem genérica escondia a causa.

O Gunicorn foi ajustado para 2 workers e 2 threads por worker, alinhando as threads às duas conexões por engine tenant. Mantivemos `max_overflow=0`, `pool_timeout=5s` e a configuração de reciclagem existente. Essa escolha limita a concorrência ao pool medido em vez de ampliar indiscriminadamente conexões para todas as engines/tenants. O tenant, usuário, perfil, versão/revogação da sessão e escopo continuam revalidados no servidor em cada request; não foi introduzido cache duradouro de autorização.

Após o ajuste, 100 requisições concorrentes autenticadas a `/api/auth/me` terminaram sem erro: p50 39,93 ms, p95 73,17 ms, máximo 93,87 ms. Em 100 chamadas sequenciais, p95 foi 13,91 ms. Na medição anterior, a chamada sequencial teve p95 26,43 ms e a carga de 100 chamadas com concorrência 8 teve p95 46,42 ms; entretanto, a navegação completa de sete perfis expôs os dois timeouts de pool. Portanto, a melhora principal é a eliminação da contenção/erros sob fluxo de navegador; o p95 concorrente isolado subiu de 46,42 para 73,17 ms e permanece muito abaixo da meta de 2 s. Não há comparação anterior equivalente para todas as rotas.

Medições posteriores por endpoint (sete contas, requests autenticados; p95 em ms):

| Endpoint | p95 |
|---|---:|
| `/api/auth/me`, 100 sequenciais | 13,91 |
| `/api/auth/me`, concorrência 8, 100 requests | 73,17 |
| Dashboard | 57 |
| Maquinários | 65,8 |
| Ordens de serviço | 98,13 |
| Calendário | 35,75 |
| Central de Operações | 15,49 |
| Equipe e Permissões | 51,3 |

Não foram observados eventos de timeout/resolução tenant nos logs desde o deploy final. Contadores MariaDB após o tráfego: `Aborted_connects=0`, `Slow_queries=0`, `Max_used_connections=9`. O status após o deploy reportou zero reinícios para database, backend e frontend. Uso de memória capturado ao final: MariaDB 106,3 MiB, backend 148,4 MiB e frontend 12,78 MiB. É uma fotografia do host, não uma série temporal ou pico de memória.

## Instalação persistente e integridade

Antes do deploy, o volume original continha 7 usuários, 2 máquinas e 3 ordens de serviço. Depois do deploy e do ciclo stop/start systemd, o readback SQL confirmou 7 usuários, 2 máquinas, 3 ordens de serviço e 1 tenant. Não foi executado `provision`, não houve migration nova e o volume `agrofrota-infra-01-mariadb` não foi removido ou recriado.

O SQL de inicialização agora está em `deploy/persistent/mariadb/10-tenant.sql` na worktree registrada e permanente `.worktrees/agro-final-07`. O Compose usa bind `read_only` e `create_host_path: false`; se o arquivo faltar, o deploy falha claramente em vez de transformá-lo num diretório. O inventário ao final não mostrou mounts operacionais de `/tmp`: apenas esse SQL, secrets em `~/.config/agrofrota-infra-01` e o volume MariaDB são montados do host. A senha do banco, root, chaves Flask/JWT e credenciais de demonstração não foram alteradas; secrets privados permanecem fora do Git.

Foi criado backup privado antes do deploy em `/home/gabriel/.config/agrofrota-infra-01/agro-final-07-predeploy.sql`, modo `0600` (29.883 bytes). O restore de validação ocorreu em projeto, rede e volume isolados e confirmou schemas, migrations e registros; o volume ativo não foi alvo. O backend anterior ao ajuste de threads recebeu uma tag local de rollback específica; nenhum dado de backup foi anexado ao repositório.

A unidade exclusiva `agrofrota-infra-01.service` foi reiniciada com sucesso e está `active (exited)`, comportamento esperado para `Type=oneshot` + `RemainAfterExit=yes`. Healthcheck local e `https://gabriel-nitro-anv15-51.tailac6509.ts.net/api/health` retornaram `{"status":"online","success":true}`. Tailscale Serve continuou privado; nenhum Funnel foi usado. O reboot completo do notebook não foi executado.

## Sessão, usuários e autorização

Em falha transitória HTTP 503/timeout de `/api/auth/me`, o frontend preserva o token mas mantém páginas e menu protegidos ocultos até a validação dar certo. A UI explica a indisponibilidade e oferece **Tentar novamente**. Recuperada a resposta, sessão e página autorizada voltam; 401 continua removendo sessão inválida, e 403 mantém o usuário autenticado sem ampliar permissões. Corridas entre restauração, login e logout foram tratadas no `AuthContext`/interceptores.

**Equipe e Permissões** permite listar contas ativas/inativas, pesquisar por nome/username, filtrar por perfil e situação, criar, editar campos administrativos autorizados e perfil, visualizar cargo/permissões efetivas e ativar/desativar com confirmação e feedback. A listagem é recarregada após mutação. Não existe exclusão física padrão nem reset administrativo de senha. O backend audita mutações, revoga sessões afetadas e bloqueia autoelevação, delegação além da capacidade do gerente, mudança de próprio perfil vedada e desativação do último administrador efetivo. Respostas não incluem hash ou senha.

Resumo de navegação efetiva da matriz existente (ações de escrita sempre seguem permissões próprias, sem promoção por visualização):

| Perfil | Abas/áreas que a matriz permite observar |
|---|---|
| `ADMIN_EMPRESA` | Visão geral, Central, Calendário, OS, Maquinários, Equipamentos e Equipe/Permissões; ações conforme permissões administrativas e operacionais. |
| `DIRETORIA` | Visão geral, Central, Calendário, OS, Maquinários, Equipamentos e Equipe/Permissões em leitura; auditoria disponível. |
| `GESTOR_FROTA` | Visão geral, Central, Calendário, OS, Maquinários, Equipamentos e consulta de Equipe; operações conforme matriz. |
| `ADMINISTRATIVO` | Visão geral, Central, Calendário, OS, Maquinários, Equipamentos e consulta de Equipe; leitura operacional. |
| `MANUTENCAO` | Central, Calendário, OS, Maquinários e Equipamentos; OS e manutenção dentro do escopo atribuído. Sem Dashboard ou gestão de usuários. |
| `OPERADOR` | Central, Calendário, OS, Maquinários e Equipamentos; OS/indisponibilidade no escopo próprio, incluindo criação de OS permitida. Sem Dashboard ou gestão de usuários. |
| `AUDITOR` | Visão geral, Central, Calendário, OS, Maquinários, Equipamentos e Equipe/Permissões em leitura; auditoria disponível, escrita negada. |

O Calendário usa `OS.VISUALIZAR` para a página e `OS.EDITAR` para escrita, igual às APIs. A Central usa `OS.VISUALIZAR` para consulta; as confirmações de criar OS/agendar voltam a verificar `OS.CRIAR`/`OS.EDITAR` e o escopo do objeto no serviço. Durante a revisão, a rota frontend da Central estava checando `MAQUINA_VISUALIZAR`, apesar da navegação e APIs exigirem `OS.VISUALIZAR`; a rota foi alinhada à autorização real do backend. A matriz dos sete perfis não foi relaxada. APIs continuam a negar operações não permitidas.

## Testes e evidência mobile

- Regressão backend/MariaDB: **266 aprovados**, 74 avisos preexistentes de depreciação. Execução final: `/tmp/agro-final-07-ci/bin/python backend/tools/ci.py`; o ambiente isolado permitiu criar e remover sua instância descartável MariaDB.
- Frontend: `npm --prefix frontend run build` passou após a correção de autorização da rota Central. `npm --prefix frontend run lint` termina com exit 0; permanecem avisos Oxlint de hooks/efeitos, pureza e Fast Refresh em arquivos existentes, incluindo avisos já conhecidos da tela Equipe.
- Carga HTTP: login das sete contas e consultas `/api/auth/me`, Dashboard, Maquinários, OS, Calendário, Central e Equipe; 100 chamadas sequenciais e 100 com concorrência 8. Sem 500 de resolução tenant. Auditor teve criação negada com 403; Manutenção e Operador tiveram administração de usuários negada com 403.
- Chrome headless emulado a 390×844, repetido depois de publicar os assets finais: login/perfil/menu para sete contas, tabelas e formulários do gerente, logout, recuperação após 503 de `/api/auth/me`, preservação do token sem liberar dados durante a falha e retry após retorno da API. A tabela de usuários rola dentro de sua área e não aumenta o scroll horizontal da página.
- URLs diretas: Operador em `/equipe-permissoes` e Auditor em `/ordens-servico/nova` viram acesso negado; a automação observou zero requests das APIs protegidas nessas tentativas.
- Screenshots sanitizados: `agro-final-07/team-admin-390x844.png`, `operator-route-denied-390x844.png`, `auditor-route-denied-390x844.png`.

O Safari físico no iPhone e a rede móvel não foram controlados nesta sessão. Para fechar a evidência no dispositivo: conectar Tailscale, desligar Wi-Fi, abrir o URL HTTPS privado no Safari, testar login, restauração, abas com pelo menos dois perfis, Equipe como gerente, OS/Calendário/Central, logout, e interromper/restaurar temporariamente a rede para usar **Tentar novamente**. Registrar somente resultado/horário; não capturar credenciais.

## PR e limitações

A mudança está na branch `fix/agro-final-07-mobile-tenant-rbac`, empilhada sobre o HEAD da PR #10, e publicada na [PR #11](https://github.com/gabrielh063/agroFrota/pull/11). Os checks remotos `backend-mariadb` e `frontend` passaram no head `8ebf44c` (run [43444489769](https://github.com/gabrielh063/agroFrota/actions/runs/43444489769)). A PR #9 e a PR #10 permanecem abertas e não houve merge. O checkout original `release/agrofrota-mvp-final` foi preservado; somente o diretório planejado da worktree foi criado ao lado dele.

Limitações: não houve reboot real do notebook nem teste físico de Safari/iPhone; métricas de memória são pontos instantâneos; warnings de lint/depreciação existentes permanecem; acessibilidade e segurança histórica continuam nos estados parciais anteriores. Nenhum segredo, dump, hash ou dado pessoal consta neste relatório.
