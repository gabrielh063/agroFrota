# AGRO-UI-01 — Refinamento visual

## Objetivo e identidade

Refinar a experiência do AgroFrota mantendo o fundo verde escuro, a navegação lateral e o verde como cor de ação. O trabalho concentra-se em consistência entre módulos, legibilidade e adaptação a telas menores.

## Base visual

- Tokens de cor, texto, borda, tipografia, largura da navegação e raio de cards consolidados em `frontend/src/styles/global.css`.
- Regras de acabamento compartilhadas para cabeçalhos, formulários, tabelas, cards, calendário e login em `frontend/src/styles/product-polish.css`.
- Foco de teclado visível e suporte a `prefers-reduced-motion` incluídos nos estilos globais.
- Não foi adicionada dependência visual nem fonte externa.

## Telas refinadas

- Login: formulário com hierarquia, foco e espaçamento consistentes; mensagens de falha orientam a pessoa sem expor detalhes internos.
- Visão geral: cards, painéis, gráficos e listas de OS com espaçamento e contraste aprimorados. O botão de notificações sem ação foi removido.
- Navegação: sidebar reorganizada nas seções Operações, Gestão e Conta. Em telas estreitas, o menu abre e fecha por controle acessível.
- Central de Operações: identidade operacional, sugestões rápidas, apresentação de propostas e estados de carregamento e erro revisados. O histórico, a criação de conversa, a consulta, a confirmação e os links continuam usando os mesmos serviços e endpoints.
- Ordens de serviço, máquinas, equipamentos e calendário: alinhamento de cabeçalhos, ações, filtros, superfícies, tabelas e breakpoints.

## Linguagem da interface

A navegação agora apresenta **Central de Operações**. Foram removidas as referências visuais a robôs e à infraestrutura de processamento. Respostas automatizadas e nomes de referências também passam por normalização apenas na renderização. Mensagens técnicas completas permanecem disponíveis nos logs do navegador.

## Responsividade

O conteúdo usa uma navegação expansível até 900px; filtros e resumos se reorganizam em telas menores, tabelas mantêm rolagem contida e a grade do calendário reduz a densidade dos eventos no celular. Login foi capturado e inspecionado em 1600×900 e 375×812.

## Validação

- `npm run build`: passou.
- `npm run lint`: passou sem erros; o Oxlint reportou avisos que já existem em componentes do frontend (contexto de autenticação, formulários, páginas de OS, painel e Central de Operações).
- Auditoria textual do código da interface e do bundle: sem rótulos explícitos de IA, nomes de modelos/serviços internos ou ícones de robô em textos apresentados. Identificadores técnicos internos foram preservados.
- Evidências reais: `docs/evidence/agro-ui-01-login-1600x900.png` e `docs/evidence/agro-ui-01-login-375x812.png`.

## Limitações de homologação

A API e uma sessão autenticada não estavam disponíveis para esta execução. Por isso, não foi possível validar visualmente páginas protegidas com dados reais nem percorrer os fluxos de consulta, gravação, confirmação e logout no navegador. Nenhuma captura de telas protegidas foi simulada. Esses fluxos devem ser homologados com a API e uma conta de teste no notebook.
