# Prontidão da release candidate do AgroFrota

Data de registro: 12/11/2026. Classificação após AGRO-FINAL-03: **`AGRO_MVP_FINAL_PARTIAL`**. OS, calendário e rede/idempotência passaram em navegador contra MariaDB descartável; backend (249), build/lint locais e CI remota passaram. Permanecem bloqueios concretos: segurança de hashes no histórico público sem decisão/mitigação do responsável e acessibilidade PARTIAL: axe-core reportou zero violações confirmadas em 27 estados, mas leitor de tela, anúncios dinâmicos da Central e contraste manual completo seguem pendentes. Não foi feito merge nem deploy.

## Branch e histórico

- Branch local/remota: `release/agrofrota-mvp-final`; HEAD publicado após AGRO-FINAL-03: `2d3c2896d4290eaebca6854134001ceab680d012`.
- `Main` é a branch padrão confirmada via GitHub. Head #5: `7759213e31666868946ba305b86841274b6a0897`.
- A cadeia consultada no remoto via `gh`: #5 (base Main), #6 (base #5), #7 (base #6), #8 (base #7). PRs #1–#8 permanecem abertas; a PR final #9 foi aberta para `Main`.
- Commit da candidata funcional: `1e8bd157a4d808b2e7f8fe01c923760422c4fee1` (`Finalize AgroFrota MVP candidate`). A atualização deste relatório será o head mais recente publicado na PR.
- PR final: [#9](https://github.com/gabrielh063/agroFrota/pull/9), `release/agrofrota-mvp-final` → `Main`.
- Checks remotos em `5c042c25547f2c221fd6accb435d4051e105f174`: `backend-mariadb` e `frontend` passaram na execução [43243144116](https://github.com/gabrielh063/agroFrota/actions/runs/43243144116). O PR #9 continua aberto; não integrado em `Main`; nenhum merge foi feito.

## Verificações executadas

| Verificação | Resultado | Evidência |
|---|---|---|
| Backend/MariaDB | **249 aprovados**, 74 avisos deprecation `datetime.utcnow`; migrações central e tenant até `7b53d2a1c804`; ambiente descartável encerrado/removido | Saída local de `python backend/tools/ci.py` em 12/11/2026 |
| Frontend build | **Aprovado** com Vite 8.3.1 | `cd frontend && npm run build` |
| Frontend lint | **Exit 0**, sem erros; avisos de hooks/efeitos, dependências e Fast Refresh persistem em código existente | `cd frontend && npm run lint` |
| Inicializador | **Passou** após smoke checks de migrations, API health, preflight OPTIONS/CORS, login, `/api/auth/me`, `/api/dashboard/capacidade` e `/api/assistente/conversas`; a sessão foi encerrada pelo próprio launcher e o diretório temporário foi removido | `python iniciar_agrofrota.py --modelo llama3.2:3b`; sessão isolada removida após homologação |
| Navegador autenticado | **Passou**: OS manual criada, editada, reaberta, concluída e cancelada; calendário criado, editado, cancelado e conflito recusado; perfil AUDITOR teve escrita OS negada com 403. | `docs/evidence/final/gate-*`; resultados diretos em `docs/evidence/final/AGRO-FINAL-02-results.md` |
| Matriz de largura | **Passou sem overflow horizontal** em 375×812, 768×1024, 1280×800 e 1600×900 em Login, Dashboard, Central, Maquinários, Equipamentos, OS, detalhe e Calendário | Chrome/CDP local |
| Persistência Central | **Passou**: OS #7, agenda #2, DEMO-TR-02, 13/11/2026 08:00–12:00; proposta consumida e ligada aos dois IDs de resultado | Consulta somente leitura ao MariaDB temporário |
| Ollama real | **Disponível**; servidor local tinha `llama3.2:3b`, `llama3.1:8b`, `qwen3:1.7b` entre modelos listados. Não foi feita inferência de conhecimento nesta homologação; fluxo operacional é determinístico | `GET /api/tags` em loopback |
| Rede/idempotência | **Passou**: offline antes do envio recuperou a proposta; resposta POST 200 foi retida após o commit; timeout real de 30 s; reload/replay e clique duplo sem duplicar IDs. | `docs/evidence/final/AGRO-FINAL-02-results.md`, screenshots `gate-confirmation-*`; MariaDB descartável |
| Frontend build/lint | **Passou**: build concluído; lint exit 0, avisos preexistentes de hooks/efeitos ainda presentes. | Execução local após correções |
| Checks remotos | **Passou** no head `5c042c2`: `backend-mariadb` e `frontend` verdes. | PR #9 / [GitHub Actions](https://github.com/gabrielh063/agroFrota/actions/runs/43243144116) |
| Segurança histórica | **Bloqueio**: 6 endereços e 7 hashes scrypt estão no dump removido da árvore atual, alcançável no histórico local do repositório público. Nenhum padrão de chave privada/token conhecido ou alerta GitHub foi encontrado; sinteticidade e uso das contas não podem ser comprovados. | `docs/evidence/final/AGRO-FINAL-02-results.md`; conteúdo não reproduzido |

## Fluxos homologados

- **A — Login/Dashboard:** login demonstrativo real; KPIs e listas carregaram dados do tenant isolado; sidebar navegou entre telas.
- **B — Gestão de ativos:** no Chrome autenticado foram criadas e editadas uma máquina e um equipamento fictícios; listas e controles de busca/filtro renderizaram. Não foi verificado um cenário de filtro que prove o subconjunto retornado.
- **C — OS:** criação manual; título, descrição e prioridade alterados; reabertura confirmou persistência. Uma OS elegível foi concluída; outra foi cancelada. O perfil AUDITOR recebeu 403 ao tentar criar. MariaDB confirma os estados e eventos `OS.EDITAR`, `OS.CONCLUIR` e `OS.CANCELAR`.
- **D — Agenda:** agendamento criado e movido de data/hora; persistência conferida; cancelamento deixou `CANCELADO`. Sobreposição foi recusada com mensagem visível e contagem de registros inalterada. H1/H3/H5/H9 foram observadas no fluxo.
- **E — Central:** conversa em duas mensagens, contexto mantido, ativo disponível identificado, proposta revisável, confirmação e links de resultado. Dados conferidos diretamente no MariaDB temporário.
- **F — Rede/repetição:** offline antes do envio exibiu recuperação; resposta POST 200 foi interceptada após commit; a UI informou resultado incerto, o reload recuperou o registro e duas repetições retornaram o mesmo ID com `idempotente=true`. O timeout Axios de 30 s também foi aguardado após commit; retry não duplicou. Dois cliques na confirmação geraram um agendamento.
- **G — Logout:** logout real realizado no browser e rota protegida redirecionou para login.

## Nielsen, visual e acessibilidade

As dez heurísticas estão avaliadas em [`NIELSEN_USABILITY_AUDIT.md`](NIELSEN_USABILITY_AUDIT.md), com observações, severidade, correções, resultados e evidências. As capturas incluem Login, Dashboard, Central inicial/proposta/confirmada, Maquinários, Equipamentos, Ordens de serviço, detalhe e Calendário em desktop; Login, Central inicial e Maquinários em 375×812. O material antes/depois do UI-02 está em `docs/evidence/agro-ui-02/`.

Capturas e inventário foram feitos em 375×812 e 1600×900; a largura também foi previamente verificada em 768×1024 e 1280×800. Os modais agora têm rótulos associados, nome de diálogo, foco inicial, ciclo Tab/Shift+Tab, Escape, restauração do foco e alertas semânticos. Chrome AX tree confirmou diálogo nomeado; amostra de contraste alfa composta mediu mínimo 4,68:1 na Central. Axe-core 4.14.0 temporário varreu 27 estados sem violações confirmadas. 89 contornos de controles medidos ficaram em pelo menos 3,55:1; casos de contraste incompletos pela ferramenta ainda requerem revisão manual. Orca foi tentado em Xvfb isolado, mas não apresentou janela Chrome acessível; Central dinâmica e leitor de tela permanecem não verificados. Não declarar conformidade WCAG.

## Problemas corrigidos nesta rodada

- Corrigido o gráfico de atividade mensal para não desenhar barras mínimas quando o valor real é zero.
- A falha de confirmação da Central agora recomenda verificar OS e Calendário antes de repetir e explica o comportamento idempotente, sem declarar rollback não verificado.
- Inicializador moveu o ambiente Python para a pasta temporária privada da sessão e valida preflight/CORS e rotas autenticadas essenciais.
- Implementado e capturado o redesign local da UI-02 para Dashboard, Central e Maquinários.
- Agenda e indisponibilidade agora compartilham o lock operacional; mudanças de estado/troca de ativo e encerramento de OS bloqueiam quando há compromisso pendente.
- Labels do formulário de equipamento estão associados aos campos; menu de ações dos equipamentos anuncia nome, expansão e itens para tecnologias assistivas.
- Labels dos campos dos modais do calendário agora estão ligados aos controles; diálogo modal, foco/teclado e erro de conflito são expostos semanticamente.

## Pendências para classificação READY

1. O responsável deve classificar os dados do dump público, identificar contas potencialmente reais e forçar redefinição/rotação quando aplicável; avaliar reutilização com os titulares sem usar os hashes como prova de inexistência de reutilização. Não reescrever histórico remoto automaticamente.
2. Concluir manualmente os casos de contraste marcados incompletos pelo axe; validar carregamento/erro dinâmicos da Central e repetir teste com leitor de tela em sessão isolada funcional.
3. Publicar esta atualização e aguardar CI remota verde no novo head da PR #9.

## Estado do gate e classificação

Classificação: **`AGRO_MVP_FINAL_PARTIAL`**. A acessibilidade está PARTIAL conforme evidência AGRO-FINAL-03. A segurança histórica permanece bloqueada porque há hashes de senha potencialmente reais em histórico de repositório público sem classificação/mitigação do responsável. A PR #9 não deve ser aprovada para merge até a decisão/mitigação histórica e a cobertura residual de acessibilidade. Ver atualização AGRO-FINAL-03 abaixo.

## Inicialização e encerramento

Na raiz do repositório, rode `python iniciar_agrofrota.py`. As credenciais aleatórias são exibidas apenas no terminal local. Para finalizar, faça logout e pressione `Ctrl+C` no terminal do inicializador. O script remove apenas a pasta temporária própria depois de encerrar os processos filhos. Não use o seed separado contra bancos fora do ambiente descartável validado.

## Limitações acadêmicas

Assistente usa parser determinístico nas operações e Ollama local para orientação documental; não é um planejador autônomo. Não existe métrica real de uso/conclusão no prazo. Não há homologação de produção, restore, múltiplos workers nem segurança operacional de infraestrutura pública. O calendário usa lock transacional compartilhado e tem testes concorrentes, mas não oferece timezone por empresa nem versão otimista de edição.

## Complemento AGRO-FINAL-05 — perfis de demonstração

O gate de apresentação de perfis foi concluído no incremento desta branch. Consulte [`DEMO_PERFIS.md`](DEMO_PERFIS.md) para a matriz observável, os fluxos por perfil e o índice de evidências.

- `iniciar_agrofrota.py` provisiona sete contas no tenant MariaDB temporário próprio do inicializador. Senhas únicas aleatórias são impressas no terminal privado; o payload de credenciais é passado somente ao subprocesso de seed, e o estado temporário fica em arquivo `0600` até o encerramento. Nenhuma senha foi incluída no repositório ou nas capturas.
- A tela **Equipe e Permissões** permite consulta de usuários/perfis/permissões efetivas e criação/edição condicionada à matriz. A UI consulta `/api/auth/me`, filtra menus e ações e informa recusa em rota direta; a API mantém a autorização final.
- Homologação Chrome: 7/7 logins; diferenças de navegação/ações comprovadas para Gerente, Gestor, Operador, Manutenção e Auditor; Auditor não acessa por URL direta a criação de OS. Gerente criou e editou uma conta fictícia pela UI com readback.
- Regressão backend: `python backend/tools/ci.py` — **250 aprovados**, 74 avisos de depreciação. O teste `backend/tests/test_demo_perfis.py` inclui matriz de HTTP permitidos/negados, escopo próprio/atribuído, edição administrativa, evento de auditoria, revogação de sessão após troca de perfil e novo login com perfil atualizado. Isolamento entre tenants é coberto também por `backend/tests/test_multitenant.py`.
- Evidências: `docs/evidence/final/profiles-demo/` (`api-results.json`, `browser-profiles.json`, `manager-create-edit.json` e screenshots reais). Build e lint passaram localmente; lint mantém avisos de hooks existentes e um aviso da nova tela sobre carregamento por efeito. O primeiro push não gerou check do GitHub; o workflow existente ganhou somente o gatilho `workflow_dispatch`, sem alterar jobs. O run [43265695141](https://github.com/gabrielh063/agroFrota/actions/runs/43265695141) passou nos dois jobs em `ae9fd578`; depois, [43266103005](https://github.com/gabrielh063/agroFrota/actions/runs/43266103005) também passou `backend-mariadb` e `frontend` no HEAD `ab6fe651`. O follow-up documental final será verificado pelos checks da PR #9.
- Este incremento não modifica a decisão/documentação de segurança histórica nem fecha a acessibilidade pendente. A classificação geral permanece **`AGRO_MVP_FINAL_PARTIAL`**; nenhuma certificação WCAG 2.2 AA é declarada e não há merge.


## Atualização AGRO-FINAL-03 — 12/11/2026

- **Acessibilidade: PARTIAL.** axe-core 4.14.0, servido temporariamente sem alterar dependências do produto, varreu 27 estados reais em Login e páginas autenticadas, desktop 1600×900/mobile 375×812; não encontrou violações confirmadas. Houve 89 medições de bordas de controles, mínimo 3,71:1 contra superfície adjacente e 3,55:1 contra preenchimento. Foco observável: outline sólido 2 px; 9,08:1 contra a superfície escura amostrada. O axe marcou nós de contraste incompletos, que requerem inspeção manual.
- Teclado no diálogo de calendário: Espaço aciona; foco entra e cicla com Tab/Shift+Tab; Escape fecha e foco retorna ao acionador. Erro de conflito está em `role=alert`; formulário de OS/login foi coberto em estados de validação.
- Cobertura ainda pendente: estado dinâmico de carregamento/erro da Central por falha de autenticação na automação de interceptação; leitor de tela — Orca com Xvfb inicializou AT-SPI/Chrome, mas nenhuma janela acessível ativa ficou disponível. A sessão desktop do operador não foi tocada. Sem declaração de conformidade/certificação WCAG 2.2 AA.
- Regressão local após correções: `python backend/tools/ci.py` 249 passed (74 avisos de depreciação); `npm run build` aprovado; `npm run lint` exit 0 com avisos existentes.
- A PR #9 segue aberta no head `2d3c2896d4290eaebca6854134001ceab680d012`; `backend-mariadb` e `frontend` passaram no run [43252716698](https://github.com/gabrielh063/agroFrota/actions/runs/43252716698).
- O gate de segurança histórica continua independente e bloqueante para classificar o MVP como READY; os dados não foram reproduzidos nem o histórico remoto reescrito.
- Relatório reproduzível e capturas: [`evidence/final/accessibility/AGRO-FINAL-03-results.md`](evidence/final/accessibility/AGRO-FINAL-03-results.md), screenshots `a11y-*` e [`axe-results.json`](evidence/final/accessibility/axe-results.json).
