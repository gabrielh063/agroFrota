# Handoff B — parcial, não integrar como produto concluído

Base `17111567fb23c04c95a3702c26a11fbad721a50e`. Commits de produto: `e4a712ec934a2f8d463d61cbe08f5790c6fe09b8` (calendário) e `d16ad79a38c4ac15eb9664417b10b82ea241f96b` (sessão). O SHA deste registro é identificado pelo commit que contém este arquivo.

Origem do calendário: diff não commitado da worktree original `codex/fundacao-rf08`, revisado e aplicado somente aos arquivos de rota, serviço e página, mais o modal novo. Os testes originais não foram copiados porque retornavam sem verificar quando não encontravam dados. Dois testes unitários determinísticos substituem essa cobertura parcial. A worktree original não foi alterada. Não foram copiados ambientes ou credenciais.

Verificações: dois testes unitários passaram; frontend build passou e lint terminou com avisos, incluindo um no modal acrescentado. Não houve teste E2E nem MariaDB nesta entrega. O tratamento de sessão expirada não foi testado em navegador. Não há prova com modelo real; nenhum modelo foi usado.

Dependências: contrato inicial de A lido em `fee051758fe3f854e04965605d70af592eb97d2d`, que declara matriz e escopo ainda pendentes. C documentou base e coordenação em `0ad66937f167426ce5a7dbcbabf32533bac86fa7`. Esses commits não foram mesclados. A integração depende das interfaces finais de A e da infraestrutura de C; C deve conciliar e validar as branches.

Pendências críticas: aplicar autorização e escopo por objeto em todos os serviços; regras de transição, conflitos e indisponibilidade, concorrência MariaDB, idempotência, controle de versão, timezone, filtros e paginação da agenda; finalizar telas operacionais e administrativas; assistente, persistência de propostas e auditoria; testes de sete perfis, isolamento, revogação, E2E, segurança de prompts e modelo real. As mudanças de calendário não asseguram essas regras e não devem ser interpretadas como prontas para operação. Falta manual por perfil e roteiro acadêmico após definição dos contratos reais.
