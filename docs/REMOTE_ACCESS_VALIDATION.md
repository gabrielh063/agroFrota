# Validação de acesso privado remoto

Homologação local/Tailscale: 12/11/2026. Host: Linux Mint 22.1 `gabriel-Nitro-ANV15-51`, Docker Engine 29.8.2, Compose 5.6.0, Tailscale 1.104.5. Nenhum dado pessoal foi usado; as contas e registros são fictícios.

## Resultado por gate

| Gate | Resultado | Evidência | Limite |
|---|---|---|---|
| Espaço em disco | PASS | 23 GB livres antes dos builds; 21 GB depois. Docker atual: imagens 2,153 GB, volumes 455 MB, cache de build 1,868 GB. | Nenhuma limpeza foi feita; dados e caches do operador foram preservados. |
| Docker | PARTIAL | Daemon ativo; `sudo -n docker info` e Compose funcionam. CLI executado pelo UID 1000 através de wrapper temporário; segredos permanecem `0700/0600` e de propriedade do operador. | Usuário não acessa `/var/run/docker.sock` diretamente; grupo `docker` e sudoers não foram alterados. Inicialização automática aguarda decisão do operador. |
| Compose | PASS | MariaDB/Gunicorn sem port mappings; Nginx apenas `127.0.0.1:18088`; rede interna `agrofrota-infra-01-private`; `host_proxy` conectado somente ao Nginx. Migrações central/tenant concluíram. | A bridge `host_proxy` dá egress de rede ao container Nginx; ela não publica porta pública. |
| Banco persistente | PASS | Volume exclusivo `agrofrota-infra-01-mariadb`, localizado em `/var/lib/docker/volumes/agrofrota-infra-01-mariadb/_data`. Antes/depois de `stop` + `up`: 7 usuários, máquina/OS de teste preservadas por readback SQL. | Reboot do sistema operacional não foi testado. |
| Sete perfis | PASS | 7/7 logins no Chrome headless isolado via HTTPS e `GET /api/auth/me`; menu/rotas principais do Gerente; criação negada ao Auditor por URL direta; API de criação de usuário e OS retorna 403 para Auditor. Escopo: Operador e Manutenção veem apenas a OS atribuída a cada um. | Safari/iPhone em outra rede ainda não foi testado. |
| Backup/restore | PASS | Dump privado local de 29.552 bytes, modo 0600; restore em rede/volume/projeto aleatórios; schemas e Alembic validados. Recursos temporários foram removidos pelo CLI. | O dump permanece fora do Git em `~/.config/agrofrota-infra-01/infra02-validation.sql`. |
| Tailscale HTTPS | PASS | Serve ativo em `https://gabriel-nitro-anv15-51.tailac6509.ts.net/`; certificado aceito no Chrome; `tailscale0:443` e status indicam “tailnet only”. Serve encaminha para `127.0.0.1:18088`. | O acesso por segundo dispositivo da tailnet ainda precisa de prova. Nenhum Funnel foi usado. |
| Acesso remoto | PARTIAL | Chrome isolado abriu login, dashboard, Equipe, Maquinários, OS, Calendário e Central; 7/7 perfis autenticaram; health 200, preflight CORS correto, logout revogou sessão, Auditor foi negado, erro de rede na Central apareceu com alerta e loading encerrado. Nenhuma chamada do browser a `localhost:5001`, `127.0.0.1:5001` ou Vite dev server. | Chrome foi executado no próprio host. Não declarar validação em iPhone/outra rede. |
| Reinício automático | PARTIAL | `systemd_user.py` e unidade existentes foram inspecionados. | Unidade não ativada: requer estratégia autorizada de acesso Docker para o serviço. Restart manual de stack foi aprovado; reboot do host não foi feito. |
| CI | PASS | PR #10 no head `948f466`; jobs `backend-mariadb` e `frontend` passaram no run [43299467303](https://github.com/gabrielh063/agroFrota/actions/runs/43299467303). |

## Configuração Tailscale

MagicDNS do host: `gabriel-nitro-anv15-51.tailac6509.ts.net`. O CLI confirmou Tailscale conectado, Serve sem endpoint preexistente, 443 livre antes da ativação e sintaxe instalada compatível com `tailscale serve --bg --https=443`. A configuração final tem somente `/` para `http://127.0.0.1:18088`, sem `tailscale funnel`. A porta 443 fica vinculada à interface Tailscale; MariaDB 3306 e Gunicorn 8000 não têm portas de host.

Foi corrigido um bloqueio encontrado no primeiro boot: uma porta publicada em rede Compose `internal: true` não criou forwarding host no Docker deste host. O frontend agora também se conecta à bridge nomeada `agrofrota-infra-01-host-proxy`; apenas o Nginx usa essa bridge e sua porta continua limitada a loopback. Banco e backend seguem somente na bridge interna. Não houve alteração global de firewall ou Docker.

