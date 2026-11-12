# Ambiente persistente AgroFrota

## Instalação isolada

`iniciar_agrofrota.py` permanece exclusivamente descartável. O ambiente durável é uma stack separada em `deploy/persistent/compose.yaml`, com projeto, rede e volume nomeados de forma exclusiva. Não se conecta ao MariaDB do sistema.

O primeiro `up` constrói imagens e inicia MariaDB 11.4 no volume Docker nomeado `agrofrota-infra-01-mariadb`; nenhum port mapping do MariaDB existe. O banco central é `agrofrota_central`, tenant é `agrofrota_tenant`. O script de init concede ao usuário SQL dedicado acesso somente a esses dois schemas. O frontend publica somente `127.0.0.1:18088`; Flask/Gunicorn não publica porta do host.

## Migrações e provisionamento

O serviço one-shot `migrate` aplica `alembic-central.ini` e `alembic-tenant.ini` usando a conta runtime dedicada. O backend inicia somente depois da conclusão bem-sucedida das migrações e do healthcheck de MariaDB. O script `backend/tools/provision_persistent_demo.py` cria o tenant, as permissões e perfis já definidos pelo produto, sete usuários e registros demonstrativos fictícios. Ele não expande permissões de perfis existentes e interrompe o processo se encontrar tenants ou usuários anteriores. Não o execute numa base populada.

A stack define `AGROFROTA_ENABLE_ASSISTANT=1` explicitamente para ativar a Central de Operações já existente em produção. Essa flag não ativa rotas de desenvolvimento. Consultas operacionais e a lógica transacional permanecem no backend. Se a consulta depender do Ollama e ele não estiver disponível dentro da stack, a API devolve erro explícito HTTP 503; ela não afirma sucesso nem confirma operação. A instalação não inicia Ollama, não transfere inferência ao servidor residencial e não permite que o modelo grave sem confirmação explícita.

O arquivo `demo_credentials.json` permite recuperação das senhas de demonstração e é privado, modo `0600`, fora do Git. A configuração contém senhas aleatórias de banco e chaves JWT/Flask independentes. O container backend executa com o mesmo UID/GID do operador para poder ler segredos montados como arquivos sem abrir as permissões locais.

## Persistência, parada e logs

`stop` para containers sem remover o volume. Reinicializar o host não apaga o volume, desde que Docker mantenha seu diretório de dados. Use `restart` para reinício dos serviços. Não use `docker compose down -v` no projeto ativo.

Logs: `python3 deploy/persistent/agrofrota.py logs`; status: `... status`. O container não deve imprimir segredos. Não inclua arquivos da pasta de estado nem dumps em commits/screenshots.

## Backup e restauração isolada

Crie destino novo, em disco com espaço suficiente e com acesso restrito:

```bash
python3 deploy/persistent/agrofrota.py backup --output /caminho/privado/agrofrota-AAAA-MM-DD.sql
python3 deploy/persistent/agrofrota.py restore-test --backup /caminho/privado/agrofrota-AAAA-MM-DD.sql
```

Backup usa `mariadb-dump --single-transaction` para os dois schemas, modo `0600`, sem imprimir o conteúdo. `restore-test` cria projeto e volume aleatórios próprios, importa o dump, valida schemas/tabela Alembic e remove somente esse projeto temporário. O ensaio real não foi possível nesta execução; consulte o resultado e a limitação em `docs/REMOTE_ACCESS_VALIDATION.md` antes de tratar backups como comprovados.

## Unidade de usuário

`deploy/persistent/systemd_user.py install` prepara arquivo apenas em `~/.config/systemd/user/`, recusando substituir arquivo sem marcador AgroFrota. Depois de revisar e testar manualmente:

```bash
systemctl --user enable --now agrofrota-infra-01.service
systemctl --user status agrofrota-infra-01.service
```

Para remoção, `python3 deploy/persistent/systemd_user.py remove`. Esse caminho não apaga volume, dados, credenciais nem configuração Tailscale. Não foi instalado/ativado durante a missão.

## Limites do host atual

O host identificado foi Linux Mint 22.1, `gabriel-Nitro-ANV15-51`, com 7,5 GiB RAM total, cerca de 2,3 GiB disponíveis e apenas 1,3 GiB livres no filesystem raiz na medição. Docker está ativo, mas o usuário não tinha permissão de acesso ao socket; MariaDB e outros serviços do operador já estavam ativos. Imagens, migrações, criação de usuários, backups e testes de restore ficaram pendentes para evitar colisão, consumo de disco ou alteração de instalação pessoal.
