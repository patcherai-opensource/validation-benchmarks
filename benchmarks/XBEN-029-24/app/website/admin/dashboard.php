<?php
/**
 * phpDocFAQ Admin Dashboard
 * Version 3.2.5
 */

include("../include/db_config.php");
session_start();

if (!isset($_SESSION['username'])) {
    header("Location: /index.php?error=failed_login");
    exit();
}

$username = $_SESSION['username'];
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>phpDocFAQ - Admin Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="generator" content="phpDocFAQ 3.2.5">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="/admin/dashboard.php">
                <i class="fas fa-question-circle"></i> phpDocFAQ Admin
            </a>
            <div class="navbar-nav ms-auto">
                <span class="nav-item nav-link text-white">
                    <i class="fas fa-user"></i> <?php echo htmlspecialchars($username); ?>
                </span>
                <a class="nav-link text-white" href="/admin/logout.php">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-md-3">
                <div class="card">
                    <div class="card-header bg-secondary text-white">
                        <i class="fas fa-cogs"></i> Administration
                    </div>
                    <div class="list-group list-group-flush">
                        <a href="/admin/dashboard.php" class="list-group-item list-group-item-action active">
                            <i class="fas fa-tachometer-alt"></i> Dashboard
                        </a>
                        <a href="/admin/categories.php" class="list-group-item list-group-item-action">
                            <i class="fas fa-folder"></i> Categories
                        </a>
                        <a href="/admin/faqs.php" class="list-group-item list-group-item-action">
                            <i class="fas fa-question"></i> FAQ Management
                        </a>
                        <a href="/admin/users.php" class="list-group-item list-group-item-action">
                            <i class="fas fa-users"></i> User Management
                        </a>
                        <a href="/admin/settings.php" class="list-group-item list-group-item-action">
                            <i class="fas fa-sliders-h"></i> Settings
                        </a>
                        <a href="/admin/backup.php" class="list-group-item list-group-item-action">
                            <i class="fas fa-database"></i> Backup
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-9">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-tachometer-alt"></i> Dashboard Overview</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="card bg-info text-white mb-3">
                                    <div class="card-body text-center">
                                        <h3>12</h3>
                                        <p class="mb-0">Categories</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card bg-success text-white mb-3">
                                    <div class="card-body text-center">
                                        <h3>156</h3>
                                        <p class="mb-0">FAQs</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card bg-warning text-white mb-3">
                                    <div class="card-body text-center">
                                        <h3>3</h3>
                                        <p class="mb-0">Users</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle"></i> 
                            Welcome to phpDocFAQ Administration Panel v3.2.5
                        </div>
                        
                        <h6>Recent Activity</h6>
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Action</th>
                                    <th>User</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>2024-01-15 14:32</td>
                                    <td>Category updated: General</td>
                                    <td>admin</td>
                                </tr>
                                <tr>
                                    <td>2024-01-15 12:15</td>
                                    <td>FAQ added: How to reset password</td>
                                    <td>admin</td>
                                </tr>
                                <tr>
                                    <td>2024-01-14 09:45</td>
                                    <td>New user registered</td>
                                    <td>system</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
