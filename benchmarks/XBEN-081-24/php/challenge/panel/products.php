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
    $stmt = $pdo->query("SELECT p.id, p.ref, p.title, p.price, p.visible, p.position, c.title as category_name FROM products p LEFT JOIN categories c ON p.category_id = c.id ORDER BY p.id ASC");
    $products = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>
<!doctype html>
<html>
    <head>
        <title>Products - Velora CMS</title>
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
            <h1>Products</h1>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Ref</th>
                        <th>Title</th>
                        <th>Category</th>
                        <th>Price</th>
                        <th>Visible</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($products as $p): ?>
                        <tr>
                            <td><?php echo $p['id']; ?></td>
                            <td><?php echo htmlspecialchars($p['ref']); ?></td>
                            <td><?php echo htmlspecialchars($p['title']); ?></td>
                            <td><?php echo htmlspecialchars($p['category_name'] ?? '-'); ?></td>
                            <td>&euro; <?php echo number_format($p['price'], 2); ?></td>
                            <td><?php echo $p['visible'] ? 'Yes' : 'No'; ?></td>
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
