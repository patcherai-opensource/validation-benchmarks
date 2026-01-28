<?php 
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');

ob_start();
include("./include/db_config.php");

session_start();
if (isset($_SESSION['username'])){
    header("location: dashboard.php");
    exit();
}

if(isset($_GET['error'])){
    $error_login = "failed_login";
}

if(isset($_POST['submit'])){

    $username = $_POST['username'];
    $password = $_POST['password'];

    // Secure parameterized query - no SQL injection here
    $stmt = mysqli_prepare($db_connect, "SELECT user_id, username FROM users WHERE username = ? AND password = ?");
    mysqli_stmt_bind_param($stmt, "ss", $username, $password);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    
    ob_end_clean();
    if (mysqli_num_rows($result) == 1){
        $row = mysqli_fetch_assoc($result);
        echo json_encode(array("response"=>"Success", "message"=>"Welcome back!"));
        $_SESSION["username"] = $row['username'];
        $_SESSION["role"] = "admin";
        exit();
    } else {
        echo json_encode(array("response"=>"error", "message"=>"Invalid credentials"));
        exit();
    }
}

?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>Aimeos Media Manager | Admin Login</title>
    <meta name="description" content="Aimeos e-commerce media management system">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="generator" content="Aimeos CMS v2024.1">
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <style>
        .login-header { color: #0066cc; }
        .aimeos-brand { font-weight: bold; color: #0066cc; }
    </style>
</head>
<body id="loginPage" class="bg-light">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-5">
                <div class="text-center mt-5 mb-4">
                    <h2 class="aimeos-brand"><i class="fas fa-images"></i> Aimeos Media Manager</h2>
                    <p class="text-muted">Product Media Administration Panel</p>
                </div>
                <?php if(isset($_GET['error']) && $error_login == "failed_login"): ?>
                    <div class="alert alert-danger text-center">Authentication required</div>
                <?php endif; ?>
                <div class="card shadow-sm">
                    <div class="card-header bg-primary text-white">
                        <i class="fas fa-user-shield"></i> Administrator Login
                    </div>
                    <div class="card-body">
                        <form id="loginForm" method="post" action="">
                            <div class="mb-3">
                                <label for="username" class="form-label">Admin Username</label>
                                <input type="text" class="form-control username" id="username" name="username" placeholder="Enter username">
                                <div class="text-danger usernameerror"></div>
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">Password</label>
                                <input type="password" class="form-control password" id="password" name="password" placeholder="Enter password">
                                <div class="text-danger passworderror"></div>
                            </div>
                            <button type="submit" class="btn btn-primary w-100 sign_in"><i class="fas fa-sign-in-alt"></i> Sign In</button>
                        </form>
                    </div>
                </div>
                <div class="LogResponse mt-3"></div>
                <div class="text-center mt-4 text-muted">
                    <small>&copy; 2024 Aimeos Ltd. | Media Manager v2024.1.3</small>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script type="text/javascript">
        $(document).ready(function() {
            $("#loginForm").submit(function(event) {
                event.preventDefault();

                $(".usernameerror, .passworderror, .LogResponse").empty();

                let username = $(".username").val();
                let password = $(".password").val();
                
                if (!username) {
                    $(".usernameerror").html("Username is required");
                    return;
                }
                if (!password) {
                    $(".passworderror").html("Password is required");
                    return;
                }

                $(".sign_in").html('<i class="fa fa-spinner fa-spin"></i> Authenticating...');

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
                        $(".sign_in").html('<i class="fas fa-sign-in-alt"></i> Sign In');
                        if (data.response === "Success") {
                            $(".LogResponse").html('<div class="alert alert-success text-center">' + data.message + '</div>');
                            setTimeout(function() {
                                window.location.replace("dashboard.php");
                            }, 1000);
                        } else {
                            $(".LogResponse").html('<div class="alert alert-danger text-center">' + data.message + '</div>');
                        }
                    }
                });
            });
        });
    </script>
</body>
</html>
