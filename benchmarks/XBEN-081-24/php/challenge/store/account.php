<?php
    require_once __DIR__ . '/../user-profile.php';
    require_once __DIR__ . '/../config.php';
    require_once __DIR__ . '/../misc.php';

    session_start();

    $customer = null;

    if (isset($_SESSION['customer_id'])) {
        $conn = new mysqli($db_host, $db_username, $db_password, $db_database);
        if (!$conn->connect_error) {
            $stmt = $conn->prepare("SELECT * FROM customer WHERE id = ?");
            $stmt->bind_param("i", $_SESSION['customer_id']);
            $stmt->execute();
            $result = $stmt->get_result();
            if ($result->num_rows === 1) {
                $customer = $result->fetch_assoc();
            }
            $stmt->close();
        }
    }

    if ($customer === null && isset($_COOKIE[CUSTOMER_REMEMBER_ME_COOKIE_NAME])) {
        $conn = new mysqli($db_host, $db_username, $db_password, $db_database);
        if (!$conn->connect_error) {
            $authenticator = new CustomerTokenAuthenticator($conn);
            $customer = $authenticator->authenticate($_COOKIE[CUSTOMER_REMEMBER_ME_COOKIE_NAME]);
            if ($customer !== null) {
                $_SESSION['customer_id'] = $customer['id'];
            }
        }
    }

    if ($customer === null) {
        header("Location: /store/login.php");
        exit();
    }

    // Fetch customer orders
    $orders = array();
    $conn = new mysqli($db_host, $db_username, $db_password, $db_database);
    if (!$conn->connect_error) {
        $stmt = $conn->prepare("SELECT * FROM orders WHERE customer_id = ? ORDER BY created_at DESC");
        $stmt->bind_param("i", $customer['id']);
        $stmt->execute();
        $result = $stmt->get_result();
        while ($row = $result->fetch_assoc()) {
            $orders[] = $row;
        }
        $stmt->close();
        $conn->close();
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>My Account - Demo Store</title>
    <link rel="stylesheet" href="/static/styles.css">
    <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <a href="/store/" class="nav-brand">Demo Store</a>
            <div class="nav-links">
                <span class="nav-user">Welcome, <?php echo htmlspecialchars($customer['firstname']); ?></span>
                <a href="/store/account.php" class="nav-link active">My Account</a>
                <a href="/store/logout.php" class="nav-link">Logout</a>
            </div>
        </div>
    </div>

    <div class="container">
        <h2>My Account</h2>
        <div class="account-info">
            <h3>Personal Information</h3>
            <table class="info-table">
                <tr><td><strong>Name:</strong></td><td><?php echo htmlspecialchars($customer['firstname'] . ' ' . $customer['lastname']); ?></td></tr>
                <tr><td><strong>Email:</strong></td><td><?php echo htmlspecialchars($customer['email']); ?></td></tr>
                <tr><td><strong>Member since:</strong></td><td><?php echo htmlspecialchars($customer['created_at']); ?></td></tr>
            </table>
        </div>

        <div class="account-info">
            <h3>Order History</h3>
            <?php if (count($orders) > 0): ?>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Reference</th>
                        <th>Date</th>
                        <th>Amount</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($orders as $order): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($order['ref']); ?></td>
                        <td><?php echo htmlspecialchars($order['created_at']); ?></td>
                        <td>&euro;<?php echo number_format($order['total_amount'], 2); ?></td>
                        <td><?php echo $order['status_id'] == 4 ? 'Delivered' : 'Processing'; ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <?php else: ?>
            <p>No orders yet.</p>
            <?php endif; ?>
        </div>
    </div>

    <div class="footer">
        <p>&copy; <?php echo date('Y'); ?> Demo Store. Powered by <a href="https://storecms.example.com">StoreCMS</a>.</p>
    </div>
</body>
</html>