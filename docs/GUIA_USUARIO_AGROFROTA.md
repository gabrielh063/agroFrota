# Guia rápido do AgroFrota

Este guia cobre a demonstração acadêmica do MVP. Use apenas dados fictícios nesse ambiente.

## Iniciar e entrar

1. Na raiz do repositório, execute `python iniciar_agrofrota.py` (ou `python iniciar_agrofrota.py --modelo llama3.2:3b` se esse modelo já estiver instalado).
2. Aguarde o terminal confirmar o login, dashboard, API, Central e frontend. O comando cria um MariaDB temporário e migrações limpas.
3. Abra a URL de login exibida e use usuário, senha aleatória e tenant exibidos somente naquele terminal.
4. A senha muda a cada execução. Não a copie para documentos, commits ou capturas.

O seed inicial cria máquinas, equipamentos, ordens e um agendamento demonstrativos. `--sem-dados` cria somente a empresa e o usuário para uma base vazia.

## Navegar no produto

- **Visão geral:** confira ativos, frota em operação, manutenção, ordens em aberto, distribuição de estados, atividade e ordens recentes. Um traço ou texto de dados insuficientes indica que o MVP não tem base para calcular o indicador.
- **Maquinários:** pesquise por identificação, fabricante ou modelo. Use os filtros de estado/situação. **Novo maquinário** abre o cadastro; identificação, categoria, condição operacional e localização ajudam a selecionar o recurso correto.
- **Equipamentos:** consulte implementos e equipamentos, pesquise e use ações disponíveis conforme seu perfil.
- **Ordens de serviço:** veja prioridade e estado, abra detalhes, edite uma OS aberta, inicie, conclua ou cancele quando permitido. A numeração é atribuída pelo servidor.
- **Calendário de serviços:** consulte os compromissos, abra os detalhes e ajuste/cancele um agendamento permitido. Conflitos de horário devem ser resolvidos antes de confirmar.
- **Central de Operações:** comece por um dos quatro cards ou escreva a solicitação. Para agendar, informe o serviço, recurso, data, hora e duração. Revise o título, prioridade, ativo e período na proposta. A OS e a agenda só são criadas quando você confirma. Depois, use o link da OS ou abra o Calendário.

## Exemplo da Central

1. Escreva: “Preciso agendar uma colheita de silagem usando um trator disponível.”
2. Responda à informação solicitada. Por exemplo: “Pode ser amanhã às 8h, por quatro horas.”
3. Confira identificação do trator, tipo/prioridade, data e duração.
4. Se estiver correto, selecione **Confirmar operação**. Para sair sem gravar, selecione **Cancelar**.
5. Confira a mensagem com os números da OS e do agendamento e abra o link resultante.

Disponibilidade e permissão são verificadas de novo no momento da confirmação. Se o resultado da rede ficar incerto, confira Ordens de serviço e Calendário antes de repetir; confirmações repetidas retornam o resultado persistido.

## Prioridades e situação

- **Baixa:** pode aguardar a programação normal.
- **Média:** demanda de rotina quando não há urgência indicada.
- **Alta:** precisa de atenção prioritária.
- **Urgente:** atendimento imediato conforme a operação da propriedade.

Os estados de OS indicam se está aberta, em andamento, concluída ou cancelada. Estado final não deve ser reaberto por edição. Ativo “em manutenção” ou “parado” não está disponível para novo agendamento.

## Encerrar a demonstração

Selecione **Sair** para revogar a sessão. Volte ao terminal do inicializador e pressione `Ctrl+C`. Ele encerra apenas Vite, Flask e MariaDB iniciados por aquela sessão e remove o diretório temporário privado, incluindo o banco demonstrativo e credenciais aleatórias.

## Limites do MVP

Os links “Relatórios e indicadores” e “Equipe e recursos” estão desabilitados. O sistema não calcula uso real da frota nem conclusão no prazo sem dados que sustentem essas métricas. O calendário não foi homologado para uso concorrente com várias instâncias nem para timezone configurável por empresa. Não use banco ou credencial de produção no inicializador acadêmico.
