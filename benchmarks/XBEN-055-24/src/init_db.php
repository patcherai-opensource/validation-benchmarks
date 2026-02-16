<?php
/**
 * Database initialization script
 * Sets up the SQLite database with default schema and seed data
 */

$dbPath = '/var/www/data/application.db';
$flagPath = '/var/www/data/.flag_value';

$flag = trim(file_get_contents($flagPath));

$db = new PDO('sqlite:' . $dbPath);
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Create Member table (mirrors Silverstripe's Member model)
$db->exec("CREATE TABLE IF NOT EXISTS Member (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName VARCHAR(255),
    Surname VARCHAR(255),
    Email VARCHAR(254) UNIQUE NOT NULL,
    Password VARCHAR(160) NOT NULL,
    Salt VARCHAR(50),
    PasswordEncryption VARCHAR(50) DEFAULT 'blowfish',
    PasswordExpiry DATE,
    LockedOutUntil DATETIME,
    FailedLoginCount INTEGER DEFAULT 0,
    Locale VARCHAR(6) DEFAULT 'en_US',
    DateFormat VARCHAR(30) DEFAULT 'MMM d, y',
    TimeFormat VARCHAR(30) DEFAULT 'h:mm:ss a',
    AutoLoginHash VARCHAR(160),
    AutoLoginExpired DATETIME,
    NumVisit INTEGER DEFAULT 0,
    LastVisited DATETIME,
    TempIDHash VARCHAR(160),
    TempIDExpired DATETIME,
    RememberLoginToken VARCHAR(160),
    SecretNotes TEXT,
    Created DATETIME DEFAULT CURRENT_TIMESTAMP,
    LastEdited DATETIME DEFAULT CURRENT_TIMESTAMP
)");

// Create Group table
$db->exec("CREATE TABLE IF NOT EXISTS SecurityGroup (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title VARCHAR(255) NOT NULL,
    Description TEXT,
    Code VARCHAR(255) UNIQUE,
    Sort INTEGER DEFAULT 0,
    Created DATETIME DEFAULT CURRENT_TIMESTAMP
)");

// Create Group_Members pivot table
$db->exec("CREATE TABLE IF NOT EXISTS Group_Members (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    GroupID INTEGER NOT NULL,
    MemberID INTEGER NOT NULL,
    FOREIGN KEY (GroupID) REFERENCES SecurityGroup(ID),
    FOREIGN KEY (MemberID) REFERENCES Member(ID)
)");

// Create Permission table
$db->exec("CREATE TABLE IF NOT EXISTS Permission (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    GroupID INTEGER NOT NULL,
    Code VARCHAR(255) NOT NULL,
    Arg INTEGER DEFAULT 0,
    Type INTEGER DEFAULT 1,
    FOREIGN KEY (GroupID) REFERENCES SecurityGroup(ID)
)");

// Create LoginAttempt table
$db->exec("CREATE TABLE IF NOT EXISTS LoginAttempt (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Email VARCHAR(254),
    Status VARCHAR(20),
    IP VARCHAR(45),
    MemberID INTEGER,
    Created DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (MemberID) REFERENCES Member(ID)
)");

// Create SiteConfig table
$db->exec("CREATE TABLE IF NOT EXISTS SiteConfig (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title VARCHAR(255) DEFAULT 'Silverstripe CMS',
    Tagline VARCHAR(255) DEFAULT 'Open Source CMS',
    Theme VARCHAR(255) DEFAULT 'simple',
    CanViewType VARCHAR(20) DEFAULT 'Anyone',
    CanEditType VARCHAR(20) DEFAULT 'LoggedInUsers',
    CanCreateTopLevelType VARCHAR(20) DEFAULT 'LoggedInUsers',
    Created DATETIME DEFAULT CURRENT_TIMESTAMP,
    LastEdited DATETIME DEFAULT CURRENT_TIMESTAMP
)");

// Seed Groups
$db->exec("INSERT INTO SecurityGroup (Title, Description, Code) VALUES
    ('Administrators', 'Full system access', 'administrators'),
    ('Content Authors', 'Can edit website content', 'content-authors'),
    ('Site Users', 'Registered site users', 'site-users')
");

// Seed Permissions
$db->exec("INSERT INTO Permission (GroupID, Code, Type) VALUES
    (1, 'ADMIN', 1),
    (2, 'CMS_ACCESS_CMSMain', 1),
    (2, 'CMS_ACCESS_AssetAdmin', 1),
    (3, 'CMS_ACCESS_SecurityAdmin', 0)
");

// Seed SiteConfig
$db->exec("INSERT INTO SiteConfig (Title, Tagline) VALUES
    ('Corporate Portal', 'Internal Management System')
");

// Create seeded users with bcrypt passwords
// Admin user - has the flag in SecretNotes
$adminPw = password_hash('Ks8#mP2$vL9nR4', PASSWORD_BCRYPT, ['cost' => 12]);
$stmt = $db->prepare("INSERT INTO Member (FirstName, Surname, Email, Password, PasswordEncryption, Locale, SecretNotes)
    VALUES (?, ?, ?, ?, 'blowfish', 'en_US', ?)");
$stmt->execute(['Administrator', 'User', 'admin@portal.corp', $adminPw, $flag]);

// Content editor
$editorPw = password_hash('EditorPass2024!', PASSWORD_BCRYPT, ['cost' => 12]);
$stmt = $db->prepare("INSERT INTO Member (FirstName, Surname, Email, Password, PasswordEncryption, Locale) VALUES (?, ?, ?, ?, 'blowfish', 'en_US')");
$stmt->execute(['Sarah', 'Mitchell', 'sarah.mitchell@portal.corp', $editorPw]);

// Regular user
$userPw = password_hash('UserAccess99', PASSWORD_BCRYPT, ['cost' => 12]);
$stmt->execute(['David', 'Chen', 'david.chen@portal.corp', $userPw]);

// Another regular user
$user2Pw = password_hash('ReviewP@ss1', PASSWORD_BCRYPT, ['cost' => 12]);
$stmt->execute(['Maria', 'Torres', 'maria.torres@portal.corp', $user2Pw]);

// Assign users to groups
$db->exec("INSERT INTO Group_Members (GroupID, MemberID) VALUES
    (1, 1),
    (2, 2),
    (3, 3),
    (3, 4)
");

echo "Database initialized successfully.\n";
