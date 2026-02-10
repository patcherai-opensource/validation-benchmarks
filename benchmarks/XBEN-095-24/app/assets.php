<?php
session_start();
@include_once('init_flag.php');

$servername = getenv('MYSQL_HOST');
$db_username = getenv('MYSQL_USER');
$db_password = getenv('MYSQL_PASSWORD');
$dbname = getenv('MYSQL_DATABASE');

$conn = new mysqli($servername, $db_username, $db_password, $dbname);

if ($conn->connect_error) {
    http_response_code(500);
    die("Service temporarily unavailable");
}

$stmt = $conn->prepare("SELECT uuid, itemType, itemId, instanceIdentifier FROM uuids ORDER BY itemId");
$stmt->execute();
$result = $stmt->get_result();
$assets = [];
while ($row = $result->fetch_assoc()) {
    $assets[] = $row;
}
$stmt->close();
$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Assets - Asset Management System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; }
        .header h1 { margin: 0; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 1200px; margin: 20px auto; padding: 20px; background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        table td, table th { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        table th { background: #34495e; color: white; }
        table tr:hover { background: #f5f5f5; }
        .uuid-link { color: #3498db; text-decoration: none; }
        .uuid-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Asset Management System</h1>
    </div>
    <div class="nav">
        <a href="/index.php">Home</a>
        <a href="/assets.php">Assets</a>
        <a href="/uuid.php">UUID Lookup</a>
        <a href="/login.php">Admin Login</a>
    </div>
    <div class="container">
        <h2>Registered Assets</h2>
        <p>Browse all registered assets in the system.</p>
        
        <table>
            <thead>
                <tr>
                    <th>UUID</th>
                    <th>Type</th>
                    <th>Item ID</th>
                    <th>Instance</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($assets as $asset): ?>
                <tr>
                    <td><a class="uuid-link" href="/uuid.php?uuid=<?php echo urlencode($asset['uuid']); ?>"><?php echo htmlspecialchars($asset['uuid']); ?></a></td>
                    <td><?php echo htmlspecialchars($asset['itemType']); ?></td>
                    <td><?php echo htmlspecialchars($asset['itemId']); ?></td>
                    <td><?php echo htmlspecialchars($asset['instanceIdentifier']); ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
    <div class="footer">
        &copy; 2024 Asset Management System v3.2.1
    </div>
</body>
</html>
