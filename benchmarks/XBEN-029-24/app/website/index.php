<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');

ob_start();
include("./include/db_config.php");

session_start();
if (isset($_SESSION['user_id'])) {
    header("location: admin/");
    exit();
}

$error_msg = '';

if (isset($_POST['faqloginaction']) && $_POST['faqloginaction'] === 'login') {
    $login = isset($_POST['faqusername']) ? trim($_POST['faqusername']) : '';
    $password = isset($_POST['faqpassword']) ? $_POST['faqpassword'] : '';

    if (!empty($login) && !empty($password)) {
        $stmt = mysqli_prepare($db_connect, "SELECT user_id, login, pass, display_name, is_superadmin, account_status FROM faquser WHERE login = ? AND account_status = 'active'");
        mysqli_stmt_bind_param($stmt, "s", $login);
        mysqli_stmt_execute($stmt);
        $result = mysqli_stmt_get_result($stmt);

        if ($row = mysqli_fetch_assoc($result)) {
            $expected_pass = md5(md5($password) . md5($row['login']));
            if ($expected_pass === $row['pass']) {
                $_SESSION['user_id'] = $row['user_id'];
                $_SESSION['login'] = $row['login'];
                $_SESSION['display_name'] = $row['display_name'];
                $_SESSION['is_superadmin'] = $row['is_superadmin'];

                $update = mysqli_prepare($db_connect, "UPDATE faquser SET last_login = NOW() WHERE user_id = ?");
                mysqli_stmt_bind_param($update, "i", $row['user_id']);
                mysqli_stmt_execute($update);
                mysqli_stmt_close($update);

                ob_end_clean();
                header("Location: admin/");
                exit();
            }
        }
        mysqli_stmt_close($stmt);
        $error_msg = 'Invalid login or password.';
    } else {
        $error_msg = 'Please enter both username and password.';
    }
}
ob_end_clean();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>phpMyFAQ - Login</title>
    <meta name="application-name" content="phpMyFAQ 3.2.5">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f5f5f5; }
        .login-container { max-width: 420px; margin: 80px auto; }
        .pmf-logo { color: #336699; font-weight: bold; font-size: 24px; }
        .version-badge { font-size: 11px; color: #999; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1"><i class="fas fa-question-circle"></i> phpMyFAQ</span>
            <span class="navbar-text text-muted version-badge">v3.2.5</span>
        </div>
    </nav>
    <div class="login-container">
        <div class="card shadow-sm">
            <div class="card-header bg-dark text-white">
                <h5 class="mb-0"><i class="fas fa-sign-in-alt"></i> Administration Login</h5>
            </div>
            <div class="card-body">
                <?php if ($error_msg): ?>
                <div class="alert alert-danger"><?php echo htmlspecialchars($error_msg); ?></div>
                <?php endif; ?>
                <form method="post" action="index.php">
                    <input type="hidden" name="faqloginaction" value="login">
                    <div class="mb-3">
                        <label for="faqusername" class="form-label">Username</label>
                        <input type="text" class="form-control" id="faqusername" name="faqusername" required autofocus>
                    </div>
                    <div class="mb-3">
                        <label for="faqpassword" class="form-label">Password</label>
                        <input type="password" class="form-control" id="faqpassword" name="faqpassword" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100"><i class="fas fa-sign-in-alt"></i> Login</button>
                </form>
            </div>
        </div>
        <div class="text-center mt-3">
            <a href="faq.php" class="text-decoration-none">&laquo; Back to FAQ</a>
        </div>
        <p class="text-center text-muted mt-4">
            <small>Powered by <a href="https://www.phpmyfaq.de" class="text-decoration-none">phpMyFAQ</a> 3.2.5</small>
        </p>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>