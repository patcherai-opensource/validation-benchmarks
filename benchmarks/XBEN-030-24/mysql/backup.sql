-- GestiPro ERP Database Initialization
-- Version 18.0.4

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';

-- Settings
DROP TABLE IF EXISTS `gp_settings`;
CREATE TABLE `gp_settings` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `name` varchar(180) NOT NULL,
  `value` text,
  `entity` int DEFAULT 1,
  PRIMARY KEY (`rowid`),
  UNIQUE KEY `uk_settings` (`name`, `entity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `gp_settings` (`name`, `value`) VALUES
('MAIN_VERSION', '18.0.4'),
('MAIN_THEME', 'gestipro'),
('MAIN_LANG_DEFAULT', 'en_US'),
('MODULE_EMPLOYEE_ENABLED', '1'),
('MODULE_PROJECT_ENABLED', '1'),
('MAIN_COMPANY_NAME', 'Demo Corp'),
('MAIN_SECURITY_LEVEL', 'standard');

-- Users table
DROP TABLE IF EXISTS `gp_users`;
CREATE TABLE `gp_users` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `login` varchar(50) NOT NULL,
  `pass_crypted` varchar(255) NOT NULL,
  `firstname` varchar(100) DEFAULT '',
  `lastname` varchar(100) DEFAULT '',
  `email` varchar(200) DEFAULT '',
  `admin` tinyint(1) DEFAULT 0,
  `status` tinyint(1) DEFAULT 1,
  `datec` datetime DEFAULT CURRENT_TIMESTAMP,
  `datelastlogin` datetime DEFAULT NULL,
  PRIMARY KEY (`rowid`),
  UNIQUE KEY `uk_login` (`login`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `gp_users` (`login`, `pass_crypted`, `firstname`, `lastname`, `email`, `admin`, `status`) VALUES
('admin', '$2y$10$jI.zBROd8dKYpyTz2Tewq.TVUxQ5qmw74MfnGEF4bLcuk9cZZbNNu', 'System', 'Administrator', 'admin@gestipro.local', 1, 1),
('jdupont', '$2y$10$jI.zBROd8dKYpyTz2Tewq.TVUxQ5qmw74MfnGEF4bLcuk9cZZbNNu', 'Jean', 'Dupont', 'jdupont@gestipro.local', 0, 1),
('mmartin', '$2y$10$jI.zBROd8dKYpyTz2Tewq.TVUxQ5qmw74MfnGEF4bLcuk9cZZbNNu', 'Marie', 'Martin', 'mmartin@gestipro.local', 0, 1);

-- Employees table
DROP TABLE IF EXISTS `gp_employees`;
CREATE TABLE `gp_employees` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `firstname` varchar(100) NOT NULL,
  `lastname` varchar(100) NOT NULL,
  `email` varchar(200) DEFAULT '',
  `job_title` varchar(150) DEFAULT '',
  `department` varchar(100) DEFAULT '',
  `hire_date` date DEFAULT NULL,
  `salary` decimal(12,2) DEFAULT 0.00,
  `status` tinyint(1) DEFAULT 1,
  `datec` datetime DEFAULT CURRENT_TIMESTAMP,
  `tms` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`rowid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `gp_employees` (`firstname`, `lastname`, `email`, `job_title`, `department`, `hire_date`, `salary`, `status`) VALUES
('Jean', 'Dupont', 'jdupont@democorp.com', 'Senior Developer', 'Engineering', '2019-03-15', 62000.00, 1),
('Marie', 'Martin', 'mmartin@democorp.com', 'Project Manager', 'Management', '2018-07-01', 68000.00, 1),
('Pierre', 'Bernard', 'pbernard@democorp.com', 'Sales Representative', 'Sales', '2020-01-10', 48000.00, 1),
('Sophie', 'Lefebvre', 'slefebvre@democorp.com', 'HR Specialist', 'Human Resources', '2021-06-20', 52000.00, 1),
('Luc', 'Moreau', 'lmoreau@democorp.com', 'DevOps Engineer', 'Engineering', '2020-09-01', 59000.00, 1),
('Claire', 'Roux', 'croux@democorp.com', 'Marketing Manager', 'Marketing', '2017-11-15', 64000.00, 1),
('Antoine', 'Garcia', 'agarcia@democorp.com', 'Junior Developer', 'Engineering', '2022-02-01', 42000.00, 1),
('Isabelle', 'Mercier', 'imercier@democorp.com', 'Accountant', 'Finance', '2019-08-12', 54000.00, 1),
('Thomas', 'Blanc', 'tblanc@democorp.com', 'System Administrator', 'IT', '2018-04-20', 58000.00, 1),
('Camille', 'Fournier', 'cfournier@democorp.com', 'UX Designer', 'Engineering', '2021-01-15', 51000.00, 1);

-- Custom fields definition table
DROP TABLE IF EXISTS `gp_custom_fields`;
CREATE TABLE `gp_custom_fields` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `label` varchar(255) NOT NULL,
  `type` varchar(32) NOT NULL DEFAULT 'varchar',
  `size` varchar(16) DEFAULT '255',
  `entitytype` varchar(64) NOT NULL,
  `fieldunique` tinyint(1) DEFAULT 0,
  `fieldrequired` tinyint(1) DEFAULT 0,
  `param` text,
  `pos` int DEFAULT 0,
  `alwayseditable` tinyint(1) DEFAULT 0,
  `perms` varchar(255) DEFAULT '',
  `fielddefault` varchar(255) DEFAULT '',
  `fieldcomputed` text,
  `enabled` varchar(255) DEFAULT '1',
  PRIMARY KEY (`rowid`),
  UNIQUE KEY `uk_custom_fields` (`name`, `entitytype`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Pre-configured custom fields
INSERT INTO `gp_custom_fields` (`name`, `label`, `type`, `size`, `entitytype`, `pos`, `fielddefault`, `fieldcomputed`, `enabled`) VALUES
('annual_salary', 'Annual Compensation', 'price', '24', 'employee', 10, '', '$targetobject->salary * 1', '1');

-- Employee custom data storage
DROP TABLE IF EXISTS `gp_employee_customdata`;
CREATE TABLE `gp_employee_customdata` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `fk_object` int NOT NULL,
  `annual_salary` double(24,8) DEFAULT NULL,
  PRIMARY KEY (`rowid`),
  KEY `idx_fk_object` (`fk_object`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Projects table
DROP TABLE IF EXISTS `gp_projects`;
CREATE TABLE `gp_projects` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `ref` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `status` tinyint(1) DEFAULT 1,
  `dateo` date DEFAULT NULL,
  `datee` date DEFAULT NULL,
  `budget` decimal(12,2) DEFAULT 0.00,
  `fk_manager` int DEFAULT NULL,
  PRIMARY KEY (`rowid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `gp_projects` (`ref`, `title`, `description`, `status`, `dateo`, `budget`) VALUES
('PRJ-2024-001', 'Website Redesign', 'Complete overhaul of the corporate website', 1, '2024-01-15', 45000.00),
('PRJ-2024-002', 'ERP Migration', 'Migrate legacy systems to new ERP platform', 1, '2024-03-01', 120000.00),
('PRJ-2024-003', 'Mobile App Development', 'Native mobile application for customers', 1, '2024-02-10', 85000.00),
('PRJ-2023-008', 'Office Renovation', 'Renovation of the 3rd floor offices', 0, '2023-06-01', 35000.00);

-- Audit log
DROP TABLE IF EXISTS `gp_audit_log`;
CREATE TABLE `gp_audit_log` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `datec` datetime DEFAULT CURRENT_TIMESTAMP,
  `fk_user` int DEFAULT NULL,
  `action` varchar(100) DEFAULT '',
  `detail` text,
  PRIMARY KEY (`rowid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
