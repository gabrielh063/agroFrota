# AGRO-MVP-100 — retomada após reboot do notebook

Data: 13/11/2026. Estado desta retomada: **`AGRO_MVP_100_PARTIAL`**.

## Recuperação

- A worktree original registrada em `/tmp/agro-mvp-100` não existe mais; o Git a
  marcava como `prunable`. A branch `feat/agro-mvp-100-finalization` permanece
  local no commit `892108a3f0b9aebf141030517ef0d3974fed9549`, que é o `Main`
  confirmado pelo GitHub e contém a integração da PR #11.
- A worktree aberta era `release/agrofrota-mvp-final` em
  `95cef28cf91e509b8adb1fdf6150db380ea73ef0`. Esse commit é ancestral do
  `Main` confirmado. A branch de retomada `feat/agro-mvp-100-resume` foi criada
  a partir de `892108a3f0b9aebf141030517ef0d3974fed9549` na worktree existente.
- Arquivos não rastreados já presentes (`.worktrees/`, backups `.bak`,
  `node_modules/`, `package*.json`, `popular_agrofrota_demo.py` e
  `reiniciar_api_demo.py`) foram preservados e ficaram fora desta alteração.
- PR #9 está integrada; PR #11 está integrada em `Main`; PR #12 permanece aberta
  para evidências de implantação privada. CI da PR #12 passou em backend e
  frontend no SHA `80d78cda003c25cdc45a87a1a3f675e07e43438b`.
- Nenhuma alteração foi feita no host `techcell`, nem nos serviços persistentes.

## Gates

| Gate | Estado | Evidência / pendência |
|---|---|---|
| A — Central de IA | **PARTIAL** | Fluxo operacional, transação e rollback têm testes; a indisponibilidade e erros são sanitizados e cobertos por teste. O relatório da PR #12 registra dois HTTP 500 em `/api/assistente/mensagem`, mas não preserva uma exceção que prove a causa específica. Sem acesso/alteração ao host, a causa histórica não foi confirmada. |
| B — Convites e cadastro | **PARTIAL** | Implementados convites tenant-bound, token aleatório armazenado como hash, prazo de 72 h, revogação, username/senha, RBAC, migrações e proteção contra corrida. Quatro testes de integração MariaDB passaram. Falta validar a tela no navegador real e a operação de compartilhamento do link. |
| C — Funcionalidades do MVP | **DONE** | Evidências prévias cobrem login, dashboard, máquinas, equipamentos, OS, calendário, equipe/permissões e Central; os testes de backend e registros de homologação estão nos documentos de release e implantação. |
| D — Frontend | **PARTIAL** | Build/lint, viewport móvel/desktop e axe-core foram registrados anteriormente. Leitor de tela, estados dinâmicos da Central, contraste manual residual e navegador da nova tela de cadastro continuam pendentes. |
| E — Infraestrutura | **PARTIAL** | PR #12 registra backup/restore isolado, health e preservação de dados; ainda aponta verificações operacionais de boot/backup e monitoramento. Nenhuma intervenção no host foi feita nesta retomada. |
| F — Qualidade | **PARTIAL** | Suíte backend local completa passou (273); build e lint passaram; PR #12 tem checks verdes. A revisão/mitigação dos hashes de senha encontrados no histórico público segue bloqueante e depende de decisão do responsável. |

## Incremento desta retomada

- `POST /api/convites/` cria convite somente para perfil delegável pelo
  administrador atual; listagem e revogação são limitadas ao tenant autenticado.
- O token de 256 bits é retornado uma única vez, salvo somente como SHA-256,
  expira em 72 horas e pode ser consumido uma vez. Cadastro valida o convite,
  exige senha de ao menos oito caracteres e grava a referência do convite no
  usuário para permitir retry seguro após falha entre bancos.
- A tela Equipe e Permissões emite, lista e revoga convites. `/cadastro` valida
  o link e permite definir username e senha. O link deve ser compartilhado
  manualmente por canal privado; não há envio de e-mail configurado.
- A Central de IA agora responde com mensagem genérica em indisponibilidade e
  loga apenas a classe da exceção; não registra URL, corpo, SQL ou conteúdo da
  conversa. A resposta 503 evita expor texto de exceção interno.

## Validação desta retomada

- `backend/tools/ci.py`: **273 aprovados**, 74 avisos de depreciação já
  existentes (`datetime.utcnow`). Inclui os quatro testes de convites, testes
  de concorrência/isolamento e dois testes de erro sanitizado da Central.
- Migrações Alembic: um head central (`8c4a2d91f630`) e um head tenant
  (`f48d32ce17a1`); ambos aplicados no MariaDB descartável durante a suíte.
- `npm run build`: aprovado.
- `npm run lint`: exit 0; avisos preexistentes de hooks/efeitos e dependências.
- `git diff --check`: aprovado antes do registro final.
- CI remota desta nova branch e revisão visual do cadastro ainda dependem da
  publicação da PR. Nenhuma migração foi aplicada à base de produção.

## Bloqueios para READY

1. O responsável deve classificar e mitigar os hashes de senha já alcançáveis
   no histórico público. O histórico remoto não foi reescrito.
2. Confirmar por evidência de logs se os HTTP 500 históricos da Central foram
   resolvidos pelo fechamento antecipado da sessão de autorização em PR #11;
   a correlação é plausível, mas não prova causalidade para aquelas requisições.
3. Homologar a nova página de cadastro em navegador e completar as verificações
   residuais de acessibilidade descritas no audit.
4. Completar os itens operacionais ainda pendentes da PR #12 antes de declarar
   infraestrutura pronta.

Não aplicar as novas migrações em `techcell` até haver backup, teste e aprovação
de publicação. Não foi feito merge nem deploy.
