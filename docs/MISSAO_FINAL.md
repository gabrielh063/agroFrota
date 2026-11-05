# Missão final — candidata em validação

Estado: **PARCIAL**. Não homologada; não implantar esta candidata em dados reais.

## Integração

Responsável único pelos merges nesta missão: sessão integradora, branch
`codex/missao-final`, worktree `/tmp/agrofrota-missao-final`.
As worktrees originais e suas alterações locais foram preservadas.
Bootstrap remoto confirmou `Main` como padrão em
`714a2c0f623f680207e1c03fd1a180efcd5e532e`.

Composição por merges, preservando ancestrais:

- Fundação #1: `17111567fb23c04c95a3702c26a11fbad721a50e`.
- Segurança #3: `aaa8afd01f9f0eccabf0c66c07bbab3614022883`.
- Produto #4: `074d03283ab73f4226b84aad5d507c62b8d461d2`.
- Infraestrutura #2: `f4b0d3bc9e6a6c52c30b8bda0d16f13406e0d7cf`.

Nenhuma dessas PRs foi mesclada ou fechada. A inclusão na candidata não
equivale à incorporação em Main. Os gates completos continuam obrigatórios.

## Evidências e correções

Checkpoint `153de46e886f604d58698b6472a37dac484f905f`:
227 testes passaram em MariaDB sintético, sem skips; build e lint executados.
[CI remoto aprovado](https://github.com/gabrielh063/agroFrota/actions/runs/42124485438)
com jobs backend/MariaDB e frontend.

- Corrigidas duas mensagens de erro de agenda. Testes de conclusão agora
  percorrem AGENDADO → EM_ANDAMENTO → CONCLUIDO.
- Migração `b82a93d0e521`: contador persistente de OS, inicializado a partir
  do maior número existente; incremento sob bloqueio transacional. Teste
  com duas conexões prova números distintos e rollback do contador.
  Não executar importações diretas de OS após a inicialização do contador.
- Máquinas/equipamentos revalidam contexto, política e permissão no serviço.
  Escritas usam o bloqueio administrativo até commit. Mudança de `ativo`
  também exige a capacidade de desativação.
- Migração `c93ba4e1f632`: auditoria de mutações administrativas e de ativos
  na mesma transação. Metadados limitados a ator, operação e instante UTC;
  nenhum payload, senha ou token é gravado. Testes de falha de auditoria e
  de commit demonstram rollback do negócio e do evento.
- `/api/auditoria/` exige `AUDITORIA.VISUALIZAR`, concedida pelo seed somente
  a novos perfis ADMIN_EMPRESA e AUDITOR. Perfis existentes não recebem a
  capacidade automaticamente; delegação explícita continua necessária.
- Runner `backend/tools/ci.py` inicia ambiente exclusivo, executa todos os
  testes de `backend/tests` e encerra o ambiente após sucesso ou falha da suíte.
  Inicialização parcialmente falha ainda exige tratamento adicional.

Incremento de OS posterior ao checkpoint: 228 testes passaram, sem skips,
em uma nova execução sintética da árvore de trabalho. Listagem e detalhe
aplicam atribuição SQL; mutações revalidam sessão, permissão e escopo e
registram auditoria. MANUTENCAO usa `responsavel_id`; OPERADOR usa
`operador_id`. A criação por operador exige uma OS ativa, não encerrada,
previamente atribuída a ele no mesmo recurso. O payload isolado não concede
esse vínculo. Só gestão pode alterar atribuições. Essa política precisa ser
integrada à interface e ao restante dos módulos antes da homologação.

Avisos: 56 avisos de depreciação `datetime.utcnow` na última suíte; ainda
falta fechar timezone de negócio. Lint: 14 avisos (estado em efeitos,
dependências de hooks, ordem de declaração, exportação de contexto e import
não usado). Não foram suprimidos; revisar antes do gate de navegador.

## Pendências materiais

- Escopo e transações comuns de agenda/manutenção/indisponibilidade/dashboard.
- Versão otimista, idempotência persistente e integridade de transições entre módulos.
- Auditoria dos demais módulos e revogação do ciclo tenant; restart/dois workers.
- Telas administrativas e ciclo completo de operação; navegador real.
- Assistente, catálogo, ferramentas, propostas e confirmação atômica; modelo real.
- Credenciais runtime/migração, pools sob fork/exaustão, bootstrap sem disputa
  de portas, WSGI/proxy/readiness, backup/restore e operação privada.
- Matriz RF → API → tela → permissão → teste, manual e roteiro acadêmico finais.
- CI no head definitivo, revisão/merge das PRs e validação limpa de origin/Main.

## Alvo privado

A documentação consultada não identifica o host AgroFrota nem o banco alvo.
O host local tem Tailscale ativo, mas isso não demonstra que seja o destino
autorizado da instalação. Foi solicitada a identidade do host/alias SSH e
o caminho da configuração, sem segredos. Nenhuma configuração Tailscale,
Nginx, banco real ou recurso NEXO foi modificada.

O Ollama local lista `qwen3:1.7b` (1,4 GB) e outros modelos existentes.
Não houve download nem inferência de homologação. Na inspeção, havia 3,1 GB
livres em disco e memória sob pressão; qualquer carga deve respeitar isso.

## Reprodução sintética

Com Python, dependências de `backend/requirements.txt` e MariaDB instalados:

```sh
python backend/tools/ci.py
cd frontend
npm ci --no-audit --no-fund
npm run build
npm run lint
```

Para ambiente sintético persistente de inspeção:

```sh
python backend/tools/ambiente_descartavel.py start
python backend/tools/ambiente_descartavel.py test DIRETORIO
python backend/tools/ambiente_descartavel.py stop DIRETORIO
```

Use o diretório retornado pelo próprio `start`. `test` e `stop` verificam
marcador, datadir e processos. Esses comandos não são instalação de produção.
As duas novas migrações recusam downgrade destrutivo; isso não substitui
o plano de restauração, ainda pendente de implementação e validação.
