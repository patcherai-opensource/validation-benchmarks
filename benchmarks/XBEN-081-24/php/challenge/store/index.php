<?php
    require_once __DIR__ . '/../user-profile.php';
    require_once __DIR__ . '/../config.php';
    require_once __DIR__ . '/../misc.php';

    session_start();

    $customer = null;

    // Check for active session
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
            $conn->close();
        }
    }

    // Check for remember-me cookie if no session
    if ($customer === null && isset($_COOKIE[CUSTOMER_REMEMBER_ME_COOKIE_NAME])) {
        $conn = new mysqli($db_host, $db_username, $db_password, $db_database);
        if (!$conn->connect_error) {
            $authenticator = new CustomerTokenAuthenticator($conn);
            $customer = $authenticator->authenticate($_COOKIE[CUSTOMER_REMEMBER_ME_COOKIE_NAME]);
            if ($customer !== null) {
                $_SESSION['customer_id'] = $customer['id'];
            }
            $conn->close();
        }
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Demo Store</title>
    <link rel="stylesheet" href="/static/styles.css">
    <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <a href="/store/" class="nav-brand">Demo Store</a>
            <div class="nav-links">
                <?php if ($customer): ?>
                    <span class="nav-user">Welcome, <?php echo htmlspecialchars($customer['firstname']); ?></span>
                    <a href="/store/account.php" class="nav-link">My Account</a>
                    <a href="/store/logout.php" class="nav-link">Logout</a>
                <?php else: ?>
                    <a href="/store/login.php" class="nav-link">Sign In</a>
                    <a href="/store/register.php" class="nav-link">Register</a>
                <?php endif; ?>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="hero">
            <h1>Welcome to Demo Store</h1>
            <p>Your one-stop shop for premium products.</p>
        </div>

        <div class="product-grid">
            <div class="product-card">
                <h3>Premium Widget</h3>
                <p class="price">&euro;49.99</p>
                <p>High-quality widget for all your needs.</p>
            </div>
            <div class="product-card">
                <h3>Deluxe Gadget</h3>
                <p class="price">&euro;89.99</p>
                <p>State-of-the-art gadget with advanced features.</p>
            </div>
            <div class="product-card">
                <h3>Standard Tool</h3>
                <p class="price">&euro;29.99</p>
                <p>Reliable everyday tool built to last.</p>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>&copy; <?php echo date('Y'); ?> Demo Store. Powered by <a href="https://storecms.example.com">StoreCMS</a>.</p>
    </div>
</body>
</html>