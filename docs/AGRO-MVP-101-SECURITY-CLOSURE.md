# AGRO-MVP-101 — fechamento de segurança

Data: 13/11/2026. **Status: `AGRO_MVP_101_SECURITY_ACTION_REQUIRED`.** Não fazer merge ou deploy até as ações do operador listadas ao final.

## Recuperação e estado publicado

- Worktree preservada: `/home/gabriel/Documents/projetos_portifolio/agrofrota-local`.
- Branch: `feat/agro-mvp-100-resume`.
- HEAD de entrada verificado: `8fa78c40bf168fca00ad5548264d1b906c647354`, igual ao HEAD remoto da PR #13 no início desta missão.
- PR #13: aberta contra `Main`, `CLEAN`, checks backend MariaDB e frontend aprovados no HEAD de entrada. Nenhum merge realizado. Estado atual: [PR #13](https://github.com/gabrielh063/agroFrota/pull/13).
- PR #12: aberta, `CLEAN`, checks aprovados; branch e evidências preservadas, sem alterações. [PR #12](https://github.com/gabrielh063/agroFrota/pull/12).
- Arquivos locais não rastreados, worktrees e backups existentes foram preservados.
- Nenhum acesso de escrita, restart, migration ou deploy foi feito no `techcell`.

## M1 — validação SSH

**Causa identificada:** `ssh -G techcell` resolve para usuário `gabriel`, host `techcell`, porta 22 e `StrictHostKeyChecking ask`. Não existe registro para `techcell` nem para `techcell.tailac6509.ts.net` em `~/.ssh/known_hosts`; `known_hosts2` também não existe. A tentativa em modo não interativo encontrou uma chave de primeira conexão e falhou porque não podia pedir confirmação. Não há evidência de chave antiga alterada ou de ataque.

Uma consulta `ssh-keyscan` obteve fingerprints **não verificados** da rede:

- ED25519: `SHA256:WL1otnAXT7bB5km48UCgGyOWjgAouJKFsWOapk/RUoM`
- ECDSA: `SHA256:wFkGLaPD7d6hn4HMUa6aSrIGRYG/BXE2qhHOkAAD23A`
- RSA: `SHA256:4wNrOnxwVPiApdDVNRoCvhz0mvUMDTW4AveR8qpl/O4`

Esses valores não foram adicionados a `known_hosts` e não autenticam o host por si sós. **Ação humana:** comparar algoritmo e fingerprint com leitura local no console confiável do servidor, por exemplo `sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`. Se coincidir, o operador pode aceitar a conexão SSH interativa, ou salvar a chave coletada somente depois da comparação. Se não coincidir, não conectar e investigar rotação/reinstalação do host.

## M2 — credenciais do histórico público

- Blob: `backend/backups/tenants_antes_migration.sql`; introduzido em `cef6af8ea94f8f9786a855928c48620f0e19c80f` e removido da árvore em `3028d7c8d204fdbb34cd9961010123045d416c6a`. Continua recuperável da história pública.
- Reinspeção sanitizada em memória: 6 valores em campos de e-mail (5 distintos), 7 hashes scrypt distintos e nenhum domínio reservado de exemplo/teste. Marcadores demonstrativos no dump não provam origem sintética. Nenhum valor sensível foi impresso ou incluído neste relatório.
- Não foi possível determinar correspondência com usuários **ativos**: o banco do servidor não foi consultado. A revisão anterior não encontrou correspondência direta com usernames do seed demonstrativo atual, o que não comprova inatividade ou origem sintética.
- Relatório privado/sanitizado criado em `/tmp/agro-mvp-101-private-credential-review.md`, modo `0600`. Contém apenas contagens, referências públicas de commit, status de correlação e procedimento; não contém e-mails, hashes, dados de produção ou senhas.
- Não foram alteradas contas, senhas ou sessões; não foi copiado banco de produção. Classificar todas as possíveis correspondências como potencialmente comprometidas até confirmação.

### Rotação segura após acesso autorizado

1. Confirmar por canal privado que pelo menos um administrador autorizado consegue autenticar e que há uma via de recuperação.
2. No host, correlacionar em memória os e-mails do blob com usuários ativos e produzir apenas referências internas/status sanitizados em armazenamento privado restrito.
3. Para cada conta ativa correspondente, forçar redefinição de senha e incrementar `session_version` para invalidar JWTs/sessões existentes. Confirmar e revogar tokens de recuperação, caso existam.
4. Validar novamente o login do administrador preservado antes de alterar ou desativar qualquer conta administrativa.
5. Orientar troca da mesma senha em quaisquer outros serviços onde possa ter sido reutilizada.
6. Depois da rotação, revisar convites pendentes emitidos por contas atingidas e revogar os que não forem mais autorizados. Não expor tokens; confirmar por testes sintéticos que tokens continuam hashed, expiram, são de uso único e não podem ser emitidos por perfis sem permissão.
7. Não reescrever o histórico público sem aprovação e coordenação; clones e caches podem manter o conteúdo após eventual rewrite.

