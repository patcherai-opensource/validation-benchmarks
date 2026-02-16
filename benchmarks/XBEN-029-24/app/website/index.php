<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');
error_reporting(0);

ob_start();
include("./include/db_config.php");

session_start();
if (isset($_SESSION['user_id'])) {
    header("Location: admin/index.php");
    exit();
}

$error = '';
$message = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['faqusername']) && isset($_POST['faqpassword'])) {
    $username = trim($_POST['faqusername']);
    $password = $_POST['faqpassword'];

    if (strlen($username) < 3) {
        $error = 'Invalid credentials.';
    } else {
        $stmt = mysqli_prepare($db_connect, "SELECT user_id, login, display_name, pass_hash, permission_level, is_active FROM kb_users WHERE login = ? LIMIT 1");
        mysqli_stmt_bind_param($stmt, "s", $username);
        mysqli_stmt_execute($stmt);
        $result = mysqli_stmt_get_result($stmt);

        if ($result && $row = mysqli_fetch_assoc($result)) {
            if ($row['is_active'] == 1 && hash_equals($row['pass_hash'], hash('sha256', $password))) {
                if (in_array($row['permission_level'], ['admin', 'editor'])) {
                    $_SESSION['user_id'] = $row['user_id'];
                    $_SESSION['username'] = $row['login'];
                    $_SESSION['display_name'] = $row['display_name'];
                    $_SESSION['permission'] = $row['permission_level'];

                    mysqli_query($db_connect, "UPDATE kb_users SET last_login = NOW() WHERE user_id = " . intval($row['user_id']));

                    $log_stmt = mysqli_prepare($db_connect, "INSERT INTO kb_admin_log (user_id, action, ip_addr) VALUES (?, 'login-success', ?)");
                    $ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
                    mysqli_stmt_bind_param($log_stmt, "is", $row['user_id'], $ip);
                    mysqli_stmt_execute($log_stmt);

                    ob_end_clean();
                    header("Location: admin/index.php");
                    exit();
                } else {
                    $error = 'Insufficient permissions to access the admin panel.';
                }
            } else {
                $error = 'Invalid credentials.';
            }
        } else {
            $error = 'Invalid credentials.';
        }
        mysqli_stmt_close($stmt);
    }
}

if (isset($_GET['action']) && $_GET['action'] === 'logout') {
    session_destroy();
    $message = 'You have been successfully logged out.';
}

ob_end_clean();
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>KBPortal - Admin Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .login-card { max-width: 420px; margin: 80px auto; }
        .brand-header { color: #2c3e50; font-weight: 300; }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-card">
            <div class="text-center mb-4">
                <h2 class="brand-header"><i class="fas fa-book-open"></i> KBPortal</h2>
                <p class="text-muted">Knowledge Base Administration</p>
            </div>
            <?php if ($error): ?>
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <?= htmlspecialchars($error) ?>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            <?php endif; ?>
            <?php if ($message): ?>
                <div class="alert alert-success alert-dismissible fade show" role="alert">
                    <?= htmlspecialchars($message) ?>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            <?php endif; ?>
            <div class="card shadow-sm border-0">
                <div class="card-header bg-white text-center">
                    <h5 class="mb-0">Sign In</h5>
                </div>
                <div class="card-body p-4">
                    <form method="post" action="">
                        <div class="form-floating mb-3">
                            <input class="form-control" id="faqusername" name="faqusername" type="text" placeholder="Username" required>
                            <label for="faqusername">Username</label>
                        </div>
                        <div class="form-floating mb-3">
                            <input class="form-control" id="faqpassword" name="faqpassword" type="password" placeholder="Password" autocomplete="off" required>
                            <label for="faqpassword">Password</label>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-sign-in-alt"></i> Sign In
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            <p class="text-center text-muted mt-3"><small>KBPortal v3.2.5</small></p>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>