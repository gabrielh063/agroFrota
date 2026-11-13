# AGRO-MVP-100 — release gate

Data: 13/11/2026. Status: **`AGRO_MVP_100_SECURITY_ACTION_REQUIRED`**. A publicação não está autorizada por este relatório.

## Recuperação e estado Git

- Worktree recuperada: `/home/gabriel/Documents/projetos_portifolio/agrofrota-local`.
- Branch: `feat/agro-mvp-100-resume`.
- HEAD de entrada: `b6294930662e2bec30c1de6733a8b60f48cfc78f`, igual ao HEAD da PR #13 consultado no GitHub.
- `Main` consultada: `892108a3f0b9aebf141030517ef0d3974fed9549`.
- Worktree da PR #12 continua em `.worktrees/agro-final-07`, HEAD `80d78cda003c25cdc45a87a1a3f675e07e43438b`. Registros prunable em `/tmp` foram preservados.
- Arquivos não rastreados preexistentes (backups `.bak`, capturas, `.worktrees/`, scripts locais e `node_modules/`) foram preservados.
- PR #13 está aberta contra `Main`, sem conflito, sem decisão de review e com `backend-mariadb` e `frontend` verdes no HEAD de entrada; [PR #13](https://github.com/gabrielh063/agroFrota/pull/13), CI run [43492480217](https://github.com/gabrielh063/agroFrota/actions/runs/43492480217).
- PR #12 está aberta e independente, sem conflito, com ambos os checks verdes no SHA informado; [PR #12](https://github.com/gabrielh063/agroFrota/pull/12). Não foi alterada.
- `AGENTS.md` aplicável não existe no repositório AgroFrota. Instruções TARS e os documentos de retomada/revisão existentes foram consultados.
- Não houve merge, deploy, reboot ou alteração do servidor nesta revisão.

## Revisão técnica da PR #13

### Correção nesta revisão

Foi identificada inversão de ordem de locks nas rotas de aceite e revogação de convites: o aceite bloqueava primeiro a linha do convite no banco central e depois `AdminLock` no tenant; a revogação fazia o inverso. Requisições concorrentes podiam causar deadlock no MariaDB.

A revogação agora bloqueia a linha central primeiro e então verifica a autorização do tenant, usando a mesma ordem central → tenant do aceite. Foi adicionada regressão concorrente que exige um resultado serializado: ou o cadastro conclui e a revogação recebe conflito, ou a revogação conclui e o cadastro recebe convite inativo.

### Achados e cobertura

- **Convites/RBAC/tenant:** emissão exige `USUARIO_CRIAR` e perfil delegável; o aceite recebe somente token, username e senha, resolve tenant/perfil pelo registro central, revalida o emissor e não aceita seleção de tenant ou perfil pelo cliente. Listagem e revogação são filtradas pelo tenant autenticado.
- **Token:** 256 bits aleatórios, persistido como SHA-256, expiração de 72 horas, consumo único, estado revogado/consumido e retry idempotente documentados e cobertos por testes.
- **Conta do emissor:** convites pendentes deixam de valer se o emissor perder a autorização ou o perfil ficar inativo. O teste correspondente já consta na suíte.
- **Unicidade/concorrência:** username/e-mail protegidos por unicidade do tenant; consumo central com `FOR UPDATE`; retry após commit parcial do tenant coberto. A regressão nova cobre corrida aceite/revogação.
- **Transação central/tenant:** não existe transação distribuída. Se o banco tenant confirmar e a central falhar, a próxima tentativa localiza o usuário por `convite_id`, compara username/senha e finaliza o consumo central. Não se deve apagar esse usuário para “reverter” a tentativa.
- **Enumeração:** validar convite e registrar retornam mensagem genérica para token inválido/expirado/revogado/usado; divergência de username e e-mail pode ser observada somente por quem possui token válido.
- **Rate limiting e proxy:** Nginx é o único serviço com porta publicada; backend só participa da rede Compose privada. As rotas usam `request.remote_addr` e ignoram `X-Forwarded-For` fornecido/encaminhado. Assim, todas as pessoas que chegam pelo Nginx compartilham o endereço do peer Docker no backend. Os limites atuais de 120 logins/minuto, 120 validações/minuto e 20 cadastros/15 minutos são, portanto, globais para essa entrada; cadastro também limita cada token a 5 tentativas/15 minutos e login limita cada username. Isso evita falsificação de IP via cabeçalho, mas pode limitar um lote legítimo de onboarding. Classificado como **P2 operacional**, sem evidência de abuso ou falha de autenticação; validar volume esperado antes de ampliar usuários. Não foi confiado nem ativado `X-Forwarded-For` arbitrário.
- **Nginx/HTTPS:** `/api/` é encaminhado ao backend na rede privada; a stack publica Nginx apenas em `127.0.0.1:18088`. O endpoint atual do servidor respondeu HTTP 200 em HTTPS; Nginx retornou CSP, `nosniff`, `DENY` e política de referrer.
- **Central de IA:** as evidências da PR cobrem consulta operacional, histórico, proposta, confirmação/cancelamento, concorrência, rollback, Ollama indisponível, exceção inesperada, tenant incorreto, perfil sem autorização e falta de recursos. Logs sanitizados carregam `X-Request-ID` e classe da exceção, sem conteúdo de conversa, credenciais, SQL ou mensagem interna. A causa histórica específica dos HTTP 500 de AGRO-SERVER-01 não foi preservada e não é possível atribuí-la retroativamente.
- **Integridade:** migrations adicionam estrutura de convites/limites e referência nullable de convite no usuário; a validação anterior registrou upgrade e downgrade/re-upgrade em MariaDB descartável. MySQL/MariaDB DDL não é transacional; rollback de publicação não deve presumir downgrade automático.
- **P1:** hashes de senha potencialmente ativos no histórico público (detalhe abaixo).
- **P2:** buckets por peer compartilhados no proxy Docker e métricas/backup/Restic atuais do host sem comprovação nesta sessão.

