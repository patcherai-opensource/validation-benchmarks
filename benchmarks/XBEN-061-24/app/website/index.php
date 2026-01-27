<?php
// SecureAuth Portal - User Management System
session_start();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SecureAuth Portal - Home</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation Bar -->
    <?php include("include/navigation-bar.php"); ?>

    <!-- Header -->
    <header class="py-5 bg-primary text-white mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">SecureAuth Portal</h1>
                <p class="lead mb-0">Enterprise Identity Management System</p>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card mb-4">
                    <div class="card-header">
                        <h4>Welcome to SecureAuth</h4>
                    </div>
                    <div class="card-body">
                        <p>SecureAuth Portal provides secure identity management for enterprise users.</p>
                        <p>Features include:</p>
                        <ul>
                            <li>Secure user authentication</li>
                            <li>Password reset functionality</li>
                            <li>Multi-factor authentication support</li>
                            <li>Audit logging and compliance</li>
                        </ul>
                        <div class="mt-4">
                            <a href="login.php" class="btn btn-primary me-2">Login</a>
                            <a href="forgot-password.php" class="btn btn-outline-secondary">Forgot Password?</a>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h5>System Status</h5>
                    </div>
                    <div class="card-body">
                        <p><span class="badge bg-success">Online</span> All systems operational</p>
                        <small class="text-muted">Version 1.3.3 - Last updated: 2024-01-15</small>
                    </div>
                </div>
            </div>
            
            <!-- Sidebar -->
            <?php include("include/sidebar.php"); ?>
        </div>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
