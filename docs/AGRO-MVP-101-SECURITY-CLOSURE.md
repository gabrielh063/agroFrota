# AGRO-MVP-101 — fechamento de segurança

Data: 13/11/2026. **Status: `AGRO_MVP_101_SECURITY_ACTION_REQUIRED`.** Não fazer merge ou deploy até as ações do operador listadas ao final.

## Recuperação e estado publicado

- Worktree preservada: `/home/gabriel/Documents/projetos_portifolio/agrofrota-local`.
- Branch: `feat/agro-mvp-100-resume`.
- HEAD de entrada verificado: `8fa78c40bf168fca00ad5548264d1b906c647354`, igual ao HEAD remoto da PR #13 no início desta missão.
- HEAD verificado no início desta retomada e de código aprovado pela CI antes desta atualização documental: `8c8c88412bfa59ff73ee22a63d3a55cc37f2b434`.
- PR #13: aberta contra `Main`, `CLEAN`, checks backend MariaDB e frontend aprovados no HEAD `8c8c884`; run [43499917867](https://github.com/gabrielh063/agroFrota/actions/runs/43499917867). Nenhum merge realizado. Estado atual: [PR #13](https://github.com/gabrielh063/agroFrota/pull/13).
- PR #12: aberta, `CLEAN`, checks aprovados; branch e evidências preservadas, sem alterações. [PR #12](https://github.com/gabrielh063/agroFrota/pull/12).
- Arquivos locais não rastreados, worktrees e backups existentes foram preservados.
- Não houve mudança na aplicação, banco persistente, serviços ou configuração do `techcell`. Foram criados somente o dump lógico solicitado e relatórios privados; não houve restart, migration ou deploy.

## M1 — validação SSH

**Causa identificada:** `ssh -G techcell` resolve para usuário `gabriel`, host `techcell`, porta 22 e `StrictHostKeyChecking ask`. Não havia registro para `techcell` nem para o FQDN em `~/.ssh/known_hosts`; `known_hosts2` não existe. A falha anterior era uma chave de primeira conexão sem confirmação disponível, não evidência de chave alterada.

Uma consulta `ssh-keyscan` obteve fingerprints **não verificados** da rede:

- ED25519: `SHA256:WL1otnAXT7bB5km48UCgGyOWjgAouJKFsWOapk/RUoM`
- ECDSA: `SHA256:wFkGLaPD7d6hn4HMUa6aSrIGRYG/BXE2qhHOkAAD23A`
- RSA: `SHA256:4wNrOnxwVPiApdDVNRoCvhz0mvUMDTW4AveR8qpl/O4`

O operador confirmou no console local que ED25519 corresponde ao fingerprint informado. O Codex repetiu a consulta e comparou novamente antes de usar uma cópia temporária em `/tmp/agro-mvp-101-techcell-key.candidate`; `ssh` com `StrictHostKeyChecking=yes` autenticou o host. A cópia temporária foi usada como `UserKnownHostsFile` isolado; `~/.ssh/known_hosts` não foi modificado. Todas as conexões seguintes mantiveram verificação estrita.

## M2 — credenciais do histórico público