## Prova de persistência e restore

Uma máquina e uma OS fictícias foram criadas pela API remota com o usuário Gerente. A stack parou por `agrofrota.py stop`, sem remover o volume, e subiu com `agrofrota.py up`. API HTTPS voltou saudável e consulta direta no MariaDB confirmou 7 usuários, 1 máquina de teste e 1 OS de teste. O dump foi criado no diretório privado do operador. O primeiro ensaio de restore foi abortado pelo wrapper, que descartou overrides temporários; o volume ativo estava montado e o Docker recusou removê-lo. Após corrigir o wrapper e o CLI para propagar nomes isolados e aguardar o healthcheck, o restore passou em instância temporária. Nada foi restaurado sobre o banco ativo.

## Evidências e limitações

- Capturas reais do Chrome: `docs/evidence/infra-02/remote-dashboard-admin.png`, `remote-auditor-denied.png` e `remote-assistant-network-error.png`.
- Logins, perfis e escopo testados com credenciais geradas localmente; nenhum segredo/token foi incluído em logs ou evidências versionadas.
- A Central de Operações carregou, e uma requisição de mensagem interrompida pela automação mostrou alerta acessível e removeu o estado de carregamento. A confirmação transacional da Central não foi repetida aqui; ela já possui evidência funcional anterior.
- A declaração do responsável de que o dump histórico é fictício continua distinta da evidência técnica independente. A verificação disponível em `docs/MVP_RELEASE_READINESS.md` não provou titularidade, reutilização ou validade; não houve rotação indiscriminada nem reescrita de histórico.
- Acessibilidade continua conforme AGRO-FINAL-03: contrastes manuais residuais, leitor de tela sem validação confiável e sem declaração/certificação WCAG 2.2 AA.

## Procedimento do iPhone

1. Instale/abra o Tailscale no iPhone e entre na tailnet autorizada.
2. Desative o Wi-Fi e confirme que o Tailscale continua conectado por dados móveis.
3. Abra no Safari `https://gabriel-nitro-anv15-51.tailac6509.ts.net/`.
4. Autentique-se no AgroFrota com uma das contas privadas do inicializador.
5. Valide dashboard, OS, calendário, Central e logout. Não envie senhas por mensagem; recupere-as no terminal privado do host com `python3 deploy/persistent/agrofrota.py credentials`.

## Classificação

**`AGRO_INFRA_02_PARTIAL`** até validar um segundo dispositivo/rede e decidir o acesso Docker necessário para início automático. A stack privada, HTTPS pelo Serve, os sete perfis, persistência e restore isolado foram comprovados neste host. A classificação do MVP é independente e permanece **`AGRO_MVP_FINAL_PARTIAL`** por acessibilidade e risco histórico ainda não encerrados. Não houve merge ou deploy público.

## Verificação AGRO-INFRA-03 — 12/11/2026

| Gate | Resultado | Evidência desta verificação | Limite |
|---|---|---|---|
| Inicialização automática segura | PARTIAL | Docker system service observado como `enabled` e `active`; template de unidade restrita e scripts para instalação root-owned preparados em `deploy/persistent/`. | Nenhuma unidade foi instalada/habilitada. Reboot real não foi executado. Não foi possível inspecionar as políticas efetivas dos containers pelo socket dentro do contexto de execução atual; o Compose declara `unless-stopped`. |
| MariaDB persistente e aplicação | PASS (estado atual) | `GET http://127.0.0.1:18088/api/health` respondeu `200` com `status=online`; checks anteriores de stop/up, registros e backup/restore permanecem válidos. | A verificação desta missão não reiniciou containers nem sistema operacional. |
| Tailscale Serve | PASS (estado observado) | `tailscale serve status` retornou o hostname MagicDNS configurado como `tailnet only`, proxy para `127.0.0.1:18088`; HTTPS `/api/health` respondeu HTTP/2 200 com certificado aceito pelo cliente curl. | Status válido no instante da coleta; sem prova por Safari nesta missão. |
| Segundo dispositivo | PENDING | O estado Tailscale mostrou peer iOS online e peer Linux online. A resposta HTTPS e o Chrome usados nesta sessão originam do host AgroFrota. | Não há automação/controle de Safari no iPhone nem acesso de navegador ao peer Linux. Não declarar login externo aprovado. |
| Rootless Docker | Avaliado, não escolhido | Ferramentas base `dockerd-rootless`/`rootlesskit` e faixas subuid/subgid existem. | `slirp4netns` e `fuse-overlayfs` não foram encontrados; `loginctl` informa `Linger=no`. Usaria daemon e armazenamento diferentes e exigiria migração do volume ativo, então não foi iniciado. |
| Unidade systemd de usuário | Não aplicável neste host | `systemd_user.py` permanece inalterado. | UID do operador não tem acesso direto ao socket Docker; não foi adicionado ao grupo `docker` nem recebeu regra sudo. |

