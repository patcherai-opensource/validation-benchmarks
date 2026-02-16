<?php
    include '../config.php';
    include '../misc.php';

    session_start();

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
    $stmt = $pdo->query("SELECT id, email, firstname, lastname, created_at FROM customers ORDER BY id ASC");
    $customers = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>
<!doctype html>
<html>
    <head>
        <title>Customers - Velora CMS</title>
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
            <h1>Customers</h1>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Email</th>
                        <th>First Name</th>
                        <th>Last Name</th>
                        <th>Registered</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($customers as $c): ?>
                        <tr>
                            <td><?php echo $c['id']; ?></td>
                            <td><?php echo htmlspecialchars($c['email']); ?></td>
                            <td><?php echo htmlspecialchars($c['firstname']); ?></td>
                            <td><?php echo htmlspecialchars($c['lastname']); ?></td>
                            <td><?php echo htmlspecialchars($c['created_at']); ?></td>
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
