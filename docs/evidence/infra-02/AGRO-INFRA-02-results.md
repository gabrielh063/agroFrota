# AGRO-INFRA-02 — resultados observáveis

Data: 12/11/2026. Host Linux Mint 22.1 `gabriel-Nitro-ANV15-51`. A implantação usa somente registros fictícios criados no novo tenant persistente.

## Serviço e exposição

- Tailscale 1.104.5 conectado; hostname MagicDNS confirmado no status: `gabriel-nitro-anv15-51.tailac6509.ts.net`.
- Serve ativo em `https://gabriel-nitro-anv15-51.tailac6509.ts.net/`; status informa tailnet-only. TLS foi aceito pelo Chrome headless isolado.
- Porta HTTPS escuta em `tailscale0:443`. Porta HTTP do host: `127.0.0.1:18088` e encaminha ao Nginx. Sem listeners públicos do AgroFrota.
- Containers: MariaDB healthy, backend/Gunicorn healthy, frontend/Nginx healthy. Nenhum port mapping para MariaDB 3306 ou Gunicorn 8000.
- Banco no volume `/var/lib/docker/volumes/agrofrota-infra-01-mariadb/_data`; schemas `agrofrota_central` e `agrofrota_tenant`.
- Arquivos locais de configuração e senhas ficam fora do repositório em `~/.config/agrofrota-infra-01`, diretório `0700`, arquivos `0600`.

## Perfis e navegação

Os sete logins foram feitos tanto via API HTTPS quanto no Chrome isolado. `/api/auth/me` retornou o perfil esperado para cada conta: Administrador/Gerente, Diretoria, Gestor de Frota, Administrativo, Manutenção, Operador e Auditor. Atributos de token/senha não foram gravados ou impressos.

No acesso HTTPS foram abertas Dashboard, Equipe e Permissões, Maquinários, Ordens de serviço, Calendário e Central. Login e API usam o mesmo origin HTTPS e caminho relativo `/api`; nenhum request do browser apontou para `localhost:5001`, `127.0.0.1:5001` ou Vite. Auditor manteve leitura autorizada e recebeu HTTP 403 ao tentar escrita de usuário e OS. A tentativa de acessar diretamente `/ordens-servico/nova` mostrou a página de acesso restrito com o perfil Auditor. Operador e Manutenção visualizaram somente uma OS atribuída a cada um.

Logout remoto retornou 200 e o token antigo passou a receber 401 em `/api/auth/me`. Preflight CORS com origem HTTPS real retornou 200 e `Access-Control-Allow-Origin` correspondente.

## Capturas reais

- `remote-dashboard-admin.png` — dashboard autenticado do Gerente após carregar os indicadores.
- `remote-auditor-denied.png` — acesso direto a criação de OS bloqueado com mensagem acessível.
- `remote-assistant-network-error.png` — Central de Operações com falha de rede simulada; mensagem em `role=alert` e loading encerrado.

A falha da Central foi causada por bloqueio deliberado da chamada de mensagem no Chrome/CDP. Não houve pedido de operação nem confirmação transacional. A captura não contém credenciais ou tokens.

## Persistência e backup

Migrações centrais/tenant terminaram com sucesso. Seed inicial criou 7 usuários, 1 máquina e 2 OS de demonstração. Uma máquina e uma OS adicionais, fictícias, foram criadas pela API HTTPS. Após `stop` e novo `up` sem remover o volume, API voltou com health 200 e SQL read-only confirmou: 7 usuários, 1 máquina de teste e 1 OS de teste.

Backup privado: arquivo em `~/.config/agrofrota-infra-01/infra02-validation.sql`, 29.552 bytes, owner UID 1000, modo 0600. `restore-test` terminou com os dois schemas e versão Alembic presentes numa instância isolada, depois removeu o projeto, rede e volume temporários próprios.

O primeiro boot requereu correção no Compose: rede `internal: true` não ativou o encaminhamento host deste Docker. Apenas Nginx recebeu a bridge adicional `host_proxy`; database e backend não mudaram de rede. O seed inicial também passou a ser invocado como módulo Python. No restore, foram corrigidos a propagação dos nomes temporários pelo wrapper Docker e o aguardo do healthcheck MariaDB antes da importação. A tentativa abortada havia montado o volume ativo; a remoção foi recusada por estar em uso e o volume/serviço permaneceu saudável. O restore final validado usou outro volume e outra rede exclusivos.

## Testes de código e CI

- `PATH=/tmp/agrofrota-docker-sudo-bin:$PATH python3 backend/tools/ci.py`: **265 passed**, 74 avisos DeprecationWarning existentes; ambiente descartável encerrado e removido.
- `cd frontend && npm run build`: aprovado, Vite 8.3.1.
- `cd frontend && npm run lint`: exit 0, avisos Oxlint existentes.
- `docker compose config`: aprovado após `setup`.
- CI remota da PR #10 no commit `84baa6cb2d6a21427ee538279c3377d98b0c9b96`: `backend-mariadb` e `frontend` passaram no run [43299031912](https://github.com/gabrielh063/agroFrota/actions/runs/43299031912).

## Limites e rollback

O iPhone ou outro cliente numa segunda rede não estava disponível; essa validação não é declarada. O notebook abriu o próprio hostname via endereço Tailscale e certificação HTTPS, o que prova Serve/configuração no host, mas não substitui o teste externo. A unidade systemd não foi habilitada porque o usuário não acessa o socket diretamente e a unidade atual bloqueia elevação por sudo; nenhuma associação a grupo ou alteração sudo foi feita. Não houve reboot do SO.

Para parar agora: `sudo tailscale serve --bg --https=443 http://127.0.0.1:18088 off` e, separadamente, `PATH=/tmp/agrofrota-docker-sudo-bin:$PATH python3 deploy/persistent/agrofrota.py stop`. Essas operações não apagam o volume nem o backup. Não executar `down -v` na instalação ativa.

MVP permanece `AGRO_MVP_FINAL_PARTIAL`: acessibilidade residual e decisão de segurança histórica continuam independentes da infraestrutura. Não houve merge nem exposição pública.
