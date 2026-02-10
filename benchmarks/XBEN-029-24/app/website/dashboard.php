<?php

include("./include/db_config.php");

session_start();

$username = '';

if (isset($_SESSION['username'])){
    $username = $_SESSION['username'];
}

if(!$username){
    header("Location: index.php?error=failed_login");
    exit();
}

?>

<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>PayBuddies Portal | Admin Dashboard</title>
    <meta name="description" content="">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.com"></script>
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">PayBuddies Admin</a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text me-3">Welcome, <?php echo htmlspecialchars($username); ?></span>
                <a class="nav-link" href="logout.php">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-3">
                <div class="card">
                    <div class="card-header">Navigation</div>
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item active"><a href="dashboard.php" class="text-decoration-none">Dashboard</a></li>
                        <li class="list-group-item"><a href="media.php" class="text-decoration-none">Media Manager</a></li>
                        <li class="list-group-item"><a href="#" class="text-decoration-none text-muted">Reports</a></li>
                        <li class="list-group-item"><a href="#" class="text-decoration-none text-muted">Settings</a></li>
                    </ul>
                </div>
            </div>
            <div class="col-md-9">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Dashboard Overview</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="card bg-info text-white mb-3">
                                    <div class="card-body text-center">
                                        <h3><i class="fas fa-users"></i> 1,234</h3>
                                        <p class="mb-0">Active Users</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card bg-success text-white mb-3">
                                    <div class="card-body text-center">
                                        <h3><i class="fas fa-dollar-sign"></i> $45.2K</h3>
                                        <p class="mb-0">Revenue</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card bg-warning text-white mb-3">
                                    <div class="card-body text-center">
                                        <h3><i class="fas fa-images"></i> 89</h3>
                                        <p class="mb-0">Media Files</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <hr>
                        <h6>Quick Actions</h6>
                        <a href="media.php" class="btn btn-primary"><i class="fas fa-upload"></i> Upload Media</a>
                        <a href="#" class="btn btn-secondary disabled"><i class="fas fa-chart-bar"></i> View Reports</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
