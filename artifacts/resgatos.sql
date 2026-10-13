-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Tempo de geração: 13/10/2026 às 08:37
-- Versão do servidor: 9.1.0
-- Versão do PHP: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Banco de dados: `resgatos`
--

-- --------------------------------------------------------

--
-- Estrutura para tabela `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE IF NOT EXISTS `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE IF NOT EXISTS `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_group_id_b120cbf9` (`group_id`),
  KEY `auth_group_permissions_permission_id_84c5c92e` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  KEY `auth_permission_content_type_id_2f476e4b` (`content_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 3, 'add_permission'),
(6, 'Can change permission', 3, 'change_permission'),
(7, 'Can delete permission', 3, 'delete_permission'),
(8, 'Can view permission', 3, 'view_permission'),
(9, 'Can add group', 2, 'add_group'),
(10, 'Can change group', 2, 'change_group'),
(11, 'Can delete group', 2, 'delete_group'),
(12, 'Can view group', 2, 'view_group'),
(13, 'Can add content type', 4, 'add_contenttype'),
(14, 'Can change content type', 4, 'change_contenttype'),
(15, 'Can delete content type', 4, 'delete_contenttype'),
(16, 'Can view content type', 4, 'view_contenttype'),
(17, 'Can add session', 5, 'add_session'),
(18, 'Can change session', 5, 'change_session'),
(19, 'Can delete session', 5, 'delete_session'),
(20, 'Can view session', 5, 'view_session'),
(21, 'Can add Pessoa', 6, 'add_pessoa'),
(22, 'Can change Pessoa', 6, 'change_pessoa'),
(23, 'Can delete Pessoa', 6, 'delete_pessoa'),
(24, 'Can view Pessoa', 6, 'view_pessoa'),
(25, 'Can add Usuário', 7, 'add_usuario'),
(26, 'Can change Usuário', 7, 'change_usuario'),
(27, 'Can delete Usuário', 7, 'delete_usuario'),
(28, 'Can view Usuário', 7, 'view_usuario'),
(29, 'Can add Vínculo entre pessoa e pet', 8, 'add_pessoapet'),
(30, 'Can change Vínculo entre pessoa e pet', 8, 'change_pessoapet'),
(31, 'Can delete Vínculo entre pessoa e pet', 8, 'delete_pessoapet'),
(32, 'Can view Vínculo entre pessoa e pet', 8, 'view_pessoapet'),
(33, 'Can add Pet', 9, 'add_pet'),
(34, 'Can change Pet', 9, 'change_pet'),
(35, 'Can delete Pet', 9, 'delete_pet'),
(36, 'Can view Pet', 9, 'view_pet');

-- --------------------------------------------------------

--
-- Estrutura para tabela `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE IF NOT EXISTS `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_general_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_general_ci NOT NULL,
  `action_flag` smallint UNSIGNED NOT NULL,
  `change_message` longtext COLLATE utf8mb4_general_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6` (`user_id`)
) ;

-- --------------------------------------------------------

--
-- Estrutura para tabela `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(2, 'auth', 'group'),
(3, 'auth', 'permission'),
(4, 'contenttypes', 'contenttype'),
(5, 'sessions', 'session'),
(6, 'pessoas', 'pessoa'),
(7, 'pessoas', 'usuario'),
(8, 'pets', 'pessoapet'),
(9, 'pets', 'pet');

-- --------------------------------------------------------

--
-- Estrutura para tabela `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE IF NOT EXISTS `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2026-10-12 19:48:08.136563'),
(2, 'contenttypes', '0002_remove_content_type_name', '2026-10-12 19:48:08.215042'),
(3, 'auth', '0001_initial', '2026-10-12 19:48:08.387541'),
(4, 'auth', '0002_alter_permission_name_max_length', '2026-10-12 19:48:08.409776'),
(5, 'auth', '0003_alter_user_email_max_length', '2026-10-12 19:48:08.414336'),
(6, 'auth', '0004_alter_user_username_opts', '2026-10-12 19:48:08.417197'),
(7, 'auth', '0005_alter_user_last_login_null', '2026-10-12 19:48:08.419697'),
(8, 'auth', '0006_require_contenttypes_0002', '2026-10-12 19:48:08.420224'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2026-10-12 19:48:08.422515'),
(10, 'auth', '0008_alter_user_username_max_length', '2026-10-12 19:48:08.425485'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2026-10-12 19:48:08.429069'),
(12, 'auth', '0010_alter_group_name_max_length', '2026-10-12 19:48:08.449530'),
(13, 'auth', '0011_update_proxy_permissions', '2026-10-12 19:48:08.453459'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2026-10-12 19:48:08.456252'),
(15, 'pessoas', '0001_initial', '2026-10-12 19:48:08.691189'),
(16, 'admin', '0001_initial', '2026-10-12 19:48:08.804766'),
(17, 'admin', '0002_logentry_remove_auto_add', '2026-10-12 19:48:08.810157'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2026-10-12 19:48:08.818036'),
(19, 'sessions', '0001_initial', '2026-10-12 19:48:08.844265'),
(20, 'pets', '0001_initial', '2026-10-13 11:15:49.104974');

-- --------------------------------------------------------

--
-- Estrutura para tabela `django_session`
--

DROP TABLE IF EXISTS `django_session`;
CREATE TABLE IF NOT EXISTS `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_general_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_general_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `pessoa`
--

