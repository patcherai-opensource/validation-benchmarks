<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');

require_once(__DIR__ . '/../include/db_config.php');
require_once(__DIR__ . '/../include/auth.php');

requireAuth();

$username = $_SESSION['username'];
$role = $_SESSION['role'];
$csrfToken = getCsrfToken();

$pages = array();
$result = mysqli_query($db_connect, "SELECT p.*, u.username as author FROM pages p LEFT JOIN users u ON p.author_id = u.id ORDER BY p.created_at DESC");
if ($result) {
    while ($row = mysqli_fetch_assoc($result)) {
        $pages[] = $row;
    }
}

?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="noindex">
    <title>SiteCraft CMS | Pages</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .sidebar { min-height: 100vh; background: #1e293b; padding-top: 20px; }
        .sidebar .nav-link { color: #94a3b8; padding: 12px 20px; }
        .sidebar .nav-link:hover, .sidebar .nav-link.active { color: #fff; background: rgba(255,255,255,0.1); }
        .sidebar .brand { color: #fff; font-size: 20px; font-weight: bold; padding: 0 20px 20px; border-bottom: 1px solid #334155; margin-bottom: 10px; }
        .content-area { padding: 30px; }
        .card { border: none; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-2 sidebar d-none d-md-block">
                <div class="brand"><i class="fas fa-cube"></i> SiteCraft</div>
                <ul class="nav flex-column">
                    <li class="nav-item"><a class="nav-link" href="/admin/dashboard.php"><i class="fas fa-tachometer-alt me-2"></i>Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link active" href="/admin/pages.php"><i class="fas fa-file-alt me-2"></i>Pages</a></li>
                    <li class="nav-item"><a class="nav-link" href="/admin/media.php"><i class="fas fa-images me-2"></i>Media</a></li>
                    <?php if ($role === 'admin'): ?>
                    <li class="nav-item"><a class="nav-link" href="/admin/settings.php"><i class="fas fa-cog me-2"></i>Settings</a></li>
                    <?php endif; ?>
                    <li class="nav-item mt-4"><a class="nav-link" href="/admin/logout.php"><i class="fas fa-sign-out-alt me-2"></i>Sign Out</a></li>
                </ul>
            </nav>
            <main class="col-md-10 ms-sm-auto content-area">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h3>Pages</h3>
                    <span class="badge bg-primary"><?php echo htmlspecialchars($role); ?>: <?php echo htmlspecialchars($username); ?></span>
                </div>
                <div class="card">
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Title</th>
                                        <th>Slug</th>
                                        <th>Status</th>
                                        <th>Author</th>
                                        <th>Created</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php foreach ($pages as $page): ?>
                                    <tr>
                                        <td><?php echo htmlspecialchars($page['title']); ?></td>
                                        <td><code>/<?php echo htmlspecialchars($page['slug']); ?></code></td>
                                        <td>
                                            <?php if ($page['status'] === 'published'): ?>
                                                <span class="badge bg-success">Published</span>
                                            <?php else: ?>
                                                <span class="badge bg-warning">Draft</span>
                                            <?php endif; ?>
                                        </td>
                                        <td><?php echo htmlspecialchars($page['author'] ?? 'System'); ?></td>
                                        <td><?php echo $page['created_at']; ?></td>
                                    </tr>
                                    <?php endforeach; ?>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
