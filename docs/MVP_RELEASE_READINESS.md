# Prontidão da release candidate do AgroFrota

Data de registro: 12/11/2026. Classificação após AGRO-FINAL-02: **`AGRO_MVP_FINAL_PARTIAL`**. OS, calendário e rede/idempotência passaram em navegador contra MariaDB descartável; backend (249), build e lint locais passaram. Permanecem bloqueios concretos: segurança de hashes no histórico público e decisão/mitigação do responsável; acessibilidade ainda não cobre axe-core/leitor de tela nem a matriz de contraste integral; CI remota do novo head precisa ser observada após o push. Não foi feito merge nem deploy.

## Branch e histórico

- Branch local: `release/agrofrota-mvp-final`; head inicial desta missão `0c22328ceb7901047f39590d8cdaa7f079891170`. Correções acessíveis de calendário e atualização documental compõem o commit final desta etapa.
- `Main` é a branch padrão confirmada via GitHub. Head #5: `7759213e31666868946ba305b86841274b6a0897`.
- A cadeia consultada no remoto via `gh`: #5 (base Main), #6 (base #5), #7 (base #6), #8 (base #7). PRs #1–#8 permanecem abertas; a PR final #9 foi aberta para `Main`.
- Commit da candidata funcional: `1e8bd157a4d808b2e7f8fe01c923760422c4fee1` (`Finalize AgroFrota MVP candidate`). A atualização deste relatório será o head mais recente publicado na PR.
- PR final: [#9](https://github.com/gabrielh063/agroFrota/pull/9), `release/agrofrota-mvp-final` → `Main`.
- Checks remotos em `0c22328ceb7901047f39590d8cdaa7f079891170`: `backend-mariadb` e `frontend` passaram. A atualização desta etapa requer nova execução remota. O PR #9 continua aberto; não integrado em `Main`; nenhum merge foi feito.

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
| Checks remotos | `backend-mariadb` e `frontend` passaram no head `0c22328`; **novo head requer CI remota após push**. | PR #9 / GitHub Actions |
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

Capturas e inventário foram feitos em 375×812 e 1600×900; a largura também foi previamente verificada em 768×1024 e 1280×800. Os modais agora têm rótulos associados, nome de diálogo, foco inicial, ciclo Tab/Shift+Tab, Escape, restauração do foco e alertas semânticos. Chrome AX tree confirmou diálogo nomeado; amostra de contraste alfa composta mediu mínimo 4,68:1 na Central. Axe-core não está instalado; Orca está instalado, mas não foi iniciado porque não havia processo ativo e isso assumiria a sessão gráfica do operador. A medição de contraste não cobriu todas as páginas/estados. Não declarar conformidade WCAG.

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
2. Completar auditoria instrumental de contraste em todas as páginas/estados, executar axe-core quando disponível e testar leitor de tela em ambiente isolado.
3. Publicar esta atualização e aguardar CI remota verde no novo head da PR #9.

## Estado do gate e classificação

Classificação: **`AGRO_MVP_FINAL_PARTIAL`**. OS, calendário, rede/idempotência, suíte backend, build e lint locais passaram. A acessibilidade geral e a CI remota do novo head ainda são parciais. A segurança histórica está bloqueada porque há hashes de senha potencialmente reais em histórico de repositório público sem classificação/mitigação do responsável. Não aprovar merge até esses bloqueios serem resolvidos.

## Inicialização e encerramento

Na raiz do repositório, rode `python iniciar_agrofrota.py`. As credenciais aleatórias são exibidas apenas no terminal local. Para finalizar, faça logout e pressione `Ctrl+C` no terminal do inicializador. O script remove apenas a pasta temporária própria depois de encerrar os processos filhos. Não use o seed separado contra bancos fora do ambiente descartável validado.

## Limitações acadêmicas

Assistente usa parser determinístico nas operações e Ollama local para orientação documental; não é um planejador autônomo. Não existe métrica real de uso/conclusão no prazo. Não há homologação de produção, restore, múltiplos workers nem segurança operacional de infraestrutura pública. O calendário usa lock transacional compartilhado e tem testes concorrentes, mas não oferece timezone por empresa nem versão otimista de edição.
