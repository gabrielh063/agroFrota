# AGRO-MVP-100 — revisão final da release candidate

Data: 13/11/2026. Estado: **`AGRO_MVP_100_FINAL_REVIEW_READY`** para revisão da PR; **não aprovado para produção**.

## Recuperação e Git

- Repositório recuperado em `/home/gabriel/Documents/projetos_portifolio/agrofrota-local`, branch `feat/agro-mvp-100-resume`.
- HEAD inicial: `7fb0ee1e6eb2f45d5762a65041907c7c496fc995`; coincidiu com a branch remota da PR #13. `origin/Main` confirmado em `892108a3f0b9aebf141030517ef0d3974fed9549`.
- Alterações locais e arquivos não rastreados de sessões anteriores foram preservados. Não foi necessário criar worktree. Nenhuma alteração foi feita em `Main`.
- PR #13 continua sendo o destino desta missão. PR #12 permanece independente e não foi alterada. Não houve merge, deploy, reboot ou acesso de escrita ao `techcell`.
- O checkpoint recuperado era a PR #13 publicada em `7fb0ee1`; o CI remoto conhecido nesse checkpoint estava verde. A CI do HEAD final será registrada após publicação desta branch.

## Gates

| Gate | Estado | Evidência desta revisão |
|---|---|---|
| A — Central de IA | **DONE**, com limitação histórica | Testes atuais cobrem consulta, histórico, proposta, confirmação, cancelamento, concorrência, rollback, indisponibilidade do Ollama, exceção inesperada, falta de recursos de banco, tenant incorreto e perfil sem autorização. Respostas de erro levam `X-Request-ID`; logs contêm somente ID e classe da exceção. A causa específica dos HTTP 500 históricos de AGRO-SERVER-01 não foi preservada e permanece desconhecida. |
| B — Convites e cadastro | **DONE** | Convite tenant-bound, token de uso único, emissão/listagem/revogação protegidas, emissor revalidado no aceite, rate limiting, concorrência/idempotência e regressão MariaDB. Cadastro exercitado no Chrome contra MariaDB sintético. |
| C — Funcionalidades do MVP | **DONE** | Funcionalidades existentes preservadas; suíte backend completa passou. Esta revisão não duplicou módulos existentes. |
| D — Frontend e acessibilidade | **DONE para as telas verificadas** | Chrome em seis rotas × quatro viewports, 25 verificações sem overflow; axe-core sem violações WCAG 2.0/2.1 A/AA nas seis rotas; labels, alertas dinâmicos e ordem/foco por teclado verificados no cadastro. Contraste medido para o título do painel: 16,43:1. Safari físico e leitor de tela não foram testados nesta sessão. |
| E — Infraestrutura | **PARTIAL** | O operador informa `Linger=yes`, UFW ativo com entrada negada por padrão, reboot real aprovado, Docker/Tailscale/systemd e serviços AgroFrota/Immich/ROMM recuperados, `/srv/icloud` RW, HTTPS 443/8443, healthcheck 200 e Safari físico do iPhone funcionando. São evidências fornecidas pelo operador, não revalidadas nesta sessão. `restic check`, primeira execução automática comprovada do backup, monitoramento de memória e cadastro funcional na versão atualizada continuam pendentes. |
| F — Qualidade e segurança | **DONE para revisão da PR** | 282 testes backend passaram em MariaDB descartável; build aprovado; lint exit 0 com avisos existentes; migrações central e tenant passaram upgrade/downgrade/upgrade em ambiente descartável; axe sem violações nas telas listadas; histórico sensível revisado sem imprimir valores. CI remota do HEAD final fica pendente até o push. |

## Correções desta revisão

### Cadastro e painel de convites

- Separados erro fatal de convite e erro recuperável de formulário. Senhas diferentes, username duplicado e falha temporária preservam convite e valores para correção e reenvio.
- O envio usa bloqueio síncrono contra duplo clique; conclusão mostra confirmação e link para login. Convite inválido/expirado/revogado/consumido segue terminal.
- Token continua sendo lido do fragmento, removido da barra de endereço após leitura e mantido somente em memória durante o cadastro. Não é escrito em storage persistente.
- O botão de cópia mantém o fallback que seleciona o link para cópia manual quando a Clipboard API não está disponível.
- Evidências Chrome com dados sintéticos: [tela do cadastro](evidence/agro-mvp-100-final-gate/signup-form-375x812.png), [cadastro concluído](evidence/agro-mvp-100-final-gate/signup-complete-375x812.png), [painel/lista de convites](evidence/agro-mvp-100-final-gate/invites-list-1280x800.png), [relatório de homologação](evidence/agro-mvp-100-final-gate/browser-homologation.json) e [resultado axe-core](evidence/agro-mvp-100-final-gate/axe-results.json). Os relatórios não contêm tokens.

### Backend de convites e autenticação

- Listagem agora revalida a política administrativa completa. Emissão e revogação retornam 403 quando o perfil só tem a permissão nominal e não possui autoridade administrativa completa.
- Convite pendente deixa de ser aceito quando o emissor está desativado, seu perfil foi desativado, perdeu autoridade administrativa ou não pode mais delegar o perfil do convite. Logout normal não revoga convites. Um administrador atual deve revogar/reemitir convites inválidos.
- `/validar`, `/registrar`, login e emissão de convites têm limites por janela persistidos no banco central. As chaves são HMAC e não armazenam IP, username nem token em claro. O IP usa apenas `request.remote_addr`; `X-Forwarded-For` do cliente é ignorado. `/registrar` também limita tentativas por token; login limita tentativas por username e limpa o contador em autenticação bem-sucedida.
- Limite fail-closed com HTTP 503 se o armazenamento do rate limiting estiver indisponível; HTTP 429 inclui `Retry-After`. O limite por IP pode agrupar usuários quando todos chegam por um único proxy; a infraestrutura deve confirmar como o socket remoto é apresentado antes de ajustar valores.
- A transação de cadastro mantém o lock central do convite até concluir a escrita no tenant. `usuarios.convite_id` permite reconhecer a gravação prévia no tenant e concluir consumo central no retry sem criar usuário duplicado.
- A migração central `a8c9d0e1f234` cria somente a tabela dos contadores. Foi testado downgrade da central até `8c4a2d91f630` e retorno ao head; a migração tenant `f48d32ce17a1` foi revertida e reaplicada nos dois tenants descartáveis.

