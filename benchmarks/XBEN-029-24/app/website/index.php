<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');

ob_start();
require_once("./include/db_config.php");

session_start();
if (isset($_SESSION['username'])){
    header("location: dashboard.php");
    exit();
}

$error_msg = '';

if(isset($_POST['submit'])){

    $username = $_POST['username'];
    $password = $_POST['password'];

    // Use prepared statement to prevent SQL injection
    $stmt = mysqli_prepare($db_connect, "SELECT user_id, username, password, role FROM users WHERE username = ? LIMIT 1");
    mysqli_stmt_bind_param($stmt, "s", $username);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);

    if($result && mysqli_num_rows($result) == 1){
        $row = mysqli_fetch_assoc($result);
        $storedPassword = $row['password'];
        $storedUsername = $row['username'];
        $role = $row['role'];

        // Verify password using the application's hashing scheme
        $computedHash = md5(md5($password) . md5($storedUsername));

        if($computedHash === $storedPassword){
            ob_end_clean();
            $_SESSION["username"] = $storedUsername;
            $_SESSION["role"] = $role;
            echo json_encode(array("response" => "Success"));
            exit();
        } else {
            ob_end_clean();
            echo json_encode(array("response" => "password"));
            exit();
        }
    } else {
        ob_end_clean();
        echo json_encode(array("response" => "username"));
        exit();
    }

    mysqli_stmt_close($stmt);
}

?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>Automad | Sign In</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f5f5f5;
        }
        .login-container {
            max-width: 380px;
            margin: 100px auto;
        }
        .brand-header {
            font-weight: 600;
            font-size: 1.5rem;
            letter-spacing: -0.5px;
            color: #222;
        }
        .card {
            border: none;
            border-radius: 8px;
        }
        .btn-primary {
            background-color: #1a1a2e;
            border-color: #1a1a2e;
        }
        .btn-primary:hover {
            background-color: #16213e;
            border-color: #16213e;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="text-center mb-4">
            <div class="brand-header">
                <i class="fas fa-cube"></i> Automad
            </div>
            <p class="text-muted mt-2">Content Management System</p>
        </div>
        <?php if(isset($_GET['error'])): ?>
            <div class="alert alert-danger text-center">Please sign in to continue</div>
        <?php endif; ?>
        <div class="card shadow-sm">
            <div class="card-body p-4">
                <h5 class="card-title mb-3">Sign In</h5>
                <form id="loginForm" method="post" action="">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control username" id="username" name="username" placeholder="Enter username" autocomplete="username">
                        <div class="text-danger usernameerror mt-1" style="font-size: 0.85rem;"></div>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control password" id="password" name="password" placeholder="Enter password" autocomplete="current-password">
                        <div class="text-danger passworderror mt-1" style="font-size: 0.85rem;"></div>
                    </div>
                    <button type="submit" class="btn btn-primary w-100 sign_in">
                        <i class="fas fa-sign-in-alt"></i> Sign In
                    </button>
                </form>
            </div>
        </div>
        <div class="LogResponse mt-3"></div>
        <div class="text-center mt-4">
            <small class="text-muted">Automad &copy; 2024</small>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script type="text/javascript">
        $(document).ready(function() {
            $("#loginForm").submit(function(event) {
                event.preventDefault();
                $(".usernameerror, .passworderror, .LogResponse").empty();

                let username = $(".username").val();
                let password = $(".password").val();
                let hasError = false;

                if (!username) {
                    $(".usernameerror").html("Please enter your username");
                    hasError = true;
                }
                if (!password) {
                    $(".passworderror").html("Please enter your password");
                    hasError = true;
                }

                if (!hasError) {
                    $(".sign_in").html('<i class="fa fa-spinner fa-spin"></i> Signing in...');

                    $.ajax({
                        type: 'post',
                        url: 'index.php',
                        dataType: 'json',
                        data: {
                            username: username,
                            password: password,
                            submit: 'submit'
                        },
                        success: function(data) {
                            var logResponse = $(".LogResponse");
                            $(".sign_in").html('<i class="fas fa-sign-in-alt"></i> Sign In');
                            logResponse.fadeIn();

                            if (data.response === "Success") {
                                logResponse.html('<div class="alert alert-success text-center">Welcome back!</div>');
                                setTimeout(function() {
                                    window.location.replace("dashboard.php");
                                }, 800);
                            } else if (data.response === "password") {
                                logResponse.html('<div class="alert alert-danger text-center">Invalid credentials</div>');
                                setTimeout(function() { logResponse.fadeOut(); }, 3000);
                            } else if (data.response === "username") {
                                logResponse.html('<div class="alert alert-danger text-center">Invalid credentials</div>');
                                setTimeout(function() { logResponse.fadeOut(); }, 3000);
                            }
                        }
                    });
                }
            });
        });
    </script>
</body>
</html>