- Blob: `backend/backups/tenants_antes_migration.sql`; introduzido em `cef6af8ea94f8f9786a855928c48620f0e19c80f` e removido da árvore em `3028d7c8d204fdbb34cd9961010123045d416c6a`. Continua recuperável da história pública.
- Reinspeção sanitizada em memória: 6 valores em campos de e-mail (5 distintos), 7 hashes scrypt distintos e nenhum domínio reservado de exemplo/teste. Marcadores demonstrativos no dump não provam origem sintética. Nenhum valor sensível foi impresso ou incluído neste relatório.
- Correlação somente de leitura executada no próprio `techcell` sobre um tenant ativo: 7 linhas históricas, 5 usernames distintos, 6 valores de e-mail (5 distintos) e 7 hashes scrypt; **zero correspondências ativas** por username, e-mail ou hash exato. Também não houve correspondência com username de conta demo ativa.
- O resultado detalhado privado está em `~/Backups/agrofrota/agro-mvp-101-correlation-full-20261113-180823.txt`, modo `0600`; contém somente referências internas e flags, sem nomes, usernames, e-mails ou hashes. Uma cópia sanitizada sem referências está em `/tmp/agro-mvp-101-private-credential-review.md`, modo `0600`.
- A correlação negativa reduz o risco de contas AgroFrota atuais diretamente atingidas; não prova que o dump seja sintético nem exclui senha reutilizada fora do AgroFrota ou mudança histórica de identificador. Não foi identificada conta ativa que exija rotação no AgroFrota nesta verificação.
- Não foram alteradas contas, senhas, hashes ou sessões; não foi copiado banco de produção para o notebook. O responsável ainda precisa decidir a comunicação/rotação de credenciais reutilizadas para titulares históricos, sem publicar identidades.

### Rotação segura após acesso autorizado

1. Preservar e testar o login de um administrador autorizado antes de qualquer ação futura.
2. Como não houve correspondência ativa, não redefinir contas AgroFrota nesta missão. O responsável deve decidir se notifica titulares históricos para trocar senhas reutilizadas em outros serviços.
3. Se surgir correspondência posterior: forçar reset aprovado, incrementar `session_version`, invalidar sessões/tokens e validar acesso administrativo antes de alterar qualquer administrador.
4. Após eventual rotação, revisar convites pendentes das contas afetadas e revogar os não autorizados. Não expor tokens; validar o fluxo com tokens sintéticos.
5. Não reescrever o histórico público sem aprovação e coordenação; clones e caches podem manter o conteúdo após eventual rewrite.

## M3 — servidor, backup e Restic

### Recursos e stack

- Amostra `2026-11-13 18:02 -03`: RAM total 3.44 GB, usada 2.59 GB, disponível 845 MB; swap total 4.01 GB, usada 722 MB. PSI `avg10/avg60/avg300` voltou a `0.00`; `oom_kill=0`.
- Durante o teste temporário de restore houve amostra transitória com 350 MB disponíveis e PSI full `avg300=0.05`; na amostra posterior a memória disponível se recuperou. Não houve OOM.
- AgroFrota: frontend/backend/MariaDB `healthy`. Limites atuais confirmados: 64/320/384 MiB, respectivamente, com memory+swap igual ao limite. Não foram alterados.
- Immich server/Postgres/Redis `healthy`. ROMM está `running`, sem healthcheck no app, e seu banco `healthy`. Outros containers observados não foram alterados.
- Health local `http://127.0.0.1:18088/api/health` respondeu `{"status":"online","success":true}`. HTTPS público permaneceu inalterado; o checkpoint anterior tinha respondido 200.
- Espaço: `/` com 57 GB livres; `/srv/icloud` com 430 GB livres.

### Backup AgroFrota e cron

- Crontab do usuário contém agendamento `30 3 * * *` para `/home/gabriel/.local/bin/agrofrota-backup` (modo `0700`; mtime 13:21). O wrapper chama o backup da stack em `/srv/agrofrota/app` e grava em `~/Backups/agrofrota`.
- Execução manual às 17:50, sem alterar o banco, terminou com exit 0 e criou `database-20261113-175004.sql`, 30.269 bytes, modo `0600`. Arquivos anteriores observados: `pre-validation-20261113-1305.sql` (28.884 bytes, `0600`) e `private-config-20261113-132109.tar.gz` (1.241 bytes, `0600`). Nenhum conteúdo foi lido.
- Não há `cron.log` e não foi comprovado backup automático no dia 13. A execução manual não comprova o cron; o próximo horário é **14/11/2026 às 03:30 -03** e precisa ser confirmado após ocorrer.
- O wrapper não tem retenção própria e nenhum job de retenção foi identificado nos timers/crontab consultados. Retenção automática permanece sem evidência; arquivos ficam na partição `/`.

