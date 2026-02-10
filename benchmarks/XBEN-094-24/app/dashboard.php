<?php
session_start();
require_once 'includes/db.php';
require_once 'includes/website.lib.php';

$user = null;
if (isset($_COOKIE['session_token'])) {
    $user = validateSession($_COOKIE['session_token']);
}

if (!$user) {
    header('Location: login.php');
    exit;
}

$message = '';
$messageType = '';

if (isset($_GET['deleted'])) {
    $message = 'Page deleted successfully.';
    $messageType = 'success';
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['delete_page'])) {
    $filename = $_POST['delete_page'];
    if (deletePage($filename)) {
        header('Location: dashboard.php?deleted=1');
        exit;
    } else {
        $message = 'Failed to delete page.';
        $messageType = 'danger';
    }
}

$pages = getPageList();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - WebBuilder Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="assets/css/style.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="index.php">
                <strong>WebBuilder Pro</strong>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="index.php">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="features.php">Features</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="dashboard.php">Dashboard</a>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <span class="nav-link">Welcome, <?php echo htmlspecialchars($user['username']); ?></span>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="logout.php">Logout</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container py-5">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1>My Pages</h1>
            <a href="create-page.php" class="btn btn-primary">Create New Page</a>
        </div>

        <?php if ($message): ?>
        <div class="alert alert-<?php echo $messageType; ?> alert-dismissible fade show">
            <?php echo htmlspecialchars($message); ?>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        <?php endif; ?>

        <?php if (empty($pages)): ?>
        <div class="alert alert-info">
            You haven't created any pages yet. <a href="create-page.php">Create your first page</a>
        </div>
        <?php else: ?>
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Page Title</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($pages as $page): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($page['title']); ?></td>
                        <td><?php echo date('Y-m-d H:i', $page['created']); ?></td>
                        <td>
                            <a href="pages/<?php echo htmlspecialchars($page['filename']); ?>" class="btn btn-sm btn-outline-primary" target="_blank">View</a>
                            <form method="POST" class="d-inline" onsubmit="return confirm('Are you sure you want to delete this page?');">
                                <input type="hidden" name="delete_page" value="<?php echo htmlspecialchars($page['filename']); ?>">
                                <button type="submit" class="btn btn-sm btn-outline-danger">Delete</button>
                            </form>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        <?php endif; ?>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
