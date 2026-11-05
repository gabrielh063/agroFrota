# Handoff — etapa 1

Branch `codex/fundacao-rf08`, HEAD `714a2c0f623f680207e1c03fd1a180efcd5e532e`. Há alterações sem commit de fundação e alterações preexistentes no calendário e frontend; não descartá-las nem incluí-las automaticamente em commits da fundação. Remoto Main confirmado no mesmo SHA; GitHub informou nenhuma PR ou execução de CI.

Estado recuperado: rotas de cargos possuem verificação de permissão, seed não acrescenta permissões a perfil existente, rotas dev são opt-in, produção agora valida parâmetros básicos, mas não está homologada e testes têm proteção inicial de banco. RF08 completo, migrações, revogação persistente e produção segura ainda não foram concluídos.

Recursos de teste da sessão anterior: MariaDB exclusivo em `/tmp/agrofrota-db-RS3wAB/data`, socket no mesmo diretório, TCP loopback 33971; API de desenvolvimento em loopback 39091. Bancos sintéticos central e dois tenants foram criados por `bootstrap.py` naquele diretório. A API e o banco estavam ativos na retomada. Não conectar testes antes de verificar identidade e configuração da API. Nunca usar esses procedimentos com banco real.

Evidências anteriores: oito testes unitários e build do frontend passaram antes desta retomada; não provam RF08 nem a instalação. Próxima ação: verificar o marcador e o datadir do servidor, confirmar que a API aponta para ele e executar testes de integração existentes; registrar falhas reais.

Marco de recuperação: identidade do datadir, marcador, configuração da API e os dois nomes de bancos sintéticos verificados antes dos testes. Em MariaDB 10.11, autenticação/segurança/multitenant/RF08/revogação: 43 passaram e 1 falhou porque `test_login_valido` usava credenciais históricas. Testes foram parametrizados após essa execução; é necessário repetir. Não representa validação da matriz RF08 proposta.

Marco de segurança: 44 testes HTTP existentes passaram em MariaDB descartável após parametrização; eles não cobrem a nova matriz nem todas as formas de escalada. Foram acrescentadas validações básicas de configuração de produção (15 testes unitários de configuração/schemas/senha passaram), removida a rota anônima de provisionamento e limitado o payload. Uma configuração que passa nesses testes ainda não comprova segurança de produção: RBAC, auditoria, logout e migrações seguem pendentes.

O dump versionado foi classificado como sensível porque contém inserções, indicadores de endereços de email e hashes de senha. Foi retirado da árvore corrente e backups foram ignorados; ele permanece no histórico Git. Identificar credenciais eventualmente afetadas e rotacioná-las, e planejar tratamento do histórico antes de qualquer decisão de reescrita. Conteúdo não foi exibido.

Marco de migrações: foram geradas as revisões iniciais Alembic central `d54b3417f6ae` e tenant `287674a77e77`. Ambas foram aplicadas em bancos MariaDB novos e descartáveis; `alembic check` não encontrou diferenças. Não há ainda caminho de adoção comprovado para instalação existente, nem teste de atualização/restore; não executar `stamp` em dados reais sem comparação e backup. Dois bancos adicionais descartáveis foram criados para essa prova.

Marco de validação atual: nova API em loopback 39092, vinculada ao mesmo MariaDB descartável; 44 testes selecionados passaram sobre o código atual. Os 15 testes unitários de configuração/schemas/senha passaram. Uma inicialização local no modo production com valores sintéticos retornou health 200 e rotas dev 404, sem testar banco. A validação de configuração não fecha as lacunas de segurança.

Para reproduzir nesta sessão, a partir de `backend/`, `../.venv/bin/python /tmp/agrofrota-db-RS3wAB/run_current_tests.py tests/test_auth.py tests/test_security.py tests/test_multitenant.py tests/test_permissoes_rf08.py tests/test_revogacao_acesso.py -q` verifica a identidade e executa os testes; depende dos processos e arquivos temporários atuais e de acesso ao loopback. Para migrações descartáveis já preparadas: `../.venv/bin/python /tmp/agrofrota-db-RS3wAB/alembic_test.py check` e `../.venv/bin/python /tmp/agrofrota-db-RS3wAB/alembic_central_test.py check`. Não são comandos portáveis de instalação; um bootstrap reproduzível e seguro ainda precisa ser entregue.

## Checkpoint Git

Commits de fundação: `3028d7c` (retirada do dump), `f50ae0b` (revisões iniciais), `47637d6` (configuração, cargos e testes). No momento deste registro, HEAD é `47637d6`. Alterações não commitadas anteriores em `backend/routes/calendario.py`, `backend/services/calendario_service.py`, `backend/tests/test_calendario.py`, `frontend/src/pages/Calendario/Calendario.jsx` e `frontend/src/components/AgendamentoDetalhesModal/` permanecem fora desses commits.

Próxima ação executável: implementar e testar a política de autorização administrativa com transações e bloqueio de escalada/último administrador, seguida de auditoria e revogação persistente; não abrir acesso ao servidor por ter passado a validação básica de configuração. Completar CLI e credenciais distintas, migração de instalações existentes e pool limitado. O ambiente de teste e seus helpers são efêmeros, não uma solução de CI.

Marco de autorização de cargos: adicionados seis casos positivos e negativos; a suíte selecionada foi repetida na API atual e terminou com **50 aprovados** em MariaDB descartável. Commit `ac85e79`; HEAD nesse checkpoint. A suíte não demonstra proteção contra escalada ou último administrador.

Marco de publicação: branch publicada em `origin/codex/fundacao-rf08`; [PR #1 em rascunho](https://github.com/gabrielh063/agroFrota/pull/1), base `Main`, explicitamente não pronta para merge ou deploy. HEAD antes deste registro: `a22b85f`. Os cinco caminhos do calendário e frontend permanecem fora dos commits. Duas APIs exclusivas de teste (39091 e 39092) e o MariaDB descartável continuam ativos; não encerrar sem verificar o processo e o uso por outras sessões.
