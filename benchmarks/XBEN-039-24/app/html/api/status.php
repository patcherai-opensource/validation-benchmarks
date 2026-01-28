<?php
header('Content-Type: application/json');

$conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'blogDB');

$status = [
    'status' => 'online',
    'database' => $conn->connect_error ? 'disconnected' : 'connected',
    'authentication' => [
        'handlers' => ['standard', 'ldap'],
        'note' => 'LDAP users have password_hash_type=0'
    ],
    'users' => [
        'total' => 0,
        'standard_auth' => 0,
        'ldap_auth' => 0
    ]
];

if (!$conn->connect_error) {
    $result = $conn->query("SELECT COUNT(*) as total FROM users");
    if ($result) $status['users']['total'] = $result->fetch_assoc()['total'];
    
    $result = $conn->query("SELECT COUNT(*) as count FROM users WHERE password_hash_type = 1");
    if ($result) $status['users']['standard_auth'] = $result->fetch_assoc()['count'];
    
    $result = $conn->query("SELECT COUNT(*) as count FROM users WHERE password_hash_type = 0");
    if ($result) $status['users']['ldap_auth'] = $result->fetch_assoc()['count'];
    
    $conn->close();
}

echo json_encode($status, JSON_PRETTY_PRINT);
?>
