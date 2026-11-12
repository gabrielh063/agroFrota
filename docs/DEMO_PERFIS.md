# Demonstração dos sete perfis

## Provisionamento

Execute `python iniciar_agrofrota.py` na raiz do repositório. O inicializador cria MariaDB, banco central e tenant próprios em diretório temporário, aplica migrations e popula os sete usuários no tenant descartável. Não altera bancos da instalação do operador. Cada senha é aleatória por execução; o usuário e a senha são exibidos somente no terminal privado do inicializador. O estado temporário que permite automação local tem permissão de arquivo `0600`, é removido pelo próprio inicializador no encerramento e não é incluído nas evidências versionadas.

| Perfil | Usuário de demonstração | Capacidades observáveis na interface |
|---|---|---|
| Administrador/Gerente (`ADMIN_EMPRESA`) | `admin_demo` | Operações e administração de usuários, perfis, permissões e auditoria |
| Diretoria (`DIRETORIA`) | `diretoria_demo` | Consulta operacional e de perfis; sem ações de escrita |
| Gestor de Frota (`GESTOR_FROTA`) | `gestor_frota_demo` | CRUD operacional de ativos/OS e consulta de equipe; sem administração de perfis |
| Administrativo (`ADMINISTRATIVO`) | `administrativo_demo` | Consultas operacionais, usuários e perfis; sem escrita |
| Manutenção (`MANUTENCAO`) | `manutencao_demo` | Consulta de ativos e OS atribuídas; edição/conclusão conforme escopo atribuído |
| Operador (`OPERADOR`) | `operador_demo` | Consulta de ativos e OS próprias; criação de OS no próprio escopo |
| Auditor (`AUDITOR`) | `auditor_demo` | Consulta operacional, perfis e auditoria; sem ações de escrita |

As capacidades são derivadas das permissões efetivas retornadas por `GET /api/auth/me`. A matriz de autorização e escopo continua sendo a definida em `backend/services/matriz_acesso.py` e reforçada no backend. A interface oculta ações não autorizadas e mostra uma mensagem para rota sem permissão; isso é orientação de UX, não controle de segurança. Os endpoints continuam responsáveis por autorizar cada operação.

OS fictícias são atribuídas ao usuário de Manutenção e ao Operador para demonstrar escopo; outros perfis de consulta empresarial veem a frota permitida pela matriz. Não são criadas credenciais fixas de senha no código, documentação ou frontend.

## Fluxos e resultados

- As sete contas autenticaram no Chrome headless. O perfil atual aparece no menu lateral e a lista de navegação acompanha as permissões efetivas.
- Administrador/Gerente visualizou usuários, perfis e permissões, e criou e editou uma conta fictícia pela tela **Equipe e Permissões**.
- Gestor de Frota viu ações de criação/edição de máquina; Diretoria e Administrativo viram somente leitura; Manutenção e Operador viram apenas OS no seu escopo; Operador recebeu a ação de criar OS.
- Auditor não viu ações de escrita; acessar diretamente `/ordens-servico/nova` exibiu a recusa de acesso.
- A suíte HTTP verificou login, `/api/auth/me`, consulta, criação/edição de máquina, criação de usuário, auditoria, consulta de perfis e escopo de OS para cada perfil. Ela verifica edição de usuário permitida somente ao Administrador/Gerente, evento de auditoria de criação, revogação da sessão antiga após troca administrativa de perfil e readback sob o novo perfil.
- Isolamento entre tenants continua coberto por `backend/tests/test_multitenant.py`; transições administrativas que revogam sessões também são cobertas por `backend/tests/test_admin_transacional.py`.

## Evidências reproduzíveis

Diretório [`docs/evidence/final/profiles-demo/`](evidence/final/profiles-demo/):

| Evidência | Conteúdo |
|---|---|
| `api-results.json` | Status HTTP permitidos/negados, escopo de OS e contagem de usuários, sem tokens ou senhas |
| `browser-profiles.json` | Sete logins Chrome, menus/ações observados e recusa de URL direta do Auditor |
| `manager-create-edit.json` | Confirmação de criação/edição via UI e readback, sem dados de autenticação |
| `gerente-equipe.png`, `gerente-equipe-permissoes.png` | Tela administrativa e permissões efetivas |
| `diretoria-overview.png`, `gestor-frota-maquinarios.png`, `administrativo-equipamentos.png` | Consultas e ações visíveis por perfil |
| `manutencao-os.png`, `operador-os.png`, `auditor-os.png`, `auditor-url-negada.png` | Escopo de OS e diferença entre consulta, criação permitida e rota negada |

As capturas são do browser de teste a 1600×900 e contêm somente dados fictícios. Esta homologação de perfis não altera a pendência independente de acessibilidade: o estado geral de prontidão permanece `AGRO_MVP_FINAL_PARTIAL`, sem certificação WCAG 2.2 AA.
