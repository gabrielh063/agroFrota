# AGRO-SERVER-01 — evidências de implantação

**Classificação: `AGRO_SERVER_01_PARTIAL`**\
**Servidor:** `techcell` — Ubuntu Server 26.04.1 LTS\
**Código:** `Main` em `892108a3f0b9aebf141030517ef0d3974fed9549`\
**Data:** 2026-11-13 (America/Sao_Paulo)

O AgroFrota está funcional em HTTPS privado pela tailnet, com MariaDB isolado, backup restaurável, limites de recursos e unidade própria `systemd --user`. A classificação fica parcial porque não foi possível executar `restic check` nem habilitar o linger do usuário sem autenticação sudo interativa; dois erros 500 foram observados no endpoint opcional do assistente e não foram reproduzidos nem tiveram exceção identificada. O Safari físico não foi testado.

## Origem e integridade do código

- `Main` remota e o checkout permanente `/srv/agrofrota/app` estavam no SHA informado, com árvore limpa.
- PRs integradas conferidas: #9 (`e5b1e6c5af8b1be7b748d52ea2e69809f9ad5865`), #10 (`66af10b7c44df1575c3972d68401726ed6d3002c`) e #11 (merge `892108a3f0b9aebf141030517ef0d3974fed9549`).
- Os jobs do commit de referência passaram: [backend-mariadb](https://github.com/gabrielh063/agroFrota/actions/runs/43454069379/job/131983466306) e [frontend](https://github.com/gabrielh063/agroFrota/actions/runs/43454069379/job/131983466087). [Execução completa](https://github.com/gabrielh063/agroFrota/actions/runs/43454069379).
- `npm ci --no-audit --no-fund` e build local com `VITE_API_URL=` e `VITE_TENANT_DATABASE=agrofrota_tenant` concluíram. `npm run lint` também concluiu com avisos já existentes.
- O conteúdo dos cinco arquivos backend críticos foi comparado por SHA-256 entre o checkout Main e o container: `routes/ordens_servico.py`, `services/ordem_servico_service.py`, `services/escopo.py`, `database/session.py` e `schemas/ordem_servico.py`; os hashes coincidiram.
- Os bundles JS/CSS servidos pelo container coincidem byte a byte com o build produzido a partir do `package-lock.json` e dos argumentos do Compose: `index-BH6a7t5K.js` (`bf4c7ea26bf131eeb1822c8d8946551c8dbec50d6abe1aff03af4b414700e5fe`) e `index-kwZNhFh6.css` (`2d35a042424241f4564389bc371c35b9a5e56f8e436150af92bbd7ccba664279`).

## Host e recursos

| Item | Antes do AgroFrota | Após implantação/testes |
|---|---:|---:|
| CPU | Intel Core i5-3330, 4 CPUs lógicas | carga ociosa; amostras com 98–99% idle |
| RAM | 3,2 GiB; 1,3–1,5 GiB disponíveis | 3,2 GiB; 1,2 GiB disponíveis |
| Swap | 3,7 GiB; 1,4 GiB usados | 3,7 GiB; 1,4 GiB usados; sem churn nas amostras finais |
| Pressão de memória | sem pressão sustentada | `avg10=0` em `some` e `full` |
| Disco do sistema | 98 GiB | 57 GiB livres; 40% usado |
| `/srv/icloud` | volume de mídia Immich separado | não usado pelo AgroFrota |

Limites aplicados e reaplicados pelo `ExecStartPost` da unidade:

| Container | Memória | CPU | Uso observado após teste |
|---|---:|---:|---:|
| MariaDB AgroFrota | 384 MiB | 0,75 CPU | 85,7 MiB |
| Backend | 320 MiB | 1 CPU | 123,9 MiB |
| Frontend | 64 MiB | 0,25 CPU | 4,5 MiB |

## Containers, rede e dados

- Containers criados: `agrofrota-infra-01-database-1`, `agrofrota-infra-01-backend-1`, `agrofrota-infra-01-frontend-1`; todos saudáveis.
- Banco: MariaDB 11.4, schemas `agrofrota_central` e `agrofrota_tenant`.
- Volume exclusivo: `agrofrota-infra-01-mariadb`.
- Redes exclusivas: `agrofrota-infra-01-private` (interna) e `agrofrota-infra-01-host-proxy`.
- `10-tenant.sql` é montado como arquivo somente leitura com `create_host_path: false`.
- MariaDB (3306) e Gunicorn (8000) não têm portas publicadas. Nginx publica somente `127.0.0.1:18088`.
- A instalação contém 2 OS, 1 máquina, 0 equipamentos e 0 agendamentos. As 2 OS permaneceram após o reinício controlado.
- A stack já estava em execução na primeira inspeção detalhada, apesar de não constar no inventário anterior. Esta sessão não executou `compose up` nem recriou sua base; o primeiro dump foi criado antes das alterações operacionais desta sessão.

## Tailscale, Immich e firewall

- MagicDNS confirmado: `techcell.tailac6509.ts.net`.
- Serve existente em `https://techcell.tailac6509.ts.net` continua apontando para `127.0.0.1:8080`.
- Endpoint do AgroFrota adicionado em `https://techcell.tailac6509.ts.net:8443`, tailnet-only, proxy para `127.0.0.1:18088`; não foi ativado Funnel nem alterada regra global da tailnet.
- Healthcheck HTTPS verificado no servidor e em um cliente da tailnet: HTTP 200 com validação TLS.
- UFW permaneceu ativo; nenhuma regra foi alterada.
- `immich_server`, `immich_postgres` e `immich_redis` estavam saudáveis antes e depois, sem reinícios durante a implantação. O timer do backup Restic mais recente terminou com `Result=success` às 04:00 -03. Não foi possível executar uma verificação completa do repositório Restic sem sudo.

## Testes funcionais

- As sete contas demonstrativas autenticaram por HTTPS; `/api/auth/me` retornou 200 para todas.
- `/api/ordens-servico/?apenas_ativas=false` retornou 200 para todas. Manutenção e Operador receberam 1 OS cada, respeitando escopo; os outros cinco perfis receberam 2.
- Para cada perfil, as três chamadas concorrentes da página (OS, máquinas e equipamentos) concluíram sem HTTP 500.
- Calendário, dashboards, máquinas e equipamentos retornaram 200 nos sete perfis.
- O administrador consultou os 7 perfis e as permissões de cada um com HTTP 200. Consultas de perfis nos demais usuários respeitaram RBAC com respostas 200 ou 403; nenhuma retornou 500.
- Reinício controlado da unidade concluiu; os três containers voltaram saudáveis, a contagem de OS permaneceu 2 e o healthcheck da API retornou 200.
- Backup lógico inicial: `/home/gabriel/Backups/agrofrota/pre-validation-20261113-1305.sql`, modo 0600, 28.884 bytes, SHA-256 `e2854f6ed4aa7c484354ce37364215a13003991d586c9ecff690116c02542537`. A restauração em volume de teste exclusivo validou os dois schemas e a versão Alembic; somente o volume temporário desse teste foi removido.
- Arquivo privado de recuperação da configuração/secrets: modo 0600, seis arquivos esperados, SHA-256 `e1c70ad240d66f6f734c22e06d53bdb3a286ae644029f210fd3b6055e6dc344d`. Nenhum segredo foi incluído neste relatório.
- Backup diário configurado para 03:30 local, antes do timer Restic das 04:00. Os dumps são mantidos sem rotina de exclusão e ficam no filesystem raiz, nunca em `/srv/icloud`.

## Viewport móvel

Chrome headless 155.0.8059.39 abriu o endereço HTTPS publicado em emulação de 390×844. A página Ordens de Serviço carregou 2 registros; `document.scrollWidth=390`, sem overflow horizontal da página, e todas as chamadas de rede da tela retornaram 200. A captura está em [AGRO-SERVER-01-ordens-390x844.png](AGRO-SERVER-01-ordens-390x844.png). Não foi realizado teste em Safari físico.

A página Calendário também carregou em 390×844 via HTTPS, sem overflow horizontal; `/api/auth/me`, `/api/usuarios/`, `/api/calendario/` e `/api/ordens-servico/` retornaram 200.

## Unidade e recuperação

A unidade `agrofrota-infra-01.service` está habilitada e ativa no `systemd --user`; seu `ExecStart` aguarda os healthchecks e seu `ExecStop` para somente o projeto AgroFrota. A unidade evita build no servidor e reaplica os limites.

`docker.service`, `tailscaled.service`, `ufw.service` e `cron.service` estão enabled; Docker e Tailscale estão ativos. `loginctl` ainda informa `Linger=no`. Assim, a unidade do usuário sobe após login; os containers têm política `unless-stopped` para reiniciar com o daemon Docker após falta de energia, desde que não tenham sido parados manualmente.
Não foi feito reboot do host. Verificação pós-falta de energia: `docker ps` do projeto, `systemctl --user status agrofrota-infra-01.service` após login, `curl -fsS https://techcell.tailac6509.ts.net:8443/api/health` e status do Immich.

Operação:

```sh
systemctl --user start agrofrota-infra-01.service
systemctl --user stop agrofrota-infra-01.service
systemctl --user restart agrofrota-infra-01.service
systemctl --user status agrofrota-infra-01.service
journalctl --user -u agrofrota-infra-01.service -n 100 --no-pager
docker compose --project-name agrofrota-infra-01 --file /srv/agrofrota/app/deploy/persistent/compose.yaml --env-file /home/gabriel/.config/agrofrota-infra-01/.env ps
/home/gabriel/.local/bin/agrofrota-backup
```

Para testar restauração isolada, use `python3 /srv/agrofrota/app/deploy/persistent/agrofrota.py --state-dir /home/gabriel/.config/agrofrota-infra-01 restore-test --backup CAMINHO_DO_DUMP`. As credenciais demonstrativas ficam em arquivo privado mode 0600 no diretório de configuração; recuperação pode ser feita pelo CLI `credentials` nessa instalação local.

## Pendências e observações

- Acesso sudo não interativo não está disponível para o usuário SSH (`sudo -n` exige autenticação interativa). Por isso, UFW foi confirmado como ativo, mas não foi possível registrar o detalhamento das regras nem executar `restic check` ou habilitar `loginctl enable-linger`.
- Foram observados dois HTTP 500 em `POST /api/assistente/mensagem` às 13:09 -03 durante a sessão. Esse endpoint opcional não fez parte dos fluxos reproduzidos; a rota devolve erro genérico para exceções e os logs disponíveis não registraram a exceção original. Não atribuí causa nem instalei Ollama.
- Não houve reboot do servidor, teste Safari físico, alteração dos dados do Immich ou uso do volume de mídia.

**Estado:** stack AgroFrota funcional e acessível pelo HTTPS privado; pendências acima mantêm o resultado como `AGRO_SERVER_01_PARTIAL`.
