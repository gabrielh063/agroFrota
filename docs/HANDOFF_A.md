# Handoff A — segurança RF08 (parcial)

Base `codex/fundacao-rf08` em `1711156`; branch `codex/seguranca-rf08`. Os commits de implementação são `5ac36b2` (contrato e consulta atual) e `3c8c480` (revogação nas mutações administrativas). A PR é dependente da base de fundação e não deve ser integrada como entrega completa da missão.

O contrato disponível para B está em [CONTRATOS_SEGURANCA.md](CONTRATOS_SEGURANCA.md). `GET /api/auth/me` retorna usuário, tenant e códigos atuais; bearer e logout continuam compatíveis. Ainda não há helper genérico de escopo nem matriz de sete perfis. Não presumir proteção de objetos operacionais.

Os serviços administrativos incrementam a versão de sessão na mudança de perfil ou estado do usuário, estado do perfil e permissões do perfil, na transação da mudança. A política e o bloqueio de último administrador já existiam na base. A desativação/reativação do tenant central ainda não revoga persistentemente os tokens, e reinício e múltiplos workers não foram provados.

Em MariaDB descartável próprio: `test_auth.py`, `test_admin_transacional.py` e `test_revogacao_acesso.py`: 22 passaram antes da inclusão do teste adicional de perfil; após incluí-lo, `test_admin_transacional.py`: 12 passaram. Cobrem consulta atual, troca de perfil, desativação/reativação de usuário e perfil, alterações de associação e concorrência administrativa. Não cobrem integralmente os requisitos da missão.

Pendente: matriz, seeds e migração explícita dos sete perfis legados; helper de autorização por escopo; auditoria persistente transacional e leitura restrita; revogação persistente por ciclo do tenant; provas de restart e dois workers; testes completos dos sete perfis e rollback de auditoria; revisão final e integração. Não houve migração nova nesta branch; cadeia tenant existente termina em `9b3b4b41d220`.
