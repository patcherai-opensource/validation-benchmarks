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

class UuidDao {
    private $db;
    const TABLE_NAME = 'uuids';
    
    public function __construct($connection) {
        $this->db = $connection;
    }
    
    public function getByUuid($uuid) {
        $sql = "SELECT * FROM " . self::TABLE_NAME . " where uuid='" . $uuid . "'";
        $result = $this->db->query($sql);
        
        if ($result === false) {
            return null;
        }
        
        return $result->fetch_assoc();
    }
    
    public function exists($uuid) {
        $stmt = $this->db->prepare("SELECT 1 FROM " . self::TABLE_NAME . " WHERE uuid = ?");
        $stmt->bind_param("s", $uuid);
        $stmt->execute();
        $result = $stmt->get_result();
        return $result->num_rows > 0;
    }
}

$dao = new UuidDao($conn);
$asset = null;
$error = null;
$searched = false;

if (isset($_REQUEST['uuid']) && !empty($_REQUEST['uuid'])) {
    $searched = true;
    $uuid = $_REQUEST['uuid'];
    $asset = $dao->getByUuid($uuid);
    if ($asset === null) {
        $error = "Asset not found";
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UUID Lookup - Asset Management System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; }
        .header h1 { margin: 0; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 800px; margin: 20px auto; padding: 20px; background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input[type="text"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #2980b9; }
        .result { margin-top: 20px; padding: 15px; background: #ecf0f1; border-radius: 4px; }
        .result h3 { margin-top: 0; }
        .error { color: #c0392b; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }
        table { width: 100%; border-collapse: collapse; }
        table td, table th { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        table th { background: #34495e; color: white; }
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
        <h2>UUID Lookup</h2>
        <p>Enter a UUID to retrieve asset information.</p>
        
        <form action="uuid.php" method="GET">
            <div class="form-group">
                <label for="uuid">Asset UUID:</label>
                <input type="text" id="uuid" name="uuid" placeholder="e.g., 550e8400-e29b-41d4-a716-446655440000" value="<?php echo isset($_REQUEST['uuid']) ? htmlspecialchars($_REQUEST['uuid']) : ''; ?>">
            </div>
            <button type="submit" class="btn">Lookup</button>
        </form>
        
        <?php if ($searched): ?>
            <div class="result">
                <?php if ($error): ?>
                    <p class="error"><?php echo htmlspecialchars($error); ?></p>
                <?php elseif ($asset): ?>
                    <h3>Asset Details</h3>
                    <table>
                        <tr><th>Field</th><th>Value</th></tr>
                        <tr><td>UUID</td><td><?php echo htmlspecialchars($asset['uuid']); ?></td></tr>
                        <tr><td>Type</td><td><?php echo htmlspecialchars($asset['itemType']); ?></td></tr>
                        <tr><td>Item ID</td><td><?php echo htmlspecialchars($asset['itemId']); ?></td></tr>
                        <tr><td>Instance</td><td><?php echo htmlspecialchars($asset['instanceIdentifier']); ?></td></tr>
                    </table>
                <?php endif; ?>
            </div>
        <?php endif; ?>
    </div>
    <div class="footer">
        &copy; 2024 Asset Management System v3.2.1
    </div>
</body>
</html>
