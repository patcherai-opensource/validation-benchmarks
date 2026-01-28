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
    <title>Aimeos Media Manager | Settings</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="dashboard.php"><i class="fas fa-images"></i> Aimeos Media Manager</a>
        </div>
    </nav>
    <div class="container mt-4">
        <h2><i class="fas fa-cog"></i> System Settings</h2>
        <div class="card mt-3">
            <div class="card-body">
                <form>
                    <div class="mb-3">
                        <label class="form-label">Storage Path</label>
                        <input type="text" class="form-control" value="./media/" disabled>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Max Upload Size</label>
                        <input type="text" class="form-control" value="10MB" disabled>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Allowed Domains</label>
                        <input type="text" class="form-control" value="product, catalog, supplier" disabled>
                    </div>
                    <button type="button" class="btn btn-secondary" disabled>Save Settings (Disabled in Demo)</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
