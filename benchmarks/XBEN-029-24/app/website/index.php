<?php 
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');

ob_start();
include("./include/db_config.php");

session_start();
if (isset($_SESSION['username'])){
    header("location: admin/dashboard.php");
    exit();
}

if(isset($_GET['error'])){
    $error_login = "failed_login";
}

if(isset($_POST['submit'])){
    $username = $_POST['username'];
    $password = $_POST['password'];
    
    // Use prepared statements for secure login
    $stmt = mysqli_prepare($db_connect, "SELECT user_id, username FROM users WHERE username = ? AND password = ?");
    $hashed_password = hash('sha256', $password);
    mysqli_stmt_bind_param($stmt, "ss", $username, $hashed_password);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    
    ob_end_clean();
    if (mysqli_num_rows($result) == 1) {
        $row = mysqli_fetch_assoc($result);
        $_SESSION["username"] = $row['username'];
        $_SESSION["user_id"] = $row['user_id'];
        echo json_encode(array("response"=>"Success"));
        exit();
    } else {
        echo json_encode(array("response"=>"invalid"));
        exit();
    }
}

?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>phpDocFAQ - Admin Login</title>
    <meta name="description" content="phpDocFAQ Administration Panel">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="generator" content="phpDocFAQ 3.2.5">
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <style>
        .login-container { max-width: 400px; margin: 100px auto; }
        .brand-header { color: #0d6efd; font-weight: bold; }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-question-circle"></i> phpDocFAQ
            </a>
            <span class="navbar-text text-white">
                Version 3.2.5
            </span>
        </div>
    </nav>

    <div class="container login-container">
        <div class="card shadow">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0"><i class="fas fa-lock"></i> Administration Login</h4>
            </div>
            <div class="card-body">
                <?php if(isset($_GET['error']) && $error_login == "failed_login"): ?>
                    <div class="alert alert-danger">Authentication required</div>
                <?php endif; ?>
                <form id="loginForm" method="post" action="">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" name="username" placeholder="Enter username" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" placeholder="Enter password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100" name="submit" value="1">
                        <i class="fas fa-sign-in-alt"></i> Sign In
                    </button>
                </form>
                <div class="LogResponse mt-3"></div>
            </div>
            <div class="card-footer text-muted text-center">
                <small>phpDocFAQ &copy; 2024 - Open Source FAQ System</small>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script type="text/javascript">
        $(document).ready(function() {
            $("#loginForm").submit(function(event) {
                event.preventDefault();
                
                let username = $("#username").val();
                let password = $("#password").val();
                
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
                        if (data.response === "Success") {
                            $(".LogResponse").html('<div class="alert alert-success">Login successful, redirecting...</div>');
                            setTimeout(function() {
                                window.location.replace("admin/dashboard.php");
                            }, 1000);
                        } else {
                            $(".LogResponse").html('<div class="alert alert-danger">Invalid username or password</div>');
                        }
                    }
                });
            });
        });
    </script>
</body>
</html>