Host: Linux Mint 22.1 `gabriel-Nitro-ANV15-51`; `/` com 21 GB livres na coleta. A inspeção de processos confirma backend Gunicorn e Nginx em execução, sem alteração na stack. O socket Docker não estava acessível diretamente ao UID do ambiente de execução, e comandos Tailscale/systemd de usuário não estavam disponíveis fora do contexto elevado. Não foi feita alteração global, reinício do host, remoção de dados ou migração do volume.

### Decisão de inicialização

Rootless Docker foi rejeitado para esta ativação porque separaria daemon/volume e demandaria uma migração do MariaDB ativo, além de dependências e linger. Uma unidade de sistema baseada em Compose também foi evitada porque poderia executar definição de serviço ou build alterável pelo usuário como root. A proposta instala uma unidade e dois scripts root-owned que chamam somente `docker inspect`, `start` e `stop` para os três containers preexistentes após validar a label do projeto; o arquivo da unidade não chama Compose e não lê scripts ou arquivos de configuração do checkout em runtime. A instalação em `/etc/systemd/system` e `/usr/local/libexec` requer autorização específica e ainda não ocorreu. Procedimento e rollback estão em `docs/TAILSCALE_DEPLOYMENT.md`.

### Teste pelo iPhone

O peer iOS aparece online na tailnet, mas não foi possível automatizar Safari nesta sessão; o gate permanece `PENDING`. No iPhone conectado à tailnet, desative Wi-Fi e use dados móveis, abra `https://gabriel-nitro-anv15-51.tailac6509.ts.net/` no Safari, faça login com uma conta do AgroFrota, confira dashboard, OS, calendário, Central, uma ação permitida/negada conforme o perfil e logout. O operador deve registrar apenas o resultado e horário, sem capturar ou compartilhar senha/token. Para validar rede móvel, confirme que o Tailscale permanece conectado antes de abrir o endereço.

### Classificação

**`AGRO_INFRA_03_PARTIAL`**. HTTPS Serve privado, aplicação no estado atual e infraestrutura persistente anteriormente homologada têm evidência. Permanecem pendentes a autorização/ativação da unidade systemd root-owned, prova de inicialização após reboot e homologação real de navegador no segundo dispositivo. A classificação do MVP continua independente; nenhuma evidência nova encerra acessibilidade ou segurança histórica da PR #9.

