# Retomada C — 2026-11-05

Worktree C limpa em `0ad66937f167426ce5a7dbcbabf32533bac86fa7`; referências remotas C, A, B e fundação confirmadas nos SHAs informados. A worktree principal contém alterações locais alheias, preservadas. Nenhum processo MariaDB, Nginx ou Gunicorn visível na inspeção inicial. A e B continuam independentes; não integrar nesta rodada.

# Handoff C — infraestrutura e integração

Base `17111567fb23c04c95a3702c26a11fbad721a50e`. Veja `PARALELISMO.md` para worktrees, propriedade e ordem. A e B foram criadas na base; na última verificação remota ainda não estavam publicadas. Confirmar commits e handoffs antes de integrar A e depois B por merge local.


## Retomada: progresso parcial e pendências

Dois bootstraps simultâneos com MariaDB e API exclusivos foram iniciados; encerrado um, o outro passou 3 testes de autenticação. Ambos foram encerrados após verificação de identidade. Um terceiro ambiente passou a suíte selecionada (63 testes, uma advertência) e foi encerrado. Testes locais de engine/configuração: 8 passaram. A escolha de portas ainda tem janela de disputa; inicialização parcial preserva recursos. Diretórios antigos em `/tmp` não foram removidos.

O runtime agora reutiliza engines por processo, com limite de 32 e pool de duas conexões sem overflow por engine; ao atingir o limite falha em vez de descartar pools possivelmente em uso. A capacidade é por processo, não global entre workers. Reinício de worker libera os pools. Os engines diretos de migração/provisionamento continuam independentes. A auditoria de fechamento de sessões ainda não foi concluída. Mudanças precisam de revisão e testes adicionais, inclusive fork e concorrência.

**Rodada incompleta:** credenciais separadas e prova de privilégios, Nginx/WSGI/MariaDB reproduzíveis, readiness e testes de indisponibilidade, recuperação e persistência ainda faltam. O bootstrap atual concede privilégios amplos ao usuário de teste e não é configuração de produção. Não fazer deploy nem declarar conclusão. O ambiente virtual usado foi efêmero; para reproduzir, criar venv isolado e instalar `backend/requirements.txt`, depois usar os comandos em `TESTES_DESCARTAVEIS.md`.

## Entregue neste checkpoint

- Contrato de paralelismo e isolamento documentado.
- Bootstrap usa o diretório temporário escolhido por Python (inclui `TMPDIR`), não um caminho fixo; portas de API e banco distintas. Verificação positiva anterior à limpeza preservada.
- Ambiente virtual exclusivo `/tmp/agrofrota-c-venv`; bootstrap aplicou migrações a central e dois tenants vazios e a suíte selecionada passou: **63 testes**, uma advertência de depreciação, 25,71 s. Ambiente descartável encerrado com verificação de identidade. O venv é efêmero, não um artefato de projeto.
- `tailscale serve status` retornou `No serve config`; nenhuma configuração alterada ou ativação realizada.

## Pendências obrigatórias

A seleção de portas ainda tem janela de disputa entre a escolha e o bind; uma falha preserva recursos parciais e não há limpeza automática. Comprovar execuções simultâneas e melhorar tratamento de colisões. Pools e ciclo de sessões, credenciais distintas, CLI coordenada com A, adoção de schema legado com comparação, fixture sintética legada e backup/restore ainda não foram implementados ou provados. Também faltam Compose, imagens, proxy, WSGI, readiness de banco, CI, limites compartilhados, benchmark, configuração HTTPS privada e testes de produção. Não considerar seguro para produção.

Quando A/B finalizarem: confirmar seus SHAs, handoffs, testes e limitações; integrar A e B nessa ordem, conciliar migrações e arquivos compartilhados, executar testes e benchmark integrados, e registrar relatório e PR integradora. Não usar dados reais nem recursos NEXO.

## Reprodução

Criar venv próprio e instalar `backend/requirements.txt`. Em `backend/`, executar `python tools/ambiente_descartavel.py start`, depois `python tools/ambiente_descartavel.py test DIRETORIO` e `python tools/ambiente_descartavel.py stop DIRETORIO`, usando o diretório informado pelo start. Consulte `TESTES_DESCARTAVEIS.md` para requisitos e limites.
