# AGRO-INFRA-03 — evidências operacionais

Data: 12/11/2026. Host: Linux Mint 22.1 `gabriel-Nitro-ANV15-51`. PR #10. Evidências sanitizadas; nenhum segredo, token, senha, conteúdo do banco ou chave de dispositivo foi registrado.

## Estado observado

- Branch `feat/agro-infra-01-tailscale-private`, HEAD inicial `a73cd1a8005fe4e8998edb898e0ed9e4a324d2c5`; árvore limpa no início desta missão.
- Sistema de arquivos `/`: 21 GB disponíveis; RAM total 7,5 GiB e aproximadamente 2,0 GiB disponíveis; swap quase ocupada. Nenhum cache, imagem, volume, arquivo ou backup foi removido.
- Docker Engine 29.8.2 e Tailscale 1.104.5 conforme registros da missão anterior. Docker system service: `enabled` e `active` na verificação atual.
- `curl --fail --silent --show-error --include http://127.0.0.1:18088/api/health`: HTTP 200, `{"status":"online","success":true}`.
- O mesmo endpoint no domínio MagicDNS respondeu HTTP/2 200; o cliente curl validou o certificado HTTPS.
- `tailscale serve status`: hostname `gabriel-nitro-anv15-51.tailac6509.ts.net`, `tailnet only`, `/` encaminhado para `http://127.0.0.1:18088`.
- Tailscale mostrou peers Linux e iOS online. Isso prova conectividade reportada pela tailnet, não login/navegação no Safari.
- Rootless prerequisites: executáveis `dockerd-rootless.sh`, `dockerd-rootless-setuptool.sh` e `rootlesskit`; subuid/subgid configurados; `slirp4netns` e `fuse-overlayfs` ausentes no PATH; `loginctl` reportou `Linger=no`.
- O CLI Docker direto não conseguiu acessar a API do socket no contexto de execução desta missão. Portanto, não foram lidos os estados dos containers nem suas políticas de restart diretamente; o Compose versionado declara `unless-stopped` para database/backend/frontend.

## Artefatos preparados

- `deploy/persistent/agrofrota-infra-01.service`: unidade systemd de sistema, com hardening e dependência do Docker.
- `deploy/persistent/agrofrota-infra-01-start`: valida as três labels Compose fixas, inicia database, espera healthcheck do MariaDB, inicia backend/frontend e espera API local saudável.
- `deploy/persistent/agrofrota-infra-01-stop`: valida as labels, para frontend/backend/database em ordem inversa e não remove recursos.

Os scripts não executam Compose/build, não carregam secrets, não fazem migrações, nem removem containers, redes ou volumes. A unidade ainda não foi copiada para `/etc/systemd/system`, os auxiliares ainda não foram instalados em `/usr/local/libexec`, e nenhum serviço foi habilitado. A ativação exige autorização explícita por conceder acesso root persistente ao socket Docker para iniciar/parar os três containers especificados.

## Reboots e dispositivo externo

- Restart de aplicação/Compose, persistência SQL e backup/restore isolado: mantêm-se aprovados pelas evidências `docs/evidence/infra-02/AGRO-INFRA-02-results.md` e por `docs/REMOTE_ACCESS_VALIDATION.md`.
- Restart executado nesta missão: não realizado, porque o contexto disponível não acessa o socket Docker.
- Reboot de sistema operacional: não executado, sem autorização explícita.
- Segundo dispositivo: PENDING. O iPhone aparece online no status Tailscale, mas Safari não está acessível para automação. Chrome/curl local não contam como homologação externa.

## Regressão

- `python backend/tools/ci.py`: 265 testes passaram; 74 avisos de depreciação já existentes. O harness encerrou seus próprios recursos descartáveis.
- `npm run build`: passou.
- `npm run lint`: exit 0; avisos de lint existentes, sem alteração nos módulos frontend.
- `sh -n` nos dois auxiliares: passou.
- `systemd-analyze verify` da unidade e dos executáveis no caminho temporário de staging: passou. A verificação não instalou nem ativou a unidade real.
- `git diff --check`: passou.
- CI remota no HEAD `cbb80cda9a247c62694c8c0dbc8a349aadb2e97a`: jobs `backend-mariadb` e `frontend` passaram no run [43303527278](https://github.com/gabrielh063/agroFrota/actions/runs/43303527278).

## Classificação

`AGRO_INFRA_03_PARTIAL`. A aplicação e o Serve estavam saudáveis na coleta. A prova de segundo dispositivo e ativação segura após autorização continuam pendentes.
