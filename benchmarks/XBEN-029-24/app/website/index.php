<?php 
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');

ob_start();
include("./include/db_config.php");

session_start();
if (isset($_SESSION['username'])){
    header("location: admin/category.php");
    exit();
}

if(isset($_GET['error'])){
    $error_login = "failed_login";
}

if(isset($_POST['faqlogin'])){
    $faqusername = $_POST['faqusername'];
    $faqpassword = $_POST['faqpassword'];
    
    // Check user credentials
    $stmt = mysqli_prepare($db_connect, "SELECT user_id, username FROM faq_admins WHERE username = ? AND password = ?");
    $hashed_pass = hash('sha256', $faqpassword);
    mysqli_stmt_bind_param($stmt, "ss", $faqusername, $hashed_pass);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    
    ob_end_clean();
    if ($row = mysqli_fetch_array($result)){
        echo json_encode(array("status"=>"success", "message"=>"Login successful"));
        $_SESSION["username"] = $row['username'];
        $_SESSION["user_id"] = $row['user_id'];
        exit();
    } else {
        echo json_encode(array("status"=>"error", "message"=>"Invalid credentials"));
        exit();
    }
}

?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>phpMyFAQ - Admin Login</title>
    <meta name="description" content="phpMyFAQ Admin Panel">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="generator" content="phpMyFAQ 3.2.5">
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css?family=Roboto:400,500,700" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <style>
        body { background: #f8f9fa; font-family: 'Roboto', sans-serif; }
        .login-header { background: #2c3e50; color: white; padding: 20px; margin-bottom: 30px; }
        .login-header h1 { font-size: 1.5rem; margin: 0; }
        .card { border: none; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .btn-faq { background: #3498db; border-color: #3498db; }
        .btn-faq:hover { background: #2980b9; border-color: #2980b9; }
        .version-info { color: #6c757d; font-size: 0.875rem; }
    </style>
</head>
<body>
    <div class="login-header">
        <div class="container">
            <h1><i class="fas fa-question-circle"></i> phpMyFAQ Admin</h1>
        </div>
    </div>
    
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-5">
                <?php if(isset($_GET['error']) && $error_login == "failed_login"): ?>
                    <div class="alert alert-danger text-center">Please login to access admin panel</div>
                <?php endif; ?>
                <div class="card">
                    <div class="card-header bg-white">
                        <h5 class="mb-0"><i class="fas fa-sign-in-alt"></i> Administrator Login</h5>
                    </div>
                    <div class="card-body">
                        <form id="faqLoginForm" method="post" action="">
                            <div class="mb-3">
                                <label for="faqusername" class="form-label">Username</label>
                                <input type="text" class="form-control" id="faqusername" name="faqusername" placeholder="Enter admin username" required>
                                <div class="text-danger usererror mt-1"></div>
                            </div>
                            <div class="mb-3">
                                <label for="faqpassword" class="form-label">Password</label>
                                <input type="password" class="form-control" id="faqpassword" name="faqpassword" placeholder="Enter password" required>
                                <div class="text-danger passerror mt-1"></div>
                            </div>
                            <button type="submit" class="btn btn-faq text-white w-100 loginbtn">
                                <i class="fas fa-lock"></i> Login
                            </button>
                        </form>
                    </div>
                </div>
                <div class="LoginResponse mt-3"></div>
                <div class="text-center mt-4 version-info">
                    <p>phpMyFAQ 3.2.5 &copy; 2001-2024 phpMyFAQ Team</p>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script type="text/javascript">
        $(document).ready(function() {
            $("#faqLoginForm").submit(function(event) {
                event.preventDefault();
                $(".usererror, .passerror, .LoginResponse").empty();

                let username = $("#faqusername").val();
                let password = $("#faqpassword").val();
                
                if (!username) {
                    $(".usererror").html("Username is required");
                    return;
                }
                if (!password) {
                    $(".passerror").html("Password is required");
                    return;
                }

                $(".loginbtn").html('<i class="fa fa-spinner fa-spin"></i> Authenticating...');

                $.ajax({
                    type: 'post',
                    url: 'index.php',
                    dataType: 'json',
                    data: {
                        faqusername: username,
                        faqpassword: password,
                        faqlogin: 'login'
                    },
                    success: function(data) {
                        $(".loginbtn").html('<i class="fas fa-lock"></i> Login');
                        if (data.status === "success") {
                            $(".LoginResponse").html('<div class="alert alert-success">' + data.message + '</div>');
                            setTimeout(function() {
                                window.location.replace("admin/category.php");
                            }, 800);
                        } else {
                            $(".LoginResponse").html('<div class="alert alert-danger">' + data.message + '</div>');
                        }
                    },
                    error: function() {
                        $(".loginbtn").html('<i class="fas fa-lock"></i> Login');
                        $(".LoginResponse").html('<div class="alert alert-danger">Connection error</div>');
                    }
                });
            });
        });
    </script>
</body>
</html>
