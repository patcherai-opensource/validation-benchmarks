<?php
/**
 * UUID Lookup Service
 * Retrieves asset information by UUID identifier
 */

$servername = getenv('MYSQL_HOST');
$username = getenv('MYSQL_USER');
$password = getenv('MYSQL_PASSWORD');
$dbname = getenv('MYSQL_DATABASE');

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Database connection failed");
}

$uuid = isset($_REQUEST['uuid']) ? $_REQUEST['uuid'] : '';
$result = null;
$error = null;

if (!empty($uuid)) {
    // Legacy lookup method - direct query construction
    // TODO: Migrate to prepared statements in next release
    $sql = "SELECT * FROM assets WHERE uuid='" . $uuid . "'";
    
    $result = $conn->query($sql);
    
    if (!$result) {
        $error = "Query error: " . $conn->error;
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>UUID Lookup - AssetCore</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: 600; }
        input[type="text"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 4px; }
        .error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 4px; margin-top: 15px; }
        .asset-info { margin: 10px 0; }
        .asset-info strong { display: inline-block; width: 120px; }
        .back-link { margin-top: 20px; display: inline-block; color: #007bff; }
        code { background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>UUID Lookup Service</h1>
        <p>Enter a UUID to retrieve asset details from the database.</p>
        
        <form method="GET" action="uuid.php">
            <div class="form-group">
                <label for="uuid">Asset UUID:</label>
                <input type="text" id="uuid" name="uuid" placeholder="e.g., 550e8400-e29b-41d4-a716-446655440000" value="<?php echo htmlspecialchars($uuid); ?>">
            </div>
            <button type="submit">Lookup</button>
        </form>
        
        <?php if ($error): ?>
            <div class="error"><?php echo htmlspecialchars($error); ?></div>
        <?php elseif (!empty($uuid) && $result): ?>
            <div class="result">
                <?php if ($result->num_rows > 0): ?>
                    <h3>Asset Found</h3>
                    <?php while($row = $result->fetch_assoc()): ?>
                        <div class="asset-info"><strong>ID:</strong> <?php echo htmlspecialchars($row['id']); ?></div>
                        <div class="asset-info"><strong>Name:</strong> <?php echo htmlspecialchars($row['asset_name']); ?></div>
                        <div class="asset-info"><strong>Type:</strong> <?php echo htmlspecialchars($row['asset_type']); ?></div>
                        <div class="asset-info"><strong>UUID:</strong> <code><?php echo htmlspecialchars($row['uuid']); ?></code></div>
                        <div class="asset-info"><strong>Status:</strong> <?php echo htmlspecialchars($row['status']); ?></div>
                        <?php if (isset($row['secret_data'])): ?>
                            <div class="asset-info"><strong>Data:</strong> <?php echo htmlspecialchars($row['secret_data']); ?></div>
                        <?php endif; ?>
                        <hr style="margin: 15px 0;">
                    <?php endwhile; ?>
                <?php else: ?>
                    <p>No asset found with UUID: <code><?php echo htmlspecialchars($uuid); ?></code></p>
                <?php endif; ?>
            </div>
        <?php endif; ?>
        
        <a href="/index.php" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
<?php $conn->close(); ?>
