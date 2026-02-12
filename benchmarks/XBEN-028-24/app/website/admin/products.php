<?php
require_once __DIR__ . '/auth.php';
requireAuth();

$user = getCurrentUser();
$db = getDb();

$products = $db->query("SELECT * FROM mshop_product ORDER BY id DESC")->fetchAll(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aimeos CMS - Products</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; background: #343a40; }
        .sidebar a { color: #adb5bd; text-decoration: none; padding: 10px 20px; display: block; }
        .sidebar a:hover, .sidebar a.active { color: white; background: #495057; }
        .content { padding: 20px; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-2 sidebar py-3">
                <h5 class="text-white px-3 mb-4">Aimeos CMS</h5>
                <a href="/admin/dashboard.php"><i class="fas fa-tachometer-alt me-2"></i>Dashboard</a>
                <a href="/admin/media.php"><i class="fas fa-images me-2"></i>Media</a>
                <a href="/admin/products.php" class="active"><i class="fas fa-box me-2"></i>Products</a>
                <hr class="text-secondary">
                <a href="/admin/logout.php"><i class="fas fa-sign-out-alt me-2"></i>Logout</a>
                <a href="/" class="mt-3"><i class="fas fa-arrow-left me-2"></i>Back to Blog</a>
            </nav>
            <main class="col-md-10 content">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2>Products</h2>
                </div>

                <div class="card">
                    <div class="card-body">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Code</th>
                                    <th>Label</th>
                                    <th>Type</th>
                                    <th>Status</th>
                                    <th>Modified</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($products as $product): ?>
                                <tr>
                                    <td><?= $product['id'] ?></td>
                                    <td><code><?= htmlspecialchars($product['code']) ?></code></td>
                                    <td><?= htmlspecialchars($product['label']) ?></td>
                                    <td><?= htmlspecialchars($product['type']) ?></td>
                                    <td>
                                        <?php if ($product['status'] == 1): ?>
                                            <span class="badge bg-success">Active</span>
                                        <?php else: ?>
                                            <span class="badge bg-secondary">Inactive</span>
                                        <?php endif; ?>
                                    </td>
                                    <td><?= htmlspecialchars($product['mtime']) ?></td>
                                </tr>
                                <?php endforeach; ?>
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
