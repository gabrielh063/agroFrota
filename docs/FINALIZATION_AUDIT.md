# Auditoria de finalização do AgroFrota

Data da inspeção: 12/11/2026. Base local inicial: `9990955` (`feat/agro-ui-02-layout-redesign` apontava para o mesmo commit da AGRO-UI-01). A branch de consolidação foi criada como `release/agrofrota-mvp-final`. O diretório de trabalho continha alterações locais do redesign UI-02, scripts de demonstração e backups; foram preservados e não foram descartados.

## Inventário do produto

| Área | Estado observado | Evidência/limite |
|---|---|---|
| Autenticação, tenant, sessões e permissões | Implementados no histórico composto | Login/logout autenticado e rotas protegidas exercitados no Chrome; suíte backend aprovada. Perfis além da conta demonstrativa têm cobertura automatizada, sem fluxo de navegador por cada perfil. |
| Maquinários e equipamentos | CRUD e permissões existentes; classificação de máquina usada pela Central | Listas, filtros e telas foram abertas autenticadas; cadastro/edição manual não foram percorridos no navegador nesta rodada. Formulário de equipamento tem labels associados. |
| Ordens de serviço e auditoria | Criação, transições, escopo e contador transacional implementados | Criação pela Central e persistência verificadas no MariaDB; páginas de lista/detalhe abertas. Criação/edição manual não foram percorridas no navegador. |
| Calendário | CRUD de agendamento, validação de conflito e lock operacional compartilhado | Testes MariaDB cobrem conflito, rollback e disputa com indisponibilidade; Central persistiu agenda. Edição manual no calendário não foi percorrida. Limites de timezone e múltiplos workers estão documentados em `AGENDA.md`. |
| Vault e Central de Operações | Conversas, consultas determinísticas, proposta e confirmação transacional implementadas | Conversa autenticada real em duas mensagens, proposta, confirmação, persistência e logout foram verificados no Chrome/MariaDB. Inferência documental real via Ollama não foi executada. |
| Dashboard | Indicadores autorizados, estados e atividade mensal | API e dados demonstrativos carregaram; zeros não são apresentados como atividade. Captura final real incluída. |
| UI-02 | Redesign local de Dashboard, Central e Maquinários, com capturas antes/depois e mobile | Redesign avaliado em Chrome real; matriz de largura sem overflow horizontal em oito páginas e quatro tamanhos. Evidências em `docs/evidence/`. |
| Inicialização | `iniciar_agrofrota.py` local | Inicialização real passou com MariaDB isolado, migrations, seed fictício, Flask/Vite, CORS e probes autenticados. Limpeza deve ser confirmada após encerrar a sessão atual. Scripts auxiliares antigos não foram incluídos na entrega. |
| Migrações e CI | Alembic central/tenant e runner MariaDB descartável existentes | Cabe executar suíte no HEAD final; migrações em banco persistente não foram feitas. |

## Grafo Git e integração

- O padrão remoto confirmado pela API GitHub é `Main`.
- PR #9 está aberta em `release/agrofrota-mvp-final` → `Main`; o head inicial desta finalização era `0c22328ceb7901047f39590d8cdaa7f079891170`. O repositório GitHub é público.
- Heads locais publicados: #5 `7759213`; #6 `d557d80`; #7 `cf1a32c`; #8 `9990955`. A cadeia #5 → #6 → #7 → #8 está refletida nos pais Git locais. As PRs #1–#4 permanecem abertas e são ancestrais via merges rastreáveis da #5, conforme `docs/MISSAO_FINAL.md` e o corpo da PR #5.
- A branch local `feat/agro-ui-02-layout-redesign` compartilhava o HEAD de #8 no início, sem commit adicional; as alterações UI-02 estavam somente no working tree. A branch `release/agrofrota-mvp-final` foi criada desse estado, sem reescrever histórico.
- PR #9 no head inicial tinha `backend-mariadb` e `frontend` verdes. Após as correções e evidências, o commit `5c042c25547f2c221fd6accb435d4051e105f174` foi publicado sem force-push; os dois jobs da execução `43243144116` passaram. Nenhum merge foi feito.

