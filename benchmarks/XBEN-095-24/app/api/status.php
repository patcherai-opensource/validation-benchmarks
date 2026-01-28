<?php
header('Content-Type: application/json');

$servername = getenv('MYSQL_HOST');
$username = getenv('MYSQL_USER');
$password = getenv('MYSQL_PASSWORD');
$dbname = getenv('MYSQL_DATABASE');

$conn = new mysqli($servername, $username, $password, $dbname);

$status = [
    'status' => 'operational',
    'version' => '2.4.1',
    'database' => $conn->connect_error ? 'disconnected' : 'connected',
    'timestamp' => date('c'),
    'endpoints' => [
        '/assets.php' => 'Asset browser',
        '/uuid.php' => 'UUID lookup service',
        '/api/status.php' => 'System status',
        '/admin/' => 'Admin panel (restricted)'
    ]
];

$conn->close();
echo json_encode($status, JSON_PRETTY_PRINT);
?>
