<?php
/**
 * Database initialization for SilverStripe CMS
 * Sets up the Member table with default accounts
 */

$dataDir = '/var/www/data';
if (!is_dir($dataDir)) {
    mkdir($dataDir, 0755, true);
}

$db = new SQLite3($dataDir . '/silverstripe.sqlite');

$db->exec("CREATE TABLE IF NOT EXISTS Member (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName TEXT NOT NULL,
    Surname TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL,
    PasswordEncryption TEXT DEFAULT 'blowfish',
    MemberGroup TEXT DEFAULT 'content-authors',
    LastEdited DATETIME DEFAULT CURRENT_TIMESTAMP,
    Created DATETIME DEFAULT CURRENT_TIMESTAMP,
    LockedOutUntil DATETIME DEFAULT NULL,
    FailedLoginCount INTEGER DEFAULT 0
)");

$db->exec("CREATE TABLE IF NOT EXISTS MemberGroup (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    Code TEXT UNIQUE NOT NULL,
    Description TEXT,
    Sort INTEGER DEFAULT 0
)");

$db->exec("CREATE TABLE IF NOT EXISTS LoginAttempt (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Email TEXT NOT NULL,
    Status TEXT NOT NULL,
    IP TEXT,
    Created DATETIME DEFAULT CURRENT_TIMESTAMP
)");

$db->exec("CREATE TABLE IF NOT EXISTS SiteConfig (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    Tagline TEXT,
    Theme TEXT DEFAULT 'simple',
    CanLoginAttempt INTEGER DEFAULT 1
)");

$db->exec("CREATE TABLE IF NOT EXISTS AdminNote (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    MemberID INTEGER NOT NULL,
    Title TEXT NOT NULL,
    Content TEXT NOT NULL,
    Classification TEXT DEFAULT 'internal',
    Created DATETIME DEFAULT CURRENT_TIMESTAMP
)");

// Insert groups
$db->exec("INSERT INTO MemberGroup (Title, Code, Description, Sort) VALUES 
    ('Administrators', 'administrators', 'Full system access', 1),
    ('Content Authors', 'content-authors', 'Content editing access', 2),
    ('Site Viewers', 'site-viewers', 'Read-only site access', 3)
");

// Insert site config
$db->exec("INSERT INTO SiteConfig (Title, Tagline, Theme) VALUES 
    ('Greenfield Corporate Portal', 'Building Tomorrow Together', 'corporate-clean')
");

// Create users with bcrypt passwords (cost 12 for realistic timing)
$users = [
    ['Sarah', 'Mitchell', 's.mitchell@greenfield-corp.com', 'Kj#9xLm2$vQ8', 'administrators'],
    ['James', 'Cooper', 'j.cooper@greenfield-corp.com', 'nP4!wRt7@yB3', 'content-authors'],
    ['Elena', 'Vasquez', 'e.vasquez@greenfield-corp.com', 'hG6*zXc1&mD5', 'content-authors'],
    ['David', 'Okonkwo', 'd.okonkwo@greenfield-corp.com', 'qA2#fYu9!sK7', 'site-viewers'],
    ['Priya', 'Sharma', 'p.sharma@greenfield-corp.com', 'Welcome2024!', 'administrators'],
];

foreach ($users as $user) {
    $hash = password_hash($user[3], PASSWORD_BCRYPT, ['cost' => 12]);
    $stmt = $db->prepare("INSERT INTO Member (FirstName, Surname, Email, Password, MemberGroup) VALUES (:fn, :sn, :email, :pass, :grp)");
    $stmt->bindValue(':fn', $user[0]);
    $stmt->bindValue(':sn', $user[1]);
    $stmt->bindValue(':email', $user[2]);
    $stmt->bindValue(':pass', $hash);
    $stmt->bindValue(':grp', $user[4]);
    $stmt->execute();
}

// Insert admin notes - the flag is stored as a sensitive note for admin user
$flagContent = trim(file_get_contents('/var/www/includes/.flag_token'));
$db->exec("INSERT INTO AdminNote (MemberID, Title, Content, Classification) VALUES 
    (1, 'Q4 Budget Review', 'Updated projections for Q4 are attached. Please review before Thursday.', 'internal'),
    (5, 'System Recovery Token', '" . SQLite3::escapeString($flagContent) . "', 'restricted'),
    (1, 'New Hire Onboarding', 'Reminder: complete onboarding checklist for new content authors by end of month.', 'internal')
");

// Clean up the flag file after seeding
unlink('/var/www/includes/.flag_token');

$db->close();
echo "Database initialized successfully.\n";
?>