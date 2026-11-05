# Plano de productização — diagnóstico inicial

Base observada: `714a2c0f623f680207e1c03fd1a180efcd5e532e`, branch local `Main`; alterações prévias no calendário e seu modal foram preservadas. Referência remota local coincide; consulta remota de PR/CI não retornou dados verificáveis. Não há AGENTS.md aplicável encontrado.

## Etapas e gates cumulativos

1. **Fundação, segurança e RF08 — em andamento:** MariaDB descartável com dois tenants, configuração e autenticação, migrações e provisionamento, pools, matriz e autorização de backend, proteção de administração, auditoria e testes. Detalhes e checkpoint em [HANDOFF_ETAPA_1.md](HANDOFF_ETAPA_1.md).
2. **Produto:** telas administrativas e fluxos operacionais, agenda e concorrência.
3. **IA e operação:** assistente, limites, desempenho, backup e implantação privada. Não iniciar nesta execução.

## Rastreabilidade inicial (proposta; não é contrato RF formal)

| Capacidade | API existente | Tela existente | Permissão observada | Teste/evidência |
|---|---|---|---|---|
| Máquinas e implementos | `/api/maquinas`, `/api/equipamentos` | Maquinários, equipamentos | `MAQUINA_*`, `EQUIPAMENTO_*` | testes HTTP existentes não executados |
| Ordens | `/api/ordens-servico` | lista, criação, edição, detalhes | `OS.*` | testes HTTP não executados |
| Agenda | `/api/calendario` | calendário | `OS.EDITAR` / `OS.VISUALIZAR`, precisa granularidade | alteração local preexistente não validada |
| Manutenção e indisponibilidade | rotas correspondentes | telas próprias ausentes | `MANUTENCAO.*`; indisponibilidade usa `OS.*` | testes HTTP não executados |
| Indicadores | `/api/dashboard` | dashboard | `OS.VISUALIZAR` | métricas e testes precisam validação |
| Usuários, cargos e perfis | rotas correspondentes | ausentes | cargos com permissões explícitas; demais com códigos próprios | RF08 não executado; testes legados usam tenant fixo |
| Assistente | ausente | ausente | ausente | nenhuma prova |

## Riscos e decisões pendentes

O middleware revalida tenant e usuário/perfil atuais e deve preservar isso. Engines são criadas repetidamente; revisar ciclo de vida e limites antes de otimizar. Revisões iniciais Alembic central e tenant foram criadas e testadas em bancos vazios; adoção de bancos existentes está pendente. Não há auditoria persistente comprovada. Dump versionado possui instruções de inserção e deve ser tratado como potencialmente sensível até classificação autorizada; não foi exposto aqui. Planejar remoção da árvore, rotação e eventual limpeza de histórico após avaliação, sem reescrever histórico automaticamente. `backend/.env` é local e não deve ser publicado. Não usar dados existentes para testes.

A proteção de testes exige `AGROFROTA_TEST_DISPOSABLE=1`, API e DB locais e nomes de banco central e tenant iniciados por `agrofrota_test_`. Isso reduz risco, mas não prova que um servidor local seja descartável. Os testes de RF08 e revogação foram parametrizados; multitenant exige um segundo nome descartável distinto. A inicialização local ainda usa `create_all`; não é migração nem instalação de produção.

## Registro de verificação

Em 05/11/2026, `git ls-remote` confirmou `Main` em `714a2c0f623f680207e1c03fd1a180efcd5e532e`; GitHub retornou listas vazias de PRs e execuções de Actions. Há uma única worktree registrada. Docker CLI está instalado, mas o acesso ao daemon foi negado. O modo de desenvolvimento não deve ser exposto: a barreira de produção depende da configuração explícita da variável e não substitui controles de infraestrutura.
