<?php
$error = "";
if($_SERVER["REQUEST_METHOD"] == "POST"){
    $error = "Invalid credentials. Please try again.";
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>eZ Content Hub | Admin Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container">
        <div class="row justify-content-center mt-5">
            <div class="col-md-6">
                <div class="card shadow">
                    <div class="card-header bg-dark text-white text-center">
                        <h4><strong>eZ</strong> Content Hub - Administration</h4>
                    </div>
                    <div class="card-body">
                        <?php if($error): ?>
                        <div class="alert alert-danger"><?php echo $error; ?></div>
                        <?php endif; ?>
                        <form method="post" action="">
                            <div class="mb-3">
                                <label class="form-label">Username</label>
                                <input type="text" name="username" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password</label>
                                <input type="password" name="password" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <button type="submit" class="btn btn-primary w-100">Sign In</button>
                            </div>
                        </form>
                        <hr>
                        <p class="text-muted small text-center">
                            eZ Content Hub v2.3.1-legacy<br>
                            For authorized administrators only.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
