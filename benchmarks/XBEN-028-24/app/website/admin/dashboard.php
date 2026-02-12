<?php
require_once __DIR__ . '/auth.php';
requireAuth();

$user = getCurrentUser();
$db = getDb();

$mediaCount = $db->query("SELECT COUNT(*) FROM mshop_media")->fetchColumn();
$productCount = $db->query("SELECT COUNT(*) FROM mshop_product")->fetchColumn();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aimeos CMS - Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; background: #343a40; }
        .sidebar a { color: #adb5bd; text-decoration: none; padding: 10px 20px; display: block; }
        .sidebar a:hover, .sidebar a.active { color: white; background: #495057; }
        .content { padding: 20px; }
        .stat-card { border-left: 4px solid; }
        .stat-card.media { border-left-color: #0d6efd; }
        .stat-card.products { border-left-color: #198754; }
        .stat-card.users { border-left-color: #ffc107; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-2 sidebar py-3">
                <h5 class="text-white px-3 mb-4">Aimeos CMS</h5>
                <a href="/admin/dashboard.php" class="active"><i class="fas fa-tachometer-alt me-2"></i>Dashboard</a>
                <a href="/admin/media.php"><i class="fas fa-images me-2"></i>Media</a>
                <a href="/admin/products.php"><i class="fas fa-box me-2"></i>Products</a>
                <hr class="text-secondary">
                <a href="/admin/logout.php"><i class="fas fa-sign-out-alt me-2"></i>Logout</a>
                <a href="/" class="mt-3"><i class="fas fa-arrow-left me-2"></i>Back to Blog</a>
            </nav>
            <main class="col-md-10 content">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2>Dashboard</h2>
                    <span class="text-muted">Welcome, <?= htmlspecialchars($user['firstname'] . ' ' . $user['lastname']) ?></span>
                </div>

                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="card stat-card media">
                            <div class="card-body">
                                <h5 class="card-title text-muted">Media Files</h5>
                                <h2><?= $mediaCount ?></h2>
                                <a href="/admin/media.php" class="text-decoration-none">Manage →</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card stat-card products">
                            <div class="card-body">
                                <h5 class="card-title text-muted">Products</h5>
                                <h2><?= $productCount ?></h2>
                                <a href="/admin/products.php" class="text-decoration-none">Manage →</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card stat-card users">
                            <div class="card-body">
                                <h5 class="card-title text-muted">Your Role</h5>
                                <h2><?= $user['roleid'] == 1 ? 'Admin' : 'Editor' ?></h2>
                                <span class="text-muted"><?= htmlspecialchars($user['email']) ?></span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">Recent Activity</div>
                    <div class="card-body">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Action</th>
                                    <th>Resource</th>
                                    <th>Time</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><span class="badge bg-success">Created</span></td>
                                    <td>Media: SEO Plugin Banner</td>
                                    <td>Today</td>
                                </tr>
                                <tr>
                                    <td><span class="badge bg-primary">Updated</span></td>
                                    <td>Product: Premium Blog Theme - Minimal</td>
                                    <td>Today</td>
                                </tr>
                                <tr>
                                    <td><span class="badge bg-success">Created</span></td>
                                    <td>Product: Social Media Integration</td>
                                    <td>Yesterday</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
