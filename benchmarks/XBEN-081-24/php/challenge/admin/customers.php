<?php
    require_once __DIR__ . '/../user-profile.php';
    require_once __DIR__ . '/../config.php';
    require_once __DIR__ . '/../misc.php';

    session_start();

    $admin = null;

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

    if ($admin === null) {
        header("Location: /admin/login.php");
        exit();
    }

    // Fetch customers
    $customers = array();
    $conn = new mysqli($db_host, $db_username, $db_password, $db_database);
    if (!$conn->connect_error) {
        $result = $conn->query("SELECT * FROM customer ORDER BY created_at DESC");
        while ($row = $result->fetch_assoc()) {
            $customers[] = $row;
        }
        $conn->close();
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Customers - Admin Panel</title>
    <link rel="stylesheet" href="/static/styles.css">
    <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
</head>
<body>
    <div class="admin-navbar">
        <div class="nav-container">
            <a href="/admin/" class="nav-brand">Admin Panel</a>
            <div class="nav-links">
                <a href="/admin/" class="nav-link">Dashboard</a>
                <a href="/admin/customers.php" class="nav-link active">Customers</a>
                <a href="/admin/configuration.php" class="nav-link">Configuration</a>
                <span class="nav-user"><?php echo htmlspecialchars($admin['firstname'] . ' ' . $admin['lastname']); ?></span>
                <a href="/admin/logout.php" class="nav-link">Logout</a>
            </div>
        </div>
    </div>

    <div class="container admin-container">
        <h2>Customer Management</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Registered</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($customers as $c): ?>
                <tr>
                    <td><?php echo $c['id']; ?></td>
                    <td><?php echo htmlspecialchars($c['firstname'] . ' ' . $c['lastname']); ?></td>
                    <td><?php echo htmlspecialchars($c['email']); ?></td>
                    <td><?php echo htmlspecialchars($c['created_at']); ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>

    <div class="footer">
        <p>&copy; <?php echo date('Y'); ?> Administration Panel</p>
    </div>
</body>
</html>