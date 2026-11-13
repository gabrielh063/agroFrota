# Evidências de acessibilidade — AGRO-FINAL-03

Data: 12/11/2026. Candidata de entrada: `49c8fa6b416135ba5e09ec68fa84be0fc36c65a8`; navegador Chrome headless autenticado pelo inicializador, API/MariaDB em ambiente descartável, sem dados do operador. axe-core 4.14.0 foi servido temporariamente a partir de `/tmp`, sem dependência produtiva. Relatório bruto e medidas: [`axe-results.json`](axe-results.json). Capturas são PNGs `a11y-*` neste diretório.

## Automação e tamanhos

- 27 estados reais foram varridos com axe-core (regras WCAG 2/2.1/2.2 A/AA e best practices): Login, validação de login, dashboard, maquinários, equipamentos, filtros, OS, formulário/validação, detalhe/edição, calendário, diálogo, conflito e Central. Há estados desktop 1600×900 e mobile 375×812. Há **0 violações axe confirmadas** nestes estados.
- A regra automatizada de contraste não encontrou violações confirmadas; manteve nós incompletos para inspeção visual, portanto isto não substitui medição humana completa de todas as combinações de texto, fundos e estados.
- 89 controles de formulário tiveram borda/fundo amostrados: contraste mínimo da borda contra superfície adjacente **3,71:1**, e contra o preenchimento **3,55:1** (referência 3:1 para informação visual de componente). O estilo de foco observado é outline sólido de 2 px; sua cor teve 9,08:1 contra uma superfície escura adjacente medida. Não foi medido pixel a pixel em todas as telas.
- Login e formulário de OS foram varridos com mensagens de validação. O conflito do calendário foi varrido aberto e anunciado em `role=alert`. Central desktop/mobile foi varrida no estado inicial. O código expõe carregamento em `role=status`/`aria-live=polite`, mensagens em `role=alert` e conversa em `aria-live=polite`/`aria-busy`; os estados dinâmicos de loading e erro de rede da Central não foram reproduzidos nesta rodada porque a sessão autenticada expirou/foi perdida antes da interceptação. Portanto, teste dinâmico de announcement da Central continua pendente.

## Teclado e diálogo

O acionador “Agendar serviço” foi alcançado e ativado com Espaço. O foco entrou no diálogo nomeado “Agendar serviço”. Tab no último controle e Shift+Tab no primeiro circularam para o controle oposto; Escape fechou o diálogo e devolveu foco ao acionador. Os cinco campos do diálogo tinham labels associados, `required` aplicável e o diálogo tinha `aria-modal="true"`. O conflito ficou visível como “Conflito com outro agendamento.” em `role=alert`.

## Leitor de tela e limite da conclusão

Foi tentada uma sessão isolada com Xvfb e Orca/AT-SPI, sem tocar no display desktop do operador. O serviço AT-SPI iniciou e reconheceu uma aplicação Chrome, mas não havia janela ativa acessível, e não foi possível obter leitura/narração utilizável. Nenhum resultado de leitor de tela é alegado. Cobertura ainda necessária: testar com leitor de tela em sessão isolada funcional, confirmar nomes/descrições e anúncios dinâmicos da Central, e concluir revisão manual das combinações de contraste incompletas do axe.

## Correções desta rodada

- Rótulos acessíveis para landmarks e controles iconográficos; filtros e busca nomeados; cabeçalhos de ações nas tabelas.
- Linhas de OS agora oferecem link textual focável, e a região rolável da tabela é alcançável por teclado.
- IDs/labels associados aos campos de edição; seção de detalhe sem landmark `<main>` duplicado.
- Erros de formulário/conflito usam `role=alert`; carregamentos da Central expostos como status/live region.
- Borda de inputs/selects/textareas elevada para contraste de componente; foco visível reforçado.

**Classificação do gate: PARTIAL.** Não há violações automatizadas confirmadas nem problema crítico/grave restante identificado nos fluxos varridos; contudo, anúncio dinâmico da Central, leitura por tecnologia assistiva e a inspeção manual completa de contraste não foram concluídos. Isto não é certificação WCAG 2.2 AA.
