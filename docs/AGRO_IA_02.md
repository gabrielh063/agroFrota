# AgroFrota AGRO-IA-02 — Assistente conversacional e operações

## Arquitetura

- As conversas ficam em `conversas_assistente_ia`, no banco do tenant. Cada registro é vinculado ao tenant, usuário, versão da sessão e validade de 24 horas. O histórico é limitado às 30 mensagens mais recentes; entradas têm limite de 800 caracteres e o texto persistido de cada resposta é limitado. Um UUID imprevisível identifica a conversa.
- O frontend carrega a conversa mais recente após atualizar a página e oferece **Nova conversa**. A API valida propriedade, tenant, banco, sessão e expiração antes de ler ou atualizar o estado.
- Consultas técnicas continuam usando o Vault FTS5 e Ollama local. Histórico curto e sanitizado pode entrar no contexto. O backend repete uma inferência malformada no máximo uma vez; falha do modelo não inicia escrita.
- Criação e alteração de propostas seguem parsers determinísticos tipados para campos operacionais. O modelo não escolhe IDs, categoria, estado, permissão ou disponibilidade. Categorias de máquinas são persistidas em `maquinas.categoria`; equipamentos usam o campo `tipo`. Cadastros antigos permanecem sem categoria até serem classificados na tela de Maquinários.
- A disponibilidade filtra recursos ativos, classificados e operacionais e verifica sobreposição com agendamentos e indisponibilidades no intervalo. A proposta é revalidada ao confirmar.
- Propostas de OS, OS + agenda e agenda de OS existente ficam em `propostas_agendamento_ia`. A migração `7b53d2a1c804` torna os campos de OS existente opcionais, adiciona payload estruturado e chaves/IDs de resultado e cria a tabela de conversas. A migration anterior `e1f74b2a9031` continua parte do caminho.
- A confirmação usa o bloqueio transacional operacional, revalida sessão/permissões/ativo, chama a criação compartilhada de OS sem commit interno, reserva o número pelo contador atual, cria agenda com `commit=False`, audita e consome a proposta no mesmo commit. Qualquer falha reverte OS, agenda, contador e auditoria. Repetir a confirmação retorna o resultado persistido.
- A criação manual de agenda agora compartilha o bloqueio operacional para serializar a validação de conflitos com a confirmação de OS + agenda. A API manual preserva o contrato de resposta.

## Intenções e conversa

O MVP identifica consultas técnicas/operacionais, consulta de disponibilidade, criação de OS, agendamento de OS existente, criação combinada, continuação, alteração, cancelamento e confirmação. A conversa coleta uma informação pendente por vez. Exemplos de continuação cobertos incluem **“E trator?”**, **“Troca para as 9h”**, **“Por quatro horas”**, escolha de recurso e repetição da confirmação.

Prioridades são filtradas exatamente. Uma pergunta por serviços `URGENTE` lista apenas OS ativas `URGENTE` em `ABERTA` ou `EM_ANDAMENTO`; não inclui `ALTA` nem concluídas. Uma OS criada recebe `MEDIA` por padrão, a menos que o usuário peça outra prioridade.

## Execução local

1. Instale as dependências existentes conforme `README.md`; não é necessário baixar um modelo novo.
2. Confira os modelos locais com `ollama list`; o padrão é `llama3.1:8b` e `AGRO_AI_MODEL=llama3.2:3b` seleciona a alternativa menor.
3. Aplique `alembic -c alembic-tenant.ini upgrade head` a cada banco de tenant de desenvolvimento que esteja na revisão `e1f74b2a9031`. Essa migration é aditiva. Faça backup conforme o procedimento local antes de qualquer atualização de banco persistente.
4. Inicie backend e frontend pelos comandos de desenvolvimento configurados no notebook. Mantenha `AGROFROTA_ENV=development`; o assistente acadêmico é bloqueado fora de `development`/`testing`.
5. Classifique os tratores/colheitadeiras existentes na tela de Maquinários para que a seleção por categoria os inclua. Registros sem categoria não são inferidos pelo modelo.

