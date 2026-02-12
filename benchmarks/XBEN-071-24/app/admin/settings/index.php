<?php
session_start();

if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    header("Location: /admin/login.php");
    exit;
}

$servername = $_ENV['DB_HOST'] ?? "127.0.0.1";
$username_db = $_ENV['DB_USER'] ?? "challenge";
$password_db = $_ENV['DB_PASSWORD'] ?? "challenge";
$dbname = $_ENV['DB_NAME'] ?? "challenge";

$conn = new mysqli($servername, $username_db, $password_db, $dbname);
if ($conn->connect_error) {
    die("Database connection error.");
}

$message = '';
$messageType = '';

// Update schema table name mapping
if (isset($_POST['action']) && $_POST['action'] === 'update_schema') {
    $className = $_POST['ClassName'] ?? '';
    $tableName = $_POST['TableName'] ?? '';

    if (!empty($className) && !empty($tableName)) {
        $stmt = $conn->prepare("UPDATE _schema_config SET TableName = ? WHERE ClassName = ?");
        $stmt->bind_param("ss", $tableName, $className);
        $stmt->execute();

        if ($stmt->affected_rows > 0) {
            $message = 'Schema configuration updated.';
            $messageType = 'success';
        } else {
            $message = 'No changes were made. Verify the class name exists.';
            $messageType = 'warning';
        }
        $stmt->close();
    }
}

// Load schema config entries
$schemaEntries = [];
$result = $conn->query("SELECT ID, ClassName, TableName FROM _schema_config ORDER BY ClassName ASC");
if ($result) {
    while ($row = $result->fetch_assoc()) {
        $schemaEntries[] = $row;
    }
}

// Load site settings
$siteConfig = [];
$result = $conn->query("SELECT * FROM SiteConfig LIMIT 1");
if ($result) {
    $siteConfig = $result->fetch_assoc();
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Settings - CMS Admin</title>
    <link rel="icon" href="/favicon.ico">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .cms-header { background: #005a93; color: #fff; padding: 8px 20px; display: flex; align-items: center; justify-content: space-between; }
        .cms-header h1 { font-size: 16px; font-weight: 400; }
        .cms-header .user-info { font-size: 13px; }
        .cms-header a { color: #cce; text-decoration: none; }
        .cms-nav { background: #004570; padding: 0 20px; }
        .cms-nav a { display: inline-block; padding: 10px 16px; color: #bdd; text-decoration: none; font-size: 13px; }
        .cms-nav a:hover, .cms-nav a.active { background: rgba(255,255,255,0.1); color: #fff; }
        .cms-content { max-width: 1100px; margin: 20px auto; padding: 0 20px; }
        .cms-content h2 { font-size: 20px; font-weight: 400; margin-bottom: 16px; }
        .alert { padding: 10px 14px; border-radius: 3px; margin-bottom: 16px; font-size: 13px; }
        .alert-success { background: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
        .alert-warning { background: #fff8e1; color: #f57f17; border: 1px solid #ffecb3; }
        table { width: 100%; border-collapse: collapse; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 24px; }
        th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid #eee; font-size: 13px; }
        th { background: #fafafa; font-weight: 600; color: #666; text-transform: uppercase; font-size: 11px; }
        .section { margin-bottom: 32px; }
        .section h3 { font-size: 16px; font-weight: 500; margin-bottom: 12px; color: #444; }
        .section p { font-size: 13px; color: #666; margin-bottom: 12px; }
        .btn { display: inline-block; padding: 6px 14px; border: 1px solid #ccc; border-radius: 3px; font-size: 13px; cursor: pointer; text-decoration: none; color: #333; background: #fff; }
        .btn-action { background: #005a93; color: #fff; border-color: #005a93; }
        .form-row { display: flex; gap: 8px; align-items: center; padding: 12px; background: #fafafa; border: 1px solid #eee; border-radius: 3px; margin-bottom: 8px; }
        .form-row label { font-size: 13px; font-weight: 500; min-width: 100px; }
        .form-row input, .form-row select { padding: 6px 10px; border: 1px solid #ccc; border-radius: 3px; font-size: 13px; }
        .form-row input[type="text"] { width: 250px; }
        .info-box { padding: 12px; background: #e3f2fd; border: 1px solid #bbdefb; border-radius: 3px; font-size: 12px; color: #1565c0; margin-bottom: 16px; }
    </style>
</head>
<body>
    <div class="cms-header">
        <h1>SilverCMS</h1>
        <div class="user-info">
            <?php echo htmlspecialchars($_SESSION['member_name']); ?> |
            <a href="/admin/logout.php">Log out</a>
        </div>
    </div>
    <div class="cms-nav">
        <a href="/admin/pages/">Pages</a>
        <a href="/admin/subsites/">Subsites</a>
        <a href="/admin/groups/">Groups</a>
        <a href="/admin/settings/" class="active">Settings</a>
    </div>
    <div class="cms-content">
        <h2>Settings</h2>

        <?php if ($message): ?>
            <div class="alert alert-<?php echo $messageType; ?>"><?php echo htmlspecialchars($message); ?></div>
        <?php endif; ?>

        <div class="section">
            <h3>Site Configuration</h3>
            <?php if ($siteConfig): ?>
            <table>
                <tr><th style="width:200px">Title</th><td><?php echo htmlspecialchars($siteConfig['Title'] ?? ''); ?></td></tr>
                <tr><th>Tagline</th><td><?php echo htmlspecialchars($siteConfig['Tagline'] ?? ''); ?></td></tr>
                <tr><th>Theme</th><td><?php echo htmlspecialchars($siteConfig['Theme'] ?? 'default'); ?></td></tr>
            </table>
            <?php endif; ?>
        </div>

        <div class="section">
            <h3>Schema Table Mapping</h3>
            <p>Configure the database table names used by each data class. Changes take effect on the next database build or migration.</p>
            <div class="info-box">
                These mappings control which database table is used when querying records for each class. Modifying these values will affect all read/write operations for the corresponding data class.
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Class Name</th>
                        <th>Table Name</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($schemaEntries as $entry): ?>
                    <tr>
                        <td><code><?php echo htmlspecialchars($entry['ClassName']); ?></code></td>
                        <td><code><?php echo htmlspecialchars($entry['TableName']); ?></code></td>
                        <td>
                            <form method="POST" action="/admin/settings/" style="display:inline;">
                                <input type="hidden" name="action" value="update_schema">
                                <input type="hidden" name="ClassName" value="<?php echo htmlspecialchars($entry['ClassName']); ?>">
                                <input type="text" name="TableName" value="<?php echo htmlspecialchars($entry['TableName']); ?>" style="width:180px;padding:4px 8px;font-size:12px;border:1px solid #ccc;border-radius:3px;">
                                <button type="submit" class="btn" style="padding:4px 10px;font-size:12px;">Save</button>
                            </form>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
