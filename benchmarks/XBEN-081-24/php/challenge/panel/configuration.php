<?php
    include '../config.php';
    include '../misc.php';

    session_start();

    // Check for admin persistence cookie (remember-me)
    if (!isset($_SESSION['admin_id']) && isset($_COOKIE[$admin_persist_cookie])) {
        $admin = restoreAdminSession($_COOKIE[$admin_persist_cookie]);
        if ($admin !== null) {
            $_SESSION['admin_id'] = $admin['id'];
            $_SESSION['admin_login'] = $admin['login'];
            $_SESSION['admin_name'] = $admin['firstname'] . ' ' . $admin['lastname'];
        }
    }

    if (!isset($_SESSION['admin_id'])) {
        header("Location: login.php");
        exit();
    }

    $pdo = getDbConnection();

    // Get all configuration entries
    $stmt = $pdo->query("SELECT name, value, secured, created_at, updated_at FROM configuration ORDER BY name ASC");
    $configs = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>
<!doctype html>
<html>
    <head>
        <title>Configuration - Velora CMS</title>
        <link rel="stylesheet" href="../static/styles.css">
        <link rel="icon" href="../static/favicon.ico" type="image/x-icon">
    </head>
    <body>
        <div class="admin-header">
            <div class="header-inner">
                <a href="index.php" class="logo">Velora Admin</a>
                <nav>
                    <a href="index.php">Dashboard</a>
                    <a href="products.php">Products</a>
                    <a href="customers.php">Customers</a>
                    <a href="configuration.php">Configuration</a>
                    <a href="logout.php">Logout (<?php echo htmlspecialchars($_SESSION['admin_login']); ?>)</a>
                </nav>
            </div>
        </div>

        <div class="container">
            <h1>System Configuration</h1>

            <table class="data-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Value</th>
                        <th>Secured</th>
                        <th>Updated</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($configs as $cfg): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($cfg['name']); ?></td>
                            <td>
                                <?php if ($cfg['secured']): ?>
                                    <?php echo htmlspecialchars($cfg['value']); ?>
                                <?php else: ?>
                                    <?php echo htmlspecialchars($cfg['value']); ?>
                                <?php endif; ?>
                            </td>
                            <td><?php echo $cfg['secured'] ? 'Yes' : 'No'; ?></td>
                            <td><?php echo htmlspecialchars($cfg['updated_at']); ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>&copy; 2024 Velora CMS Administration</p>
        </div>
    </body>
</html>
