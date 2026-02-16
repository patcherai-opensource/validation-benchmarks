<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');

require_once(__DIR__ . '/../include/db_config.php');
require_once(__DIR__ . '/../include/auth.php');

requireAuth();

$username = $_SESSION['username'];
$role = $_SESSION['role'];
$csrfToken = getCsrfToken();

$pageCount = 0;
$mediaCount = 0;
$result = mysqli_query($db_connect, "SELECT COUNT(*) as cnt FROM pages");
if ($row = mysqli_fetch_assoc($result)) $pageCount = $row['cnt'];
$result = mysqli_query($db_connect, "SELECT COUNT(*) as cnt FROM media_files");
if ($row = mysqli_fetch_assoc($result)) $mediaCount = $row['cnt'];

?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf" content="<?php echo $csrfToken; ?>">
    <meta name="robots" content="noindex">
    <title>SiteCraft CMS | Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .sidebar { min-height: 100vh; background: #1e293b; padding-top: 20px; }
        .sidebar .nav-link { color: #94a3b8; padding: 12px 20px; }
        .sidebar .nav-link:hover, .sidebar .nav-link.active { color: #fff; background: rgba(255,255,255,0.1); }
        .sidebar .brand { color: #fff; font-size: 20px; font-weight: bold; padding: 0 20px 20px; border-bottom: 1px solid #334155; margin-bottom: 10px; }
        .stat-card { border: none; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .content-area { padding: 30px; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-2 sidebar d-none d-md-block">
                <div class="brand"><i class="fas fa-cube"></i> SiteCraft</div>
                <ul class="nav flex-column">
                    <li class="nav-item"><a class="nav-link active" href="/admin/dashboard.php"><i class="fas fa-tachometer-alt me-2"></i>Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="/admin/pages.php"><i class="fas fa-file-alt me-2"></i>Pages</a></li>
                    <li class="nav-item"><a class="nav-link" href="/admin/media.php"><i class="fas fa-images me-2"></i>Media</a></li>
                    <?php if ($role === 'admin'): ?>
                    <li class="nav-item"><a class="nav-link" href="/admin/settings.php"><i class="fas fa-cog me-2"></i>Settings</a></li>
                    <?php endif; ?>
                    <li class="nav-item mt-4"><a class="nav-link" href="/admin/logout.php"><i class="fas fa-sign-out-alt me-2"></i>Sign Out</a></li>
                </ul>
            </nav>
            <main class="col-md-10 ms-sm-auto content-area">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h3>Dashboard</h3>
                    <span class="badge bg-primary"><?php echo htmlspecialchars($role); ?>: <?php echo htmlspecialchars($username); ?></span>
                </div>
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <div class="card stat-card">
                            <div class="card-body">
                                <h6 class="text-muted">Pages</h6>
                                <h2><?php echo $pageCount; ?></h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <div class="card stat-card">
                            <div class="card-body">
                                <h6 class="text-muted">Media Files</h6>
                                <h2><?php echo $mediaCount; ?></h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <div class="card stat-card">
                            <div class="card-body">
                                <h6 class="text-muted">System</h6>
                                <h2 class="text-success"><i class="fas fa-check-circle"></i></h2>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card stat-card mt-3">
                    <div class="card-body">
                        <h5>Quick Actions</h5>
                        <a href="/admin/pages.php" class="btn btn-outline-primary me-2"><i class="fas fa-plus"></i> New Page</a>
                        <a href="/admin/media.php" class="btn btn-outline-secondary"><i class="fas fa-upload"></i> Upload Media</a>
                    </div>
                </div>
            </main>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
