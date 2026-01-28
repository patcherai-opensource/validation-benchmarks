<?php
// Asset browser - displays public asset information
$servername = getenv('MYSQL_HOST');
$username = getenv('MYSQL_USER');
$password = getenv('MYSQL_PASSWORD');
$dbname = getenv('MYSQL_DATABASE');

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Database error");
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Asset Browser - AssetCore</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #007bff; color: white; }
        tr:hover { background: #f5f5f5; }
        .back-link { margin-top: 20px; display: inline-block; color: #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Asset Browser</h1>
        <p>Browse available digital assets in the system.</p>
        
        <table>
            <thead>
                <tr>
                    <th>Asset Name</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>UUID</th>
                </tr>
            </thead>
            <tbody>
<?php
$result = $conn->query("SELECT asset_name, asset_type, status, uuid FROM assets WHERE status = 'public'");
if ($result && $result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        echo "<tr>";
        echo "<td>" . htmlspecialchars($row['asset_name']) . "</td>";
        echo "<td>" . htmlspecialchars($row['asset_type']) . "</td>";
        echo "<td>" . htmlspecialchars($row['status']) . "</td>";
        echo "<td><code>" . htmlspecialchars($row['uuid']) . "</code></td>";
        echo "</tr>";
    }
} else {
    echo "<tr><td colspan='4'>No public assets found.</td></tr>";
}
$conn->close();
?>
            </tbody>
        </table>
        
        <a href="/index.php" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
