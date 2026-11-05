# AgroFrota

**Estado atual: PARCIAL, sem homologação privada.** A candidata de integração,
evidências e pendências estão em [docs/MISSAO_FINAL.md](docs/MISSAO_FINAL.md).
O checklist abaixo é histórico e não comprova os fluxos completos.

Sistema SaaS de gestão para propriedades rurais, com foco no controle de máquinas, equipamentos, manutenção, ordens de serviço, indisponibilidade e gestão operacional.

O projeto está sendo desenvolvido de forma modular, priorizando primeiro a estrutura do backend e a validação das regras de negócio antes da construção do frontend.

---

## Status do projeto

### Backend

- [x] Estrutura inicial do projeto
- [x] Ambiente virtual Python
- [x] Configuração por `.env`
- [x] Conexão com MariaDB
- [x] Banco central
- [x] Arquitetura multi-tenant
- [x] Banco separado por empresa
- [x] Models SQLAlchemy
- [x] Services
- [x] Schemas Pydantic
- [x] JWT
- [x] Middleware de autenticação
- [x] Middleware de resolução de tenant
- [x] CORS
- [x] Cadastro de máquinas
- [x] Cadastro de equipamentos/implementos
- [x] Validações básicas
- [x] Exclusão lógica
- [x] Testes via `curl`

### Frontend

- [ ] Estrutura React/Vite
- [ ] Login
- [ ] Dashboard
- [ ] Tela de máquinas
- [ ] Tela de equipamentos
- [ ] Ordens de serviço
- [ ] Calendário
- [ ] Manutenção
- [ ] Indisponibilidade

---

# 1. Objetivo

O AgroFrota tem como objetivo centralizar a gestão do parque de máquinas e equipamentos de uma propriedade rural.

A ideia é permitir o acompanhamento de:

- máquinas;
- implementos e equipamentos;
- manutenção;
- ordens de serviço;
- serviços programados;
- indisponibilidade;
- capacidade instalada;
- usuários;
- cargos;
- perfis;
- permissões.

Posteriormente poderão ser adicionados recursos como telemetria e funcionamento offline.

---

# 2. Tecnologias

## Backend

- Python
- Flask
- SQLAlchemy
- PyMySQL
- MariaDB
- Pydantic
- Flask-JWT-Extended
- Flask-CORS
- Flask-Migrate
- Alembic
- pytest

## Frontend

Planejado:

- React
- Vite
- Bootstrap

---

# 3. Arquitetura Multi-Tenant

O sistema utiliza uma arquitetura de **banco de dados por tenant**.

Existe um banco central:

```text
fazenda_saas