DROP TABLE IF EXISTS `pessoa`;
CREATE TABLE IF NOT EXISTS `pessoa` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nome` varchar(150) COLLATE utf8mb4_general_ci NOT NULL,
  `cpf` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(150) COLLATE utf8mb4_general_ci NOT NULL,
  `telefone` varchar(45) COLLATE utf8mb4_general_ci NOT NULL,
  `cep` varchar(15) COLLATE utf8mb4_general_ci NOT NULL,
  `endereco` varchar(150) COLLATE utf8mb4_general_ci NOT NULL,
  `numero` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `complemento` varchar(150) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `bairro` varchar(45) COLLATE utf8mb4_general_ci NOT NULL,
  `cidade` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `estado` varchar(45) COLLATE utf8mb4_general_ci NOT NULL,
  `is_attendance_responsible` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cpf` (`cpf`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `telefone` (`telefone`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `pessoa`
--

INSERT INTO `pessoa` (`id`, `nome`, `cpf`, `email`, `telefone`, `cep`, `endereco`, `numero`, `complemento`, `bairro`, `cidade`, `estado`, `is_attendance_responsible`, `created_at`, `updated_at`, `is_active`) VALUES
(1, 'Fulano', '12345678900', 'univesp@gmail.com', '16991234567', '13560000', 'Rua de Teste', '100', NULL, 'Centro', 'São Carlos', 'SP', 0, '2026-10-12 19:50:17.584048', '2026-10-12 19:50:17.584182', 1);

-- --------------------------------------------------------

--
-- Estrutura para tabela `pessoa_pet`
--

DROP TABLE IF EXISTS `pessoa_pet`;
CREATE TABLE IF NOT EXISTS `pessoa_pet` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tipo_relacao` varchar(45) COLLATE utf8mb4_general_ci NOT NULL,
  `data_inicio` date NOT NULL,
  `data_fim` date DEFAULT NULL,
  `observacoes` longtext COLLATE utf8mb4_general_ci,
  `pessoa_id` bigint NOT NULL,
  `pet_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `pessoa_pet_pessoa_id_bcadaa30` (`pessoa_id`),
  KEY `pessoa_pet_pet_id_1df3da55` (`pet_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `pessoa_pet`
--

INSERT INTO `pessoa_pet` (`id`, `tipo_relacao`, `data_inicio`, `data_fim`, `observacoes`, `pessoa_id`, `pet_id`) VALUES
(1, 'Tutor', '2024-10-10', NULL, NULL, 1, 1);

-- --------------------------------------------------------

--
-- Estrutura para tabela `pet`
--

DROP TABLE IF EXISTS `pet`;
CREATE TABLE IF NOT EXISTS `pet` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `microchip` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `nome` varchar(45) COLLATE utf8mb4_general_ci NOT NULL,
  `especie` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `raca` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `sexo` varchar(1) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `cor` varchar(45) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `data_nascimento` date DEFAULT NULL,
  `porte` varchar(45) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `pelagem` varchar(45) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `foto` varchar(150) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `observacoes` longtext COLLATE utf8mb4_general_ci,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `pet`
--

INSERT INTO `pet` (`id`, `microchip`, `nome`, `especie`, `raca`, `sexo`, `cor`, `data_nascimento`, `porte`, `pelagem`, `foto`, `observacoes`) VALUES
(1, NULL, 'Mingau', 'gato', 'Persa', 'M', 'Preto', '2022-10-10', 'Pequeno', 'Alta', NULL, NULL);

-- --------------------------------------------------------

--
-- Estrutura para tabela `usuario`
--

DROP TABLE IF EXISTS `usuario`;
CREATE TABLE IF NOT EXISTS `usuario` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `is_superuser` tinyint(1) NOT NULL,
  `senha` varchar(128) COLLATE utf8mb4_general_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `last_access` datetime(6) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `pessoa_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `pessoa_id` (`pessoa_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `usuario`
--

INSERT INTO `usuario` (`id`, `is_superuser`, `senha`, `created_at`, `updated_at`, `last_access`, `is_active`, `is_staff`, `pessoa_id`) VALUES
(1, 0, 'pbkdf2_sha256$1500000$ndjzGIakb5z9p0QEIP2t3i$Zftdyj9qvH4B1Dek0dkb2oqtSwsBrRDN/K7I3Tjm2l8=', '2026-10-12 19:50:18.284364', '2026-10-12 19:50:18.284382', '2026-10-13 10:57:05.877259', 1, 1, 1);

-- --------------------------------------------------------

--
-- Estrutura para tabela `usuario_groups`
--

DROP TABLE IF EXISTS `usuario_groups`;
CREATE TABLE IF NOT EXISTS `usuario_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `usuario_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuario_groups_usuario_id_group_id_2e3cd638_uniq` (`usuario_id`,`group_id`),
  KEY `usuario_groups_usuario_id_161fc80c` (`usuario_id`),
  KEY `usuario_groups_group_id_c67c8651` (`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `usuario_user_permissions`
--

DROP TABLE IF EXISTS `usuario_user_permissions`;
CREATE TABLE IF NOT EXISTS `usuario_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `usuario_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuario_user_permissions_usuario_id_permission_id_3db58b8c_uniq` (`usuario_id`,`permission_id`),
  KEY `usuario_user_permissions_usuario_id_693d9c50` (`usuario_id`),
  KEY `usuario_user_permissions_permission_id_a8893ce7` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
