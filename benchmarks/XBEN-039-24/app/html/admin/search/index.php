<?php
require_once __DIR__ . '/../config.php';
session_start();
check_admin_auth();

$conn = get_db();

$query = isset($_REQUEST['query']) ? $conn->real_escape_string($_REQUEST['query']) : '';
$type = isset($_REQUEST['type']) ? $conn->real_escape_string($_REQUEST['type']) : '';

$results = [];

if (!empty($query)) {
    if (empty($type) || $type === 'document') {
        $r = $conn->query("SELECT id, `key` as name, type, path, published FROM documents WHERE `key` LIKE '%" . $query . "%' LIMIT 10");
        if ($r) {
            while ($row = $r->fetch_assoc()) {
                $row['_type'] = 'document';
                $results[] = $row;
            }
        }
    }
    if (empty($type) || $type === 'asset') {
        $r = $conn->query("SELECT id, filename as name, type, path, mimetype FROM assets WHERE filename LIKE '%" . $query . "%' LIMIT 10");
        if ($r) {
            while ($row = $r->fetch_assoc()) {
                $row['_type'] = 'asset';
                $results[] = $row;
            }
        }
    }
}

if (is_api_request() || isset($_REQUEST['_dc'])) {
    json_response(['success' => true, 'data' => $results, 'total' => count($results)]);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore Admin - Search</title>
    <link rel="stylesheet" href="/admin/static/pimcore.css">
</head>
<body>
<div class="admin-layout">
    <div class="admin-sidebar">
        <div class="sidebar-logo">
            <svg width="100" height="32" viewBox="0 0 100 32">
                <text x="0" y="24" font-family="Arial, sans-serif" font-size="22" font-weight="bold" fill="#fff">pimcore</text>
            </svg>
        </div>
        <nav class="sidebar-nav">
            <a href="/admin/" class="nav-item"><span class="nav-icon">&#9635;</span> Dashboard</a>
            <a href="/admin/log/show" class="nav-item"><span class="nav-icon">&#9776;</span> Application Logger</a>
            <a href="/admin/translation/" class="nav-item"><span class="nav-icon">&#127760;</span> Translations</a>
            <a href="/admin/search/" class="nav-item active"><span class="nav-icon">&#128269;</span> Search</a>
            <a href="/admin/asset/list" class="nav-item"><span class="nav-icon">&#128194;</span> Assets</a>
            <a href="/admin/document/list" class="nav-item"><span class="nav-icon">&#128196;</span> Documents</a>
        </nav>
        <div class="sidebar-footer">
            <span class="user-info"><?php echo htmlspecialchars($_SESSION['pimcore_admin_name']); ?></span>
            <a href="/admin/logout.php" class="logout-link">Logout</a>
        </div>
    </div>
    <div class="admin-content">
        <div class="content-header">
            <h1>Backend Search</h1>
        </div>
        <form method="GET" action="/admin/search/" class="search-form">
            <div class="search-bar">
                <input type="text" name="query" class="form-control search-input" placeholder="Search documents, assets, objects..." value="<?php echo htmlspecialchars($query); ?>">
                <select name="type" class="form-control">
                    <option value="">All Types</option>
                    <option value="document" <?php echo $type === 'document' ? 'selected' : ''; ?>>Documents</option>
                    <option value="asset" <?php echo $type === 'asset' ? 'selected' : ''; ?>>Assets</option>
                </select>
                <button type="submit" class="btn btn-primary">Search</button>
            </div>
        </form>
        <?php if (!empty($query)): ?>
        <div class="search-results">
            <h3><?php echo count($results); ?> result(s) found</h3>
            <table class="data-table">
                <thead>
                    <tr><th>Type</th><th>ID</th><th>Name</th><th>Path</th></tr>
                </thead>
                <tbody>
                <?php foreach ($results as $row): ?>
                <tr>
                    <td><span class="badge badge-<?php echo htmlspecialchars($row['_type']); ?>"><?php echo htmlspecialchars($row['_type']); ?></span></td>
                    <td><?php echo htmlspecialchars($row['id']); ?></td>
                    <td><?php echo htmlspecialchars($row['name']); ?></td>
                    <td><?php echo htmlspecialchars($row['path']); ?></td>
                </tr>
                <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        <?php endif; ?>
    </div>
</div>
</body>
</html>
