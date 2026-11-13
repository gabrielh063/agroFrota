# AgroFrota: Vault, assistente local e dashboard

## O que está integrado

- O Vault fica em `backend/knowledge/`. O indexador SQLite FTS5 lê somente arquivos Markdown sob essa raiz, ignora links para fora dela, divide por seção e reindexa arquivos alterados por SHA-256. O índice é gravado em `backend/instance/vault.sqlite3` (ignorado pelo Git), ou no caminho definido em `AGRO_AI_INDEX_PATH`.
- O assistente usa trechos recuperados e exibe arquivo/seção na conversa. Consultas operacionais autorizadas usam os serviços e as permissões do tenant; a listagem de ativos e OS não usa SQL fornecido pelo modelo. Falha ou JSON inválido do Ollama resulta em erro tratado, sem confirmação de escrita.
- Propostas de agenda são guardadas em `propostas_agendamento_ia` no banco do tenant. O token não é armazenado em claro; confirmação bloqueia a linha, revalida usuário, tenant, sessão, OS e disponibilidade e grava consumo junto do agendamento. Propostas expiram em cinco minutos.
- A página inicial reúne cards da capacidade atual, OS recentes, rosca de quatro estados exclusivos e histórico mensal de OS criadas no endpoint autorizado `/api/dashboard/atividade`. O produto não tem telemetria de utilização nem data de conclusão; essas taxas aparecem como insuficientes, sem valores fabricados.
- Os links de gestão sem página implementada ficam desabilitados. A indicação de demonstração exige `VITE_AGROFROTA_DEMO=true`.

## Conhecimento no Vault

Inclui guias de inspeção pré-operacional e operação segura de tratores, sistemas de tratores, colheitadeiras, implementos, manutenção preventiva/corretiva/baseada em condição e abertura/agendamento de OS. Os textos não definem intervalos, capacidades, limites, fluidos ou parâmetros de fabricante. Consulte sempre o manual do modelo e profissionais habilitados.

## Configuração local

1. Copie `backend/.env.example` para `backend/.env` e preencha apenas credenciais locais do ambiente de demonstração. Não use dados reais com o seed descartável.
2. Copie `frontend/.env.example` para `frontend/.env`; configure a URL da API. Habilite o rótulo de demonstração somente quando a base usada for demonstrativa.
3. Instale dependências do backend (`pip install -r backend/requirements.txt`) e frontend (`cd frontend && npm ci`).
4. Confirme os modelos sem baixar nada com `ollama list`. O padrão é `llama3.1:8b`; pode-se definir `AGRO_AI_MODEL=llama3.2:3b` para o fallback instalado.
5. Aplique a migração tenant até `e1f74b2a9031` no banco de desenvolvimento antes de usar agendamentos por chat.
6. Inicie o backend e o frontend pelos comandos de desenvolvimento do README principal. Não execute `popular_agrofrota_demo.py` contra um banco que não esteja explicitamente identificado como descartável.

## Verificações realizadas nesta entrega

```sh
cd backend
../.venv/bin/python tools/ci.py
../.venv/bin/python -m pytest -q tests/test_vault_rag.py tests/test_assistente_ia_consultas.py
cd ../frontend
npm run build
npm run lint
```

A suíte isolada usa MariaDB descartável. `npm run lint` mantém avisos já existentes no projeto. A inferência real com Ollama pode depender dos limites de memória da máquina; nenhuma operação baixa modelos automaticamente.

## Limitações conhecidas

- O sistema ainda bloqueia o assistente fora de `development`/`testing`; a candidata não está homologada para produção.
- A resposta técnica é gerada por modelo local e pode falhar em formato estruturado; consulte as fontes documentais e o manual do fabricante.
- Não existem datas de conclusão de OS ou histórico de utilização da frota, então não há indicador de conclusão no prazo nem taxa real de utilização.
- A confirmação de agenda persiste no MariaDB, mas a interface/navegador real e o fluxo completo com sessão acadêmica devem ser homologados no notebook do operador.