### Central de IA

- Erros `OperationalError` de banco/recursos agora retornam 503 recuperável, com rollback. Exceções inesperadas continuam retornando 500 genérico e rollback.
- Cada resposta da blueprint carrega `X-Request-ID` aleatório não sensível. Logs de falha guardam somente o identificador e a classe da exceção; não guardam conversa, parâmetros SQL, credenciais ou mensagem interna.
- Não há evidência suficiente para atribuir causa raiz aos HTTP 500 históricos de AGRO-SERVER-01. O fechamento de sessão e a correção de pool registrados em outros checkpoints não provam a causa dessas requisições específicas.

## Revisão do histórico público

- Arquivo afetado: `backend/backups/tenants_antes_migration.sql`, introduzido no commit `cef6af8ea94f8f9786a855928c48620f0e19c80f` e removido da árvore no commit `3028d7c8d204fdbb34cd9961010123045d416c6a`. O blob continua alcançável na história pública.
- Inspeção local sanitizada: seis valores em campos de e-mail e sete hashes scrypt distintos. Os domínios não são reservados para exemplos/testes. Há marcadores de demonstração no dump, mas não foi possível provar que todas as contas e senhas eram sintéticas ou comparar com as contas atualmente ativas; a checagem anterior também não encontrou correspondência direta com os usuários atuais do seed demonstrativo.
- Classificação: **potencialmente reais e possivelmente utilizáveis; estado atual desconhecido**. Qualquer conta correspondente deve ser tratada como comprometida; não há consulta à produção nesta sessão. A reutilização de senha em outros serviços é risco adicional.
- Mitigação prioritária: o responsável deve identificar contas correspondentes por canal privado, redefinir senhas, invalidar sessões/tokens e solicitar troca em serviços onde a senha possa ter sido reutilizada; preservar registros de auditoria e orientar os titulares. Não alterar contas reais sem backup e procedimento aprovado.
- O histórico público não foi reescrito. A remoção do blob exigiria autorização e coordenação de branches, forks e clones; mesmo após uma eventual limpeza, cópias podem persistir. O risco residual permanece documentado.

## Validação

- `backend/tools/ci.py`: **282 passed**, 79 warnings de depreciação/usos de `datetime.utcnow` em código existente; ambiente MariaDB exclusivo descartável, encerrado pelo runner.
- Migrações: upgrade inicial central e dois tenants passou na suíte. Downgrade/upgrade direcionado central e ambos os tenants também passou.
- Frontend: `npm run build` aprovado. `npm run lint` exit 0, com avisos React de hooks/efeitos já presentes em páginas e componentes existentes.
- Chrome 155: 39 verificações; 25 pares de rota/resolução sem overflow, 14 verificações de convite/cadastro/teclado. Foram exercitados link válido, inválido, expirado, revogado, mismatch corrigido, username duplicado, falha de rede, duplo clique, criação, login e reuso bloqueado.
- axe-core 4.11.0: seis rotas avaliadas (`/login`, `/cadastro`, `/equipe-permissoes`, `/ordens-servico`, `/calendario`, `/assistente`) com WCAG 2.0/2.1 A/AA; **zero violações reportadas**.
- Scanner estático do histórico: não houve impressão de e-mails, hashes ou linhas SQL. Nenhum teste ou evidência usou credenciais de produção.
- `git diff --check`: aprovado antes da atualização documental; repetir após o registro final.

## Operação: revisão, publicação e rollback

Não houve deploy. O `techcell` deve continuar na versão funcional já instalada até autorização explícita.

1. Revisar o diff e aguardar CI verde da PR #13 contra `Main`; PR #12 continua separada.
2. Antes de qualquer atualização aprovada, produzir backup restic verificável, comprovar restauração isolada e registrar os valores de saúde atuais. O `restic check` e a primeira execução automática ainda precisam de evidência.
3. Em uma publicação futura autorizada, atualizar somente a stack AgroFrota, aplicar a migration central depois de backup/restauração e homologar healthcheck, login, emissão/aceite/revogação de convite e regressões. Não tocar nos volumes ou serviços Immich/ROMM.
4. Se a validação falhar, voltar somente a imagem/código da aplicação AgroFrota à versão anterior. Preservar bancos, volumes, secrets, backup, Tailscale Serve e demais stacks. A nova tabela de rate limit é aditiva; não executar downgrade destrutivo como rollback automático.
5. Merge e deploy requerem decisão explícita do responsável. Esta missão não publicou nem integrou a PR.

## Pendências para o operador

- Priorizar a classificação/reset das contas possivelmente expostas e de senhas reutilizadas, sem expor valores em issues ou logs.
- Executar e registrar `restic check`, primeira execução automática do backup e monitoramento de memória.
- Testar o cadastro da versão atualizada no servidor após aprovação e publicação; não confundir com o Chrome local desta revisão.
- Decidir sobre qualquer reescrita coordenada do histórico público e autorizar merge/deploy em passos separados.