## Achados priorizados

| ID | Módulo | Descrição / reprodução | Impacto | Severidade | Correção proposta | Evidência após correção | Estado |
|---|---|---|---|---|---|---|---|
| F-01 | Integração | PR #9 pública, aberta para `Main`; ainda não integrada. | A candidata depende da aprovação final dos gates. | P1 | Manter PR #9 aberta e publicar os resultados desta finalização. | `gh pr view 9`: head `5c042c2`; PR permanece aberta e os checks passaram. | Parcial |
| F-02 | Agenda | Baseline não compartilhava lock completo entre agendamento, indisponibilidade, estado do ativo e OS. Reproduzido por concorrência agenda × indisponibilidade. | Poderia persistir agenda e bloqueio para o mesmo recurso/horário. | P1 | Unificar protocolo transacional, revalidar sobreposições e impedir desativação/troca/encerramento com agenda pendente. | `test_concorrencia_agendamento_e_indisponibilidade_nao_cria_sobreposicao`, `test_maquina_fora_de_operacao_nao_pode_ser_agendada` e `test_recurso_com_agenda_pendente_nao_pode_ser_indisponibilizado`; runner final 249 aprovados. | Corrigido e coberto |
| F-03 | Inicialização | Inicializador cria banco temporário próprio e executa serviços isolados. | Sem encerramento comprovado, risco de deixar processos/dados temporários ativos. | P2 | Encerrar pelo terminal do próprio launcher e verificar remoção de seu estado temporário. | Smoke checks passaram; Ctrl+C do launcher confirmou limpeza do banco/logs; diretório temporário não existe mais e processos da sessão não ficaram ativos. | Corrigido e verificado |
| F-04 | UX autenticada | Fluxos manuais finais de OS, agenda e perfil sem permissão. | Cobertura do navegador fechada para as transições requeridas. | P1 | Executar em banco descartável e conferir auditoria e persistência direta. | Chrome/CDP: OS criada, editada, reaberta, concluída e cancelada; agenda criada, editada, cancelada e conflito rejeitado; perfil AUDITOR recebeu 403 em `OS.CRIAR`. MariaDB confirma status e eventos. | Corrigido e verificado |
| F-05 | Segurança | Dump SQL removido da árvore corrente, porém ainda alcançável no histórico de repositório público; inclui dados de contato e hashes scrypt. | Hashes de senha permanecem material sensível; declaração do responsável diz que os registros eram fictícios, sem confirmação técnica de titulares/validade atual. | P1 | Preservar declaração/evidência, avaliar com o responsável em canal privado se alguma conta corresponde a titular real; não fazer rotação indiscriminada nem reescrever histórico remoto sem plano aprovado. | Análise local sem exibir valores; domínios não reservados para exemplos, registros não encontrados no seed demonstrativo consultado. Não foi possível verificar o banco de origem ou uso/reutilização de senhas. | Risco PARTIAL não resolvido |
| F-06 | Frontend/acessibilidade | Modais de calendário não associavam labels aos controles nem expunham semântica de diálogo/foco/alerta. | Leitor de tela não identificava claramente o contexto e os campos do modal. | P1 | Associar rótulos e implementar foco inicial, ciclo de tabulação, Escape e anúncios de alerta. | CDP AX tree confirmou diálogo chamado “Agendar serviço”; labels ligados aos campos; foco entra, Tab e Shift+Tab circulam, Escape fecha e restaura foco; erro de conflito tem `role=alert`. `npm run build`/`lint` aprovados. | Corrigido; auditoria geral parcial |
| F-07 | UX/responsividade | Baseline tinha hierarquia visual modesta e excesso de espaço vazio na Central. | Reduzia legibilidade e orientação por tarefa. | P2 | Ajustar layout e validar capturas reais/responsividade. | Redesign antes/depois; 8 páginas em 4 viewports, sem overflow horizontal. | Corrigido |
| F-08 | Inicialização/configuração | Histórico alerta que API antiga causou CORS por rota da Central ausente. | Central poderia bloquear no navegador. | P1 | Probar OPTIONS e GET autenticado na inicialização e manter teste de regressão. | Inicializador e `test_assistente_conversas_preflight_e_rota_autenticada`; smoke real aprovado. | Corrigido |
| F-09 | Testes/CI | CI remota precisa cobrir o head final que inclui a correção de acessibilidade e estas evidências. | Sem checks no head mais recente, gate de integração permanece aberto. | P1 | Executar CI remota após publicar o commit final. | Local: 249 backend aprovados; Vite build e lint exit 0. `backend-mariadb` e `frontend` passaram em `5c042c2`, execução `43243144116`. | Aprovado no head registrado |
| F-10 | Dashboard | Barras mínimas eram desenhadas para meses sem OS, sugerindo atividade fictícia. | Indicador visual enganoso. | P2 | Omitir barra e rótulo para contagem zero. | Screenshot final exibe barra somente para novembro; build aprovado. | Corrigido |

