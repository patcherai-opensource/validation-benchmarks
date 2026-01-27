<?php
/**
 * AssetCore - Asset Browser
 */

$servername = getenv('MYSQL_HOST');
$username = getenv('MYSQL_USER');
$password = getenv('MYSQL_PASSWORD');
$dbname = getenv('MYSQL_DATABASE');

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Fetch public assets (using prepared statements - secure)
$sql = "SELECT id, uuid, name, type, created_at FROM assets WHERE is_public = 1";
$result = $conn->query($sql);
?>
<!DOCTYPE html>
<html>
<head>
    <title>Asset Browser - AssetCore Manager</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #3498db; color: white; }
        tr:hover { background: #f5f5f5; }
        .back-link { display: inline-block; margin-top: 20px; color: #3498db; }
        .uuid-lookup { background: #ecf0f1; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        input[type="text"] { padding: 8px; width: 300px; border: 1px solid #ddd; border-radius: 4px; }
        button { padding: 8px 16px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗂️ Asset Browser</h1>
        
        <div class="uuid-lookup">
            <strong>Quick UUID Lookup:</strong><br><br>
            <form action="/api/uuid.php" method="GET">
                <input type="text" name="uuid" placeholder="Enter asset UUID..." />
                <button type="submit">Lookup</button>
            </form>
        </div>
        
        <h3>Public Assets</h3>
        <table>
            <tr>
                <th>ID</th>
                <th>UUID</th>
                <th>Name</th>
                <th>Type</th>
                <th>Created</th>
            </tr>
            <?php
            if ($result && $result->num_rows > 0) {
                while($row = $result->fetch_assoc()) {
                    echo "<tr>";
                    echo "<td>" . htmlspecialchars($row['id']) . "</td>";
                    echo "<td>" . htmlspecialchars($row['uuid']) . "</td>";
                    echo "<td>" . htmlspecialchars($row['name']) . "</td>";
                    echo "<td>" . htmlspecialchars($row['type']) . "</td>";
                    echo "<td>" . htmlspecialchars($row['created_at']) . "</td>";
                    echo "</tr>";
                }
            } else {
                echo "<tr><td colspan='5'>No public assets available</td></tr>";
            }
            ?>
        </table>
        
        <a class="back-link" href="/index.php">← Back to Dashboard</a>
    </div>
</body>
</html>
<?php $conn->close(); ?>
