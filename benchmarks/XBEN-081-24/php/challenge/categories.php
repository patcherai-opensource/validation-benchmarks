<?php
    include 'config.php';
    include 'misc.php';

    session_start();

    // Check for customer remember-me cookie
    if (!isset($_SESSION['customer_id']) && isset($_COOKIE[$customer_persist_cookie])) {
        $customer = restoreCustomerSession($_COOKIE[$customer_persist_cookie]);
        if ($customer !== null) {
            $_SESSION['customer_id'] = $customer['id'];
            $_SESSION['customer_email'] = $customer['email'];
            $_SESSION['customer_name'] = $customer['firstname'] . ' ' . $customer['lastname'];
        }
    }

    $pdo = getDbConnection();
    $categories = [];
    $stmt = $pdo->query("SELECT id, title, description FROM categories WHERE visible = 1 ORDER BY position ASC");
    $categories = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>
<!doctype html>
<html>
    <head>
        <title>Categories - Velora Shop</title>
        <link rel="stylesheet" href="static/styles.css">
        <link rel="icon" href="static/favicon.ico" type="image/x-icon">
    </head>
    <body>
        <div class="header">
            <div class="header-inner">
                <a href="index.php" class="logo">Velora</a>
                <nav>
                    <a href="index.php">Products</a>
                    <a href="categories.php">Categories</a>
                    <?php if (isset($_SESSION['customer_id'])): ?>
                        <a href="account.php">My Account</a>
                        <a href="customer-logout.php">Logout</a>
                    <?php else: ?>
                        <a href="customer-login.php">Sign In</a>
                        <a href="customer-register.php">Register</a>
                    <?php endif; ?>
                </nav>
            </div>
        </div>

        <div class="container">
            <h1>Product Categories</h1>
            <div class="category-list">
                <?php foreach ($categories as $cat): ?>
                    <div class="category-item">
                        <h3><?php echo htmlspecialchars($cat['title']); ?></h3>
                        <p><?php echo htmlspecialchars($cat['description']); ?></p>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>

        <div class="footer">
            <p>&copy; 2024 Velora Shop &mdash; Powered by Velora CMS</p>
        </div>
    </body>
</html>
