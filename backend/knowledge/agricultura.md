# AgroFrota: guia de conhecimento agrícola para demonstração acadêmica

Este material complementa o modelo de linguagem; não substitui o manual do fabricante, a avaliação de um profissional habilitado nem uma inspeção da máquina.

## Gestão de frota agrícola
- Máquina autopropelida: trator, colheitadeira, pulverizador autopropelido. Implementos e equipamentos incluem plantadeira, grade, distribuidor de fertilizante, pulverizador acoplado e roçadeira.
- Cada equipamento deve ter identificação única, modelo, fabricante, condição operacional, local e histórico de serviços. Um item parado por manutenção afeta a capacidade operacional, mesmo que esteja cadastrado como ativo.
- Uma ordem de serviço (OS) descreve o serviço a executar, o ativo relacionado, prioridade, responsáveis e prazo. Um agendamento reserva um intervalo para executar uma OS existente.
- Manutenção preventiva é planejada para reduzir falhas; corretiva trata defeitos já identificados; preditiva acompanha condição e sinais para decidir quando intervir.
- Priorize serviços considerando segurança das pessoas, risco de dano, criticidade da operação agrícola, disponibilidade de peças e janela operacional.

## Rotina básica de inspeção, com segurança
- Antes do uso: inspecionar visualmente vazamentos, nível de fluidos conforme o manual, condição de pneus ou esteiras, proteções, conexões, iluminação, freios e alarmes. Registrar anomalias.
- Motor e arrefecimento: verificar indicadores, sujeira nos radiadores e sinais de aquecimento; jamais abrir sistema de arrefecimento pressurizado e quente.
- Sistema hidráulico: observar mangueiras danificadas e vazamentos. Fluido hidráulico sob pressão pode penetrar a pele; nunca procurar vazamento com a mão.
- Transmissão e tomada de potência (TDP/PTO): manter proteções e afastamento de partes giratórias. Desligar, bloquear e aguardar a parada total antes da manutenção.
- Pulverizadores: verificar filtros, mangueiras, bicos, vazamentos e calibração de acordo com o manual e as regras aplicáveis; exigir os EPIs adequados aos produtos usados.
- Plantadeiras: inspecionar discos, dosadores, mangueiras, transmissão e ajustes de profundidade e distribuição conforme a cultura e o implemento.
- Colheitadeiras: observar correias, rolamentos, plataforma, peneiras, sistema de alimentação e limpeza; atenção ao risco de incêndio por acúmulo de resíduos.
- A manutenção deve ser feita com a máquina imobilizada, energia isolada e procedimento seguro apropriado, especialmente para peças elevadas e sistemas pressurizados.

## Planejamento e registro
- Registre sintomas observados, condição de uso, horímetro quando disponível, última intervenção, peças necessárias, responsável e resultado.
- O intervalo exato de troca de óleo, filtros, correias e lubrificação varia conforme fabricante, modelo, ano, regime de uso e manual. Não invente intervalos fixos nem especificações de fluido.
- Uma máquina com fumaça anormal, perda de freio, vazamento pressurizado, superaquecimento ou falha em proteção deve ser avaliada antes de continuar em operação.
- Agendamento só é válido se houver uma OS existente, ativa e não encerrada, recurso ativo e janela livre. A confirmação do sistema vale mais que a sugestão do modelo.

## Vocabulário
- Horímetro: contador de horas de funcionamento; útil para planos de manutenção baseados em uso.
- Implemento: equipamento destinado a operação agrícola, frequentemente acoplado ao trator.
- OS: ordem de serviço, registro formal de uma atividade.
- Indisponibilidade: intervalo em que a máquina ou equipamento não pode ser usado.
- Preventiva, corretiva e preditiva: modalidades distintas; a explicação não é diagnóstico.

## Limites do assistente
- Para respostas sobre a frota cadastrada, use somente dados fornecidos pela API do AgroFrota; não invente máquinas, identificações, OS, condições ou agendamentos.
- Não produza diagnósticos definitivos, procedimentos arriscados para sistemas pressurizados/eletrificados ou especificações técnicas não verificadas. Oriente a consultar manual e profissional capacitado.
- Agendamento neste MVP é exclusivamente de OS existente; criar OS continua na interface convencional.

## Referências para aprofundamento (consultar manual específico antes de executar qualquer serviço)
- Embrapa Gado de Leite, Termo de Referência de manutenção de máquinas agrícolas (2026): https://www.embrapa.br/documents/1355117/1948445/PREG%C3%83O%2B90002-2026%2B-%2BMANUTEN%C3%87%C3%83O%2BM%C3%81QUINAS%2BAGR%C3%8DCOLAS.pdf/bb97b835-e318-b0d1-9028-4f921311c454?t=1774608677731
- Manual de operação e manutenção do fabricante do modelo/ano real da máquina.