### Restore e Restic

- Foi tentado restore da cópia recém-criada em MariaDB `mariadb:11.4` temporário, sem rede/portas/volumes persistentes, dump read-only e limite de 384 MiB. O healthcheck não ficou `healthy` em 60 s; o import não começou, portanto a integridade por restauração deste dump **não foi validada**. Uma consulta posterior confirmou que não restou container temporário. O banco persistente não foi tocado.
- O timer `immich-restic-backup.timer` mostra última ativação às 04:00:02 de 13/11 e próxima às 04:00 de 14/11; `Result=success`, `ExecMainStatus=0`. Isso comprova o acionamento e sucesso reportado pelo systemd, não uma verificação de integridade do repositório.
- Unidade identificada: `/etc/systemd/system/immich-restic-backup.service`; executável root-only `/usr/local/sbin/immich-restic-backup` modo `0700`. `sudo -n` não autorizou leitura do script e o caminho da configuração Restic permaneceu desconhecido. `restic check` **não foi executado**; não se usou configuração presumida. Immich e ROMM não foram alterados.
- Para obter a estrutura sem expor valores, o operador pode executar em terminal interativo confiável o comando sanitizado abaixo; ele pode solicitar senha sudo e imprime somente nomes de variáveis, caminhos de include e ações Restic, nunca valores/argumentos:

```bash
sudo python3 - <<'PY'
from pathlib import Path
import re

p = Path('/usr/local/sbin/immich-restic-backup')
for n, raw in enumerate(p.read_text(errors='replace').splitlines(), 1):
    line = raw.strip()
    if not line or line.startswith('#'):
        continue
    if re.search(r'password|secret|token|credential|authorization', line, re.I):
        names = sorted(set(re.findall(r'\b[A-Z][A-Z0-9_]{2,}\b', line)))
        print(f'{n}: sensitive_line_redacted names={",".join(names)}')
    elif re.search(r'\b(?:source|\.)\s+', line):
        paths = re.findall(r'/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+', line)
        print(f'{n}: include_paths={",".join(paths)}')
    elif 'restic' in line.lower():
        actions = [x for x in ('backup', 'check', 'forget', 'prune', 'repair') if re.search(r'\b' + x + r'\b', line)]
        print(f'{n}: restic_action={",".join(actions) or "unspecified"}; arguments_redacted=yes')
    elif re.search(r'\b[A-Z][A-Z0-9_]{2,}\s*=', line):
        names = re.findall(r'\b([A-Z][A-Z0-9_]{2,})\s*=', line)
        print(f'{n}: variable_names={",".join(names)}; values_redacted=yes')
PY
```

Depois de confirmar o arquivo/configuração e horário de baixo uso, executar somente `restic check` com essa configuração. Não usar `prune`, `forget`, `repair` ou restore sobre dados reais.

## M4 — revisão final da PR #13