## Testes presentes e ausentes

Existem testes backend cobrindo autenticação, sessões, isolamento, permissões, migrações, agenda, Vault, operações conversacionais, idempotência e concorrência; ver `backend/tests` e o runner `backend/tools/ci.py`. A execução local nesta candidata aprovou 249 testes. Há workflow GitHub com jobs backend/MariaDB e frontend; build e lint locais foram aprovados.

Foram percorridas no Chrome as transições requeridas de OS/agenda, erro de conflito, falha offline, timeout do cliente e resposta perdida após commit, com replay e clique duplo. A matriz instrumental de contraste em todas as páginas não foi concluída; amostra corrigida na Central mediu mínimo 4,68:1 e nenhum item abaixo do AA. Axe-core não está instalado. Orca existe, mas não estava em execução; não foi iniciada uma sessão que pudesse assumir a área de trabalho do operador. A árvore de acessibilidade do Chrome foi examinada. Múltiplos workers, timezone por empresa, backup/restore e gravação direta fora dos serviços seguem sem homologação.

## Limitações acadêmicas conhecidas

- Assistente é determinístico para decisões operacionais e depende de Ollama para respostas documentais; não deve escolher IDs, permissões ou gravar sem confirmação.
- Não há telemetria ou data de conclusão que sustente utilização ou taxa de conclusão no prazo.
- O calendário tem lock compartilhado e cobertura concorrente entre agenda e indisponibilidade, mas não comprova timezone por empresa, múltiplos workers ou escrita direta no banco fora dos serviços da aplicação.
- Não foi homologado para produção, backup/restore, múltiplos workers ou infraestrutura pública.
- A revisão de dump histórico e eventual rotação de credenciais ficam documentadas; histórico remoto não será reescrito.

## Estado do gate

Classificação final desta etapa: **`AGRO_MVP_FINAL_PARTIAL`**. OS, calendário, rede/idempotência e CI (local e remota) passaram. Acessibilidade geral ainda é parcial; segurança histórica está bloqueada até decisão/mitigação do responsável. Nenhum merge foi feito. Ver `MVP_RELEASE_READINESS.md`.

## Complemento AGRO-FINAL-05 — apresentação de perfis

O incremento de perfis adiciona provisionamento somente no tenant descartável do inicializador, a página administrativa **Equipe e Permissões** e menus/ações condicionados a `/api/auth/me`. Não altera `MATRIZ`, políticas de escopo ou privilégios do backend. Senhas de demonstração são únicas por inicialização, ficam em estado temporário `0600`, são passadas ao subprocesso seed e são mostradas somente no terminal do launcher; não há senha em arquivo versionado ou captura.

Chrome real/headless validou 7/7 logins, rótulos de perfil, navegação/ações diferentes, escopo de OS atribuídas para Manutenção e Operador e bloqueio da URL de criação ao Auditor. A tela do Gerente criou e editou uma conta fictícia, com readback. Evidências sem credenciais em `docs/evidence/final/profiles-demo/`; matriz e passos em `docs/DEMO_PERFIS.md`.

