# Paralelismo AgroFrota

Base compartilhada: `17111567fb23c04c95a3702c26a11fbad721a50e` (fundação `codex/fundacao-rf08`, PR #1 em rascunho). Alterações locais de calendário/frontend na worktree original não fazem parte da base e não devem ser copiadas automaticamente.

| Instância | Branch | Worktree | Responsabilidade |
| --- | --- | --- | --- |
| A | `codex/seguranca-rf08` | `/home/gabriel/Documents/projetos_portifolio/agrofrota-seguranca-rf08` | Autenticação, permissões, auditoria e respectivas migrações |
| B | `codex/produto-assistente` | `/home/gabriel/Documents/projetos_portifolio/agrofrota-produto-assistente` | Telas, serviços operacionais, agenda e IA |
| C | `codex/infra-integracao` | `/home/gabriel/Documents/projetos_portifolio/agrofrota-infra-integracao` | `backend/database/**`, conexão, bootstrap, CLI, operação, CI, benchmark e documentação de instalação/operação |

A e B podem ler os arquivos de C, mas não devem editá-los. `backend/app.py`, `backend/config.py` e manifests são compartilhados: alterações mínimas, sem reformatação ampla; C concilia na integração. Cada instância registra seu próprio handoff, incluindo contratos, testes, limitações e SHA; não há comunicação automática entre sessões.

## Contratos conhecidos

- Banco central e um banco por tenant; revisões Alembic central e tenant independentes. Alterações de schema devem ter migração e preservar a sequência de atualização.
- Sessão JWT contém versão persistida no tenant; logout e troca de senha invalidam todas as sessões do usuário. Perfil ativo e permissões são reavaliados no backend; ver `docs/SESSOES.md` e `docs/POLITICA_ADMINISTRATIVA.md`.
- Provisionamento e runtime devem usar credenciais distintas; a CLI deve ser conciliada com os serviços de A. Nenhuma adoção de schema legado por `stamp` sem comparação e backup.
- Não usar dump sensível como fixture. Não modificar recursos, arquivos ou serviços do NEXO.

## Integração e testes

C verifica commits, handoffs e evidências e integra por merge local rastreável primeiro A, depois B; não fazer cherry-pick duplicado nem rebase de branches alheias. Conciliar app, config, manifests e heads Alembic; testar a árvore integrada antes de atualizar a PR integradora. Não integrar código crítico apenas por ter sido publicado.

Cada execução usa ambiente virtual, datadir, socket, bancos, portas e diretórios próprios. Utilizar `backend/tools/ambiente_descartavel.py` e registrar o diretório retornado; jamais apontar testes para banco real ou recursos de outra instância. Verificar identidade antes de limpeza, preservar recursos parciais para inspeção e não depender de diretório fixo em `/tmp`. Carga e benchmark somente nos recursos exclusivos AgroFrota, sem saturar NEXO.
