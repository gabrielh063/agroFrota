# Handoff A — matriz e escopo RF08

Branch `codex/seguranca-rf08`, PR #3, base `codex/fundacao-rf08` em `1711156`. Contrato inicial publicado em `728edd749ae81623b64ddf8871ec4d17ff528705`; implementação administrativa `f0bbef6147a91a6c33a7b04b2a06f87764148d47`; testes e matriz documentada `a6f9b15030c047af6826bbc44c506c88d3b6685e`. Consulte `git rev-parse HEAD` para o commit deste handoff e eventuais alterações posteriores.

Os sete perfis, códigos e escopos estão na [matriz e contrato](CONTRATOS_SEGURANCA.md). O helper `services.escopo.consultar_autorizado` usa contexto resolvido pelo servidor, sessão do banco do tenant, perfil e permissões atuais; aplica filtro SQL para lista e detalhe. Ausência de política, permissão, contexto ou coluna necessária nega. Cargo não confere acesso. Serviços administrativos e troca de senha aplicam a autorização nos serviços; o bloqueio transacional e a definição de administrador efetivo permanecem. As leituras de usuário usam filtro; demais leituras administrativas exigem escopo de empresa. A troca administrativa de senha passou a exigir autoridade administrativa efetiva e senha atual, mesmo em chamadas diretas ao serviço.

O seed cria os sete perfis somente quando ausentes; não altera permissões ou política de perfis existentes. O provisionamento inicial novo usa `ADMIN_EMPRESA`. A migração tenant exclusiva `a71f82c9d410` sucede `9b3b4b41d220`: associa explicitamente legados `GERENTE`, `MANUTENCAO`, `OPERADOR` às suas políticas, sem criar permissões ou reatribuir usuários, e incrementa a versão das sessões afetadas. Perfis personalizados restantes não recebem escopo operacional automaticamente; devem ser tratados explicitamente na integração de instalações existentes. Como as permissões legadas são preservadas, o acesso permitido pelo helper é a interseção delas com a matriz. A migração altera a interpretação de escopo: instale e valide o código coordenadamente com a migração antes de servir tráfego.

Validação em MariaDB e API descartáveis próprios: **78 passaram** com `test_matriz_escopo.py`, `test_auth.py`, `test_security.py`, `test_multitenant.py`, `test_permissoes_rf08.py`, `test_revogacao_acesso.py` e `test_admin_transacional.py`; duas advertências existentes de `datetime.utcnow`. Mais 15 testes unitários de configuração, schemas e segurança passaram. Os testes cobrem os sete perfis, ações permitidas/negadas, contexto de outro tenant, registro próprio e atribuição, lista e detalhe, seed repetido, migração legada e revogação, inclusive concorrência administrativa existente. O ambiente foi encerrado após uso.

Reprodução (com dependências Python e MariaDB instaladas):

```sh
cd backend
python tools/ambiente_descartavel.py start
python tools/ambiente_descartavel.py test DIRETORIO tests/test_matriz_escopo.py tests/test_auth.py tests/test_security.py tests/test_multitenant.py tests/test_permissoes_rf08.py tests/test_revogacao_acesso.py tests/test_admin_transacional.py
python tools/ambiente_descartavel.py stop DIRETORIO
```

O seed de teste cria um usuário sintético para cada perfil nos bancos descartáveis; o usuário inicial representa `ADMIN_EMPRESA`. `DIRETORIO` é o caminho retornado por `start`; não executar contra instalações reais.

Limites: B precisa aplicar e testar o helper em cada serviço operacional, incluindo a fonte confiável da atribuição e a autorização de criação. Escopo operacional ainda não foi validado. Auditoria persistente completa, revogação persistente em ciclo do tenant e provas de dois workers permanecem para próximo incremento. A PR continua em rascunho e depende da fundação; não houve merge ou deploy.
