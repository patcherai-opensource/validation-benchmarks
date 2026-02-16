<?php
session_start();
require_once __DIR__ . '/includes/config.php';

if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    header("Location: /");
    exit;
}

$conn = db_connect();
$folders = [];
$items_count = 0;

if ($conn) {
    $result = $conn->query("SELECT id, title, parent_id FROM vault_folders ORDER BY parent_id, title");
    if ($result) {
        while ($row = $result->fetch_assoc()) {
            $folders[] = $row;
        }
    }

    $result = $conn->query("SELECT COUNT(*) as cnt FROM vault_items WHERE inactif = 0");
    if ($result) {
        $row = $result->fetch_assoc();
        $items_count = $row['cnt'];
    }
    $conn->close();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VaultPass - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f6fa; color: #2c3e50; }
        .header { background: #2c3e50; color: white; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 22px; }
        .header a { color: #aaa; text-decoration: none; font-size: 14px; }
        .header a:hover { color: white; }
        .container { max-width: 960px; margin: 30px auto; padding: 0 20px; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 30px; }
        .stat-card { background: white; border-radius: 8px; padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
        .stat-card .label { font-size: 13px; color: #888; margin-bottom: 4px; }
        .stat-card .value { font-size: 28px; font-weight: 700; color: #2c3e50; }
        .card { background: white; border-radius: 8px; padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); margin-bottom: 20px; }
        .card h3 { margin-bottom: 16px; font-size: 16px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 14px; }
        th { font-weight: 600; color: #888; font-size: 12px; text-transform: uppercase; }
    </style>
</head>
<body>
    <div class="header">
        <h1>VaultPass</h1>
        <div>
            <span style="margin-right: 16px;">Welcome, <?php echo htmlspecialchars($_SESSION['user_login']); ?></span>
            <a href="/logout.php">Sign Out</a>
        </div>
    </div>
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <div class="label">Total Items</div>
                <div class="value"><?php echo $items_count; ?></div>
            </div>
            <div class="stat-card">
                <div class="label">Folders</div>
                <div class="value"><?php echo count($folders); ?></div>
            </div>
            <div class="stat-card">
                <div class="label">Active Users</div>
                <div class="value">3</div>
            </div>
        </div>
        <div class="card">
            <h3>Vault Folders</h3>
            <table>
                <thead>
                    <tr><th>ID</th><th>Folder Name</th><th>Parent</th></tr>
                </thead>
                <tbody>
                    <?php foreach ($folders as $f): ?>
                    <tr>
                        <td><?php echo (int)$f['id']; ?></td>
                        <td><?php echo htmlspecialchars($f['title']); ?></td>
                        <td><?php echo $f['parent_id'] == 0 ? '—' : (int)$f['parent_id']; ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
