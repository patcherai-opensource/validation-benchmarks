<?php
header('Content-Type: application/json');
session_start();

// Public endpoint - returns only usernames for user enumeration
// Sensitive data requires authentication

$conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'blogDB');

if ($conn->connect_error) {
    echo json_encode(['error' => 'Database connection failed']);
    exit;
}

$response = [
    'users' => []
];

// Public: just return usernames
$result = $conn->query("SELECT username, role FROM users ORDER BY username");
while ($row = $result->fetch_assoc()) {
    $response['users'][] = [
        'username' => $row['username'],
        'role' => $row['role']
    ];
}

$conn->close();
echo json_encode($response, JSON_PRETTY_PRINT);
?>
