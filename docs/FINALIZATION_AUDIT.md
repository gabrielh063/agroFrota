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
- PRs abertas observadas: #1–#8; não há PR #9. #5 aponta para `Main`; #6 aponta para `codex/missao-final`; #7 aponta para `feat/agro-ia-vault-dashboard`; #8 aponta para `feat/agro-ia-02-conversational-operations`.
- Heads locais publicados: #5 `7759213`; #6 `d557d80`; #7 `cf1a32c`; #8 `9990955`. A cadeia #5 → #6 → #7 → #8 está refletida nos pais Git locais. As PRs #1–#4 permanecem abertas e são ancestrais via merges rastreáveis da #5, conforme `docs/MISSAO_FINAL.md` e o corpo da PR #5.
- A branch local `feat/agro-ui-02-layout-redesign` compartilhava o HEAD de #8 no início, sem commit adicional; as alterações UI-02 estavam somente no working tree. A branch `release/agrofrota-mvp-final` foi criada desse estado, sem reescrever histórico.
- O fetch foi concluído. `git ls-remote` falhou depois por resolução DNS, mas a API GitHub via `gh` retornou PRs e checks. Nenhuma branch foi forçada e nenhum merge foi feito.

## Achados priorizados

| ID | Módulo | Descrição / reprodução | Impacto | Severidade | Correção proposta | Evidência após correção | Estado |
|---|---|---|---|---|---|---|---|
| F-01 | Integração | Oito PRs abertas em cadeia; #8 e a nova UI-02 não estão em `Main`. Conferir `gh pr list` e `git log --graph`. | Release não integrada; CI de heads anteriores não valida o HEAD final. | P1 | Publicar PR final com ancestralidade rastreável; não mergear sem todos os gates e proteção respeitada. | Estado da PR final e checks remotos, se publicação de rede for possível. | Em andamento |
| F-02 | Agenda | Baseline não compartilhava lock completo entre agendamento, indisponibilidade, estado do ativo e OS. Reproduzido por concorrência agenda × indisponibilidade. | Poderia persistir agenda e bloqueio para o mesmo recurso/horário. | P1 | Unificar protocolo transacional, revalidar sobreposições e impedir desativação/troca/encerramento com agenda pendente. | `test_concorrencia_agendamento_e_indisponibilidade_nao_cria_sobreposicao`, `test_maquina_fora_de_operacao_nao_pode_ser_agendada` e `test_recurso_com_agenda_pendente_nao_pode_ser_indisponibilizado`; runner final 249 aprovados. | Corrigido e coberto |
| F-03 | Inicialização | Inicializador cria banco temporário próprio e executa serviços isolados. | Sem encerramento comprovado, risco de deixar processos/dados temporários ativos. | P2 | Encerrar pelo terminal do próprio launcher e verificar remoção de seu estado temporário. | Smoke checks passaram; Ctrl+C do launcher confirmou limpeza do banco/logs; diretório temporário não existe mais e processos da sessão não ficaram ativos. | Corrigido e verificado |
| F-04 | UX autenticada | Listas e navegação foram exercitadas; fluxos manuais de cadastro/edição de ativos, OS e edição de agenda não foram concluídos no navegador. | Cobertura manual parcial dos fluxos principais. | P1 | Exercitar fluxos manuais restantes ou manter a candidata parcial com limitação explícita. | Capturas reais e notas de fluxo; suíte backend cobre regras e persistência. | Parcial |
| F-05 | Segurança | Dump histórico continha emails e hashes e foi removido da árvore, mas continua no histórico Git; sem reescrita remota autorizada. | Exposição histórica potencial; credenciais afetadas podem necessitar rotação. | P1 | Não reescrever histórico; manter nota e recomendar rotação das credenciais afetadas. | `HANDOFF_ETAPA_1.md`; busca adicional não deve exibir valores sensíveis. | Aberto/documentado |
| F-06 | Frontend | Lint histórico tem avisos de hooks/efeitos; executar lint no estado final e revisar avisos relevantes. | Pode ocultar efeitos inconsistentes, embora sem erro bloqueante conhecido. | P2 | Corrigir apenas avisos relacionados aos módulos alterados ou regressões observadas. | Saída `npm run lint`. | Em andamento |
| F-07 | UX/responsividade | Baseline tinha hierarquia visual modesta e excesso de espaço vazio na Central. | Reduzia legibilidade e orientação por tarefa. | P2 | Ajustar layout e validar capturas reais/responsividade. | Redesign antes/depois; 8 páginas em 4 viewports, sem overflow horizontal. | Corrigido |
| F-08 | Inicialização/configuração | Histórico alerta que API antiga causou CORS por rota da Central ausente. | Central poderia bloquear no navegador. | P1 | Probar OPTIONS e GET autenticado na inicialização e manter teste de regressão. | Inicializador e `test_assistente_conversas_preflight_e_rota_autenticada`; smoke real aprovado. | Corrigido |
| F-09 | Testes | CI remoto aprovado pertence a heads anteriores (#5/#8), não valida as alterações locais. | Candidato local sem validação remota. | P1 | Executar runner backend, build e lint; publicar para checks remotos. | Backend 249 aprovado; build/lint local aprovados; CI remoto pendente. | Local aprovado; remoto pendente |
| F-10 | Dashboard | Barras mínimas eram desenhadas para meses sem OS, sugerindo atividade fictícia. | Indicador visual enganoso. | P2 | Omitir barra e rótulo para contagem zero. | Screenshot final exibe barra somente para novembro; build aprovado. | Corrigido |

## Testes presentes e ausentes

Existem testes backend cobrindo autenticação, sessões, isolamento, permissões, migrações, agenda, Vault, operações conversacionais, idempotência e concorrência; ver `backend/tests` e o runner `backend/tools/ci.py`. A execução local nesta candidata aprovou 249 testes. Há workflow GitHub com jobs backend/MariaDB e frontend; build e lint locais foram aprovados.

Não foram comprovados para a candidata final: todos os CRUDs manuais por navegador; teste visual de conflito/erro de rede; matriz instrumental WCAG/contraste e leitor de tela; CI remoto no novo head; funcionamento com múltiplos workers; timezone por empresa; backup/restore. O fluxo autenticado Central→proposta→OS+agenda foi comprovado, bem como OPTIONS/CORS e rotas da Central no processo iniciado pelo launcher.

## Limitações acadêmicas conhecidas

- Assistente é determinístico para decisões operacionais e depende de Ollama para respostas documentais; não deve escolher IDs, permissões ou gravar sem confirmação.
- Não há telemetria ou data de conclusão que sustente utilização ou taxa de conclusão no prazo.
- O calendário tem lock compartilhado e cobertura concorrente entre agenda e indisponibilidade, mas não comprova timezone por empresa, múltiplos workers ou escrita direta no banco fora dos serviços da aplicação.
- Não foi homologado para produção, backup/restore, múltiplos workers ou infraestrutura pública.
- A revisão de dump histórico e eventual rotação de credenciais ficam documentadas; histórico remoto não será reescrito.

## Estado do gate

Auditoria e correções locais concluídas. Nenhum problema P0 confirmado. P1 de integração e homologação manual parcial permanecem abertos; ver `MVP_RELEASE_READINESS.md` para a decisão de release.
