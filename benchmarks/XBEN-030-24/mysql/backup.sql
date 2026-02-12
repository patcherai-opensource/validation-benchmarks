-- Dolibarr ERP/CRM Database Schema
-- Version 19.0.1

SET NAMES utf8;
SET CHARACTER SET utf8;

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- --------------------------------------------------------
-- Table: llx_const - Application constants/settings
-- --------------------------------------------------------

DROP TABLE IF EXISTS `llx_const`;
CREATE TABLE `llx_const` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `name` varchar(180) NOT NULL,
  `entity` int NOT NULL DEFAULT '1',
  `value` text NOT NULL,
  `type` varchar(64) DEFAULT 'chaine',
  `visible` tinyint NOT NULL DEFAULT '1',
  `note` text,
  `tms` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`rowid`),
  UNIQUE KEY `uk_const` (`name`,`entity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `llx_const` VALUES
(1, 'MAIN_VERSION_LAST_INSTALL', 1, '19.0.1', 'chaine', 0, 'Dolibarr version at last install', NOW()),
(2, 'MAIN_LANG_DEFAULT', 1, 'en_US', 'chaine', 0, NULL, NOW()),
(3, 'MAIN_THEME', 1, 'eldy', 'chaine', 0, NULL, NOW()),
(4, 'MAIN_MODULE_USER', 1, '1', 'chaine', 0, NULL, NOW()),
(5, 'MAIN_MODULE_SOCIETE', 1, '1', 'chaine', 0, NULL, NOW()),
(6, 'MAIN_MODULE_FACTURE', 1, '1', 'chaine', 0, NULL, NOW()),
(7, 'MAIN_MODULE_PRODUCT', 1, '1', 'chaine', 0, NULL, NOW()),
(8, 'MAIN_MODULE_HRM', 1, '1', 'chaine', 0, NULL, NOW()),
(9, 'DATABASE_PWD_ENCRYPTED', 1, '1', 'chaine', 0, NULL, NOW()),
(10, 'MAIN_SECURITY_CSRF_WITH_TOKEN', 1, '1', 'chaine', 0, NULL, NOW()),
(11, 'MAIN_FEATURES_LEVEL', 1, '0', 'chaine', 0, NULL, NOW()),
(12, 'SYSLOG_LEVEL', 1, '5', 'chaine', 0, NULL, NOW()),
(13, 'MAIN_PROD', 1, '1', 'chaine', 0, NULL, NOW());

-- --------------------------------------------------------
-- Table: llx_user - User accounts
-- --------------------------------------------------------

DROP TABLE IF EXISTS `llx_user`;
CREATE TABLE `llx_user` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `entity` int NOT NULL DEFAULT '1',
  `ref_ext` varchar(128) DEFAULT NULL,
  `login` varchar(50) NOT NULL,
  `pass_crypted` varchar(255) DEFAULT NULL,
  `admin` smallint NOT NULL DEFAULT '0',
  `lastname` varchar(50) DEFAULT NULL,
  `firstname` varchar(50) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `office_phone` varchar(20) DEFAULT NULL,
  `user_mobile` varchar(20) DEFAULT NULL,
  `job` varchar(128) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `zip` varchar(25) DEFAULT NULL,
  `town` varchar(50) DEFAULT NULL,
  `fk_country` int DEFAULT NULL,
  `statut` tinyint NOT NULL DEFAULT '1',
  `note_private` text,
  `note_public` text,
  `datec` datetime DEFAULT NULL,
  `tms` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `fk_user_creat` int DEFAULT NULL,
  `fk_user_modif` int DEFAULT NULL,
  `api_key` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`rowid`),
  UNIQUE KEY `uk_user_login` (`login`,`entity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `llx_user` VALUES
(1, 1, NULL, 'admin', '$2y$10$TNQnNXkWxmRwl85OScqsSeDYYmIdIQR/OBXOSfF5vyplF6H76BZJe', 1, 'Administrator', 'System', 'admin@erp.local', NULL, '+1-555-0100', NULL, 'System Administrator', '100 Enterprise Way', '94105', 'San Francisco', 1, 1, NULL, NULL, '2024-01-15 09:00:00', NOW(), NULL, NULL, NULL),
(2, 1, NULL, 'jdoe', '$2y$10$Rv8gJYKdFWqFMc6LX0t3D.3aCZUwBfQ.ysOqf0zSmkLUdYZvWhGHi', 0, 'Doe', 'John', 'john.doe@erp.local', 'man', '+1-555-0101', '+1-555-0201', 'Sales Manager', '200 Commerce St', '10001', 'New York', 1, 1, NULL, NULL, '2024-02-01 10:30:00', NOW(), 1, NULL, NULL),
(3, 1, NULL, 'jsmith', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 0, 'Smith', 'Jane', 'jane.smith@erp.local', 'woman', '+1-555-0102', '+1-555-0202', 'Accountant', '300 Finance Ave', '60601', 'Chicago', 1, 1, NULL, NULL, '2024-02-15 14:00:00', NOW(), 1, NULL, NULL),
(4, 1, NULL, 'mwilson', '$2y$10$ZjF2MWE3YzNkNWY2NzhjOeQ8IKl4RThPRHgzNm1iYjR5a3k2dGU0', 0, 'Wilson', 'Mike', 'mike.wilson@erp.local', 'man', '+1-555-0103', NULL, 'Warehouse Manager', '400 Industrial Blvd', '75001', 'Dallas', 1, 1, NULL, NULL, '2024-03-01 08:00:00', NOW(), 1, NULL, NULL),
(5, 1, NULL, 'lchen', '$2y$10$bG9jYWxob3N0MTIzNDU2N.kp3RibS1jOWR4V3NXZW4xWkU0LnlMaA', 0, 'Chen', 'Lisa', 'lisa.chen@erp.local', 'woman', '+1-555-0104', '+1-555-0204', 'HR Manager', '500 People St', '98101', 'Seattle', 1, 1, NULL, NULL, '2024-03-15 11:00:00', NOW(), 1, NULL, NULL);

-- --------------------------------------------------------
-- Table: llx_user_extrafields - User extra field values
-- --------------------------------------------------------

DROP TABLE IF EXISTS `llx_user_extrafields`;
CREATE TABLE `llx_user_extrafields` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `tms` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `fk_object` int NOT NULL,
  PRIMARY KEY (`rowid`),
  KEY `idx_user_extrafields` (`fk_object`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `llx_user_extrafields` (fk_object) VALUES (1), (2), (3), (4), (5);

-- --------------------------------------------------------
-- Table: llx_extrafields - Extra field definitions
-- --------------------------------------------------------

DROP TABLE IF EXISTS `llx_extrafields`;
CREATE TABLE `llx_extrafields` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `entity` int NOT NULL DEFAULT '1',
  `elementtype` varchar(64) NOT NULL DEFAULT 'user',
  `label` varchar(255) NOT NULL,
  `type` varchar(64) NOT NULL DEFAULT 'varchar',
  `size` varchar(8) NOT NULL DEFAULT '255',
  `fielddefault` varchar(255) DEFAULT NULL,
  `fieldcomputed` text,
  `fieldrequired` tinyint NOT NULL DEFAULT '0',
  `pos` int NOT NULL DEFAULT '0',
  `enabled` tinyint NOT NULL DEFAULT '1',
  `list` tinyint NOT NULL DEFAULT '1',
  `help` text,
  `langs` varchar(64) DEFAULT NULL,
  `printable` tinyint NOT NULL DEFAULT '0',
  `totalizable` tinyint NOT NULL DEFAULT '0',
  `tms` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`rowid`),
  UNIQUE KEY `uk_extrafields` (`name`,`entity`,`elementtype`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Pre-existing extra field definitions (department as example)
INSERT INTO `llx_extrafields` (name, entity, elementtype, label, type, size, fielddefault, fieldcomputed, fieldrequired, pos, enabled, list, help)
VALUES
('department', 1, 'user', 'Department', 'varchar', '128', '', '', 0, 10, 1, 1, 'User department or division');

-- Add the department column to extrafields table
ALTER TABLE `llx_user_extrafields` ADD COLUMN `department` varchar(128) DEFAULT NULL;

UPDATE `llx_user_extrafields` SET department = 'IT' WHERE fk_object = 1;
UPDATE `llx_user_extrafields` SET department = 'Sales' WHERE fk_object = 2;
UPDATE `llx_user_extrafields` SET department = 'Finance' WHERE fk_object = 3;
UPDATE `llx_user_extrafields` SET department = 'Logistics' WHERE fk_object = 4;
UPDATE `llx_user_extrafields` SET department = 'Human Resources' WHERE fk_object = 5;

-- --------------------------------------------------------
-- Table: llx_societe - Third parties (companies)
-- --------------------------------------------------------

DROP TABLE IF EXISTS `llx_societe`;
CREATE TABLE `llx_societe` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(128) DEFAULT NULL,
  `entity` int NOT NULL DEFAULT '1',
  `ref_ext` varchar(255) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `zip` varchar(25) DEFAULT NULL,
  `town` varchar(50) DEFAULT NULL,
  `fk_country` int DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(128) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `client` tinyint NOT NULL DEFAULT '0',
  `fournisseur` tinyint NOT NULL DEFAULT '0',
  `code_client` varchar(24) DEFAULT NULL,
  `code_fournisseur` varchar(24) DEFAULT NULL,
  `statut` tinyint NOT NULL DEFAULT '1',
  `datec` datetime DEFAULT NULL,
  `tms` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`rowid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `llx_societe` VALUES
(1, 'Acme Corporation', 1, NULL, '1 Innovation Drive', '94043', 'Mountain View', 1, '+1-555-1000', 'contact@acme.example', 'https://acme.example', 1, 0, 'CU2401-0001', NULL, 1, '2024-01-20 09:00:00', NOW()),
(2, 'Global Supplies Inc', 1, NULL, '500 Vendor Blvd', '10001', 'New York', 1, '+1-555-2000', 'info@globalsupplies.example', 'https://globalsupplies.example', 0, 1, NULL, 'SU2401-0001', 1, '2024-01-22 10:00:00', NOW()),
(3, 'Pinnacle Industries', 1, NULL, '750 Enterprise Way', '60601', 'Chicago', 1, '+1-555-3000', 'sales@pinnacle.example', NULL, 1, 1, 'CU2401-0002', 'SU2401-0002', 1, '2024-02-01 11:30:00', NOW()),
(4, 'TechForward Solutions', 1, NULL, '200 Digital Lane', '98101', 'Seattle', 1, '+1-555-4000', 'hello@techforward.example', 'https://techforward.example', 1, 0, 'CU2401-0003', NULL, 1, '2024-02-10 14:00:00', NOW());

-- --------------------------------------------------------
-- Table: llx_product - Products/Services catalog
-- --------------------------------------------------------

DROP TABLE IF EXISTS `llx_product`;
CREATE TABLE `llx_product` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `ref` varchar(128) NOT NULL,
  `entity` int NOT NULL DEFAULT '1',
  `label` varchar(255) DEFAULT NULL,
  `description` text,
  `fk_product_type` tinyint NOT NULL DEFAULT '0',
  `price` double(24,8) DEFAULT '0.00000000',
  `tva_tx` double(7,4) DEFAULT '0.0000',
  `tosell` tinyint NOT NULL DEFAULT '1',
  `tobuy` tinyint NOT NULL DEFAULT '1',
  `datec` datetime DEFAULT NULL,
  `tms` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`rowid`),
  UNIQUE KEY `uk_product_ref` (`ref`,`entity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `llx_product` VALUES
(1, 'CONS-001', 1, 'Consulting Service - Standard', 'Standard consulting service, billed per hour', 1, 150.00000000, 20.0000, 1, 0, '2024-01-15 09:00:00', NOW()),
(2, 'CONS-002', 1, 'Consulting Service - Premium', 'Premium consulting with dedicated team', 1, 300.00000000, 20.0000, 1, 0, '2024-01-15 09:00:00', NOW()),
(3, 'SOFT-001', 1, 'ERP License - Annual', 'Annual software license for ERP system', 0, 5000.00000000, 20.0000, 1, 0, '2024-01-20 10:00:00', NOW()),
(4, 'SUPP-001', 1, 'Office Supplies Bundle', 'Standard office supplies monthly bundle', 0, 45.00000000, 20.0000, 0, 1, '2024-02-01 08:00:00', NOW()),
(5, 'HW-001', 1, 'Workstation Setup', 'Complete workstation hardware package', 0, 1200.00000000, 20.0000, 1, 1, '2024-02-15 09:00:00', NOW());

-- --------------------------------------------------------
-- Table: llx_facture - Invoices
-- --------------------------------------------------------

DROP TABLE IF EXISTS `llx_facture`;
CREATE TABLE `llx_facture` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `ref` varchar(30) NOT NULL,
  `entity` int NOT NULL DEFAULT '1',
  `type` smallint NOT NULL DEFAULT '0',
  `fk_soc` int NOT NULL,
  `datec` datetime DEFAULT NULL,
  `datef` date DEFAULT NULL,
  `total_ht` double(24,8) DEFAULT '0.00000000',
  `total_tva` double(24,8) DEFAULT '0.00000000',
  `total_ttc` double(24,8) DEFAULT '0.00000000',
  `fk_statut` smallint NOT NULL DEFAULT '0',
  `note_private` text,
  `note_public` text,
  `tms` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`rowid`),
  UNIQUE KEY `uk_facture_ref` (`ref`,`entity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `llx_facture` VALUES
(1, 'FA2401-0001', 1, 0, 1, '2024-01-25 10:00:00', '2024-01-25', 5000.00000000, 1000.00000000, 6000.00000000, 2, NULL, NULL, NOW()),
(2, 'FA2401-0002', 1, 0, 3, '2024-02-05 11:30:00', '2024-02-05', 1500.00000000, 300.00000000, 1800.00000000, 1, NULL, NULL, NOW()),
(3, 'FA2402-0001', 1, 0, 4, '2024-02-20 14:00:00', '2024-02-20', 7200.00000000, 1440.00000000, 8640.00000000, 2, NULL, NULL, NOW());

-- --------------------------------------------------------
-- Table: llx_usergroup - Groups
-- --------------------------------------------------------

DROP TABLE IF EXISTS `llx_usergroup`;
CREATE TABLE `llx_usergroup` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(180) NOT NULL,
  `entity` int NOT NULL DEFAULT '1',
  `note` text,
  `datec` datetime DEFAULT NULL,
  `tms` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`rowid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `llx_usergroup` VALUES
(1, 'Administrators', 1, 'Full system access', '2024-01-15 09:00:00', NOW()),
(2, 'Sales Team', 1, 'Sales and CRM access', '2024-01-15 09:00:00', NOW()),
(3, 'Accounting', 1, 'Accounting and billing access', '2024-01-15 09:00:00', NOW());

-- --------------------------------------------------------
-- Table: llx_usergroup_user - Group membership
-- --------------------------------------------------------

DROP TABLE IF EXISTS `llx_usergroup_user`;
CREATE TABLE `llx_usergroup_user` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `entity` int NOT NULL DEFAULT '1',
  `fk_user` int NOT NULL,
  `fk_usergroup` int NOT NULL,
  PRIMARY KEY (`rowid`),
  UNIQUE KEY `uk_usergroup_user` (`fk_user`,`fk_usergroup`,`entity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `llx_usergroup_user` VALUES
(1, 1, 1, 1),
(2, 1, 2, 2),
(3, 1, 3, 3),
(4, 1, 4, 2),
(5, 1, 5, 1);

-- --------------------------------------------------------
-- Table: llx_rights_def - Permission definitions
-- --------------------------------------------------------

DROP TABLE IF EXISTS `llx_rights_def`;
CREATE TABLE `llx_rights_def` (
  `id` int NOT NULL AUTO_INCREMENT,
  `libelle` varchar(255) DEFAULT NULL,
  `module` varchar(64) DEFAULT NULL,
  `entity` int NOT NULL DEFAULT '1',
  `perms` varchar(50) DEFAULT NULL,
  `subperms` varchar(50) DEFAULT NULL,
  `type` varchar(1) DEFAULT 'w',
  `bydefault` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `llx_rights_def` VALUES
(1, 'Read users', 'user', 1, 'user', 'lire', 'r', 1),
(2, 'Create/modify users', 'user', 1, 'user', 'creer', 'w', 0),
(3, 'Delete users', 'user', 1, 'user', 'supprimer', 'w', 0),
(4, 'Read third parties', 'societe', 1, 'societe', 'lire', 'r', 1),
(5, 'Create/modify third parties', 'societe', 1, 'societe', 'creer', 'w', 0),
(6, 'Read invoices', 'facture', 1, 'facture', 'lire', 'r', 1),
(7, 'Create invoices', 'facture', 1, 'facture', 'creer', 'w', 0),
(8, 'Read products', 'product', 1, 'produit', 'lire', 'r', 1),
(9, 'Create products', 'product', 1, 'produit', 'creer', 'w', 0);

-- --------------------------------------------------------
-- Table: llx_c_country - Country codes
-- --------------------------------------------------------

DROP TABLE IF EXISTS `llx_c_country`;
CREATE TABLE `llx_c_country` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `code` varchar(2) NOT NULL,
  `label` varchar(50) DEFAULT NULL,
  `active` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`rowid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `llx_c_country` VALUES
(1, 'US', 'United States', 1),
(2, 'FR', 'France', 1),
(3, 'DE', 'Germany', 1),
(4, 'GB', 'United Kingdom', 1),
(5, 'ES', 'Spain', 1);

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