## M3 — servidor, backup e Restic

Não iniciei as verificações remotas, pois o usuário condicionou o acesso à validação da chave. Assim, nesta sessão:

- Memória, swap, PSI, OOM, containers e limites ativos de recursos: **não verificados**.
- Cron/timer das 03:30 e primeira execução automática: **não verificados**. Uma execução manual do script, se existir, não comprova o agendamento futuro.
- Último backup AgroFrota, retenção, espaço, integridade e restore isolado atual: **não verificados**. Há registro histórico de backup/restauração em ambiente isolado, mas não foi tratado como estado atual.
- Configuração do Restic do Immich e `restic check`: **não identificados/executados**; não se usou config presumida e não houve alteração no Immich ou ROMM.
- Única verificação operacional independente nesta sessão: health HTTPS de AgroFrota respondeu `200` com `status=online` em `https://techcell.tailac6509.ts.net:8443/api/health`.
- Nenhum reboot, `prune`, `forget`, `repair`, restore em dados reais, `down -v`, alteração de sudoers ou contorno de autenticação ocorreu.

Depois de validar a chave, executar as coletas read-only documentadas em [AGRO-MVP-100-RELEASE-GATE.md](AGRO-MVP-100-RELEASE-GATE.md). Identificar a unidade Restic e executar exclusivamente o comando existente que comprovadamente chama `restic check`, de preferência fora do horário de pico. Nunca imprimir configurações, tokens, conteúdo dos dumps ou ambiente com segredos.

## M4 — revisão final da PR #13

- **Convites e RBAC:** token aleatório de uso único, armazenado como hash, expira em 72 horas; tenant/perfil são resolvidos pelo backend; emissão e revogação exigem autorização; o emissor e o perfil delegável são revalidados; convites de emissores desativados/permissões perdidas não podem ser aceitos.
- **Concorrência:** a revisão anterior corrigiu inversão de locks entre aceite e revogação na ordem central → tenant; regressão concorrente e suíte de convites passaram em MariaDB descartável. A implementação trata falha parcial central/tenant com retry baseado em `convite_id`.
- **Autenticação/enumeração:** login tem limites por username e peer; validar/registrar têm respostas genéricas para token inválido, expirado, revogado ou consumido. O backend ignora `X-Forwarded-For` arbitrário.
- **Proxy/rate limit:** backend não publica porta de host e recebe tráfego do Nginx pela bridge privada. Portanto os limites por `request.remote_addr` são compartilhados por usuários atrás desse peer: login 120/minuto, validação 120/minuto e registro 20/15 minutos; registro também limita por token. É um risco operacional P2 em pico de onboarding, não uma forma de falsificar IP ou contornar autenticação. Não foi alterado sem evidência de volume incompatível.
- **Central de IA:** cobertura anterior inclui consulta, histórico, proposta, confirmação/cancelamento, concorrência, rollback, Ollama indisponível, exceção, recursos insuficientes e autorização/tenant. Logs sanitizados preservam identificador de correlação sem conteúdo de conversa/SQL/segredos. A causa específica dos 500 históricos de AGRO-SERVER-01 não pode ser recuperada.
- **Migrações:** validação anterior registrou upgrade/downgrade e re-upgrade em MariaDB descartável. DDL MariaDB pode não ser transacional; falha de migration exige inspeção e correção forward-only, sem downgrade automático. Nenhuma migration foi aplicada ao banco de produção.
- **PR/CI:** HEAD de entrada `8fa78c40bf168fca00ad5548264d1b906c647354`; PR #13 `CLEAN`, checks backend MariaDB e frontend verdes no run [43496587674](https://github.com/gabrielh063/agroFrota/actions/runs/43496587674). Mudanças apenas nesta documentação ainda precisarão de CI no HEAD que a incluir.
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

1. Operador fornecer o fingerprint SSH esperado, obtido no console confiável, para comparação com a chave apresentada.
2. Após validação, executar correlação privada das contas, decidir/autorizar redefinições e invalidação de sessões e confirmar acesso administrativo.
3. Verificar recursos, cron/execução automática, último backup, retenção, espaço, restore isolado e `restic check` com a configuração autorizada do Immich.
4. Atualizar este relatório e a PR com evidências sanitizadas; repetir CI no HEAD que contenha este documento.
5. Aguardar autorização explícita e separada para merge e publicação. **A PR não foi integrada e o servidor não foi atualizado.**
