# Sessões e revogação

O JWT permanece no `sessionStorage` e tem expiração configurada no servidor. Login inclui a versão de sessão atual do usuário; a resolução do tenant consulta usuário e versão no banco em cada requisição e rejeita tokens sem versão ou com versão diferente. Tokens emitidos antes da migração são rejeitados. O perfil atual continua sendo consultado e avaliado no backend.

`POST /api/auth/logout`, autenticado, incrementa atomicamente a versão no banco do tenant e invalida **todas** as sessões desse usuário, inclusive outros dispositivos. Alteração de senha também incrementa a versão na mesma transação. O frontend só remove a sessão local após confirmação do servidor; se falhar, informa que deve tentar novamente. Uma nova autenticação emite token com a nova versão. A versão é persistente, sem uma lista crescente de tokens. A aplicação deve aplicar a migração tenant `58a724c498ce` antes do código; a aplicação anterior não reconhece a versão e não deve ficar servindo tráfego durante atualização ou rollback.

Testes em MariaDB descartável verificaram logout, reutilização de dois tokens, novo login e troca de senha; reinício da API, múltiplos workers, corrida com requisição já autorizada e experiência E2E do frontend ainda não foram provados. Não há refresh token. Essa alteração não substitui auditoria, proteção de força bruta ou os gates de produção.
# Perfil inativo

O login rejeita perfil inexistente ou inativo e o contexto autenticado revalida seu estado mesmo quando a rota não exige uma permissão específica. O teste `test_perfil_inativo_impede_login_e_rota_sem_permissao` cobre login e logout com um perfil sintético desativado. Isso não comprova revogação após reativação, reinício ou múltiplos workers.

