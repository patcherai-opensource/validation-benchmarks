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

    if (!isset($_SESSION['customer_id'])) {
        header("Location: customer-login.php");
        exit();
    }

    $pdo = getDbConnection();
    $orders = [];
    $stmt = $pdo->prepare("SELECT id, ref, total_amount, status, created_at FROM orders WHERE customer_id = ? ORDER BY created_at DESC");
    $stmt->execute([$_SESSION['customer_id']]);
    $orders = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>
<!doctype html>
<html>
    <head>
        <title>My Account - Velora Shop</title>
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
                    <a href="account.php">My Account</a>
                    <a href="customer-logout.php">Logout</a>
                </nav>
            </div>
        </div>

        <div class="container">
            <h1>My Account</h1>
            <p>Welcome, <?php echo htmlspecialchars($_SESSION['customer_name']); ?> (<?php echo htmlspecialchars($_SESSION['customer_email']); ?>)</p>

            <h2>Order History</h2>
            <?php if (empty($orders)): ?>
                <p>No orders found.</p>
            <?php else: ?>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Order Ref</th>
                            <th>Amount</th>
                            <th>Status</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($orders as $order): ?>
                            <tr>
                                <td><?php echo htmlspecialchars($order['ref']); ?></td>
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
            <p>&copy; 2024 Velora Shop &mdash; Powered by Velora CMS</p>
        </div>
    </body>
</html>