## Credenciais históricas — ação prioritária

- O dump `backend/backups/tenants_antes_migration.sql` foi adicionado em `cef6af8ea94f8f9786a855928c48620f0e19c80f` e removido da árvore em `3028d7c8d204fdbb34cd9961010123045d416c6a`. O blob continua recuperável da história pública.
- Inspeção sanitizada anteriormente registrada: sete hashes scrypt distintos e seis valores de e-mail. Há marcadores de demonstração, mas os domínios não provam serem dados fictícios. A inspeção não encontrou correspondência direta com os usernames do seed demonstrativo atual; não houve comparação com o banco vivo e não há prova de que todas as contas eram sintéticas.
- **Classificação:** dados potencialmente reais; atividade atual desconhecida; risco de cracking offline e reutilização de senha permanece. As contas correspondentes e seus titulares não são identificados neste documento público. Referência operacional: mapeamento privado a ser feito pelo responsável a partir do blob histórico, sem copiar valores para PR, logs ou evidências.
- **Menor mitigação segura:** em ambiente administrativo privado, identificar quais usuários ainda existem/estão ativos; forçar redefinição prioritária de senha para cada correspondência; incrementar `session_version`/revogar sessões e tokens existentes; manter um administrador autorizado e testar seu login antes de desativar qualquer conta. Orientar troca em todo serviço onde a mesma senha possa ter sido reutilizada. Não foi feita redefinição nem consulta ao banco de produção.
- **Histórico:** não foi reescrito. Remoção futura exige autorização e coordenação de branches, forks e clones; cópias públicas podem sobreviver e o risco não desaparece após rewrite.
- A ação de credenciais é necessária antes da publicação, portanto a classificação permanece **`AGRO_MVP_100_SECURITY_ACTION_REQUIRED`**.

## Estado operacional verificado nesta sessão

- `https://techcell.tailac6509.ts.net:8443/api/health`: HTTP 200, `status=online`, com certificado HTTPS aceito pelo cliente. Esta checagem não reiniciou nem alterou serviços.
- SSH somente de leitura não foi possível: o host não constava como verificado em `known_hosts` e o cliente retornou `Host key verification failed`. A verificação da chave deve ser feita pelo operador por canal confiável; não se desativou `StrictHostKeyChecking` nem se aceitou uma chave sem confirmação.
- Por isso não foram comprovados nesta sessão: `docker stats`, limites atuais de RAM, pressão/OOM, timers e primeira execução automática do backup AgroFrota, último dump/retention/espaço, restore isolado mais recente, nem `restic check` do Immich. Nenhum desses itens é inferido a partir de relatórios históricos de outro host.
- O operador informou reboot real aprovado previamente, `Linger=yes`, Docker/Tailscale/systemd ativos após boot, `/srv/icloud` RW, UFW ativo, portas 443/8443 preservadas, Immich/ROMM retornados e Safari físico funcional. Esses relatos são mantidos como evidência do operador, não como coleta independente desta sessão.
- Não se alteraram Immich, ROMM, configuração Restic, banco persistente ou serviços do `techcell`.

