# Ambiente persistente AgroFrota

## Instalação isolada

`iniciar_agrofrota.py` permanece exclusivamente descartável. O ambiente durável é uma stack separada em `deploy/persistent/compose.yaml`, com projeto, rede e volume nomeados de forma exclusiva. Não se conecta ao MariaDB do sistema.

O primeiro `up` constrói imagens e inicia MariaDB 11.4 no volume Docker nomeado `agrofrota-infra-01-mariadb`; nenhum port mapping do MariaDB existe. O banco central é `agrofrota_central`, tenant é `agrofrota_tenant`. O script de init concede ao usuário SQL dedicado acesso somente a esses dois schemas. O frontend publica somente `127.0.0.1:18088`; Flask/Gunicorn não publica porta do host. Nginx pertence às bridges `private` e `host_proxy`; banco e Gunicorn pertencem somente à bridge interna `private`.

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

Backup usa `mariadb-dump --single-transaction` para os dois schemas, modo `0600`, sem imprimir o conteúdo. Em 12/11/2026, o backup e a restauração isolada foram executados. O dump ficou no estado privado local, fora do repositório. A restauração usou projeto, rede e volume aleatórios, aguardou healthcheck e validou os dois schemas e a versão Alembic; o CLI removeu somente esses recursos temporários após a verificação. Nunca restaure sobre `agrofrota-infra-01-mariadb` ativo.

## Unidade de usuário

`deploy/persistent/systemd_user.py install` prepara arquivo apenas em `~/.config/systemd/user/`, recusando substituir arquivo sem marcador AgroFrota. Depois de revisar e testar manualmente:

```bash
systemctl --user enable --now agrofrota-infra-01.service
systemctl --user status agrofrota-infra-01.service
```

Para remoção, `python3 deploy/persistent/systemd_user.py remove`. Esse caminho não apaga volume, dados, credenciais nem configuração Tailscale. A unidade não foi ativada: o usuário do host não acessa o socket sem sudo e a unidade usa `NoNewPrivileges=true`, portanto não poderia chamar sudo.

## Estado do host e evidência de persistência

Em 12/11/2026, o Linux Mint 22.1 `gabriel-Nitro-ANV15-51` tinha 23 GB livres (margem mínima pretendida: 8–10 GB), 7,5 GiB de RAM e Docker Engine 29.8.2/Compose 5.6.0. O MariaDB do host em `127.0.0.1:3306` não foi usado. O usuário não pertence ao grupo `docker`; o socket é `0660` e o CLI foi executado com `sudo -n` por um wrapper temporário, mantendo o inicializador e os segredos com UID do operador. Nenhum cache, imagem, volume ou arquivo do operador foi removido.

A instância persistente está em `/var/lib/docker/volumes/agrofrota-infra-01-mariadb/_data`, montada pelo volume nomeado exclusivo `agrofrota-infra-01-mariadb`. O estado privado de credenciais/configuração está em `~/.config/agrofrota-infra-01` (diretório `0700`, arquivos `0600`). O seed criou sete usuários, uma máquina e duas OS demonstrativas. Uma máquina/OS adicional foi criada pelo endpoint HTTPS; após `stop` e novo `up`, a leitura SQL confirmou que ambos os registros e as sete contas continuavam presentes. Ver `docs/evidence/infra-02/AGRO-INFRA-02-results.md`.

## Inicialização após reboot

O Docker system service está habilitado e ativo no host. Os três serviços duráveis declaram `restart: unless-stopped`, mas a prova AGRO-INFRA-03 não reiniciou o sistema operacional. Como `docker compose stop` registra os containers como parados, as políticas `unless-stopped` podem manter essa parada depois de um reboot; não contar apenas com elas como prova de inicialização automática.

`deploy/persistent/systemd_user.py` continua sendo uma alternativa de usuário, mas não serve neste host: o UID do operador não acessa o socket Docker e a unidade tem `NoNewPrivileges=true`. Não adicionar o operador ao grupo `docker` nem criar sudoers genérico para Compose.

Foi preparada a unidade systemd de sistema `deploy/persistent/agrofrota-infra-01.service` e os auxiliares `agrofrota-infra-01-start`/`agrofrota-infra-01-stop`. A unidade invoca somente cópias root-owned desses scripts; eles validam a label do projeto dos três containers nomeados, iniciam MariaDB e esperam seu healthcheck antes do backend/frontend, aguardam o healthcheck HTTP e param em ordem inversa. Não executam Compose, build, migração, leitura de secrets ou remoção de volumes. A configuração já estática e revisável ainda não foi instalada em `/etc` nem habilitada.

A ativação cria três arquivos root-owned em `/usr/local/libexec` e uma unidade em `/etc/systemd/system`, executa `systemctl daemon-reload` e habilita a unidade no boot. Isso concede à unidade root permissão para iniciar/parar apenas os containers preexistentes verificados pelo nome e pela label de projeto via socket Docker. O passo é persistente e depende de autorização específica do operador. O template e o procedimento reversível estão em `docs/TAILSCALE_DEPLOYMENT.md`.
