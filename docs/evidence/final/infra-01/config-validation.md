# Validação estática da stack AGRO-FINAL-06

Executada em worktree isolada da branch `feat/agro-infra-01-tailscale-private`.

- `docker compose --project-name agrofrota-infra-01 --file deploy/persistent/compose.yaml --env-file /tmp/agrofrota-compose-check/.env config --quiet`: exit 0. O arquivo temporário continha apenas valores sintéticos e foi usado para validar interpolação YAML/Compose; não houve contato com Docker daemon.
- Asserções sobre `docker compose config --format json`: banco, backend e migration sem portas publicadas; Nginx ligado somente a `127.0.0.1:18088`; volume com nome próprio; produção habilitada e build frontend sem host de API. Exit 0.
- `python3 -m py_compile` para CLI, unit helper, provisionador, configuração e testes: exit 0.
- Backend `python3 backend/tools/ci.py`: **263 passed, 74 warnings**, migrations central/tenant em MariaDB descartável. O launcher informou que os recursos próprios foram removidos.
- `cd frontend && npm run build`: exit 0 (Vite 8.3.1); `npm run lint`: exit 0, avisos preexistentes de hooks/efeitos/Fast Refresh.
- Testes novos: secrets `*_FILE`, diretório/permissões do estado local, geração de sete credenciais únicas sem sobrescrita e ativação explícita da Central em produção sem rotas dev; falha do Ollama é erro explícito.
- `git diff --check`: exit 0.
- PR empilhada #10 em `release/agrofrota-mvp-final`, HEAD `6003c40aadf20d81f58b56040a51f489f9c9104d`; run remoto [43273961926](https://github.com/gabrielh063/agroFrota/actions/runs/43273961926): `backend-mariadb` PASS, `frontend` PASS. A PR #9 permaneceu aberta e inalterada no HEAD `95cef28cf91e509b8adb1fdf6150db380ea73ef0`.
- Nenhuma imagem foi baixada, container criado, migration aplicada, serviço ativado ou banco do operador acessado.

Essas validações comprovam código, CI e parsing/configuração, não o runtime Docker.
