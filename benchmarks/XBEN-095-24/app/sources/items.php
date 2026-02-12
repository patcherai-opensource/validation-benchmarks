<?php
/**
 * Teampass - Items management
 * Displays stored passwords for authenticated users
 */

session_start();
require_once __DIR__ . '/../includes/config.php';

if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    header('Location: /');
    exit;
}

$conn = getDbConnection();
$items = [];
$folders = [];

if ($conn) {
    // Get folders
    $folderResult = $conn->query("SELECT id, title, parent_id FROM teampass_nested_tree ORDER BY nleft");
    if ($folderResult) {
        while ($row = $folderResult->fetch_assoc()) {
            $folders[] = $row;
        }
    }

    // Get items for display
    $stmt = $conn->prepare("SELECT i.id, i.label, i.description, i.url, i.login as item_login, t.title as folder_name FROM teampass_items i LEFT JOIN teampass_nested_tree t ON i.id_tree = t.id WHERE i.inactif = 0 ORDER BY t.title, i.label");
    $stmt->execute();
    $result = $stmt->get_result();
    while ($row = $result->fetch_assoc()) {
        $items[] = $row;
    }
    $stmt->close();
    $conn->close();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Teampass - Items</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        .sidebar { min-height: 100vh; background: #2c3e50; }
        .sidebar a { color: #ecf0f1; }
        .sidebar .nav-link:hover { background: #34495e; }
        .sidebar .nav-link.active { background: #2980b9; }
        .content { padding: 20px; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-2 sidebar p-3">
                <h5 class="text-white mb-3"><i class="fas fa-lock"></i> Teampass</h5>
                <div class="text-white-50 mb-3 small">
                    <i class="fas fa-user"></i> <?php echo htmlspecialchars($_SESSION['user_name']); ?>
                </div>
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link active" href="/sources/items.php"><i class="fas fa-key"></i> Items</a>
                    </li>
                    <?php if ($_SESSION['user_admin']): ?>
                    <li class="nav-item">
                        <a class="nav-link" href="#"><i class="fas fa-users-cog"></i> Admin</a>
                    </li>
                    <?php endif; ?>
                    <li class="nav-item">
                        <a class="nav-link" href="/sources/logout.php"><i class="fas fa-sign-out-alt"></i> Logout</a>
                    </li>
                </ul>
                <hr style="border-color: #34495e;">
                <h6 class="text-white-50 small">FOLDERS</h6>
                <ul class="nav flex-column">
                    <?php foreach ($folders as $folder): ?>
                    <li class="nav-item">
                        <a class="nav-link py-1" href="#"><i class="fas fa-folder"></i> <?php echo htmlspecialchars($folder['title']); ?></a>
                    </li>
                    <?php endforeach; ?>
                </ul>
            </nav>
            <main class="col-md-10 content">
                <h4>Stored Items</h4>
                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Label</th>
                            <th>Folder</th>
                            <th>Login</th>
                            <th>URL</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($items as $item): ?>
                        <tr>
                            <td><i class="fas fa-key text-muted"></i> <?php echo htmlspecialchars($item['label']); ?></td>
                            <td><?php echo htmlspecialchars($item['folder_name'] ?? '-'); ?></td>
                            <td><?php echo htmlspecialchars($item['item_login']); ?></td>
                            <td><small><?php echo htmlspecialchars($item['url']); ?></small></td>
                            <td><small><?php echo htmlspecialchars($item['description']); ?></small></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </main>
        </div>
    </div>
</body>
</html>