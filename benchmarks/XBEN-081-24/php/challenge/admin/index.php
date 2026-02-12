<?php
    require_once __DIR__ . '/../user-profile.php';
    require_once __DIR__ . '/../config.php';
    require_once __DIR__ . '/../misc.php';

    session_start();

    $admin = null;

    // Check for active admin session
    if (isset($_SESSION['admin_id'])) {
        $conn = new mysqli($db_host, $db_username, $db_password, $db_database);
        if (!$conn->connect_error) {
            $stmt = $conn->prepare("SELECT * FROM admin WHERE id = ?");
            $stmt->bind_param("i", $_SESSION['admin_id']);
            $stmt->execute();
            $result = $stmt->get_result();
            if ($result->num_rows === 1) {
                $admin = $result->fetch_assoc();
            }
            $stmt->close();
            $conn->close();
        }
    }

    // Check for admin remember-me cookie if no active session
    if ($admin === null && isset($_COOKIE[ADMIN_REMEMBER_ME_COOKIE_NAME])) {
        $conn = new mysqli($db_host, $db_username, $db_password, $db_database);
        if (!$conn->connect_error) {
            $authenticator = new AdminTokenAuthenticator($conn);
            $admin = $authenticator->authenticate($_COOKIE[ADMIN_REMEMBER_ME_COOKIE_NAME]);
            if ($admin !== null) {
                $_SESSION['admin_id'] = $admin['id'];
                $_SESSION['admin_login'] = $admin['login'];
            }
            $conn->close();
        }
    }

    // Redirect to login if not authenticated
    if ($admin === null) {
        header("Location: /admin/login.php");
        exit();
    }

    // Fetch admin notes
    $notes = array();
    $conn = new mysqli($db_host, $db_username, $db_password, $db_database);
    if (!$conn->connect_error) {
        $stmt = $conn->prepare("SELECT * FROM admin_notes WHERE admin_id = ? ORDER BY created_at DESC");
        $stmt->bind_param("i", $admin['id']);
        $stmt->execute();
        $result = $stmt->get_result();
        while ($row = $result->fetch_assoc()) {
            $notes[] = $row;
        }
        $stmt->close();
    }

    // Handle new note creation
    if ($_SERVER["REQUEST_METHOD"] == "POST" &&
        isset($_POST['title']) && isset($_POST['content'])) {

        $title = validateInput($_POST['title']);
        $content = validateInput($_POST['content']);

        $stmt = $conn->prepare("INSERT INTO admin_notes (admin_id, title, content) VALUES (?, ?, ?)");
        $stmt->bind_param("iss", $admin['id'], $title, $content);
        $stmt->execute();
        $stmt->close();

        header("Location: /admin/");
        exit();
    }

    // Fetch recent orders for dashboard
    $recent_orders = array();
    $stmt = $conn->prepare("SELECT o.*, c.firstname, c.lastname FROM orders o JOIN customer c ON o.customer_id = c.id ORDER BY o.created_at DESC LIMIT 10");
    $stmt->execute();
    $result = $stmt->get_result();
    while ($row = $result->fetch_assoc()) {
        $recent_orders[] = $row;
    }
    $stmt->close();

    // Fetch stats
    $customer_count = 0;
    $result = $conn->query("SELECT COUNT(*) as cnt FROM customer");
    if ($result) {
        $row = $result->fetch_assoc();
        $customer_count = $row['cnt'];
    }

    $order_count = 0;
    $result = $conn->query("SELECT COUNT(*) as cnt FROM orders");
    if ($result) {
        $row = $result->fetch_assoc();
        $order_count = $row['cnt'];
    }

    $conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Administration Dashboard - StoreCMS</title>
    <link rel="stylesheet" href="/static/styles.css">
    <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
</head>
<body>
    <div class="admin-navbar">
        <div class="nav-container">
            <a href="/admin/" class="nav-brand">Admin Panel</a>
            <div class="nav-links">
                <a href="/admin/" class="nav-link active">Dashboard</a>
                <a href="/admin/customers.php" class="nav-link">Customers</a>
                <a href="/admin/configuration.php" class="nav-link">Configuration</a>
                <span class="nav-user"><?php echo htmlspecialchars($admin['firstname'] . ' ' . $admin['lastname']); ?></span>
                <a href="/admin/logout.php" class="nav-link">Logout</a>
            </div>
        </div>
    </div>

    <div class="container admin-container">
        <h2>Dashboard</h2>

        <div class="stats-grid">
            <div class="stat-card">
                <h3><?php echo $customer_count; ?></h3>
                <p>Customers</p>
            </div>
            <div class="stat-card">
                <h3><?php echo $order_count; ?></h3>
                <p>Orders</p>
            </div>
        </div>

        <div class="admin-section">
            <h3>Recent Orders</h3>
            <?php if (count($recent_orders) > 0): ?>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Reference</th>
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
                        <td><?php echo htmlspecialchars($order['firstname'] . ' ' . $order['lastname']); ?></td>
                        <td>&euro;<?php echo number_format($order['total_amount'], 2); ?></td>
                        <td><?php echo $order['status_id'] == 4 ? 'Delivered' : 'Processing'; ?></td>
                        <td><?php echo htmlspecialchars($order['created_at']); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <?php else: ?>
            <p>No orders yet.</p>
            <?php endif; ?>
        </div>

        <div class="admin-section">
            <h3>Admin Notes</h3>
            <?php foreach ($notes as $note): ?>
            <div class="note-card">
                <h4><?php echo htmlspecialchars($note['title']); ?></h4>
                <p><?php echo htmlspecialchars($note['content']); ?></p>
                <small><?php echo htmlspecialchars($note['created_at']); ?></small>
            </div>
            <?php endforeach; ?>

            <h4>Add Note</h4>
            <form method="post" action="<?php echo htmlspecialchars($_SERVER['PHP_SELF']); ?>">
                <div class="form-group">
                    <label for="title">Title</label>
                    <input type="text" id="title" name="title" required>
                </div>
                <div class="form-group">
                    <label for="content">Content</label>
                    <textarea id="content" name="content" rows="4" required></textarea>
                </div>
                <button type="submit" class="btn btn-admin">Add Note</button>
            </form>
        </div>
    </div>

    <div class="footer">
        <p>&copy; <?php echo date('Y'); ?> Administration Panel</p>
    </div>
</body>
</html>