# Handoff C — infraestrutura e integração

Base `17111567fb23c04c95a3702c26a11fbad721a50e`. Veja `PARALELISMO.md` para worktrees, propriedade e ordem. A e B foram criadas na base; na última verificação remota ainda não estavam publicadas. Confirmar commits e handoffs antes de integrar A e depois B por merge local.

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