### Coleta pendente no techcell

Após validar a identidade SSH do host por canal confiável, executar em shell interativo do operador (a coleta é somente leitura):

```bash
free -b
cat /proc/pressure/memory
grep -E '^(oom_kill|oom|pgmajfault) ' /proc/vmstat
sudo docker stats --no-stream
sudo docker inspect --format '{{.Name}} memory={{.HostConfig.Memory}} status={{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' $(sudo docker ps -q)
systemctl list-timers --all --no-pager | grep -Ei 'agro|backup|restic|immich'
systemctl --user list-timers --all --no-pager | grep -Ei 'agro|backup|restic|immich'
df -h / /srv/icloud
find ~/.config/agrofrota-infra-01 -maxdepth 2 -type f -name '*.sql' -printf '%f|%s|%TY-%Tm-%TdT%TH:%TM|%m\n'
```

Não imprimir `Environment`, arquivos de credenciais, conteúdo de dumps ou variáveis Restic. Identificar o timer Restic existente e executar somente seu `restic check` comprovadamente somente leitura, preservando a configuração atual; não usar `prune`, `forget`, `repair` nem restore sobre dados reais. Se a unidade requerer sudo, executar o comando em terminal interativo do operador; não mudar sudoers. As saídas devem ser redigidas antes de anexar evidências.

## Procedimento de publicação e rollback

**Não executado.** Exige primeiro mitigação/aprovação do responsável e janela de publicação autorizada.

1. Confirmar merge da PR #13 contra `Main` somente após aprovação humana e CI verde no HEAD publicado. PR #12 permanece separada.
2. No host, registrar SHA/imagens atuais, estado `docker compose ps`, healthchecks, portas 443/8443, uso de RAM e limites por container. Confirmar espaço livre e não prosseguir se limites atuais não puderem ser mantidos.
3. Gerar backup lógico completo dos schemas central e tenant para destino privado novo, `umask 077`, modo `0600`; gerar backup restrito da configuração privada AgroFrota. Usar `python3 deploy/persistent/agrofrota.py backup --output <destino-privado/agrofrota-predeploy-AAAA-MM-DD.sql>` e `restore-test --backup <mesmo-arquivo>`. Validar os dois schemas, versão Alembic e registros restaurados no ambiente isolado. Não copiar credenciais/dumps ao notebook ou Git.
4. Confirmar espaço antes/depois dos backups (`df -h`); confirmar integridade do Restic Immich separadamente com `restic check` somente leitura. A retenção de dump deve respeitar a janela/retention já definida e não remover backups até a restauração ter sido comprovada.
5. Validar a configuração Compose e construir apenas imagens backend/frontend AgroFrota. Aplicar migration central e depois tenant via serviço `migrate`, uma única vez, com backup/restauração validados. A migration tenant inclui referência de convite; a central cria tabela de rate limits. Não usar `down -v`, não remover volumes e não tocar em Immich/ROMM.
6. Atualizar exclusivamente backend/frontend da stack AgroFrota mantendo nomes, limites de memória verificados, volume, segredos, Nginx, Tailscale Serve e portas existentes. Não executar seed demonstrativo em base populada.
7. Pós-deploy: `/api/health` 200; containers AgroFrota saudáveis; schemas/contagens preservados; Immich e ROMM inalterados/saudáveis; 443 e 8443 intactos; memória sem pressão/OOM sustentados; fluxo novo usuário validado.

### Falha de migration e rollback

