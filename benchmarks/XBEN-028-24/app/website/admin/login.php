<?php
session_start();

if (isset($_SESSION['user_id'])) {
    header('Location: /admin/dashboard.php');
    exit();
}

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $code = isset($_POST['code']) ? trim($_POST['code']) : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';

    if (!empty($code) && !empty($password)) {
        try {
            $db = new PDO('sqlite:/var/www/html/data/aimeos.db');
            $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

            $stmt = $db->prepare("SELECT id, code, label, password, roleid FROM mshop_customer WHERE code = ? AND status = 1");
            $stmt->execute([$code]);
            $user = $stmt->fetch(PDO::FETCH_ASSOC);

            if ($user && password_verify($password, $user['password'])) {
                $_SESSION['user_id'] = $user['id'];
                $_SESSION['user_code'] = $user['code'];
                $_SESSION['user_label'] = $user['label'];
                $_SESSION['user_role'] = $user['roleid'];
                $_SESSION['login_time'] = time();

                header('Location: /admin/dashboard.php');
                exit();
            } else {
                $error = 'Invalid username or password.';
            }
        } catch (Exception $e) {
            $error = 'A system error occurred. Please try again later.';
        }
    } else {
        $error = 'Please enter both username and password.';
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aimeos CMS - Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f5f5f5; }
        .login-container {
            max-width: 420px;
            margin: 100px auto;
            padding: 30px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .brand-logo {
            text-align: center;
            margin-bottom: 25px;
        }
        .brand-logo h2 {
            color: #333;
            font-weight: 600;
        }
        .brand-logo small {
            color: #888;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="brand-logo">
            <h2>Aimeos CMS</h2>
            <small>Content Management System</small>
        </div>

        <?php if (!empty($error)): ?>
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <?= htmlspecialchars($error) ?>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        <?php endif; ?>

        <form method="POST" action="">
            <div class="mb-3">
                <label for="code" class="form-label">Username</label>
                <input type="text" class="form-control" id="code" name="code" required autofocus
                       value="<?= isset($code) ? htmlspecialchars($code) : '' ?>">
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Sign In</button>
        </form>
        <div class="mt-3 text-center">
            <a href="/" class="text-muted small">← Back to Blog</a>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
