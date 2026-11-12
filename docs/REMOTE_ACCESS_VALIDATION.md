# Validação de acesso privado remoto

Data da inspeção do host: 2026-11-12.

## Evidência observada

- Host: Linux Mint 22.1, kernel 6.8, x86_64; Tailscale CLI 1.104.5.
- Daemon Tailscale ativo e host conectado; MagicDNS presente. Valores de IP/identidade completos foram omitidos deste relatório.
- `tailscale serve status` vazio e `tailscale serve get-config --all` sem endpoint Serve configurado.
- MariaDB local já estava ativo em `127.0.0.1:3306`; PostgreSQL/Ollama também possuíam listeners locais. Nenhum foi reutilizado ou alterado.
- Docker e Compose instalados e daemon ativo, mas leituras de `docker info`, containers e imagens falharam por permissão negada em `/var/run/docker.sock`.
- Raiz com aproximadamente 1,3 GB livres. Não foi seguro baixar/buildar imagens ou iniciar a dupla de banco ativo e banco de restauração.
- Sem Docker acessível, não havia endpoint local do AgroFrota para validar, portanto Tailscale Serve não foi alterado.

## Resultado por gate

| Gate | Resultado | Evidência | Estado |
|---|---|---|---|
| CP1 host/Tailscale | PASS para diagnóstico | Comandos de estado executados; sem IP/token registrado | Host certo e conectado |
| CP2 stack persistente | PARTIAL | `deploy/persistent/compose.yaml`, Dockerfiles, script de provisionamento | Configuração preparada; containers não iniciados |
| CP3 segredos | PARTIAL | CLI cria arquivos 0600, secrets Compose, produção rejeita defaults | Verificação de container/runtime pendente |
| CP4 Serve/HTTPS | PARTIAL | documentação e comando Serve reversível; configuração existente vazia | Não ativado, URL HTTPS não existe ainda |
| CP5 sete perfis remoto | PARTIAL | reutiliza `MATRIZ`, seed fail-closed, sete logins anteriores na PR #9 | Nenhum login por esta stack ou por Tailscale |
| CP6 restart/backup/restore | PARTIAL | scripts de stop/restart/backup/restore isolado | execução em MariaDB não feita |
| CP7 acessibilidade/segurança histórica | PARTIAL | prontidão MVP existente e limites mantidos | sem nova prova de leitor de tela; ver readiness |
| CP8 CI/PR | PASS (código) | PR #10 `6003c40`; jobs `backend-mariadb` e `frontend` verdes no run [43273961926](https://github.com/gabrielh063/agroFrota/actions/runs/43273961926) | atualização documental final requer novo check |

## Acesso remoto

Não existe URL HTTPS comprovada para esta candidata. Após implantação, obtenha a URL real em `tailscale serve status`, e não derive um hostname por suposição. O operador deve concluir um teste com o cliente Tailscale em outra rede (por exemplo, iPhone em dados móveis), efetuar login AgroFrota, validar refresh, navegação/API, logout e perfil sem permissão, e registrar timestamp, perfil, HTTP health e capturas sem credenciais.

Passos reprodutíveis estão em `docs/TAILSCALE_DEPLOYMENT.md`. Não relatar esse teste como feito até haver evidência do dispositivo externo.