- **Convites e RBAC:** token aleatório de uso único, armazenado como hash, expira em 72 horas; tenant/perfil são resolvidos pelo backend; emissão e revogação exigem autorização; o emissor e o perfil delegável são revalidados; convites de emissores desativados/permissões perdidas não podem ser aceitos.
- **Concorrência:** a revisão anterior corrigiu inversão de locks entre aceite e revogação na ordem central → tenant; regressão concorrente e suíte de convites passaram em MariaDB descartável. A implementação trata falha parcial central/tenant com retry baseado em `convite_id`.
- **Autenticação/enumeração:** login tem limites por username e peer; validar/registrar têm respostas genéricas para token inválido, expirado, revogado ou consumido. O backend ignora `X-Forwarded-For` arbitrário.
- **Proxy/rate limit:** backend não publica porta de host e recebe tráfego do Nginx pela bridge privada. Portanto os limites por `request.remote_addr` são compartilhados por usuários atrás desse peer: login 120/minuto, validação 120/minuto e registro 20/15 minutos; registro também limita por token. É um risco operacional P2 em pico de onboarding, não uma forma de falsificar IP ou contornar autenticação. Não foi alterado sem evidência de volume incompatível.
- **Central de IA:** cobertura anterior inclui consulta, histórico, proposta, confirmação/cancelamento, concorrência, rollback, Ollama indisponível, exceção, recursos insuficientes e autorização/tenant. Logs sanitizados preservam identificador de correlação sem conteúdo de conversa/SQL/segredos. A causa específica dos 500 históricos de AGRO-SERVER-01 não pode ser recuperada.
- **Migrações:** validação anterior registrou upgrade/downgrade e re-upgrade em MariaDB descartável. DDL MariaDB pode não ser transacional; falha de migration exige inspeção e correção forward-only, sem downgrade automático. Nenhuma migration foi aplicada ao banco de produção.
- **PR/CI:** os checks backend MariaDB e frontend passaram no HEAD `3827a1c2d6b0dcda9c31ec119cc94d0d15ffcd0a` no run [43510141773](https://github.com/gabrielh063/agroFrota/actions/runs/43510141773); a PR estava `CLEAN`. O relatório também registra que esta atualização documental será validada pela CI do HEAD final.
- **Testes registrados:** 10 testes de convites passaram no MariaDB descartável no checkpoint anterior, incluindo a nova regressão de aceite/revogação. CI de backend e frontend passou no HEAD acima. Os 284 testes completos, build, lint, Chrome e axe-core são evidências do checkpoint anterior, não foram repetidos nesta rodada sem mudança correspondente.
- A instalação atual, os dados e os serviços do servidor devem continuar intactos até autorização separada.

## Publicação controlada — somente após autorização

1. Validar credenciais/contas afetadas e documentar a rotação privada; confirmar a chave SSH e completar os checks de recursos, backup e Restic.
2. Aprovar a PR #13 contra `Main` após CI verde no HEAD que a inclui. PR #12 continua independente. Esta missão não executa merge.
3. Abrir janela de publicação aprovada. Registrar HEAD/imagens atuais, saúde, portas, uso/limites de RAM, espaço e integridade dos sistemas.
4. Criar backup lógico privado dos schemas central e tenant, backup privado da configuração, verificar espaço e testar restauração em stack/volume descartável. Não anexar dados ou segredos ao Git.
5. Validar Compose e atualizar apenas imagens AgroFrota. Aplicar migration central e depois tenant pelo serviço de migration, após backup/restore validados. Preservar limites RAM efetivamente observados, volume, configuração, Nginx/Tailscale e portas 443/8443.
6. Confirmar health API 200, containers saudáveis, registros/tenants preservados, login, convite/revogação/cadastro e escopo RBAC; verificar Immich/ROMM intactos e ausência de pressão de memória.
7. Se aplicação falhar após migration, retornar somente às imagens anteriores e manter schema/volume. Não presumir reversão automática de DDL. Em falha parcial, preservar estado e backup; inspecionar versões Alembic e continuar forward-only após revisão. Restore de produção exige aprovação explícita.

## Pendências para encerrar o gate

1. A correlação não encontrou contas ativas correspondentes; o responsável deve decidir se a incerteza sobre origem/reutilização externa requer aviso/rotação de titulares históricos.
2. Confirmar o primeiro backup automático às 03:30 de 14/11; definir retenção e corrigir/validar o processo se não houver arquivo novo.
3. Repetir restore isolado do dump em janela de recursos adequada, investigando o healthcheck temporário que falhou, sem tocar no banco persistente.
4. Obter com sudo interativo a configuração Restic sem exibir segredos e executar `restic check` em horário de baixo uso.
5. Aguardar CI verde no HEAD que incluir esta atualização do relatório; depois, aprovar merge e publicação separadamente. **A PR não foi integrada e a instalação do servidor não foi atualizada.**
