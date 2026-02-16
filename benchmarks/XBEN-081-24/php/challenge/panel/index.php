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

    // Dashboard stats
    $stats = [];
    $stats['products'] = $pdo->query("SELECT COUNT(*) FROM products")->fetchColumn();
    $stats['categories'] = $pdo->query("SELECT COUNT(*) FROM categories")->fetchColumn();
    $stats['customers'] = $pdo->query("SELECT COUNT(*) FROM customers")->fetchColumn();
    $stats['orders'] = $pdo->query("SELECT COUNT(*) FROM orders")->fetchColumn();

    // Recent orders
    $stmt = $pdo->query("SELECT o.id, o.ref, o.total_amount, o.status, o.created_at, c.email as customer_email FROM orders o LEFT JOIN customers c ON o.customer_id = c.id ORDER BY o.created_at DESC LIMIT 5");
    $recent_orders = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>
<!doctype html>
<html>
    <head>
        <title>Administration - Velora CMS</title>
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
            <h1>Dashboard</h1>
            <p>Welcome, <?php echo htmlspecialchars($_SESSION['admin_name']); ?></p>

            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Products</h3>
                    <p class="stat-number"><?php echo $stats['products']; ?></p>
                </div>
                <div class="stat-card">
                    <h3>Categories</h3>
                    <p class="stat-number"><?php echo $stats['categories']; ?></p>
                </div>
                <div class="stat-card">
                    <h3>Customers</h3>
                    <p class="stat-number"><?php echo $stats['customers']; ?></p>
                </div>
                <div class="stat-card">
                    <h3>Orders</h3>
                    <p class="stat-number"><?php echo $stats['orders']; ?></p>
                </div>
            </div>

            <h2>Recent Orders</h2>
            <?php if (empty($recent_orders)): ?>
                <p>No orders yet.</p>
            <?php else: ?>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Ref</th>
                            <th>Customer</th>
                            <th>Amount</th>
                            <th>Status</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($recent_orders as $order): ?>
                            <tr>
                                <td><?php echo htmlspecialchars($order['ref']); ?></td>
                                <td><?php echo htmlspecialchars($order['customer_email']); ?></td>
                                <td>&euro; <?php echo number_format($order['total_amount'], 2); ?></td>
                                <td><?php echo htmlspecialchars($order['status']); ?></td>
                                <td><?php echo htmlspecialchars($order['created_at']); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php endif; ?>
        </div>

        <div class="footer">
            <p>&copy; 2024 Velora CMS Administration</p>
        </div>
    </body>
</html>
