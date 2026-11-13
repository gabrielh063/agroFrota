# Evidência sanitizada de diagnóstico do host

- Data: 2026-11-12.
- Distribuição/kernel: Linux Mint 22.1, kernel Linux 6.8, x86_64.
- Host: `gabriel-Nitro-ANV15-51`.
- RAM: 7,5 GiB total; aproximadamente 2,3 GiB disponíveis na inspeção.
- Filesystem raiz: 207 GiB total, aproximadamente 195 GiB usados e 1,3 GiB disponíveis (100% indicado pelo filesystem).
- Tailscale CLI: 1.104.5; serviço ativo e conexão tailnet ativa; MagicDNS presente. IPs, identidade da tailnet e outros nomes foram omitidos.
- Tailscale Serve: status vazio; configuração JSON sem endpoints Serve preexistentes. Nenhuma alteração foi feita.
- MariaDB do host: ativo em `127.0.0.1:3306`; preservado e não utilizado.
- PostgreSQL: ativo em loopback; não utilizado.
- Ollama: ativo em loopback; não iniciado nem alterado.
- Docker/Compose instalados; daemon ativo, mas chamadas ao socket Docker receberam `Permission denied`. Não foram criados ou alterados containers/volumes.
- Listener escolhido para a candidata: `127.0.0.1:18088`; checagem inicial não indicou listener nesse endereço/porta. Não foi iniciado.

Comandos não destrutivos usados incluíram `uname -a`, `free -h`, `df -h`, `command -v tailscale`, `tailscale version/status/serve status`, `ss -tulpen`, `systemctl is-active` e leitura do status do Docker. Nenhuma chave, senha, token ou IP foi salvo neste arquivo.
