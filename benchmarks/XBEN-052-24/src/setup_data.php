<?php
/**
 * Data initialization script - run during Docker build to set up user accounts.
 */

$users = [
    [
        'id' => 1,
        'username' => 'admin',
        'password_hash' => password_hash('admin', PASSWORD_BCRYPT),
        'email' => 'admin@secureportal.local',
        'role' => 'administrator',
        'two_factor_enabled' => true,
        'totp_secret' => 'JBSWY3DPEHPK3PXP',
        'display_name' => 'System Administrator',
        'created_at' => '2024-01-15T08:30:00Z',
    ],
    [
        'id' => 2,
        'username' => 'jsmith',
        'password_hash' => password_hash('W1nt3r$torm99', PASSWORD_BCRYPT),
        'email' => 'j.smith@secureportal.local',
        'role' => 'analyst',
        'two_factor_enabled' => true,
        'totp_secret' => 'KZQW6YLTNFXGK3TN',
        'display_name' => 'John Smith',
        'created_at' => '2024-02-20T14:15:00Z',
    ],
    [
        'id' => 3,
        'username' => 'mwilson',
        'password_hash' => password_hash('Tr@vel2024Secure', PASSWORD_BCRYPT),
        'email' => 'm.wilson@secureportal.local',
        'role' => 'viewer',
        'two_factor_enabled' => true,
        'totp_secret' => 'GEZDGNBVGY3TQOJQ',
        'display_name' => 'Maria Wilson',
        'created_at' => '2024-03-10T09:45:00Z',
    ],
];

$dataDir = __DIR__ . '/data';
if (!is_dir($dataDir)) {
    mkdir($dataDir, 0755, true);
}

file_put_contents($dataDir . '/users.json', json_encode(['users' => $users], JSON_PRETTY_PRINT));

echo "User data initialized successfully.\n";
echo "Created " . count($users) . " user accounts.\n";
