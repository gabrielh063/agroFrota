# Prontidão da release candidate do AgroFrota

Data de registro: 12/11/2026. Classificação nesta etapa: **`AGRO_MVP_FINAL_PARTIAL`**. Há implementação, suíte backend e build aprovados e uma homologação local real autenticada; ainda faltam checks remotos do head definitivo, PR final publicada, alguns fluxos de erro/conflito via browser e fechamento de limitações materiais de agenda. Não foi feito merge nem deploy.

## Branch e histórico

- Branch local: `release/agrofrota-mvp-final`, derivada do head de #8 `9990955a8bcb5c4487721f2f6f933f555c04dd37` (AGRO-UI-02 estava sem commit no início e agora compõe esta branch local).
- `Main` é a branch padrão confirmada via GitHub. Head #5: `7759213e31666868946ba305b86841274b6a0897`.
- A cadeia consultada no remoto via `gh`: #5 (base Main), #6 (base #5), #7 (base #6), #8 (base #7). PRs #1–#8 permanecem abertas na consulta. Não há PR #9.
- Resultado final local: **ainda não commitado/publicado nesta edição do relatório**. Atualizar este campo depois do commit/push e substituir pelo SHA final.
- Estado de integração: **não integrado em Main**. Nenhuma branch protection foi contornada; nenhuma PR foi fechada.

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
- **B — Gestão de ativos:** listas reais de máquinas/equipamentos renderizaram; busca/filtros disponíveis. Criação e edição manual pelo formulário não foram percorridas nesta sessão de navegador.
- **C — OS manual:** tabela e detalhe autenticados abriram; edição/criação manual não foram percorridas no browser. Criação de OS pela Central foi confirmada e persistida; backend cobre criação e transições.
- **D — Agenda:** calendário autenticado abriu; a Central gravou uma agenda. Alteração manual não foi exercitada nesta sessão; testes backend cobrem conflito/rollback, disputa concorrente com indisponibilidade, bloqueio de ativo não operacional e de OS com agenda pendente.
- **E — Central:** conversa em duas mensagens, contexto mantido, ativo disponível identificado, proposta revisável, confirmação e links de resultado. Dados conferidos diretamente no MariaDB temporário.
- **F — Repetição/falha:** suíte backend cobre idempotência, concorrência e rollback; não foi simulada falha de rede nem clique duplicado via browser nesta sessão.
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
2. Percorrer cadastro/edição manual de ativos, OS manual e edição/cancelamento de agenda em navegador; simular conflito e erro de rede.
3. Atualizar CI remota para o head de release e revisar branch protection/review exigida.
4. Criar commit, publicar `release/agrofrota-mvp-final` e abrir PR final apontada para `Main`; atualizar este documento com SHA, URL e checks.
5. Manter pendência histórica de credenciais/dump como ação do responsável do repositório; nenhuma rotação externa foi realizada nesta missão.

## Estado do gate e classificação

Classificação: **`AGRO_MVP_FINAL_PARTIAL`**. Implementação local, testes backend, build/lint, inicializador isolado e fluxo autenticado da Central passaram. A release ainda não tem commit/head remoto, checks GitHub ou PR final. Os fluxos manuais de CRUD/agenda no browser e a revisão de acessibilidade ainda estão parciais. Portanto, não está autorizada a integração na branch `Main` pelos gates definidos na missão.

## Inicialização e encerramento

Na raiz do repositório, rode `python iniciar_agrofrota.py`. As credenciais aleatórias são exibidas apenas no terminal local. Para finalizar, faça logout e pressione `Ctrl+C` no terminal do inicializador. O script remove apenas a pasta temporária própria depois de encerrar os processos filhos. Não use o seed separado contra bancos fora do ambiente descartável validado.

## Limitações acadêmicas

Assistente usa parser determinístico nas operações e Ollama local para orientação documental; não é um planejador autônomo. Não existe métrica real de uso/conclusão no prazo. Não há homologação de produção, restore, múltiplos workers nem segurança operacional de infraestrutura pública. O calendário usa lock transacional compartilhado e tem testes concorrentes, mas não oferece timezone por empresa nem versão otimista de edição.