Para executar os testes isolados, com Python, dependências e MariaDB instalados:

```sh
python backend/tools/ci.py
cd frontend
npm run build
npm run lint
```

O runner cria e encerra um MariaDB descartável próprio. Ele não reutiliza o banco de demonstração do operador.

## Testes desta missão

A suíte backend cobre parsing de continuação, prioridade urgente exata, retomada de conversa, categoria/classificação, conflito no intervalo, criação e confirmação, repetição de mensagem, confirmação concorrente via duas sessões MariaDB, resultado idempotente, expiração, cancelamento/alteração da proposta, rollback quando a agenda conflita e consulta das listas manuais de OS/agenda. O build e lint do frontend também são gates.

Validação com Ollama local e tela completa em navegador são registradas separadamente como evidência real; teste de parser/mocks não substitui inferência real. A data/hora relativa segue `America/Sao_Paulo`.

### Execução de validação desta branch

- `python backend/tools/ci.py`: **245 aprovados** em MariaDB descartável isolado; migrations central/tenant aplicadas até `7b53d2a1c804`. O runner encerrou e removeu somente os recursos descartáveis que criou.
- `npm run build`: **aprovado** (Vite 8.3.1).
- `npm run lint`: **exit 0**, com avisos já existentes e avisos de hooks/efeitos no frontend; sem erros bloqueantes.
- Inferência real pelo serviço `chamar_ollama`: **aprovada** com `llama3.1:8b`; a resposta técnica retornou fontes do Vault (`tratores/operacao-segura.md` e `agricultura.md`). Também foi confirmada uma chamada direta de `llama3.2:3b` já instalado.
- A captura real do dashboard anterior está em [`docs/evidence/dashboard-demo-1600x900.png`](evidence/dashboard-demo-1600x900.png). Não foi capturada nesta execução uma sessão autenticada do fluxo completo de chat no navegador; a confirmação de ponta a ponta foi exercitada por API/serviços contra MariaDB descartável.

## Roteiro de demonstração

1. Pergunte: **“Quais serviços estão com prioridade urgente?”** Compare os números/estados retornados com a tela de Ordens de serviço.
2. Pergunte: **“O que devo verificar antes de operar um trator?”** Confira as fontes Markdown apresentadas.
3. Inicie: **“Agenda uma colheita de silagem no dia 18 desse mês, vamos usar o trator que estiver disponível.”** Responda **“E trator?”**, depois informe hora/duração se o assistente pedir.
4. Se houver mais de um trator compatível, escolha uma das identificações reais. Confira título, descrição, prioridade, recurso, data e horário no card.
5. Confirme pelo botão. Verifique o número da OS em Ordens de serviço e o compromisso em Calendário. Envie a confirmação de novo para observar que o mesmo resultado é retornado sem duplicação.
6. Para demonstrar edição, proponha uma agenda de OS existente e diga **“Troca para as 9h”**. A proposta anterior deixa de ser válida e o novo horário precisa de nova confirmação.

## Limitações conhecidas

- Conversa/intent parsing é um MVP determinístico em português, não um planejador aberto. Datas, serviços e recursos ambíguos pedem esclarecimento. Datas em mês/dia devem ser confirmadas no card antes de persistir.
- Categoria de ativos antigos é opcional e precisa ser preenchida por uma pessoa; não é inferida a partir de fabricante/modelo.
- Não há atribuição automática de responsável/operador e nem compatibilidade mecânica inferida. Esses vínculos permanecem vazios até serem informados por um fluxo que tenha validação e permissão.
- Navegador autenticado e inferência real variam por memória disponível. Nenhum modelo é baixado automaticamente. A candidata é acadêmica e ainda exige homologação no notebook do operador.
