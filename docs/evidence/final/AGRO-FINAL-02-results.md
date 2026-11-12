# Evidências finais — AGRO-FINAL-02

Data: 12/11/2026. Repositório: `gabrielh063/agroFrota`, PR #9 (`release/agrofrota-mvp-final`). Head de entrada: `0c22328ceb7901047f39590d8cdaa7f079891170`. Os fluxos de navegador foram executados no Chrome contra uma instância MariaDB descartável iniciada pelo inicializador do projeto. Nenhum dado ou banco do operador foi usado. A instância descartável será removida após os testes.

## Gate A — Ordens de serviço: PASS

No navegador autenticado foi criada uma OS manualmente, editados título, descrição e prioridade e reaberta a tela para conferir os valores persistidos. Uma OS elegível foi concluída e outra foi cancelada. Consulta direta ao MariaDB confirmou os estados e a descrição/prioridade editadas. A trilha de auditoria contém eventos `OS.EDITAR`, `OS.CONCLUIR` e `OS.CANCELAR`.

O perfil `perfil_auditor` tentou criar uma OS e recebeu HTTP 403 com mensagem de permissão insuficiente; a tentativa não persistiu. Uma OS concluída não foi tratada como aberta nem editada.

Capturas: [criação](gate-os-created.png), [edição](gate-os-edited.png), [conclusão](gate-os-completed.png), [cancelamento](gate-os-cancelled.png). O teste negativo de permissão foi conferido pela resposta HTTP e consulta de persistência; não há captura de tela desse request.

## Gate B — Calendário: PASS

Foi criado um agendamento válido, alterados data e horário e conferida a persistência após reabrir. Outro agendamento foi cancelado e permaneceu com estado `CANCELADO` no banco. Uma tentativa de reserva conflitante exibiu erro na interface; a consulta direta confirmou que a operação conflitante não criou registro.

Capturas: [criado](gate-calendar-created.png), [data/horário alterados](gate-calendar-edited.png), [cancelado](gate-calendar-cancelled.png), [conflito](gate-calendar-conflict-accessible-desktop.png), [conflito em 375×812](gate-calendar-conflict-accessible-mobile.png). H1, H3, H5 e H9 foram observadas conforme `NIELSEN_USABILITY_AUDIT.md`.

## Gate C — Rede e idempotência: PASS

Com interceptação controlada no Chrome/CDP:

1. A conectividade foi desligada antes do envio. A interface exibiu recuperação; depois de restaurada a rede, a operação pôde ser proposta.
2. A resposta de confirmação HTTP 200 foi retida depois do commit. A interface indicou resultado incerto, sem anunciar sucesso; a consulta ao MariaDB mostrou que o agendamento havia sido gravado. Atualizar a página recuperou o resultado.
3. Repetir a mesma confirmação duas vezes retornou o mesmo ID, com `idempotente=true`.
4. Clique duplo na confirmação produziu um único agendamento para aquele horário.
5. Um timeout real do cliente Axios de 30 segundos foi induzido após o commit. A repetição retornou o ID existente, sem inserir outra linha.

Consultas diretas ao MariaDB confirmaram um único registro para cada operação testada e o mesmo ID nas repetições. Sessão recuperada após reload; tokens e senhas não foram registrados nem exibidos. Captura de estado incerto: [confirmação pendente](gate-confirmation-pending.png).

## Gate D — Acessibilidade: PARTIAL

As páginas essenciais foram inspecionadas em 375×812 e 1600×900; as capturas adicionais estão no diretório. No calendário, o diálogo anuncia o nome “Agendar serviço” na árvore AX do Chrome, os campos têm labels associados, o foco entra no modal, Tab/Shift+Tab circulam, Escape fecha e restaura o foco e o erro de conflito usa `role=alert`. A Central foi capturada em mobile.

Uma amostra de 52 textos visíveis da Central, com composição de transparências, teve contraste mínimo 4,68:1 e nenhum item amostrado abaixo de 4,5:1. A medição não percorre todas as páginas, estados ou tipos de texto. axe-core não está instalado. Orca está instalado, mas não foi iniciado porque não havia sessão ativa e assumir a sessão gráfica poderia interferir com o operador. O leitor de tela não foi validado; não se declara conformidade WCAG 2.2 AA.

## Gate E — Segurança histórica: PARTIAL, bloqueio para READY

O arquivo `backend/backups/tenants_antes_migration.sql` foi removido da árvore atual em commit histórico, mas permanece alcançável no histórico Git da PR. O repositório GitHub é público. A inspeção processou o conteúdo localmente sem imprimir ou copiar valores: 6 valores com formato de email, 7 hashes no formato scrypt, 7 hashes distintos e nenhum domínio de exemplo/teste/invalid entre os emails. Não há evidência suficiente para provar que os dados são sintéticos; portanto, foram classificados como potencialmente reais.

Hashes distintos não provam ausência de reutilização de senha, pois hashes salgados podem diferir para a mesma senha. Não é possível descobrir reutilização ou se as contas ainda estão ativas a partir desses hashes. Uma varredura local de 831 blobs alcançáveis não encontrou padrões de chaves privadas PEM, tokens AWS/GitHub/Slack ou JWT, nem caminhos rastreados com nomes de segredo. A API de alertas de secret scanning do GitHub retornou zero alertas. Essas verificações não excluem todo segredo ou credencial em texto livre.

Decisão necessária do responsável pelo repositório: identificar os titulares/contas afetados, invalidar ou redefinir senhas ainda válidas, apurar reutilização com os titulares por canal seguro e rotacionar outros segredos caso sejam identificados. Nenhuma rotação ou reescrita de histórico remoto foi executada. O gate segue aberto até a decisão e mitigação do responsável; não reproduzir os valores no PR ou nos logs.

## Gate F — CI e release: PASS

No head `5c042c25547f2c221fd6accb435d4051e105f174`, os jobs remotos `backend-mariadb` e `frontend` passaram na execução [43243144116](https://github.com/gabrielh063/agroFrota/actions/runs/43243144116). Localmente, `python backend/tools/ci.py` aprovou 249 testes (74 avisos de depreciação); `npm run build` passou e `npm run lint` terminou com exit 0 e avisos de lint/deprecation.

Nenhum merge ou deploy foi feito.

## Inventário de capturas desta etapa

- OS: `gate-os-created.png`, `gate-os-edited.png`, `gate-os-completed.png`, `gate-os-cancelled.png`.
- Calendário: `gate-calendar-created.png`, `gate-calendar-edited.png`, `gate-calendar-cancelled.png`, `gate-calendar-conflict.png`, `gate-calendar-conflict-accessible-desktop.png`, `gate-calendar-conflict-accessible-mobile.png`, `gate-calendar-mobile.png`, `gate-calendar-desktop.png`.
- Rede e navegação: `gate-confirmation-pending.png`, `gate-login-desktop.png`, `gate-operations-mobile.png`.