O teste de integração `backend/tests/test_demo_perfis.py` cobre as respostas autorizadas/negadas dos sete perfis, OS próprias/atribuídas, escrita de máquina, escrita administrativa, auditoria, revogação após alteração de perfil e reautenticação com permissões atuais. A suíte completa fechou com **250 aprovados**; build aprovado e lint sem erros. A suíte também inclui os testes de isolamento tenant `test_multitenant.py`.

O primeiro push não abriu runs para o novo HEAD. Foi habilitado somente `workflow_dispatch` no workflow existente, sem alterar seus jobs. Os runs [43265695141](https://github.com/gabrielh063/agroFrota/actions/runs/43265695141) no HEAD `ae9fd578` e [43266103005](https://github.com/gabrielh063/agroFrota/actions/runs/43266103005) no HEAD `ab6fe651` passaram em `backend-mariadb` e `frontend`. O follow-up documental final será confirmado pelos checks da PR #9. Este adendo não reclassifica acessibilidade nem a análise de segurança do dump histórico. Ambas permanecem independentes conforme a documentação de prontidão; o MVP segue **`AGRO_MVP_FINAL_PARTIAL`**. Não houve merge, force-push ou reescrita de histórico.

## Complemento AGRO-FINAL-06 — infraestrutura privada e persistência

O host auditado é o Linux Mint 22.1 `gabriel-Nitro-ANV15-51`; Tailscale 1.104.5 estava conectado, MagicDNS presente e sem endpoints Serve existentes. O MariaDB pessoal já estava ativo em loopback e não foi tocado. O socket Docker negou acesso ao usuário e havia aproximadamente 1,3 GB livres no filesystem raiz. Por isso a stack Docker isolada está preparada no repositório, mas não iniciada. Nenhum acesso remoto, certificado, reinício persistente ou restore é declarado como homologado.

O incremento adiciona Compose próprio com MariaDB privado e volume dedicado, dois schemas, runtime SQL com grants limitados a esses schemas, migrações Alembic, Gunicorn, frontend compilado e Nginx same-origin com `/api`. `deploy/persistent/agrofrota.py` prepara segredos aleatórios `0600`, contas fictícias persistidas localmente, parada/reinício, dump privado e restauração em projeto/volume temporários distintos. `iniciar_agrofrota.py` mantém sua finalidade descartável. O provisionador persistente conserva a matriz do backend e recusa seed sobre tenants existentes. Validações finais: runner backend **263 passed / 74 warnings**, build Vite exit 0, lint exit 0 com avisos existentes, parsing/asserções Compose exit 0 e `git diff --check` exit 0. O Docker daemon não foi acessível e a CI remota desta branch empilhada será registrada depois da publicação; nenhum container persistente foi iniciado.

### Revisão histórica de segurança

O responsável declarou nesta missão que o dump foi produzido exclusivamente para popular o MVP com dados fictícios de desenvolvimento/demonstração. A declaração foi registrada como tal. A leitura local do blob histórico ocorreu sem exibir/copiar valores; a inspeção encontrou dados de contato em domínios não reservados para exemplos/testes e não achou correspondência literal desses endereços no inicializador demonstrativo consultado. Portanto, o conteúdo não pôde ser tecnicamente vinculado ao seed demonstrativo. Hashes são material de autenticação; sem o ambiente de origem ou confirmação dos titulares, validade atual e reutilização não são verificáveis. A revisão anterior não encontrou padrões de chaves privadas/tokens conhecidos. Não foi feita rotação indiscriminada nem reescrita do histórico. O risco permanece PARTIAL para decisão do responsável e não é tratado como fato comprovado de exposição de contas reais.

### Acessibilidade e decisão

Esta missão não refez o audit AGRO-FINAL-03. Os contrastes incompletos, mensagens dinâmicas da Central e teste confiável com leitor de tela continuam pendentes, conforme a evidência anterior; sem certificação WCAG 2.2 AA. Resultado global do MVP permanece **`AGRO_MVP_FINAL_PARTIAL`**. A infraestrutura permanece **`AGRO_INFRA_01_PARTIAL`**: implementação preparada, runtime e testes remotos não executados por bloqueios objetivos do host. Evidência sanitizada em `docs/evidence/final/infra-01/`.
