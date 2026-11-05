# Testes locais descartáveis

Requisitos: Python com dependências de `backend/requirements.txt`, binários `mariadbd` e `mariadb-install-db`, e permissão para processos e sockets locais. O bootstrap cria diretório privado em `/tmp`, escolhe portas loopback livres e gera credenciais aleatórias locais. Não usar um banco já existente. Os dados e logs ficam nesse diretório; não os publique.

```bash
cd backend
../.venv/bin/python tools/ambiente_descartavel.py start
# Substitua DIRETORIO pelo caminho retornado pelo comando anterior.
../.venv/bin/python tools/ambiente_descartavel.py test DIRETORIO
../.venv/bin/python tools/ambiente_descartavel.py stop DIRETORIO
```

`start` aplica as migrações iniciais e gera duas empresas sintéticas com usuários legados de teste. `test` verifica marcador, datadir, tenants e processos antes de executar a suíte selecionada. Para escolher arquivos, acrescente seus caminhos após DIRETORIO. `stop` verifica a mesma identidade e encerra somente os processos identificados antes de remover o diretório. Se a preparação falhar, recursos parciais são preservados para inspeção; o comando `stop` exige um ambiente completo. A suíte inclui a política administrativa e a concorrência do último administrador; ainda não cobre a matriz de sete perfis nem todos os gates da etapa 1. Consulte [a política administrativa](POLITICA_ADMINISTRATIVA.md).