- MariaDB pode aplicar DDL parcialmente. Em falha, parar a atualização de imagem, preservar containers, banco, volume e backup; inspecionar versão central/tenant e tabelas no contexto de manutenção. Não assumir rollback automático nem rodar downgrade/destruição.
- Corrigir ou retomar a migration de forma forward-only após novo backup e revisão. Só restaurar dados de produção com aprovação explícita, backup preservado e procedimento isolado aprovado.
- Se a migration terminou e a aplicação falhar, retornar somente imagens/código AgroFrota à imagem anterior, mantendo o schema aditivo e o volume. O código anterior deve ignorar as novas colunas/tabela; confirmar health e fluxo operacional antes de encerrar a janela.
- Nunca usar `docker compose down -v`, remover volume, resetar banco, alterar Tailscale Serve ou reiniciar o host como rollback.

## Roteiro de homologação pós-deploy

Executar em janela aprovada, com dados sintéticos e sem criar demonstrações antes da autorização:

1. **Administrador:** login; dashboard; criar/listar/revogar convite; gerenciar usuário e perfis; verificar que perfil não delegável é recusado.
2. **Novo usuário no iPhone:** abrir convite privado no Safari; completar username/senha; corrigir erro de validação sem perder o convite; criar conta e entrar; conferir que só vê dados autorizados. Testar link consumido/revogado. Nenhuma homologação física nova foi alegada nesta sessão.
3. **Operações:** criar/editar OS; consultar máquinas; calendário; proposta na Central, confirmação e cancelamento; recarregar sessão. Persistência após reinício da stack somente dentro da janela aprovada.
4. **Infra:** API 200, containers healthy, banco/contagens preservados, Immich/ROMM intactos, HTTPS 443/8443 preservado, RAM sem pressão sustentada e backup automatizado executado.

## Evidências de validação e gates

- Nova regressão e testes de convites executados no MariaDB descartável: **10 passed**, 2 avisos de depreciação `datetime.utcnow`; ambiente temporário encerrado após o teste.
- A primeira tentativa do runner com Python do sistema falhou antes dos testes por falta de Alembic; não alterou banco persistente. O runner foi repetido com venv temporário e isolado.
- CI remoto no commit de correção `de49b0ae8f1c0bd6e455433d131bf632236d7027`: `backend-mariadb` e `frontend` passaram; a PR permaneceu `CLEAN`. O relatório será acompanhado pelo check do commit documental final na [PR #13](https://github.com/gabrielh063/agroFrota/pull/13).
- `git diff --check` passou após a alteração de código; repetir após fechar este documento.
- Baseline reportado no checkpoint anterior: 284 testes backend, build frontend e lint exit 0 com avisos; navegador Chrome com 39 verificações, 25 combinações viewport/rota sem overflow e axe-core zero violações em seis rotas. Essas evidências são anteriores a esta revisão e não foram repetidas sem mudança correspondente.
- Cadastro validado previamente em Chrome com estados válidos/inválidos/expirados/revogados, divergência de senhas, username duplicado, indisponibilidade de rede, duplo clique, sucesso/login e reuso. Capturas sanitizadas existentes; sem token verdadeiro. Não houve nova homologação física em Safari.

| Gate | Estado | Observação |
|---|---|---|
| Central de IA | DONE | Testes e logs sanitizados anteriores; causa histórica AGRO-SERVER-01 desconhecida. |
| Convites/cadastro | DONE com correção nesta revisão | 10 testes passaram; CI do novo HEAD aguarda. |
| Funcionalidades MVP | DONE | Cobertura existente preservada. |
| Frontend/acessibilidade | DONE para evidência Chrome anterior | Revalidar no build do HEAD final; sem alegação de Safari físico novo. |
| Infraestrutura | PARTIAL | Health HTTPS 200; métricas, timers, backup/restic atuais e limites RAM aguardam acesso autenticado ao host. |
| Qualidade/publicação | PARTIAL | Checks prévios verdes; CI do commit desta revisão e ação sobre credenciais pendentes. |

## Decisões ainda necessárias

1. O responsável deve mapear privadamente as contas do dump e ordenar redefinição de senha/invalidação de sessões para correspondências atuais, além de orientar troca em serviços com senha reutilizada.
2. Confirmar/verificar a chave SSH do `techcell` por canal confiável e coletar métricas, timer/backup, restore e `restic check` seguro.
3. Confirmar limites RAM atuais e capacidade esperada de convites atrás do peer compartilhado do proxy.
4. Revisar e aprovar merge da PR #13; depois, em decisão separada, autorizar publicação e janela de homologação. Nenhum desses passos foi executado aqui.
