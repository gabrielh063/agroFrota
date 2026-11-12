# Prontidão da release candidate do AgroFrota

Data de registro: 12/11/2026. Classificação nesta etapa: **`AGRO_MVP_FINAL_PARTIAL`**. Há implementação, suíte backend, build e checks remotos aprovados, além de homologação local autenticada; permanecem parciais as transições finais de OS/agendamento, recuperação de falha de rede e revisão de acessibilidade. Não foi feito merge nem deploy.

## Branch e histórico

- Branch local: `release/agrofrota-mvp-final`, derivada do head de #8 `9990955a8bcb5c4487721f2f6f933f555c04dd37` (AGRO-UI-02 estava sem commit no início e agora compõe esta branch local).
- `Main` é a branch padrão confirmada via GitHub. Head #5: `7759213e31666868946ba305b86841274b6a0897`.
- A cadeia consultada no remoto via `gh`: #5 (base Main), #6 (base #5), #7 (base #6), #8 (base #7). PRs #1–#8 permanecem abertas; a PR final #9 foi aberta para `Main`.
- Commit da candidata funcional: `1e8bd157a4d808b2e7f8fe01c923760422c4fee1` (`Finalize AgroFrota MVP candidate`). A atualização deste relatório será o head mais recente publicado na PR.
- PR final: [#9](https://github.com/gabrielh063/agroFrota/pull/9), `release/agrofrota-mvp-final` → `Main`.
- Checks remotos no head `b6b014884f8b65d52e8570b0b849bbd3b63ca575`: `backend-mariadb` e `frontend` passaram. Decisão de revisão vazia; merge state `CLEAN`; API informa que `Main` não tem branch protection configurada. Não integrado em `Main`; nenhuma PR anterior foi fechada. Esta atualização posterior de evidências/documentação precisa disparar e passar CI novamente.

## Verificações executadas

| Verificação | Resultado | Evidência |
|---|---|---|
| Backend/MariaDB | **249 aprovados**, 74 avisos deprecation `datetime.utcnow`; migrações central e tenant até `7b53d2a1c804`; ambiente descartável encerrado/removido | Saída local de `python backend/tools/ci.py` em 12/11/2026 |
| Frontend build | **Aprovado** com Vite 8.3.1 | `cd frontend && npm run build` |
| Frontend lint | **Exit 0**, sem erros; avisos de hooks/efeitos, dependências e Fast Refresh persistem em código existente | `cd frontend && npm run lint` |
| Inicializador | **Passou** após smoke checks de migrations, API health, preflight OPTIONS/CORS, login, `/api/auth/me`, `/api/dashboard/capacidade` e `/api/assistente/conversas`; a sessão foi encerrada pelo próprio launcher e o diretório temporário foi removido | `python iniciar_agrofrota.py --modelo llama3.2:3b`; sessão isolada removida após homologação |
| Navegador autenticado | **Passou**: login, navegação Dashboard/Central/Maquinários/Equipamentos/OS/detalhe/Calendário, proposta, confirmação e logout; dados apenas demonstrativos | `docs/evidence/final/` |
| Matriz de largura | **Passou sem overflow horizontal** em 375×812, 768×1024, 1280×800 e 1600×900 em Login, Dashboard, Central, Maquinários, Equipamentos, OS, detalhe e Calendário | Chrome/CDP local |
| Persistência Central | **Passou**: OS #7, agenda #2, DEMO-TR-02, 13/11/2026 08:00–12:00; proposta consumida e ligada aos dois IDs de resultado | Consulta somente leitura ao MariaDB temporário |
| Ollama real | **Disponível**; servidor local tinha `llama3.2:3b`, `llama3.1:8b`, `qwen3:1.7b` entre modelos listados. Não foi feita inferência de conhecimento nesta homologação; fluxo operacional é determinístico | `GET /api/tags` em loopback |
| Checks remotos | **Ainda não executados para este head**; os checks consultados são anteriores (#5/#8). A PR final ainda não foi publicada nesta etapa | GitHub via `gh pr list` |
| Segurança / segredos | Não foram feitos scans completos de histórico nesta etapa. Dump sensível removido do tree em commit antigo continua no histórico, conforme `HANDOFF_ETAPA_1.md`; não reescrever histórico | Documentação de segurança existente |

## Fluxos homologados

- **A — Login/Dashboard:** login demonstrativo real; KPIs e listas carregaram dados do tenant isolado; sidebar navegou entre telas.
- **B — Gestão de ativos:** no Chrome autenticado foram criadas e editadas uma máquina e um equipamento fictícios; listas e controles de busca/filtro renderizaram. Não foi verificado um cenário de filtro que prove o subconjunto retornado.
- **C — OS:** tabela e detalhe autenticados abriram; criação manual por formulário e criação via Central foram exercitadas. Editar, concluir e cancelar manualmente não foram percorridos no browser; testes backend cobrem transições e auditoria.
- **D — Agenda:** calendário autenticado; criação e edição manuais foram exercitadas, e uma reserva sobreposta foi recusada com erro visível. A Central também gravou agenda. Cancelamento manual não foi percorrido; testes backend cobrem rollback, disputa concorrente com indisponibilidade, bloqueio de ativo não operacional e OS com agenda pendente.
- **E — Central:** conversa em duas mensagens, contexto mantido, ativo disponível identificado, proposta revisável, confirmação e links de resultado. Dados conferidos diretamente no MariaDB temporário.
- **F — Repetição/falha:** conflito real no navegador foi bloqueado; suíte backend cobre idempotência, concorrência e rollback. Falha de rede após confirmação e clique duplicado pelo browser não foram simulados.
- **G — Logout:** logout real realizado no browser e rota protegida redirecionou para login.

## Nielsen, visual e acessibilidade

As dez heurísticas estão avaliadas em [`NIELSEN_USABILITY_AUDIT.md`](NIELSEN_USABILITY_AUDIT.md), com observações, severidade, correções, resultados e evidências. As capturas incluem Login, Dashboard, Central inicial/proposta/confirmada, Maquinários, Equipamentos, Ordens de serviço, detalhe e Calendário em desktop; Login, Central inicial e Maquinários em 375×812. O material antes/depois do UI-02 está em `docs/evidence/agro-ui-02/`.

Capturas mobile foram feitas em 375×812 e desktop em 1600×900. A largura do documento foi verificada também em 768×1024 e 1280×800. Teclado detalhado, contraste WCAG 2.2 AA e leitor de tela ainda precisam de homologação. Não declarar certificação de acessibilidade.

## Problemas corrigidos nesta rodada

- Corrigido o gráfico de atividade mensal para não desenhar barras mínimas quando o valor real é zero.
- A falha de confirmação da Central agora recomenda verificar OS e Calendário antes de repetir e explica o comportamento idempotente, sem declarar rollback não verificado.
- Inicializador moveu o ambiente Python para a pasta temporária privada da sessão e valida preflight/CORS e rotas autenticadas essenciais.
- Implementado e capturado o redesign local da UI-02 para Dashboard, Central e Maquinários.
- Agenda e indisponibilidade agora compartilham o lock operacional; mudanças de estado/troca de ativo e encerramento de OS bloqueiam quando há compromisso pendente.
- Labels do formulário de equipamento estão associados aos campos; menu de ações dos equipamentos anuncia nome, expansão e itens para tecnologias assistivas.

## Pendências para classificação READY

1. Medir contraste, validar todos os fluxos por teclado e testar leitor de tela.
2. Percorrer editar/concluir/cancelar OS, cancelar agendamento, testar filtros, erro de rede e confirmação repetida em navegador.
3. Atualizar e aguardar CI remoto referente à atualização documental/evidências da PR #9; confirmar revisão necessária antes de eventual merge.
4. Executar os fluxos manuais de navegador pendentes e completar a avaliação de acessibilidade antes de reclassificar a release.
5. Manter pendência histórica de credenciais/dump como ação do responsável do repositório; nenhuma rotação externa foi realizada nesta missão.

## Estado do gate e classificação

Classificação: **`AGRO_MVP_FINAL_PARTIAL`**. Implementação local, testes backend, build/lint, inicializador isolado, Central autenticada e checks GitHub no head funcional passaram. Alguns fluxos manuais de OS/agenda, erro de rede e revisão de acessibilidade ainda estão parciais. Portanto, não está autorizada a integração na branch `Main` pelos gates definidos na missão.

## Inicialização e encerramento

Na raiz do repositório, rode `python iniciar_agrofrota.py`. As credenciais aleatórias são exibidas apenas no terminal local. Para finalizar, faça logout e pressione `Ctrl+C` no terminal do inicializador. O script remove apenas a pasta temporária própria depois de encerrar os processos filhos. Não use o seed separado contra bancos fora do ambiente descartável validado.

## Limitações acadêmicas

Assistente usa parser determinístico nas operações e Ollama local para orientação documental; não é um planejador autônomo. Não existe métrica real de uso/conclusão no prazo. Não há homologação de produção, restore, múltiplos workers nem segurança operacional de infraestrutura pública. O calendário usa lock transacional compartilhado e tem testes concorrentes, mas não oferece timezone por empresa nem versão otimista de edição.