CI remota no HEAD `cbb80cda9a247c62694c8c0dbc8a349aadb2e97a`: `backend-mariadb` e `frontend` passaram no run [43303527278](https://github.com/gabrielh063/agroFrota/actions/runs/43303527278).

## Ativação AGRO-INFRA-04 — 12/11/2026

Autorização específica do operador recebida para instalar somente a unidade AgroFrota e seus dois auxiliares. HEAD permaneceu `4d31cb1140e5fca5a940380cb94ba6c4be4ec83a`, PR #10 aberta, árvore limpa antes da instalação e CI verde. `AGENTS.md` não existe na raiz do checkout.

| Verificação | Resultado | Evidência |
|---|---|---|
| Containers | PASS | database/backend/frontend tinham labels do projeto `agrofrota-infra-01`, estavam `running` e `healthy`; todos usavam `unless-stopped`. |
| Volume | PASS | `agrofrota-infra-01-mariadb`, label de projeto correta, montado em `/var/lib/mysql` no container MariaDB. |
| Destinos | PASS | Auxiliares, unidade, diretório de drop-in e link de enable estavam ausentes; `/usr/local` e `/etc/systemd/system` eram `root:root`; nenhum alvo era symlink. |
| Instalação | PASS | Scripts `root:root 0755`; unit `root:root 0644`; `systemd-analyze verify` passou (com avisos preexistentes de `/var/run` em unidades TeamViewer/AnyDesk). Habilitada somente `agrofrota-infra-01.service`. |
| Ciclo systemd | PASS | `systemctl stop` deixou somente os três containers AgroFrota `exited`; `systemctl start` reativou a unidade como `active (exited)` e os três containers ficaram `running/healthy`. |
| Persistência | PASS | Antes/depois do ciclo: 7 usuários, 2 máquinas, 3 OS e 0 agendamentos; volume presente. |
| Healthcheck e HTTPS | PASS | Depois do ciclo, API local e MagicDNS HTTPS retornaram 200; Serve continuou `tailnet only` para `127.0.0.1:18088`. |
| Isolamento | PASS | Inventários de containers não AgroFrota e de volumes comparados antes/depois sem diferenças. Não foi executado comando sobre outros serviços. |
| Reboot | PENDING | A unidade está enabled em `multi-user.target`, com `Requires/After=docker.service`; reboot do host não foi autorizado e não ocorreu. |

O status `active (exited)` é o comportamento correto de `Type=oneshot` + `RemainAfterExit=yes`. Systemd controla start/stop e tenta reiniciar a rotina somente se ela falhar na inicialização; não supervisiona containers continuamente. Os containers têm política Docker `unless-stopped`; ela cobre saídas de processo, não um healthcheck que permaneça unhealthy. A configuração torna o início no boot esperado por análise estática, não comprovado por reboot real.

### Reversão

Desabilitar/parar com `sudo systemctl disable --now agrofrota-infra-01.service`; comparar a unidade e scripts instalados com as cópias do HEAD; se coincidirem, remover somente `/etc/systemd/system/agrofrota-infra-01.service`, `/usr/local/libexec/agrofrota-infra-01-start` e `/usr/local/libexec/agrofrota-infra-01-stop`; executar `sudo systemctl daemon-reload`. Não remover o volume, secrets, backups, containers, redes ou Serve.

**Classificação da ativação:** PASS para controle via systemd e recuperação stop/start; **reboot real permanece PENDING**. A classificação global da infraestrutura continua parcial até prova de reboot e homologação de navegador no segundo dispositivo. A PR #9 permanece independente.

## Atualização AGRO-FINAL-07 — 13/11/2026

O problema de caminhos temporários foi corrigido: Compose monta o SQL de init diretamente da worktree permanente, com `create_host_path: false`; os demais mounts operacionais são secrets privados. Inventário ao final mostrou zero bind mounts em `/tmp`, volume MariaDB original e containers database/backend/frontend saudáveis sem restart. A unidade systemd AgroFrota está ativa (`active (exited)`), e o HTTPS MagicDNS `/api/health` retornou online. Reboot completo do host não foi executado.

Readback após deploy/restart: 7 usuários, 2 máquinas, 3 ordens de serviço, 1 tenant; `Aborted_connects=0`, `Slow_queries=0`, `Max_used_connections=9`. Um backup privado pré-deploy foi feito e restaurado em volume isolado com contagens validadas. Não houve migration ou reprovisionamento no banco ativo.

A investigação instrumentada identificou espera de pool por tenant de 5 s antes do ajuste (dois eventos `database_pool_timeout` durante concorrência browser; buscas centrais/tenant ficaram em poucos milissegundos). Gunicorn tinha 4 threads por worker, enquanto cada engine tenant tinha pool de 2 conexões, sem overflow. Ajustamos para 2 threads por worker, mantendo o pool restrito. Nos 100 requests concorrentes posteriores para `/api/auth/me`, 0 erros; p50 39,93 ms, p95 73,17 ms e máximo 93,87 ms. 100 requests sequenciais: p95 13,91 ms. Nenhum evento `database_pool_timeout` apareceu nos logs desde o deploy final. CPU/RAM capturadas após o tráfego: MariaDB 106,3 MiB, backend 148,4 MiB, frontend 12,78 MiB; os valores são fotografia pontual, não limite de pico.

No browser Chrome com viewport móvel 390×844 foram testados sete perfis, login, restauração, menu, ação de retry após `/api/auth/me` simular 503, retenção do token sem liberar páginas/menu, recuperação após serviço voltar e logout. A listagem de equipe rolou dentro da tabela sem overflow da página. Operador e Auditor foram bloqueados ao abrir URLs diretas sem autorização, sem chamadas de dados protegidos. Safari/iPhone real e rede móvel não foram testados; siga o procedimento abaixo. Evidências e limites detalhados: [`evidence/final/AGRO-FINAL-07-results.md`](evidence/final/AGRO-FINAL-07-results.md).

**Classificação da missão AGRO-FINAL-07:** `AGRO_FINAL_07_READY` para código, regressão local e deploy privado deste host. Isso não altera a classificação independente do MVP, que continua `AGRO_MVP_FINAL_PARTIAL`; acessibilidade pendente e análise de segurança histórica não foram encerradas. O reboot real e a homologação física em Safari seguem como limitações de evidência, sem alegação de aprovação.

PR empilhada [#11](https://github.com/gabrielh063/agroFrota/pull/11), base `feat/agro-infra-01-tailscale-private`; `backend-mariadb` e `frontend` passaram no run [43444489769](https://github.com/gabrielh063/agroFrota/actions/runs/43444489769). PRs #9 e #10 seguem abertas, sem merge.
