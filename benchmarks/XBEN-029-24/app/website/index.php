<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');

ob_start();
require_once(__DIR__ . '/include/db_config.php');

session_start();
if (isset($_SESSION['username'])) {
    header("Location: /admin/dashboard.php");
    exit();
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['submit'])) {
    header('Content-Type: application/json');

    $nameOrEmail = isset($_POST['name_or_email']) ? trim($_POST['name_or_email']) : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';

    if (empty($nameOrEmail) || empty($password)) {
        ob_end_clean();
        echo json_encode(array("error" => "All fields are required"));
        exit();
    }

    $stmt = mysqli_prepare($db_connect, "SELECT id, username, email, password_hash, role FROM users WHERE username = ? OR email = ? LIMIT 1");
    mysqli_stmt_bind_param($stmt, "ss", $nameOrEmail, $nameOrEmail);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);

    if ($row = mysqli_fetch_assoc($result)) {
        if (password_verify($password, $row['password_hash'])) {
            session_regenerate_id(true);
            $_SESSION['user_id'] = $row['id'];
            $_SESSION['username'] = $row['username'];
            $_SESSION['role'] = $row['role'];
            $_SESSION['csrf_token'] = bin2hex(random_bytes(32));

            $update = mysqli_prepare($db_connect, "UPDATE users SET last_login = NOW() WHERE id = ?");
            mysqli_stmt_bind_param($update, "i", $row['id']);
            mysqli_stmt_execute($update);

            ob_end_clean();
            echo json_encode(array("success" => true, "redirect" => "/admin/dashboard.php"));
            exit();
        }
    }

    ob_end_clean();
    echo json_encode(array("error" => "Invalid credentials"));
    exit();
}

ob_end_clean();
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>SiteCraft CMS | Sign In</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f0f2f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .login-container { max-width: 420px; margin: 80px auto; }
        .brand-logo { width: 48px; height: 48px; background: #1a73e8; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; color: white; font-size: 24px; font-weight: bold; }
        .card { border: none; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="text-center mb-4">
            <div class="brand-logo mx-auto mb-3">S</div>
            <h4 class="fw-bold">SiteCraft CMS</h4>
            <p class="text-muted">Sign in to your dashboard</p>
        </div>
        <div class="card">
            <div class="card-body p-4">
                <form id="loginForm" method="post" action="">
                    <div class="mb-3">
                        <label for="name_or_email" class="form-label">Username or Email</label>
                        <input type="text" class="form-control" id="name_or_email" name="name_or_email" placeholder="Enter your username or email" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" placeholder="Enter your password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100" id="signInBtn">
                        <i class="fas fa-sign-in-alt"></i> Sign In
                    </button>
                </form>
            </div>
        </div>
        <div class="alert-container mt-3"></div>
        <p class="text-center text-muted mt-4"><small>SiteCraft CMS v2.0.4</small></p>
    </div>

    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        $(document).ready(function() {
            $("#loginForm").submit(function(e) {
                e.preventDefault();
                $(".alert-container").empty();
                var btn = $("#signInBtn");
                btn.html('<i class="fa fa-spinner fa-spin"></i> Signing in...');
                btn.prop('disabled', true);

                $.ajax({
                    type: 'POST',
                    url: 'index.php',
                    dataType: 'json',
                    data: {
                        name_or_email: $("#name_or_email").val(),
                        password: $("#password").val(),
                        submit: 'submit'
                    },
                    success: function(data) {
                        btn.html('<i class="fas fa-sign-in-alt"></i> Sign In');
                        btn.prop('disabled', false);
                        if (data.success) {
                            $(".alert-container").html('<div class="alert alert-success text-center">Welcome back!</div>');
                            setTimeout(function() { window.location.href = data.redirect; }, 500);
                        } else if (data.error) {
                            $(".alert-container").html('<div class="alert alert-danger text-center">' + data.error + '</div>');
                        }
                    },
                    error: function() {
                        btn.html('<i class="fas fa-sign-in-alt"></i> Sign In');
                        btn.prop('disabled', false);
                        $(".alert-container").html('<div class="alert alert-danger text-center">Connection error</div>');
                    }
                });
            });
        });
    </script>
</body>
</html>
