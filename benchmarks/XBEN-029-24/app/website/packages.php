<?php
session_start();
if (!isset($_SESSION['username'])) {
    header("Location: index.php?error=failed_login");
    exit();
}
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Automad | Packages</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f5f5f5; }
        .sidebar { min-height: 100vh; background-color: #1a1a2e; color: #fff; }
        .sidebar .nav-link { color: rgba(255,255,255,0.7); padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 2px; }
        .sidebar .nav-link:hover, .sidebar .nav-link.active { color: #fff; background-color: rgba(255,255,255,0.1); }
        .sidebar .brand { font-weight: 600; font-size: 1.2rem; padding: 1rem; letter-spacing: -0.5px; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-2 d-none d-md-block sidebar py-3">
                <div class="brand"><i class="fas fa-cube"></i> Automad</div>
                <ul class="nav flex-column mt-3">
                    <li class="nav-item"><a class="nav-link" href="dashboard.php"><i class="fas fa-tachometer-alt me-2"></i> Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="pages.php"><i class="fas fa-file-alt me-2"></i> Pages</a></li>
                    <li class="nav-item"><a class="nav-link" href="shared.php"><i class="fas fa-cog me-2"></i> Shared</a></li>
                    <li class="nav-item"><a class="nav-link active" href="packages.php"><i class="fas fa-box me-2"></i> Packages</a></li>
                    <li class="nav-item mt-4"><a class="nav-link" href="logout.php"><i class="fas fa-sign-out-alt me-2"></i> Sign Out</a></li>
                </ul>
            </nav>
            <main class="col-md-10 ms-sm-auto px-4 py-4">
                <h4 class="fw-bold mb-3">Packages</h4>
                <div class="card shadow-sm">
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table">
                                <thead>
                                    <tr><th>Package</th><th>Version</th><th>Status</th></tr>
                                </thead>
                                <tbody>
                                    <tr><td>automad/standard</td><td>2.0.0</td><td><span class="badge bg-success">Installed</span></td></tr>
                                    <tr><td>automad/blocks</td><td>1.4.2</td><td><span class="badge bg-success">Installed</span></td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>
</body>
</html>
