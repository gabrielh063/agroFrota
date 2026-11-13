# AGRO-INFRA-04 — ativação controlada

Data: 12/11/2026. Host: `gabriel-Nitro-ANV15-51`. PR #10, HEAD examinado: `4d31cb1140e5fca5a940380cb94ba6c4be4ec83a`. Nenhum segredo/token foi incluído.

## Precondições e instalação

- PR aberta no HEAD autorizado, árvore limpa, CI `backend-mariadb` e `frontend` verdes.
- `AGENTS.md` ausente na raiz do checkout.
- Containers `agrofrota-infra-01-database-1`, `-backend-1`, `-frontend-1`: label Compose `agrofrota-infra-01`, estado `running`, health `healthy`, política `unless-stopped`.
- MariaDB monta o volume `agrofrota-infra-01-mariadb`, também com label do projeto correta.
- Destinos de instalação e drop-in estavam ausentes; `/usr/local` e `/etc/systemd/system` eram diretórios `root:root`; nenhum destino era symlink.
- Arquivos versionados foram conferidos integralmente. A instalação usou `install` para copiar dados; nenhuma rotina do checkout foi executada como root. Em runtime, a unidade executa as cópias root-owned estáticas em `/usr/local/libexec`, não o checkout.
- Resultado instalado: helpers `root:root 0755`; unit `root:root 0644`. `daemon-reload` e `enable --now` aplicados somente a `agrofrota-infra-01.service`.
- `systemd-analyze verify` passou; relatou apenas avisos preexistentes de caminho `/var/run` nas unidades TeamViewer e AnyDesk.

## Stop/start e persistência

1. `systemctl stop agrofrota-infra-01.service` deixou a unidade inativa e os três containers AgroFrota em `exited`.
2. O volume `agrofrota-infra-01-mariadb` permaneceu disponível, com label de projeto AgroFrota.
3. `systemctl start agrofrota-infra-01.service` encerrou com sucesso e aguardou healthchecks.
4. O status tornou-se `active (exited)`; database/backend/frontend voltaram a `running/healthy`.
5. Leitura agregada MariaDB antes/depois foi idêntica: 7 usuários, 2 máquinas, 3 OS, 0 agendamentos.
6. `/api/health` local e HTTPS MagicDNS retornaram 200. `tailscale serve status` continuou indicando `tailnet only` para `127.0.0.1:18088`.
7. Inventário de containers fora do projeto e inventário de volumes comparados antes/depois sem diferenças.

## Semântica de execução

`Type=oneshot` + `RemainAfterExit=yes` representa a unidade como `active (exited)` após a rotina de start terminar. `Restart=on-failure` é aplicável a falha dessa rotina; não dá supervisão contínua depois do sucesso. O serviço controla ciclo start/stop. A política `unless-stopped` do Docker trata processo de container que termina; não reinicia exclusivamente porque um healthcheck fica unhealthy. A unidade habilitada em `multi-user.target`, ordenada após e dependente do Docker, deve iniciar no boot; o reboot real não foi executado e permanece PENDING.

## Pendências

- Reboot real do host: PENDING; não autorizado nesta missão.
- Teste de navegação no Safari/iPhone: continua pendente conforme AGRO-INFRA-03.
- Nenhum merge, alteração de histórico, grupo Docker, daemon global, firewall, serviço alheio ou volume foi alterado.
