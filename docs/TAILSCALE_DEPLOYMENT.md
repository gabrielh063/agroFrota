# Implantação privada por Tailscale

## Estado desta missão

Implementação reproduzível preparada em `deploy/persistent/`. A ativação no host não foi feita: o disco raiz tinha aproximadamente 1,3 GB livres e o usuário atual não conseguiu acessar o socket Docker. O MariaDB do operador já está ativo em `127.0.0.1:3306` e não foi utilizado. Tailscale 1.104.5 estava conectado, MagicDNS aparecia disponível e `tailscale serve status` não mostrava endpoints próprios. Nenhum endereço do AgroFrota foi anunciado nesta execução.

## Arquitetura

```text
cliente conectado à tailnet
  → Tailscale Serve HTTPS (443, tailnet privada)
  → 127.0.0.1:18088 (Nginx: estáticos Vite e proxy /api)
  → rede interna Compose
      → Gunicorn/Flask (sem porta publicada)
      → MariaDB 11.4 (sem porta publicada; volume nomeado)
```

O login e os tokens do AgroFrota continuam obrigatórios. O frontend compila com API relativa (`/api`) e tenant `agrofrota_tenant`; o navegador não chama `localhost:5001`. Não existe configuração de Funnel, NAT, regra de firewall ou publicação de banco.

A flag explícita `AGROFROTA_ENABLE_ASSISTANT=1` ativa a Central existente na stack persistente; ela não habilita as rotas `/api/dev/*`. A ausência do Ollama faz consultas dependentes do modelo retornarem erro explícito, sem sucesso falso ou gravação operacional.

## Dependências e configuração

- Linux com Docker Engine e plugin Compose v2 funcionais para o usuário que executará a unidade.
- Python 3 para o CLI local, `tailscale` conectado, HTTPS/MagicDNS habilitados na tailnet e ACLs que autorizem os dispositivos desejados.
- O estado local padrão fica em `~/.config/agrofrota-infra-01`, modo `0700`; arquivos de segredo ficam modo `0600`. Pode-se passar `--state-dir` para outro diretório privado.
- A origem precisa ser o domínio MagicDNS real, em HTTPS, sem caminho. Não use exemplo ou endereço inventado.
- A porta HTTP interna ao host é `127.0.0.1:18088`. Verifique conflito antes de iniciar. Porta 3306 não é publicada; Gunicorn 8000 só existe na rede Compose.
- O volume é `agrofrota-infra-01-mariadb`; rede `agrofrota-infra-01-private`.

O arquivo oficial MariaDB aceita sufixos `*_FILE` para senhas iniciais; essas variáveis só inicializam um datadir vazio, mantendo a distinção entre volume recém-criado e banco existente ([documentação oficial](https://mariadb.com/docs/server/server-management/automated-mariadb-deployment-and-administration/docker-and-mariadb/mariadb-server-docker-official-image-environment-variables)). O Compose local monta secrets por arquivo; por isso o backend usa UID/GID numéricos do operador para ler os arquivos `0600`, sem torná-los globais ([Docker Compose secrets](https://docs.docker.com/compose/how-tos/use-secrets/)).

## Instalação e ativação

No checkout atualizado da branch de infraestrutura:

```bash
python3 deploy/persistent/agrofrota.py setup --origin https://<magicdns-real>
python3 deploy/persistent/agrofrota.py up
python3 deploy/persistent/agrofrota.py provision
curl --fail http://127.0.0.1:18088/api/health
```

`setup` gera segredos aleatórios, cria as sete senhas e as grava localmente com permissões privadas. Exibe as credenciais uma vez no terminal do operador. Para recuperação local, `credentials` as exibe novamente; não compartilhe a saída.

Antes de Serve, confirme de novo o estado atual e que não foi criado endpoint por outro serviço:

```bash
tailscale status
tailscale serve status
tailscale serve get-config --all
curl --fail http://127.0.0.1:18088/api/health
```

Se o estado Serve continuar vazio e o healthcheck responder, ativar apenas a rota desta aplicação:

```bash
sudo tailscale serve --bg --https=443 http://127.0.0.1:18088
tailscale serve status
```

Serve fornece HTTPS com certificado provisionado pelo Tailscale e é privado à tailnet; não utilizar `tailscale funnel`. A configuração `--bg` persiste depois de reinicialização. Antes de ativar, confirme que MagicDNS e certificados HTTPS estão habilitados na tailnet; isso pode depender de um administrador. Consulte a [referência atual do CLI Serve](https://tailscale.com/docs/reference/tailscale-cli/serve) e o guia [Serve versus Funnel](https://tailscale.com/docs/features/tailscale-funnel).

Se houver interrupção, retire somente a rota que este procedimento criou:

```bash
sudo tailscale serve --bg --https=443 http://127.0.0.1:18088 off
```

Não use `tailscale serve reset`, pois apagaria configuração não relacionada.

## Acesso pelo iPhone

1. Instale/abra o cliente Tailscale e autentique na mesma tailnet autorizada.
2. Confirme que a conexão está ativa.
3. Abra no Safari a URL HTTPS exata mostrada por `tailscale serve status` (MagicDNS do host, sem inventar sufixo).
4. Entre com a conta AgroFrota; acesso à tailnet não autentica o usuário do produto.
5. Se o teste for feito em dados móveis, desligue Wi-Fi e confirme que o iPhone permanece conectado à tailnet.

Esse teste externo não foi executado nesta missão. A classificação de implantação remota permanece pendente até ocorrer no iPhone ou em outro cliente Tailscale por uma rede externa.

## Operação e diagnósticos

```bash
python3 deploy/persistent/agrofrota.py status
python3 deploy/persistent/agrofrota.py logs
python3 deploy/persistent/agrofrota.py restart
python3 deploy/persistent/agrofrota.py stop
python3 deploy/persistent/agrofrota.py up
```

Os logs são emitidos pelo Compose; tokens, senhas e corpo de autenticação não devem ser registrados. A API mantém mensagens genéricas de erro. Verifique `GET /api/health`, `docker compose ps`, DNS MagicDNS, certificado e ACL da tailnet.

Para inicialização após reboot, o arquivo `systemd_user.py install` prepara apenas uma unidade do usuário; a ativação é explícita com `systemctl --user enable --now agrofrota-infra-01.service`. Requer que a sessão de usuário/systemd esteja habilitada no boot e que o Docker seja acessível por esse usuário. `remove` apaga apenas unidade identificada por marcador e preserva volume e segredos. Nenhuma unidade foi instalada ou ativada nesta execução.

## Atualização e rollback

Revise o diff e a CI antes de atualizar o checkout. Execute `up` para rebuild/recreate da aplicação; o volume permanece fora do ciclo de vida de containers. Migrações Alembic são aplicadas antes do backend. Faça backup antes de qualquer atualização que inclua migração. Em caso de regressão, volte o checkout à revisão anterior validada e rode `up`; restaure backup apenas em uma instância isolada, nunca sobre a base ativa durante o ensaio.

Limitação desta homologação: sem acesso ao Docker e sem espaço suficiente para imagens e duas instâncias de MariaDB, não foram executados build/boot de containers, Serve, certificado HTTPS, login remoto, restauração ou reinicialização persistente. Ver `docs/REMOTE_ACCESS_VALIDATION.md`.
