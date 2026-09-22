#!/bin/bash

set -e

echo "=========================================="
echo "  CRIANDO ESTRUTURA DO PROJETO"
echo "=========================================="

# Diretório raiz do projeto
PROJECT_DIR="$(pwd)"

echo ""
echo "Projeto: $PROJECT_DIR"
echo ""

# ============================================================
# DIRETÓRIOS PRINCIPAIS
# ============================================================

mkdir -p backend

# Database
mkdir -p backend/database

# Models
mkdir -p backend/models

# Schemas
mkdir -p backend/schemas

# Routes
mkdir -p backend/routes

# Services
mkdir -p backend/services

# Middleware
mkdir -p backend/middleware

# Utils
mkdir -p backend/utils

# Migrations
mkdir -p backend/migrations

# Tests
mkdir -p backend/tests

# ============================================================
# ARQUIVOS PRINCIPAIS
# ============================================================

touch backend/app.py
touch backend/config.py
touch backend/extensions.py

# ============================================================
# DATABASE
# ============================================================

touch backend/database/__init__.py
touch backend/database/central.py
touch backend/database/tenant.py

# ============================================================
# MODELS
# ============================================================

touch backend/models/__init__.py

touch backend/models/usuario.py
touch backend/models/cargo.py
touch backend/models/perfil.py
touch backend/models/permissao.py

touch backend/models/maquina.py
touch backend/models/equipamento.py
touch backend/models/localizacao.py

touch backend/models/tipo_servico.py
touch backend/models/ordem_servico.py
touch backend/models/agendamento.py

touch backend/models/manutencao.py
touch backend/models/indisponibilidade.py

touch backend/models/auditoria.py

# ============================================================
# SCHEMAS
# ============================================================

touch backend/schemas/__init__.py

touch backend/schemas/auth.py
touch backend/schemas/usuario.py
touch backend/schemas/cargo.py
touch backend/schemas/perfil.py

touch backend/schemas/maquina.py
touch backend/schemas/equipamento.py

touch backend/schemas/ordem_servico.py
touch backend/schemas/agendamento.py

touch backend/schemas/manutencao.py
touch backend/schemas/indisponibilidade.py

# ============================================================
# ROUTES
# ============================================================

touch backend/routes/__init__.py

touch backend/routes/auth.py
touch backend/routes/usuarios.py
touch backend/routes/cargos.py
touch backend/routes/perfis.py

touch backend/routes/maquinas.py
touch backend/routes/equipamentos.py

touch backend/routes/ordens_servico.py
touch backend/routes/calendario.py

touch backend/routes/manutencoes.py
touch backend/routes/indisponibilidades.py

touch backend/routes/dashboard.py

# ============================================================
# SERVICES
# ============================================================

touch backend/services/__init__.py

touch backend/services/auth_service.py
touch backend/services/usuario_service.py
touch backend/services/cargo_service.py
touch backend/services/perfil_service.py

touch backend/services/maquina_service.py
touch backend/services/equipamento_service.py

touch backend/services/ordem_servico_service.py
touch backend/services/calendario_service.py

touch backend/services/manutencao_service.py
touch backend/services/indisponibilidade_service.py

touch backend/services/dashboard_service.py

# ============================================================
# MIDDLEWARE
# ============================================================

touch backend/middleware/__init__.py

touch backend/middleware/auth.py
touch backend/middleware/tenant.py
touch backend/middleware/permissions.py

# ============================================================
# UTILS
# ============================================================

touch backend/utils/__init__.py

touch backend/utils/security.py
touch backend/utils/pagination.py
touch backend/utils/responses.py
touch backend/utils/exceptions.py

# ============================================================
# TESTES
# ============================================================

touch backend/tests/__init__.py

touch backend/tests/test_auth.py
touch backend/tests/test_tenant.py
touch backend/tests/test_maquinas.py
touch backend/tests/test_equipamentos.py
touch backend/tests/test_ordens_servico.py

# ============================================================
# ARQUIVOS DE CONFIGURAÇÃO
# ============================================================

touch backend/.env
touch backend/.env.example

touch backend/requirements.txt

# ============================================================
# GITIGNORE
# ============================================================

touch .gitignore

# ============================================================
# README
# ============================================================

touch README.md

# ============================================================
# FINALIZAÇÃO
# ============================================================

echo ""
echo "=========================================="
echo "  ESTRUTURA CRIADA COM SUCESSO"
echo "=========================================="
echo ""

echo "Backend:"
echo ""

find backend -type f | sort

echo ""
echo "=========================================="
echo "  PROJETO PRONTO PARA A PRÓXIMA ETAPA"
echo "=========================================="
