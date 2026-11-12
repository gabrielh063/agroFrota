# Auditoria heurística de usabilidade

Data: 12/11/2026. Método: inspeção heurística de telas e fluxos, com screenshots reais no Chrome autenticado e dados fictícios. Referência: [Jakob Nielsen, 10 Usability Heuristics for User Interface Design](https://www.nngroup.com/articles/ten-usability-heuristics/) (NN/g; revisão indicada na página: 30/01/2024). As heurísticas são regras gerais de inspeção; esta avaliação não substitui pesquisa ou teste moderado com usuários.

## Escala de severidade

0 — não é um problema; 1 — cosmético; 2 — menor; 3 — grave; 4 — crítico. A coluna “severidade observada” registra o problema antes da correção quando aplicável. Nenhum problema de severidade 3 ou 4 foi observado nos fluxos exercitados ao final desta inspeção. Isso não declara conformidade WCAG: contraste numérico e leitores de tela ainda não foram medidos.

## Capturas examinadas

Todas foram obtidas de páginas reais, em Chrome headless, autenticado e contra MariaDB temporário com dados demonstrativos. Há versões mobile de Login, Central e Maquinários.

| Tela | Desktop | Mobile |
|---|---|---|
| Login | [login-desktop](evidence/final/login-desktop.png) | [login-mobile](evidence/final/login-mobile.png) |
| Dashboard | [dashboard-desktop](evidence/final/dashboard-desktop.png) | — |
| Central inicial | [operations-desktop](evidence/final/operations-desktop.png) | [operations-mobile](evidence/final/operations-mobile.png) |
| Central proposta | [operations-proposal-desktop](evidence/final/operations-proposal-desktop.png) | — |
| Central confirmada | [operations-confirmation-desktop](evidence/final/operations-confirmation-desktop.png) | — |
| Maquinários | [machines-desktop](evidence/final/machines-desktop.png) | [machines-mobile](evidence/final/machines-mobile.png) |
| Equipamentos | [equipment-desktop](evidence/final/equipment-desktop.png) | — |
| Ordens de serviço | [work-orders-desktop](evidence/final/work-orders-desktop.png) | — |
| Detalhes da OS | [work-order-detail-desktop](evidence/final/work-order-detail-desktop.png) | — |
| Calendário | [calendar-desktop](evidence/final/calendar-desktop.png) | — |

As imagens de referência anteriores e posteriores do redesign estão em [`evidence/agro-ui-02/`](evidence/agro-ui-02/). Dados de todas as capturas são fictícios. Nenhuma senha aparece nas capturas.

## Matriz de avaliação

### H1 — Visibilidade do estado do sistema

- **Telas avaliadas:** Dashboard, Maquinários, Central, OS e Calendário.
- **Problema observado / reprodução:** Na primeira inspeção do gráfico do Dashboard, meses com zero OS ainda mostravam uma barra mínima de 3%, podendo ser lida como atividade. Severidade observada: **2**.
- **Correção implementada:** Barras e rótulos só são renderizados quando a contagem mensal é maior que zero. Cards aguardam o carregamento antes de expor os totais; Central mostra carregamento, proposta não gravada, confirmação e resultado persistido.
- **Resultado:** A captura final apresenta somente novembro com valor 7; os demais meses permanecem sem barra. A proposta mostra explicitamente “Não gravada” e o resultado exibe “OS #7 criada. Agendamento #2 confirmado.”
- **Teste de regressão:** Inspeção visual real antes/depois; `npm run build` aprovado. Testes backend de proposta/confirmação/idempotência incluídos na suíte (249 aprovados). Capturas citadas acima.

### H2 — Correspondência entre sistema e mundo real

- **Telas avaliadas:** Login, navegação, Dashboard, formulários e Central.
- **Problema observado / reprodução:** A UI anterior usava “Painel de controle” e uma conversa inicial genérica, sem orientar uma tarefa. Severidade observada: **2**.
- **Correção implementada:** Terminologia de operação agrícola (“Maquinários”, “Ordem de serviço”, “Disponibilidade”, “Agendamento”), resumo da frota e ações com descrições em linguagem direta. A Central abre com “O que você precisa fazer hoje?”.
- **Resultado:** As telas e a conversa capturada usam termos operacionais; nomes técnicos não aparecem nos controles comuns. Referências documentais são preservadas como fonte, sem reescrita para disfarçar sua origem.
- **Teste de regressão:** Navegação e conversa real percorridas em Chrome autenticado; screenshots Login, Dashboard e Central.

### H3 — Controle e liberdade do usuário

- **Telas avaliadas:** Central, formulário de OS, detalhes da OS, Calendário e navegação móvel.
- **Problema observado / reprodução:** Na Central anterior não havia entrada orientada a tarefa nem proposta estruturada clara para revisar antes da gravação. Severidade observada: **2**.
- **Correção implementada:** Cards abrem tarefas sem retirar a entrada livre; proposta oferece **Confirmar operação** e **Cancelar**; existe **Nova conversa**; formulário mantém botões de retorno/cancelamento e detalhes oferecem as transições permitidas. A sidebar móvel pode ser aberta e fechada.
- **Resultado:** A operação testada permaneceu sem gravação até confirmação e depois apresentou link para abrir a OS. Uma OS elegível foi concluída e outra foi cancelada; um agendamento também foi cancelado pelo calendário.
- **Teste de regressão:** Chrome autenticado e MariaDB descartável confirmaram as transições e os respectivos estados persistidos. Havia controles visíveis para retornar/cancelar antes de confirmar.

### H4 — Consistência e padrões

- **Telas avaliadas:** Dashboard, Central, Maquinários, Equipamentos, OS, detalhe e Calendário.
- **Problema observado / reprodução:** No baseline da #8, o Dashboard e a Central tinham cabeçalhos, proporções e densidade incompatíveis com as demais telas. Severidade observada: **2**.
- **Correção implementada:** Tokens e estilos compartilhados em `global.css` e `product-polish.css`; títulos, filtros, badges, superfícies, ações e breakpoints alinhados. Elementos de navegação sem ação estão desabilitados e marcados “Em breve”.
- **Resultado:** Capturas de todas as páginas mostram identidade verde-escura e hierarquia visual consistente.
- **Teste de regressão:** `npm run build` e lint aprovados sem erros bloqueantes; inspeção comparativa das capturas desktop e mobile.

### H5 — Prevenção de erros

- **Telas avaliadas:** Formulário de máquina, OS, agenda e proposta da Central.
- **Problema observado / reprodução:** Uma disponibilidade consultada pode ficar desatualizada antes da confirmação; conflito concorrente precisa ser revalidado no servidor. Severidade observada: **3** no fluxo de reserva caso a revalidação não exista.
- **Correção implementada:** Propostas são temporárias e revalidam permissão e disponibilidade dentro da transação; agenda e indisponibilidade compartilham lock operacional; a criação/edição de indisponibilidade verifica reservas existentes; status não operacional, desativação, troca ou encerramento de OS não invalidam agenda pendente silenciosamente. Formulários desabilitam submissão enquanto processam.
- **Resultado:** A Central selecionou o DEMO-TR-02 e confirmou apenas após mostrar recurso, OS, horário e estado inicial. Calendário rejeitou reserva conflitante e não criou linha adicional.
- **Teste de regressão:** `python backend/tools/ci.py` — 249 aprovados em MariaDB descartável, incluindo conflito/rollback/idempotência, corrida agenda × indisponibilidade e bloqueio de máquina não operacional ou com agenda pendente. No Chrome autenticado foi criado, editado e cancelado agendamento; a tentativa sobreposta mostrou erro visível e a contagem no MariaDB permaneceu igual.

### H6 — Reconhecimento em vez de memorização

- **Telas avaliadas:** Seletor de recurso da Central, Maquinários, Dashboard, OS e detalhe.
- **Problema observado / reprodução:** Não foi identificado requisito para decorar IDs; selecionar um ativo só pelo número técnico seria inadequado. Severidade observada: **0** nas telas verificadas.
- **Correção implementada:** Seleção e proposta exibem identificação do ativo; lista de máquinas apresenta fabricante/modelo e categoria; detalhes mostram o ativo relacionado. Breadcrumb/retorno para lista é exibido no detalhe de OS.
- **Resultado:** A OS criada na Central mostra “DEMO-TR-02” antes de confirmar; no detalhe, fabricante, modelo e localização estão visíveis.
- **Teste de regressão:** Fluxo real de proposta e detalhe no Chrome; suíte backend valida que IDs/opções correspondem aos recursos persistidos.

### H7 — Flexibilidade e eficiência de uso

- **Telas avaliadas:** Dashboard, filtros de Maquinários/OS, Central e Calendário.
- **Problema observado / reprodução:** A Central anterior reservava uma coluna de ajuda estática e grande área de conversa vazia, sem fluxo inicial por tarefa. Severidade observada: **2**.
- **Correção implementada:** Quatro cards de ação rápida, entrada livre na tela inicial e ações contextuais; Dashboard traz atalho de criação de OS; filtros e busca permanecem disponíveis nas listas.
- **Resultado:** A tarefa de agendar foi concluída com duas mensagens e confirmação, sem navegar entre telas para escolher recurso. OS e agenda persistiram em uma confirmação.
- **Teste de regressão:** Chrome autenticado registrou conversa de contexto, proposta, confirmação e links; criação manual de ativos/OS e agenda foi concluída com menos navegação. Backend cobre repetição/idempotência. Não houve teste com usuário representativo.

### H8 — Estética e design minimalista

- **Telas avaliadas:** Dashboard, Central, Maquinários, equipamentos, OS, detalhe e calendário.
- **Problema observado / reprodução:** Dashboard sem hierarquia forte, Central com espaço vazio excessivo e tabela pequena eram visíveis nas capturas do baseline. Severidade observada: **2**.
- **Correção implementada:** Dashboard reorganizado com hero, KPIs mais proeminentes, atividade, status e listas; Central usa workspace de tarefas e conversa; Maquinários usa resumo e cards compactos em telas estreitas. O gráfico não desenha valores zero.
- **Resultado:** As capturas antes/depois mostram diferenças concretas; em 375×812 os filtros e cartões ficam dentro do fluxo móvel e o menu usa controle explícito.
- **Teste de regressão:** Screenshots reais e build. Chrome mediu `document.scrollWidth == viewport width` em 375×812, 768×1024, 1280×800 e 1600×900 nas oito telas essenciais. Inspeção visual de composição foi feita em mobile e desktop; teclado do modal de calendário foi exercitado. Leitor de tela e matriz integral de contraste permanecem pendentes.

### H9 — Reconhecer, diagnosticar e recuperar erros

- **Telas avaliadas:** Login, formulário e Central.
- **Problema observado / reprodução:** A mensagem de confirmação anterior dizia apenas para conferir os dados e tentar de novo, sem orientar o usuário a verificar possível persistência após falha de resposta. Severidade observada: **2**.
- **Correção implementada:** Mensagem de falha de confirmação agora orienta conferir Ordens de serviço e Calendário antes de tentar de novo e explica que repetição da confirmação retorna o mesmo resultado se já persistiu. Outras mensagens do login e da Central dão ação de recuperação.
- **Resultado:** A interface não afirma rollback quando não sabe o resultado da rede. Offline antes do envio mostrou orientação de recuperação; resposta perdida após commit e timeout mostraram resultado incerto, sem informar sucesso prematuro.
- **Teste de regressão:** No Chrome, a confirmação repetida retornou o mesmo ID após resposta perdida, timeout e reload; clique duplo persistiu uma linha. Conflito de agenda exibiu mensagem para o usuário, e a UI usou `role=alert` no modal de conflito.

### H10 — Ajuda e documentação

- **Telas avaliadas:** Formulários, telas vazias, proposta da Central e sidebar.
- **Problema observado / reprodução:** Não havia guia final curto para um apresentador acadêmico e o significado de uma proposta ainda não gravada precisava ser explícito. Severidade observada: **2**.
- **Correção implementada:** Criado `GUIA_USUARIO_AGROFROTA.md`; proposta explica o que será gravado e que permissões/disponibilidade serão verificadas novamente. Telas vazias e campos mantêm instruções; módulos fora do MVP são marcados “Em breve”.
- **Resultado:** Guia descreve o percurso de login, ativos, OS, agenda, Central e encerramento; não apresenta módulos não existentes como utilizáveis.
- **Teste de regressão:** Revisão do guia contra rotas presentes no `App.jsx` e inspeção real da Central e sidebar.

## Fechamento AGRO-FINAL-02 — 12/11/2026

- **H1/H9:** offline antes do envio exibiu recuperação; resposta HTTP 200 interceptada depois do commit e timeout de 30 s deixaram o resultado incerto na interface. Atualizar a página recuperou o estado; reenviar a mesma confirmação retornou o mesmo agendamento sem duplicação. Ver `evidence/final/gate-confirmation-pending.png` e `evidence/final/AGRO-FINAL-02-results.md`.
- **H3:** cancelamento de OS e de agendamento realizado pelo navegador; após cancelar, o banco exibiu estado `CANCELADO`. O erro de conflito foi apresentado em `role=alert`.
- **H5:** reserva conflitante foi rejeitada com mensagem de indisponibilidade; a contagem de agendamentos persistidos não mudou.
- **Modal/teclado:** diálogo “Agendar serviço” aparece nomeado na árvore de acessibilidade do Chrome. Foco inicia dentro do modal; Tab e Shift+Tab circulam; Escape fecha e devolve foco ao acionador. Os labels estão associados aos campos. A captura do erro acessível está em `evidence/final/gate-calendar-conflict-accessible-desktop.png` e sua versão mobile em `evidence/final/gate-calendar-conflict-accessible-mobile.png`.
- **Contraste:** amostra composta de 52 textos visíveis na Central, incluindo transparências, teve mínimo medido de 4,68:1 e nenhum resultado amostrado abaixo de 4,5:1. Isso não cobre toda a aplicação, todos os estados, texto grande, foco ou conteúdo dinâmico.
- **Automação/leitor de tela:** axe-core não está instalado. Orca está disponível no sistema, mas não havia sessão ativa; não foi iniciada para evitar assumir ou alterar a sessão gráfica do operador. A árvore AX do Chrome foi inspecionada. Não houve validação por leitor de tela e não se declara conformidade WCAG 2.2 AA.
- **Limite de pesquisa:** não houve teste moderado com pessoa usuária representativa.
