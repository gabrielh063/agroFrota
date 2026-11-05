# Estado de prontidão

**PARCIAL — não homologado nem seguro para operação privada.** Base `714a2c0f623f680207e1c03fd1a180efcd5e532e`. Detalhes e evidências em [HANDOFF_ETAPA_1.md](HANDOFF_ETAPA_1.md).

- [x] Revisões iniciais central e tenant aplicadas em MariaDB vazio; comparação Alembic sem diferenças.
- [x] Suíte existente selecionada de autenticação, segurança, multitenant, RF08 legado e revogação: 50 passaram no ambiente descartável, incluindo seis verificações novas de cargos.
- [ ] Atualização de instalação existente, provisionamento isolado, backup e restore.
- [ ] Matriz RF08 proposta, escopo por objeto, proteção contra escalada e último administrador, auditoria transacional.
- [ ] Logout e revogação persistente, pools limitados, CI e segurança restante.
- [ ] Interfaces e fluxos operacionais; IA, limites e desempenho; implantação privada e homologação.

O modo de produção agora valida configurações básicas e pode iniciar com valores que passam nas verificações, mas isso **não** demonstra segurança operacional. Não exponha a aplicação nem use dados reais antes de fechar os gates. Ver [plano](PRODUCTIZATION_PLAN.md).
