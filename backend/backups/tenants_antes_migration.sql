/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.14-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: tenant_000001
-- ------------------------------------------------------
-- Server version	10.11.14-MariaDB-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `tenant_000001`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `tenant_000001` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

USE `tenant_000001`;

--
-- Table structure for table `cargos`
--

DROP TABLE IF EXISTS `cargos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cargos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cargos`
--

LOCK TABLES `cargos` WRITE;
/*!40000 ALTER TABLE `cargos` DISABLE KEYS */;
INSERT INTO `cargos` VALUES
(1,'Mecânico','Responsável pela manutenção preventiva e corretiva.',1);
/*!40000 ALTER TABLE `cargos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfil_permissoes`
--

DROP TABLE IF EXISTS `perfil_permissoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `perfil_permissoes` (
  `perfil_id` int(11) NOT NULL,
  `permissao_id` int(11) NOT NULL,
  PRIMARY KEY (`perfil_id`,`permissao_id`),
  KEY `permissao_id` (`permissao_id`),
  CONSTRAINT `perfil_permissoes_ibfk_1` FOREIGN KEY (`perfil_id`) REFERENCES `perfis` (`id`),
  CONSTRAINT `perfil_permissoes_ibfk_2` FOREIGN KEY (`permissao_id`) REFERENCES `permissoes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfil_permissoes`
--

LOCK TABLES `perfil_permissoes` WRITE;
/*!40000 ALTER TABLE `perfil_permissoes` DISABLE KEYS */;
/*!40000 ALTER TABLE `perfil_permissoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfis`
--

DROP TABLE IF EXISTS `perfis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `perfis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfis`
--

LOCK TABLES `perfis` WRITE;
/*!40000 ALTER TABLE `perfis` DISABLE KEYS */;
/*!40000 ALTER TABLE `perfis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissoes`
--

DROP TABLE IF EXISTS `permissoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissoes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissoes`
--

LOCK TABLES `permissoes` WRITE;
/*!40000 ALTER TABLE `permissoes` DISABLE KEYS */;
/*!40000 ALTER TABLE `permissoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(150) NOT NULL,
  `username` varchar(80) NOT NULL,
  `email` varchar(150) DEFAULT NULL,
  `senha_hash` varchar(255) NOT NULL,
  `cargo_id` int(11) DEFAULT NULL,
  `perfil_id` int(11) NOT NULL,
  `ativo` tinyint(1) NOT NULL,
  `ultimo_login` datetime DEFAULT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_usuarios_username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `cargo_id` (`cargo_id`),
  KEY `perfil_id` (`perfil_id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`cargo_id`) REFERENCES `cargos` (`id`),
  CONSTRAINT `usuarios_ibfk_2` FOREIGN KEY (`perfil_id`) REFERENCES `perfis` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Current Database: `tenant_000002`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `tenant_000002` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

USE `tenant_000002`;

--
-- Table structure for table `cargos`
--

DROP TABLE IF EXISTS `cargos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cargos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cargos`
--

LOCK TABLES `cargos` WRITE;
/*!40000 ALTER TABLE `cargos` DISABLE KEYS */;
INSERT INTO `cargos` VALUES
(1,'Gerente','Responsável pela gestão da fazenda.',1),
(2,'Mecânico','Responsável pela manutenção preventiva e corretiva.',1);
/*!40000 ALTER TABLE `cargos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipamentos`
--

DROP TABLE IF EXISTS `equipamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipamentos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `identificacao` varchar(100) NOT NULL,
  `nome` varchar(150) NOT NULL,
  `tipo` varchar(100) NOT NULL,
  `fabricante` varchar(100) DEFAULT NULL,
  `modelo` varchar(150) DEFAULT NULL,
  `ano` int(11) DEFAULT NULL,
  `localizacao` varchar(150) DEFAULT NULL,
  `status` varchar(30) NOT NULL,
  `ativo` tinyint(1) NOT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_equipamentos_identificacao` (`identificacao`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipamentos`
--

LOCK TABLES `equipamentos` WRITE;
/*!40000 ALTER TABLE `equipamentos` DISABLE KEYS */;
INSERT INTO `equipamentos` VALUES
(1,'IMP-001','Grade Niveladora','GRADE','Baldan','GNV 36',2023,'Pátio Norte','EM_USO',1,'2026-09-22 20:20:16','2026-09-22 20:20:16'),
(2,'IMP-002','Plantadeira','PLANTADEIRA','John Deere','DB74',2024,'Pátio Sul','MANUTENCAO',1,'2026-09-22 20:22:45','2026-09-22 22:23:42');
/*!40000 ALTER TABLE `equipamentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maquinas`
--

DROP TABLE IF EXISTS `maquinas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `maquinas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `identificacao` varchar(100) NOT NULL,
  `modelo` varchar(150) NOT NULL,
  `fabricante` varchar(100) NOT NULL,
  `ano` int(11) DEFAULT NULL,
  `localizacao` varchar(150) DEFAULT NULL,
  `status` varchar(30) NOT NULL,
  `controla_telemetria` tinyint(1) NOT NULL,
  `ativo` tinyint(1) NOT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_maquinas_identificacao` (`identificacao`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maquinas`
--

LOCK TABLES `maquinas` WRITE;
/*!40000 ALTER TABLE `maquinas` DISABLE KEYS */;
INSERT INTO `maquinas` VALUES
(1,'TR-001','6110J','John Deere',2022,'Pátio Sul','PARADA',0,1,'2026-09-22 19:27:15','2026-09-22 19:30:57'),
(2,'TR-002','6150J','John Deere',2023,'Pátio Sul','MANUTENCAO',0,1,'2026-09-22 19:53:57','2026-09-22 20:13:24');
/*!40000 ALTER TABLE `maquinas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfil_permissoes`
--

DROP TABLE IF EXISTS `perfil_permissoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `perfil_permissoes` (
  `perfil_id` int(11) NOT NULL,
  `permissao_id` int(11) NOT NULL,
  PRIMARY KEY (`perfil_id`,`permissao_id`),
  KEY `permissao_id` (`permissao_id`),
  CONSTRAINT `perfil_permissoes_ibfk_1` FOREIGN KEY (`perfil_id`) REFERENCES `perfis` (`id`),
  CONSTRAINT `perfil_permissoes_ibfk_2` FOREIGN KEY (`permissao_id`) REFERENCES `permissoes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfil_permissoes`
--

LOCK TABLES `perfil_permissoes` WRITE;
/*!40000 ALTER TABLE `perfil_permissoes` DISABLE KEYS */;
INSERT INTO `perfil_permissoes` VALUES
(1,1),
(1,2),
(1,3),
(1,4),
(1,5),
(1,6),
(1,7),
(1,8),
(1,9),
(1,10),
(1,11),
(1,12),
(1,13),
(1,14),
(1,15),
(1,16),
(1,17),
(1,18),
(1,19),
(1,20),
(1,21),
(1,22),
(1,23),
(1,24),
(1,25),
(1,26),
(1,27),
(1,28),
(1,29),
(1,30),
(1,31),
(1,32),
(2,2),
(2,4),
(2,15),
(2,16),
(2,19),
(2,20),
(2,22),
(2,24),
(2,25),
(2,26),
(2,27),
(2,28),
(2,29),
(2,30),
(2,31),
(2,32),
(3,2),
(3,3),
(3,15),
(3,19),
(3,26),
(3,29),
(3,30);
/*!40000 ALTER TABLE `perfil_permissoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfis`
--

DROP TABLE IF EXISTS `perfis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `perfis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfis`
--

LOCK TABLES `perfis` WRITE;
/*!40000 ALTER TABLE `perfis` DISABLE KEYS */;
INSERT INTO `perfis` VALUES
(1,'GERENTE','Perfil destinado às operações de manutenção, serviços e ordens de serviço.',1),
(2,'MANUTENCAO','Perfil destinado às operações de manutenção, serviços e ordens de serviço.',1),
(3,'OPERADOR','Perfil padrão de operador.',1);
/*!40000 ALTER TABLE `perfis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissoes`
--

DROP TABLE IF EXISTS `permissoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissoes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissoes`
--

LOCK TABLES `permissoes` WRITE;
/*!40000 ALTER TABLE `permissoes` DISABLE KEYS */;
INSERT INTO `permissoes` VALUES
(1,'USUARIO_CRIAR','Permite criar usuários.'),
(2,'OS.CRIAR','Permite criar novas ordens de serviço.'),
(3,'OS.VISUALIZAR','Permite consultar e visualizar ordens de serviço.'),
(4,'USUARIO_VISUALIZAR','Permite visualizar usuários.'),
(5,'USUARIO_EDITAR','Permite editar usuários.'),
(6,'USUARIO_DESATIVAR','Permite ativar ou desativar usuários.'),
(7,'CARGO_CRIAR','Permite criar cargos.'),
(8,'CARGO_VISUALIZAR','Permite visualizar cargos.'),
(9,'CARGO_EDITAR','Permite editar cargos.'),
(10,'PERFIL_CRIAR','Permite criar perfis.'),
(11,'PERFIL_VISUALIZAR','Permite visualizar perfis.'),
(12,'PERFIL_EDITAR','Permite editar perfis.'),
(13,'PERFIL_PERMISSAO_GERENCIAR','Permite associar e remover permissões de perfis.'),
(14,'MAQUINA_CRIAR','Permite cadastrar máquinas.'),
(15,'MAQUINA_VISUALIZAR','Permite visualizar máquinas.'),
(16,'MAQUINA_EDITAR','Permite editar máquinas.'),
(17,'MAQUINA_DESATIVAR','Permite ativar ou desativar máquinas.'),
(18,'EQUIPAMENTO_CRIAR','Permite cadastrar equipamentos.'),
(19,'EQUIPAMENTO_VISUALIZAR','Permite visualizar equipamentos.'),
(20,'EQUIPAMENTO_EDITAR','Permite editar equipamentos.'),
(21,'EQUIPAMENTO_DESATIVAR','Permite ativar ou desativar equipamentos.'),
(22,'OS.EDITAR','Permite editar ordens de serviço.'),
(23,'OS.CANCELAR','Permite cancelar ordens de serviço.'),
(24,'OS.CONCLUIR','Permite concluir ordens de serviço.'),
(25,'MANUTENCAO.CRIAR','Permite registrar manutenções.'),
(26,'MANUTENCAO.VISUALIZAR','Permite visualizar manutenções.'),
(27,'MANUTENCAO.EDITAR','Permite editar registros de manutenção.'),
(28,'MANUTENCAO.CONCLUIR','Permite concluir manutenções.'),
(29,'INDISPONIBILIDADE.CRIAR','Permite registrar indisponibilidades.'),
(30,'INDISPONIBILIDADE.VISUALIZAR','Permite visualizar indisponibilidades.'),
(31,'INDISPONIBILIDADE.EDITAR','Permite editar indisponibilidades.'),
(32,'DASHBOARD.VISUALIZAR','Permite visualizar o dashboard.');
/*!40000 ALTER TABLE `permissoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(150) NOT NULL,
  `username` varchar(80) NOT NULL,
  `email` varchar(150) DEFAULT NULL,
  `senha_hash` varchar(255) NOT NULL,
  `cargo_id` int(11) DEFAULT NULL,
  `perfil_id` int(11) NOT NULL,
  `ativo` tinyint(1) NOT NULL,
  `ultimo_login` datetime DEFAULT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_usuarios_username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `cargo_id` (`cargo_id`),
  KEY `perfil_id` (`perfil_id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`cargo_id`) REFERENCES `cargos` (`id`),
  CONSTRAINT `usuarios_ibfk_2` FOREIGN KEY (`perfil_id`) REFERENCES `perfis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES
(1,'Administrador','admin','admin@fazendateste.com','scrypt:32768:8:1$oVxTYYc0B5vg0u0R$4d6646eb5724f06f8071155419b33f53a3a84598115742e267cbc0aba6ce2beb9a92c897e989b1d655a29dc025e057489ee5345a6f14897155fd49102ed6f2b9',1,1,1,NULL,'2026-09-22 18:31:58','2026-09-22 18:31:58');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Current Database: `tenant_000003`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `tenant_000003` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

USE `tenant_000003`;

--
-- Table structure for table `cargos`
--

DROP TABLE IF EXISTS `cargos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cargos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cargos`
--

LOCK TABLES `cargos` WRITE;
/*!40000 ALTER TABLE `cargos` DISABLE KEYS */;
INSERT INTO `cargos` VALUES
(1,'Gerente','Cargo padrão de gerente.',1);
/*!40000 ALTER TABLE `cargos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipamentos`
--

DROP TABLE IF EXISTS `equipamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipamentos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `identificacao` varchar(100) NOT NULL,
  `nome` varchar(150) NOT NULL,
  `tipo` varchar(100) NOT NULL,
  `fabricante` varchar(100) DEFAULT NULL,
  `modelo` varchar(150) DEFAULT NULL,
  `ano` int(11) DEFAULT NULL,
  `localizacao` varchar(150) DEFAULT NULL,
  `status` varchar(30) NOT NULL,
  `ativo` tinyint(1) NOT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_equipamentos_identificacao` (`identificacao`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipamentos`
--

LOCK TABLES `equipamentos` WRITE;
/*!40000 ALTER TABLE `equipamentos` DISABLE KEYS */;
/*!40000 ALTER TABLE `equipamentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maquinas`
--

DROP TABLE IF EXISTS `maquinas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `maquinas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `identificacao` varchar(100) NOT NULL,
  `modelo` varchar(150) NOT NULL,
  `fabricante` varchar(100) NOT NULL,
  `ano` int(11) DEFAULT NULL,
  `localizacao` varchar(150) DEFAULT NULL,
  `status` varchar(30) NOT NULL,
  `controla_telemetria` tinyint(1) NOT NULL,
  `ativo` tinyint(1) NOT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_maquinas_identificacao` (`identificacao`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maquinas`
--

LOCK TABLES `maquinas` WRITE;
/*!40000 ALTER TABLE `maquinas` DISABLE KEYS */;
/*!40000 ALTER TABLE `maquinas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfil_permissoes`
--

DROP TABLE IF EXISTS `perfil_permissoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `perfil_permissoes` (
  `perfil_id` int(11) NOT NULL,
  `permissao_id` int(11) NOT NULL,
  PRIMARY KEY (`perfil_id`,`permissao_id`),
  KEY `permissao_id` (`permissao_id`),
  CONSTRAINT `perfil_permissoes_ibfk_1` FOREIGN KEY (`perfil_id`) REFERENCES `perfis` (`id`),
  CONSTRAINT `perfil_permissoes_ibfk_2` FOREIGN KEY (`permissao_id`) REFERENCES `permissoes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfil_permissoes`
--

LOCK TABLES `perfil_permissoes` WRITE;
/*!40000 ALTER TABLE `perfil_permissoes` DISABLE KEYS */;
INSERT INTO `perfil_permissoes` VALUES
(1,1),
(1,2),
(1,3),
(1,4),
(1,5),
(1,6),
(1,7),
(1,8),
(1,9),
(1,10),
(1,11),
(1,12),
(1,13),
(1,14),
(1,15),
(1,16),
(1,17),
(1,18),
(1,19),
(1,20),
(1,21),
(1,22),
(1,23),
(1,24),
(1,25),
(1,26),
(1,27),
(1,28),
(1,29),
(1,30),
(1,31),
(1,32),
(2,2),
(2,13),
(2,14),
(2,17),
(2,18),
(2,20),
(2,21),
(2,22),
(2,24),
(2,25),
(2,26),
(2,27),
(2,28),
(2,29),
(2,30),
(2,31),
(2,32),
(3,13),
(3,17),
(3,20),
(3,21),
(3,26),
(3,29),
(3,30);
/*!40000 ALTER TABLE `perfil_permissoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfis`
--

DROP TABLE IF EXISTS `perfis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `perfis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfis`
--

LOCK TABLES `perfis` WRITE;
/*!40000 ALTER TABLE `perfis` DISABLE KEYS */;
INSERT INTO `perfis` VALUES
(1,'GERENTE','Perfil padrão de gerente.',1),
(2,'MANUTENCAO','Perfil padrão de manutencao.',1),
(3,'OPERADOR','Perfil padrão de operador.',1);
/*!40000 ALTER TABLE `perfis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissoes`
--

DROP TABLE IF EXISTS `permissoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissoes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissoes`
--

LOCK TABLES `permissoes` WRITE;
/*!40000 ALTER TABLE `permissoes` DISABLE KEYS */;
INSERT INTO `permissoes` VALUES
(1,'USUARIO_CRIAR','Permite criar usuários.'),
(2,'USUARIO_VISUALIZAR','Permite visualizar usuários.'),
(3,'USUARIO_EDITAR','Permite editar usuários.'),
(4,'USUARIO_DESATIVAR','Permite ativar ou desativar usuários.'),
(5,'CARGO_CRIAR','Permite criar cargos.'),
(6,'CARGO_VISUALIZAR','Permite visualizar cargos.'),
(7,'CARGO_EDITAR','Permite editar cargos.'),
(8,'PERFIL_CRIAR','Permite criar perfis.'),
(9,'PERFIL_VISUALIZAR','Permite visualizar perfis.'),
(10,'PERFIL_EDITAR','Permite editar perfis.'),
(11,'PERFIL_PERMISSAO_GERENCIAR','Permite associar e remover permissões de perfis.'),
(12,'MAQUINA_CRIAR','Permite cadastrar máquinas.'),
(13,'MAQUINA_VISUALIZAR','Permite visualizar máquinas.'),
(14,'MAQUINA_EDITAR','Permite editar máquinas.'),
(15,'MAQUINA_DESATIVAR','Permite ativar ou desativar máquinas.'),
(16,'EQUIPAMENTO_CRIAR','Permite cadastrar equipamentos.'),
(17,'EQUIPAMENTO_VISUALIZAR','Permite visualizar equipamentos.'),
(18,'EQUIPAMENTO_EDITAR','Permite editar equipamentos.'),
(19,'EQUIPAMENTO_DESATIVAR','Permite ativar ou desativar equipamentos.'),
(20,'OS.CRIAR','Permite criar novas ordens de serviço.'),
(21,'OS.VISUALIZAR','Permite visualizar ordens de serviço.'),
(22,'OS.EDITAR','Permite editar ordens de serviço.'),
(23,'OS.CANCELAR','Permite cancelar ordens de serviço.'),
(24,'OS.CONCLUIR','Permite concluir ordens de serviço.'),
(25,'MANUTENCAO.CRIAR','Permite registrar manutenções.'),
(26,'MANUTENCAO.VISUALIZAR','Permite visualizar manutenções.'),
(27,'MANUTENCAO.EDITAR','Permite editar registros de manutenção.'),
(28,'MANUTENCAO.CONCLUIR','Permite concluir manutenções.'),
(29,'INDISPONIBILIDADE.CRIAR','Permite registrar indisponibilidades.'),
(30,'INDISPONIBILIDADE.VISUALIZAR','Permite visualizar indisponibilidades.'),
(31,'INDISPONIBILIDADE.EDITAR','Permite editar indisponibilidades.'),
(32,'DASHBOARD.VISUALIZAR','Permite visualizar o dashboard.');
/*!40000 ALTER TABLE `permissoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(150) NOT NULL,
  `username` varchar(80) NOT NULL,
  `email` varchar(150) DEFAULT NULL,
  `senha_hash` varchar(255) NOT NULL,
  `cargo_id` int(11) DEFAULT NULL,
  `perfil_id` int(11) NOT NULL,
  `ativo` tinyint(1) NOT NULL,
  `ultimo_login` datetime DEFAULT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_usuarios_username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `cargo_id` (`cargo_id`),
  KEY `perfil_id` (`perfil_id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`cargo_id`) REFERENCES `cargos` (`id`),
  CONSTRAINT `usuarios_ibfk_2` FOREIGN KEY (`perfil_id`) REFERENCES `perfis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES
(1,'Administrador da Fazenda','admin','admin@fazendateste.com','scrypt:32768:8:1$ZkJW1JY2vCnb05tp$ce8793fb620ac0b523575c1112c8d15573b07618e3a1064a5f7d2f12e7da54b1e1e0696336ff7cb5826c6723fc21fdc00887bff4513029d6b2b0dc59b8401a60',1,1,1,NULL,'2026-09-23 18:39:37','2026-09-23 18:39:37');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Current Database: `tenant_000004`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `tenant_000004` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

USE `tenant_000004`;

--
-- Table structure for table `agendamentos`
--

DROP TABLE IF EXISTS `agendamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `agendamentos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ordem_servico_id` int(11) NOT NULL,
  `responsavel_id` int(11) DEFAULT NULL,
  `inicio` datetime NOT NULL,
  `fim` datetime NOT NULL,
  `status` varchar(30) NOT NULL,
  `observacoes` text DEFAULT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `responsavel_id` (`responsavel_id`),
  KEY `ix_agendamentos_ordem_servico_id` (`ordem_servico_id`),
  CONSTRAINT `agendamentos_ibfk_1` FOREIGN KEY (`ordem_servico_id`) REFERENCES `ordens_servico` (`id`),
  CONSTRAINT `agendamentos_ibfk_2` FOREIGN KEY (`responsavel_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=97 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `agendamentos`
--

LOCK TABLES `agendamentos` WRITE;
/*!40000 ALTER TABLE `agendamentos` DISABLE KEYS */;
INSERT INTO `agendamentos` VALUES
(1,6,1,'2026-09-25 09:00:00','2026-09-25 13:00:00','CANCELADO','Horário atualizado para manutenção preventiva.','2026-09-24 13:11:18','2026-09-24 13:12:08');
/*!40000 ALTER TABLE `agendamentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cargos`
--

DROP TABLE IF EXISTS `cargos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cargos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cargos`
--

LOCK TABLES `cargos` WRITE;
/*!40000 ALTER TABLE `cargos` DISABLE KEYS */;
INSERT INTO `cargos` VALUES
(1,'Gerente','Cargo padrão de gerente.',1);
/*!40000 ALTER TABLE `cargos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipamentos`
--

DROP TABLE IF EXISTS `equipamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipamentos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `identificacao` varchar(100) NOT NULL,
  `nome` varchar(150) NOT NULL,
  `tipo` varchar(100) NOT NULL,
  `fabricante` varchar(100) DEFAULT NULL,
  `modelo` varchar(150) DEFAULT NULL,
  `ano` int(11) DEFAULT NULL,
  `localizacao` varchar(150) DEFAULT NULL,
  `status` varchar(30) NOT NULL,
  `ativo` tinyint(1) NOT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_equipamentos_identificacao` (`identificacao`)
) ENGINE=InnoDB AUTO_INCREMENT=102 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipamentos`
--

LOCK TABLES `equipamentos` WRITE;
/*!40000 ALTER TABLE `equipamentos` DISABLE KEYS */;
/*!40000 ALTER TABLE `equipamentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `indisponibilidades`
--

DROP TABLE IF EXISTS `indisponibilidades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `indisponibilidades` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `maquina_id` int(11) DEFAULT NULL,
  `equipamento_id` int(11) DEFAULT NULL,
  `manutencao_id` int(11) DEFAULT NULL,
  `inicio` datetime NOT NULL,
  `fim` datetime DEFAULT NULL,
  `motivo` varchar(100) NOT NULL,
  `tipo` varchar(30) NOT NULL,
  `observacoes` text DEFAULT NULL,
  `status` varchar(30) NOT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_indisponibilidades_equipamento_id` (`equipamento_id`),
  KEY `ix_indisponibilidades_maquina_id` (`maquina_id`),
  KEY `ix_indisponibilidades_manutencao_id` (`manutencao_id`),
  CONSTRAINT `indisponibilidades_ibfk_1` FOREIGN KEY (`maquina_id`) REFERENCES `maquinas` (`id`),
  CONSTRAINT `indisponibilidades_ibfk_2` FOREIGN KEY (`equipamento_id`) REFERENCES `equipamentos` (`id`),
  CONSTRAINT `indisponibilidades_ibfk_3` FOREIGN KEY (`manutencao_id`) REFERENCES `manutencoes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=130 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `indisponibilidades`
--

LOCK TABLES `indisponibilidades` WRITE;
/*!40000 ALTER TABLE `indisponibilidades` DISABLE KEYS */;
INSERT INTO `indisponibilidades` VALUES
(1,1,NULL,1,'2026-09-25 09:00:00','2026-09-25 13:00:00','Manutenção preventiva programada','MANUTENCAO','Revisão geral da máquina.','FINALIZADA','2026-09-24 13:32:05','2026-09-24 13:33:31');
/*!40000 ALTER TABLE `indisponibilidades` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `manutencoes`
--

DROP TABLE IF EXISTS `manutencoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `manutencoes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ordem_servico_id` int(11) NOT NULL,
  `responsavel_id` int(11) DEFAULT NULL,
  `tipo` varchar(30) NOT NULL,
  `inicio` datetime NOT NULL,
  `fim` datetime DEFAULT NULL,
  `descricao` text DEFAULT NULL,
  `custo` decimal(12,2) DEFAULT NULL,
  `status` varchar(30) NOT NULL,
  `observacoes` text DEFAULT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `responsavel_id` (`responsavel_id`),
  KEY `ix_manutencoes_ordem_servico_id` (`ordem_servico_id`),
  CONSTRAINT `manutencoes_ibfk_1` FOREIGN KEY (`ordem_servico_id`) REFERENCES `ordens_servico` (`id`),
  CONSTRAINT `manutencoes_ibfk_2` FOREIGN KEY (`responsavel_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=135 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `manutencoes`
--

LOCK TABLES `manutencoes` WRITE;
/*!40000 ALTER TABLE `manutencoes` DISABLE KEYS */;
INSERT INTO `manutencoes` VALUES
(1,6,1,'PREVENTIVA','2026-09-25 09:00:00','2026-09-25 13:00:00','Revisão completa de óleo, filtros, pneus e sistema hidráulico.',975.75,'CONCLUIDA','Foi identificada necessidade de revisão adicional.','2026-09-24 13:17:58','2026-09-24 13:19:02');
/*!40000 ALTER TABLE `manutencoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maquinas`
--

DROP TABLE IF EXISTS `maquinas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `maquinas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `identificacao` varchar(100) NOT NULL,
  `modelo` varchar(150) NOT NULL,
  `fabricante` varchar(100) NOT NULL,
  `ano` int(11) DEFAULT NULL,
  `localizacao` varchar(150) DEFAULT NULL,
  `status` varchar(30) NOT NULL,
  `controla_telemetria` tinyint(1) NOT NULL,
  `ativo` tinyint(1) NOT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_maquinas_identificacao` (`identificacao`)
) ENGINE=InnoDB AUTO_INCREMENT=638 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maquinas`
--

LOCK TABLES `maquinas` WRITE;
/*!40000 ALTER TABLE `maquinas` DISABLE KEYS */;
INSERT INTO `maquinas` VALUES
(1,'TR-TESTE-001','6110J','John Deere',2022,'Pátio Norte','OPERANDO',0,1,'2026-09-24 13:00:33','2026-09-24 13:00:33');
/*!40000 ALTER TABLE `maquinas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ordens_servico`
--

DROP TABLE IF EXISTS `ordens_servico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ordens_servico` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `numero` int(11) NOT NULL,
  `tipo` varchar(30) NOT NULL,
  `titulo` varchar(150) NOT NULL,
  `descricao` text DEFAULT NULL,
  `maquina_id` int(11) DEFAULT NULL,
  `equipamento_id` int(11) DEFAULT NULL,
  `operador_id` int(11) DEFAULT NULL,
  `responsavel_id` int(11) DEFAULT NULL,
  `prioridade` varchar(30) NOT NULL,
  `status` varchar(30) NOT NULL,
  `prazo` datetime DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_ordens_servico_numero` (`numero`),
  KEY `maquina_id` (`maquina_id`),
  KEY `equipamento_id` (`equipamento_id`),
  KEY `operador_id` (`operador_id`),
  KEY `responsavel_id` (`responsavel_id`),
  CONSTRAINT `ordens_servico_ibfk_1` FOREIGN KEY (`maquina_id`) REFERENCES `maquinas` (`id`),
  CONSTRAINT `ordens_servico_ibfk_2` FOREIGN KEY (`equipamento_id`) REFERENCES `equipamentos` (`id`),
  CONSTRAINT `ordens_servico_ibfk_3` FOREIGN KEY (`operador_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `ordens_servico_ibfk_4` FOREIGN KEY (`responsavel_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=429 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordens_servico`
--

LOCK TABLES `ordens_servico` WRITE;
/*!40000 ALTER TABLE `ordens_servico` DISABLE KEYS */;
INSERT INTO `ordens_servico` VALUES
(5,1,'MANUTENCAO','Revisão preventiva atualizada','Revisão geral da máquina e verificação dos componentes.',1,NULL,NULL,NULL,'URGENTE','CONCLUIDA','2026-09-30 17:00:00',1,'2026-09-24 13:00:52','2026-09-24 13:02:36'),
(6,2,'MANUTENCAO','Manutenção preventiva do trator','Verificação de óleo, filtros, pneus e sistema hidráulico.',1,NULL,NULL,NULL,'MEDIA','ABERTA','2026-10-05 17:00:00',1,'2026-09-24 13:09:02','2026-09-24 13:09:02');
/*!40000 ALTER TABLE `ordens_servico` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfil_permissoes`
--

DROP TABLE IF EXISTS `perfil_permissoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `perfil_permissoes` (
  `perfil_id` int(11) NOT NULL,
  `permissao_id` int(11) NOT NULL,
  PRIMARY KEY (`perfil_id`,`permissao_id`),
  KEY `permissao_id` (`permissao_id`),
  CONSTRAINT `perfil_permissoes_ibfk_1` FOREIGN KEY (`perfil_id`) REFERENCES `perfis` (`id`),
  CONSTRAINT `perfil_permissoes_ibfk_2` FOREIGN KEY (`permissao_id`) REFERENCES `permissoes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfil_permissoes`
--

LOCK TABLES `perfil_permissoes` WRITE;
/*!40000 ALTER TABLE `perfil_permissoes` DISABLE KEYS */;
INSERT INTO `perfil_permissoes` VALUES
(1,1),
(1,2),
(1,3),
(1,4),
(1,5),
(1,6),
(1,7),
(1,8),
(1,9),
(1,10),
(1,11),
(1,12),
(1,13),
(1,14),
(1,15),
(1,16),
(1,17),
(1,18),
(1,19),
(1,20),
(1,21),
(1,22),
(1,23),
(1,24),
(1,25),
(1,26),
(1,27),
(1,28),
(1,29),
(1,30),
(1,31),
(1,32),
(1,33),
(2,2),
(2,13),
(2,14),
(2,17),
(2,18),
(2,20),
(2,21),
(2,22),
(2,24),
(2,25),
(2,26),
(2,27),
(2,28),
(2,29),
(2,30),
(2,31),
(2,32),
(2,33),
(3,13),
(3,17),
(3,20),
(3,21),
(3,26),
(3,29),
(3,30);
/*!40000 ALTER TABLE `perfil_permissoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfis`
--

DROP TABLE IF EXISTS `perfis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `perfis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfis`
--

LOCK TABLES `perfis` WRITE;
/*!40000 ALTER TABLE `perfis` DISABLE KEYS */;
INSERT INTO `perfis` VALUES
(1,'GERENTE','Perfil padrão de gerente.',1),
(2,'MANUTENCAO','Perfil padrão de manutencao.',1),
(3,'OPERADOR','Perfil padrão de operador.',1);
/*!40000 ALTER TABLE `perfis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissoes`
--

DROP TABLE IF EXISTS `permissoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissoes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissoes`
--

LOCK TABLES `permissoes` WRITE;
/*!40000 ALTER TABLE `permissoes` DISABLE KEYS */;
INSERT INTO `permissoes` VALUES
(1,'USUARIO_CRIAR','Permite criar usuários.'),
(2,'USUARIO_VISUALIZAR','Permite visualizar usuários.'),
(3,'USUARIO_EDITAR','Permite editar usuários.'),
(4,'USUARIO_DESATIVAR','Permite ativar ou desativar usuários.'),
(5,'CARGO_CRIAR','Permite criar cargos.'),
(6,'CARGO_VISUALIZAR','Permite visualizar cargos.'),
(7,'CARGO_EDITAR','Permite editar cargos.'),
(8,'PERFIL_CRIAR','Permite criar perfis.'),
(9,'PERFIL_VISUALIZAR','Permite visualizar perfis.'),
(10,'PERFIL_EDITAR','Permite editar perfis.'),
(11,'PERFIL_PERMISSAO_GERENCIAR','Permite associar e remover permissões de perfis.'),
(12,'MAQUINA_CRIAR','Permite cadastrar máquinas.'),
(13,'MAQUINA_VISUALIZAR','Permite visualizar máquinas.'),
(14,'MAQUINA_EDITAR','Permite editar máquinas.'),
(15,'MAQUINA_DESATIVAR','Permite ativar ou desativar máquinas.'),
(16,'EQUIPAMENTO_CRIAR','Permite cadastrar equipamentos.'),
(17,'EQUIPAMENTO_VISUALIZAR','Permite visualizar equipamentos.'),
(18,'EQUIPAMENTO_EDITAR','Permite editar equipamentos.'),
(19,'EQUIPAMENTO_DESATIVAR','Permite ativar ou desativar equipamentos.'),
(20,'OS.CRIAR','Permite criar novas ordens de serviço.'),
(21,'OS.VISUALIZAR','Permite visualizar ordens de serviço.'),
(22,'OS.EDITAR','Permite editar ordens de serviço.'),
(23,'OS.CANCELAR','Permite cancelar ordens de serviço.'),
(24,'OS.CONCLUIR','Permite concluir ordens de serviço.'),
(25,'MANUTENCAO.CRIAR','Permite registrar manutenções.'),
(26,'MANUTENCAO.VISUALIZAR','Permite visualizar manutenções.'),
(27,'MANUTENCAO.EDITAR','Permite editar registros de manutenção.'),
(28,'MANUTENCAO.CONCLUIR','Permite concluir manutenções.'),
(29,'INDISPONIBILIDADE.CRIAR','Permite registrar indisponibilidades.'),
(30,'INDISPONIBILIDADE.VISUALIZAR','Permite visualizar indisponibilidades.'),
(31,'INDISPONIBILIDADE.EDITAR','Permite editar indisponibilidades.'),
(32,'DASHBOARD.VISUALIZAR','Permite visualizar o dashboard.'),
(33,'MANUTENCAO.CANCELAR','Permite cancelar manutenções.');
/*!40000 ALTER TABLE `permissoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(150) NOT NULL,
  `username` varchar(80) NOT NULL,
  `email` varchar(150) DEFAULT NULL,
  `senha_hash` varchar(255) NOT NULL,
  `cargo_id` int(11) DEFAULT NULL,
  `perfil_id` int(11) NOT NULL,
  `ativo` tinyint(1) NOT NULL,
  `ultimo_login` datetime DEFAULT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_usuarios_username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `cargo_id` (`cargo_id`),
  KEY `perfil_id` (`perfil_id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`cargo_id`) REFERENCES `cargos` (`id`),
  CONSTRAINT `usuarios_ibfk_2` FOREIGN KEY (`perfil_id`) REFERENCES `perfis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES
(1,'Administrador','admin','admin@fazendacompleta.com','scrypt:32768:8:1$0WNQeaj7NfuVjZxS$ddfca4e97a48b2c980f070859afce84823761181e93427568fdad63bb8cfac384acd359de97d8443e36c10356c9fa80251e853eb26e59a2f10f8af9934d3cef4',1,1,1,'2026-09-24 16:06:51','2026-09-23 18:43:17','2026-09-24 16:06:51'),
(2,'João da Silva Atualizado','joao','joao.atualizado@fazenda.com','scrypt:32768:8:1$xPnbuomhWjvU2K6F$c5f52a7573a40ae0e4fd5ac18edbbd4c53eb94ac30bf04326898430668fbf2a933c5cad4fdb2391016a0e27df9edd29720649d0acfd4263c3d5cb193900b8555',1,2,0,NULL,'2026-09-23 19:01:45','2026-09-23 19:01:46'),
(3,'Carlos Oliveira Atualizado','carlos','carlos.novo@fazenda.com','scrypt:32768:8:1$tjSNqHh6JtBD1U92$ce9f50054ace19e9b7a80f7a06face09474ddb301a60f1feab7fd828b2c0800bff83d6b9991224d330ae5d100dd8a20e789f663ff0acc3401eb11f280b213a41',1,2,1,NULL,'2026-09-23 19:06:02','2026-09-23 22:58:16'),
(4,'Teste Senha','teste_senha','teste.senha@fazenda.com','scrypt:32768:8:1$16GrZbZ07DzNkWB2$d9f7534a6bc8a32d2cdf150983efee1cf8ba37b4aecff599c6b8fedf5b4aca2b587a71d784aa10991fd42219bffe58f6ba439ca3fbd4158d2301b33353bae976',1,2,1,NULL,'2026-09-24 12:44:18','2026-09-24 12:44:23');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Current Database: `tenant_000005`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `tenant_000005` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

USE `tenant_000005`;

--
-- Table structure for table `agendamentos`
--

DROP TABLE IF EXISTS `agendamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `agendamentos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ordem_servico_id` int(11) NOT NULL,
  `responsavel_id` int(11) DEFAULT NULL,
  `inicio` datetime NOT NULL,
  `fim` datetime NOT NULL,
  `status` varchar(30) NOT NULL,
  `observacoes` text DEFAULT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `responsavel_id` (`responsavel_id`),
  KEY `ix_agendamentos_ordem_servico_id` (`ordem_servico_id`),
  CONSTRAINT `agendamentos_ibfk_1` FOREIGN KEY (`ordem_servico_id`) REFERENCES `ordens_servico` (`id`),
  CONSTRAINT `agendamentos_ibfk_2` FOREIGN KEY (`responsavel_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `agendamentos`
--

LOCK TABLES `agendamentos` WRITE;
/*!40000 ALTER TABLE `agendamentos` DISABLE KEYS */;
/*!40000 ALTER TABLE `agendamentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cargos`
--

DROP TABLE IF EXISTS `cargos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cargos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cargos`
--

LOCK TABLES `cargos` WRITE;
/*!40000 ALTER TABLE `cargos` DISABLE KEYS */;
INSERT INTO `cargos` VALUES
(1,'Gerente','Cargo padrão de gerente.',1);
/*!40000 ALTER TABLE `cargos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipamentos`
--

DROP TABLE IF EXISTS `equipamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipamentos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `identificacao` varchar(100) NOT NULL,
  `nome` varchar(150) NOT NULL,
  `tipo` varchar(100) NOT NULL,
  `fabricante` varchar(100) DEFAULT NULL,
  `modelo` varchar(150) DEFAULT NULL,
  `ano` int(11) DEFAULT NULL,
  `localizacao` varchar(150) DEFAULT NULL,
  `status` varchar(30) NOT NULL,
  `ativo` tinyint(1) NOT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_equipamentos_identificacao` (`identificacao`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipamentos`
--

LOCK TABLES `equipamentos` WRITE;
/*!40000 ALTER TABLE `equipamentos` DISABLE KEYS */;
/*!40000 ALTER TABLE `equipamentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `indisponibilidades`
--

DROP TABLE IF EXISTS `indisponibilidades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `indisponibilidades` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `maquina_id` int(11) DEFAULT NULL,
  `equipamento_id` int(11) DEFAULT NULL,
  `manutencao_id` int(11) DEFAULT NULL,
  `inicio` datetime NOT NULL,
  `fim` datetime DEFAULT NULL,
  `motivo` varchar(100) NOT NULL,
  `tipo` varchar(30) NOT NULL,
  `observacoes` text DEFAULT NULL,
  `status` varchar(30) NOT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_indisponibilidades_maquina_id` (`maquina_id`),
  KEY `ix_indisponibilidades_equipamento_id` (`equipamento_id`),
  KEY `ix_indisponibilidades_manutencao_id` (`manutencao_id`),
  CONSTRAINT `indisponibilidades_ibfk_1` FOREIGN KEY (`maquina_id`) REFERENCES `maquinas` (`id`),
  CONSTRAINT `indisponibilidades_ibfk_2` FOREIGN KEY (`equipamento_id`) REFERENCES `equipamentos` (`id`),
  CONSTRAINT `indisponibilidades_ibfk_3` FOREIGN KEY (`manutencao_id`) REFERENCES `manutencoes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `indisponibilidades`
--

LOCK TABLES `indisponibilidades` WRITE;
/*!40000 ALTER TABLE `indisponibilidades` DISABLE KEYS */;
/*!40000 ALTER TABLE `indisponibilidades` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `manutencoes`
--

DROP TABLE IF EXISTS `manutencoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `manutencoes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ordem_servico_id` int(11) NOT NULL,
  `responsavel_id` int(11) DEFAULT NULL,
  `tipo` varchar(30) NOT NULL,
  `inicio` datetime NOT NULL,
  `fim` datetime DEFAULT NULL,
  `descricao` text DEFAULT NULL,
  `custo` decimal(12,2) DEFAULT NULL,
  `status` varchar(30) NOT NULL,
  `observacoes` text DEFAULT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `responsavel_id` (`responsavel_id`),
  KEY `ix_manutencoes_ordem_servico_id` (`ordem_servico_id`),
  CONSTRAINT `manutencoes_ibfk_1` FOREIGN KEY (`ordem_servico_id`) REFERENCES `ordens_servico` (`id`),
  CONSTRAINT `manutencoes_ibfk_2` FOREIGN KEY (`responsavel_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `manutencoes`
--

LOCK TABLES `manutencoes` WRITE;
/*!40000 ALTER TABLE `manutencoes` DISABLE KEYS */;
/*!40000 ALTER TABLE `manutencoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maquinas`
--

DROP TABLE IF EXISTS `maquinas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `maquinas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `identificacao` varchar(100) NOT NULL,
  `modelo` varchar(150) NOT NULL,
  `fabricante` varchar(100) NOT NULL,
  `ano` int(11) DEFAULT NULL,
  `localizacao` varchar(150) DEFAULT NULL,
  `status` varchar(30) NOT NULL,
  `controla_telemetria` tinyint(1) NOT NULL,
  `ativo` tinyint(1) NOT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_maquinas_identificacao` (`identificacao`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maquinas`
--

LOCK TABLES `maquinas` WRITE;
/*!40000 ALTER TABLE `maquinas` DISABLE KEYS */;
/*!40000 ALTER TABLE `maquinas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ordens_servico`
--

DROP TABLE IF EXISTS `ordens_servico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ordens_servico` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `numero` int(11) NOT NULL,
  `tipo` varchar(30) NOT NULL,
  `titulo` varchar(150) NOT NULL,
  `descricao` text DEFAULT NULL,
  `maquina_id` int(11) DEFAULT NULL,
  `equipamento_id` int(11) DEFAULT NULL,
  `operador_id` int(11) DEFAULT NULL,
  `responsavel_id` int(11) DEFAULT NULL,
  `prioridade` varchar(30) NOT NULL,
  `status` varchar(30) NOT NULL,
  `prazo` datetime DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_ordens_servico_numero` (`numero`),
  KEY `maquina_id` (`maquina_id`),
  KEY `equipamento_id` (`equipamento_id`),
  KEY `operador_id` (`operador_id`),
  KEY `responsavel_id` (`responsavel_id`),
  CONSTRAINT `ordens_servico_ibfk_1` FOREIGN KEY (`maquina_id`) REFERENCES `maquinas` (`id`),
  CONSTRAINT `ordens_servico_ibfk_2` FOREIGN KEY (`equipamento_id`) REFERENCES `equipamentos` (`id`),
  CONSTRAINT `ordens_servico_ibfk_3` FOREIGN KEY (`operador_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `ordens_servico_ibfk_4` FOREIGN KEY (`responsavel_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordens_servico`
--

LOCK TABLES `ordens_servico` WRITE;
/*!40000 ALTER TABLE `ordens_servico` DISABLE KEYS */;
/*!40000 ALTER TABLE `ordens_servico` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfil_permissoes`
--

DROP TABLE IF EXISTS `perfil_permissoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `perfil_permissoes` (
  `perfil_id` int(11) NOT NULL,
  `permissao_id` int(11) NOT NULL,
  PRIMARY KEY (`perfil_id`,`permissao_id`),
  KEY `permissao_id` (`permissao_id`),
  CONSTRAINT `perfil_permissoes_ibfk_1` FOREIGN KEY (`perfil_id`) REFERENCES `perfis` (`id`),
  CONSTRAINT `perfil_permissoes_ibfk_2` FOREIGN KEY (`permissao_id`) REFERENCES `permissoes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfil_permissoes`
--

LOCK TABLES `perfil_permissoes` WRITE;
/*!40000 ALTER TABLE `perfil_permissoes` DISABLE KEYS */;
INSERT INTO `perfil_permissoes` VALUES
(1,1),
(1,2),
(1,3),
(1,4),
(1,5),
(1,6),
(1,7),
(1,8),
(1,9),
(1,10),
(1,11),
(1,12),
(1,13),
(1,14),
(1,15),
(1,16),
(1,17),
(1,18),
(1,19),
(1,20),
(1,21),
(1,22),
(1,23),
(1,24),
(1,25),
(1,26),
(1,27),
(1,28),
(1,29),
(1,30),
(1,31),
(1,32),
(1,33),
(2,2),
(2,13),
(2,14),
(2,17),
(2,18),
(2,20),
(2,21),
(2,22),
(2,24),
(2,25),
(2,26),
(2,27),
(2,28),
(2,29),
(2,30),
(2,31),
(2,32),
(2,33),
(3,13),
(3,17),
(3,20),
(3,21),
(3,26),
(3,30),
(3,31);
/*!40000 ALTER TABLE `perfil_permissoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfis`
--

DROP TABLE IF EXISTS `perfis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `perfis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfis`
--

LOCK TABLES `perfis` WRITE;
/*!40000 ALTER TABLE `perfis` DISABLE KEYS */;
INSERT INTO `perfis` VALUES
(1,'GERENTE','Perfil padrão de gerente.',1),
(2,'MANUTENCAO','Perfil padrão de manutencao.',1),
(3,'OPERADOR','Perfil padrão de operador.',1);
/*!40000 ALTER TABLE `perfis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissoes`
--

DROP TABLE IF EXISTS `permissoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissoes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissoes`
--

LOCK TABLES `permissoes` WRITE;
/*!40000 ALTER TABLE `permissoes` DISABLE KEYS */;
INSERT INTO `permissoes` VALUES
(1,'USUARIO_CRIAR','Permite criar usuários.'),
(2,'USUARIO_VISUALIZAR','Permite visualizar usuários.'),
(3,'USUARIO_EDITAR','Permite editar usuários.'),
(4,'USUARIO_DESATIVAR','Permite ativar ou desativar usuários.'),
(5,'CARGO_CRIAR','Permite criar cargos.'),
(6,'CARGO_VISUALIZAR','Permite visualizar cargos.'),
(7,'CARGO_EDITAR','Permite editar cargos.'),
(8,'PERFIL_CRIAR','Permite criar perfis.'),
(9,'PERFIL_VISUALIZAR','Permite visualizar perfis.'),
(10,'PERFIL_EDITAR','Permite editar perfis.'),
(11,'PERFIL_PERMISSAO_GERENCIAR','Permite associar e remover permissões de perfis.'),
(12,'MAQUINA_CRIAR','Permite cadastrar máquinas.'),
(13,'MAQUINA_VISUALIZAR','Permite visualizar máquinas.'),
(14,'MAQUINA_EDITAR','Permite editar máquinas.'),
(15,'MAQUINA_DESATIVAR','Permite ativar ou desativar máquinas.'),
(16,'EQUIPAMENTO_CRIAR','Permite cadastrar equipamentos.'),
(17,'EQUIPAMENTO_VISUALIZAR','Permite visualizar equipamentos.'),
(18,'EQUIPAMENTO_EDITAR','Permite editar equipamentos.'),
(19,'EQUIPAMENTO_DESATIVAR','Permite ativar ou desativar equipamentos.'),
(20,'OS.CRIAR','Permite criar novas ordens de serviço.'),
(21,'OS.VISUALIZAR','Permite visualizar ordens de serviço.'),
(22,'OS.EDITAR','Permite editar ordens de serviço.'),
(23,'OS.CANCELAR','Permite cancelar ordens de serviço.'),
(24,'OS.CONCLUIR','Permite concluir ordens de serviço.'),
(25,'MANUTENCAO.CRIAR','Permite registrar manutenções.'),
(26,'MANUTENCAO.VISUALIZAR','Permite visualizar manutenções.'),
(27,'MANUTENCAO.EDITAR','Permite editar registros de manutenção.'),
(28,'MANUTENCAO.CONCLUIR','Permite concluir manutenções.'),
(29,'MANUTENCAO.CANCELAR','Permite cancelar manutenções.'),
(30,'INDISPONIBILIDADE.CRIAR','Permite registrar indisponibilidades.'),
(31,'INDISPONIBILIDADE.VISUALIZAR','Permite visualizar indisponibilidades.'),
(32,'INDISPONIBILIDADE.EDITAR','Permite editar indisponibilidades.'),
(33,'DASHBOARD.VISUALIZAR','Permite visualizar o dashboard.');
/*!40000 ALTER TABLE `permissoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(150) NOT NULL,
  `username` varchar(80) NOT NULL,
  `email` varchar(150) DEFAULT NULL,
  `senha_hash` varchar(255) NOT NULL,
  `cargo_id` int(11) DEFAULT NULL,
  `perfil_id` int(11) NOT NULL,
  `ativo` tinyint(1) NOT NULL,
  `ultimo_login` datetime DEFAULT NULL,
  `criado_em` datetime NOT NULL,
  `atualizado_em` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_usuarios_username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `cargo_id` (`cargo_id`),
  KEY `perfil_id` (`perfil_id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`cargo_id`) REFERENCES `cargos` (`id`),
  CONSTRAINT `usuarios_ibfk_2` FOREIGN KEY (`perfil_id`) REFERENCES `perfis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES
(1,'Administrador Isolamento','admin_isolamento',NULL,'scrypt:32768:8:1$mTxJQQIWNkMJfGcN$449336253477ff4d63f4002cd2c2196ed4ee9853e3ac656884949977e6fb9c46083ef84b5413e14990fad0b2ca6dc041bca9708219f0af08501dd3219407311c',1,1,1,'2026-09-24 16:07:11','2026-09-24 15:53:57','2026-09-24 16:07:11');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-24 13:17:33
