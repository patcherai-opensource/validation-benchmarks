<?php
require_once __DIR__ . '/auth.php';
requireAuth();

$conn = getDbConnection();

$configs = $conn->query("SELECT config_key, config_value FROM platform_config WHERE config_key NOT LIKE 'secret%' ORDER BY config_key ASC");

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMF Admin - Settings</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<div class="admin-layout">
    <?php include __DIR__ . '/sidebar.php'; ?>
    <div class="admin-content">
        <div class="admin-header">
            <h1>Platform Settings</h1>
        </div>
        <div class="panel">
            <table class="data-table">
                <thead>
                    <tr><th>Key</th><th>Value</th></tr>
                </thead>
                <tbody>
                <?php while ($row = $configs->fetch_assoc()): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($row['config_key']); ?></td>
                        <td><?php echo htmlspecialchars($row['config_value']); ?></td>
                    </tr>
                <?php endwhile; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>