<?php
session_start();

// Verify authentication
if (!isset($_SESSION['be_user']) || $_SESSION['be_authenticated'] !== true) {
    header('Location: index.php');
    exit;
}

// Session timeout check
$config = include __DIR__ . '/config.php';
$timeout = isset($config['sessionTimeout']) ? $config['sessionTimeout'] : 3600;
if (isset($_SESSION['be_login_time']) && (time() - $_SESSION['be_login_time']) > $timeout) {
    session_destroy();
    header('Location: index.php');
    exit;
}

$conn = new mysqli(
    getenv('MYSQL_HOST') ?: '127.0.0.1',
    getenv('MYSQL_USER') ?: 'user',
    getenv('MYSQL_PASSWORD') ?: 'password',
    getenv('MYSQL_DATABASE') ?: 'blogDB'
);

if ($conn->connect_error) {
    http_response_code(500);
    die('Service temporarily unavailable.');
}

// Handle logout
if (isset($_GET['action']) && $_GET['action'] === 'logout') {
    session_destroy();
    header('Location: index.php');
    exit;
}

// Fetch dashboard data
$postCount = 0;
$userCount = 0;
$systemNotes = [];

$res = $conn->query("SELECT COUNT(*) as cnt FROM posts");
if ($res) {
    $row = $res->fetch_assoc();
    $postCount = $row['cnt'];
}

$res = $conn->query("SELECT COUNT(*) as cnt FROM be_accounts WHERE is_active = 1");
if ($res) {
    $row = $res->fetch_assoc();
    $userCount = $row['cnt'];
}

// Load system notes for admin users
if ($_SESSION['be_role'] === 'admin') {
    $res = $conn->query("SELECT * FROM system_notes ORDER BY created_at DESC LIMIT 10");
    if ($res) {
        while ($row = $res->fetch_assoc()) {
            $systemNotes[] = $row;
        }
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContentHub - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f2f5; }
        .topbar {
            background: #1a1a2e;
            color: white;
            padding: 12px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .topbar .brand { font-size: 16px; font-weight: bold; }
        .topbar .user-info { font-size: 13px; }
        .topbar a { color: #8ecae6; text-decoration: none; margin-left: 15px; }
        .sidebar {
            position: fixed;
            left: 0;
            top: 44px;
            width: 220px;
            height: calc(100% - 44px);
            background: #16213e;
            color: #ccc;
            padding-top: 20px;
        }
        .sidebar a {
            display: block;
            padding: 10px 20px;
            color: #aaa;
            text-decoration: none;
            font-size: 13px;
        }
        .sidebar a:hover, .sidebar a.active {
            background: #1a1a2e;
            color: white;
        }
        .sidebar .section-title {
            padding: 10px 20px 5px;
            font-size: 10px;
            text-transform: uppercase;
            color: #666;
        }
        .content {
            margin-left: 220px;
            padding: 25px;
        }
        .content h2 {
            font-size: 20px;
            margin-bottom: 20px;
            color: #333;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }
        .stat-card .label { font-size: 12px; color: #888; text-transform: uppercase; }
        .stat-card .value { font-size: 28px; font-weight: bold; color: #333; margin-top: 5px; }
        .panel {
            background: white;
            padding: 20px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            margin-bottom: 20px;
        }
        .panel h3 { font-size: 15px; color: #333; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .note-item {
            padding: 10px 0;
            border-bottom: 1px solid #f5f5f5;
            font-size: 13px;
        }
        .note-item:last-child { border-bottom: none; }
        .note-item .note-title { font-weight: bold; color: #333; }
        .note-item .note-content { color: #666; margin-top: 3px; }
        .note-item .note-date { color: #aaa; font-size: 11px; margin-top: 3px; }
        .role-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .role-admin { background: #e8f4fd; color: #0078d4; }
        .role-editor { background: #e8f8e8; color: #2d8a2d; }
    </style>
</head>
<body>
    <div class="topbar">
        <div class="brand">ContentHub Administration</div>
        <div class="user-info">
            Logged in as: <strong><?php echo htmlspecialchars($_SESSION['be_user']); ?></strong>
            <span class="role-badge role-<?php echo htmlspecialchars($_SESSION['be_role']); ?>">
                <?php echo htmlspecialchars($_SESSION['be_role']); ?>
            </span>
            <a href="?action=logout">Logout</a>
        </div>
    </div>

    <div class="sidebar">
        <div class="section-title">Main</div>
        <a href="dashboard.php" class="active">Dashboard</a>
        <a href="#">Content</a>
        <a href="#">Media</a>
        <div class="section-title">Administration</div>
        <a href="#">User Management</a>
        <a href="#">Extensions</a>
        <a href="#">Configuration</a>
        <div class="section-title">System</div>
        <a href="#">Log</a>
        <a href="#">Maintenance</a>
    </div>

    <div class="content">
        <h2>Dashboard</h2>

        <div class="stats">
            <div class="stat-card">
                <div class="label">Published Content</div>
                <div class="value"><?php echo $postCount; ?></div>
            </div>
            <div class="stat-card">
                <div class="label">Active Users</div>
                <div class="value"><?php echo $userCount; ?></div>
            </div>
            <div class="stat-card">
                <div class="label">Your Role</div>
                <div class="value" style="font-size:18px;"><?php echo htmlspecialchars(ucfirst($_SESSION['be_role'])); ?></div>
            </div>
        </div>

        <?php if ($_SESSION['be_role'] === 'admin' && !empty($systemNotes)): ?>
        <div class="panel">
            <h3>System Notes</h3>
            <?php foreach ($systemNotes as $note): ?>
                <div class="note-item">
                    <div class="note-title"><?php echo htmlspecialchars($note['title']); ?></div>
                    <div class="note-content"><?php echo htmlspecialchars($note['content']); ?></div>
                    <div class="note-date"><?php echo htmlspecialchars($note['created_at']); ?></div>
                </div>
            <?php endforeach; ?>
        </div>
        <?php endif; ?>

        <div class="panel">
            <h3>Recent Activity</h3>
            <p style="color: #999; font-size: 13px;">No recent activity to display.</p>
        </div>
    </div>
</body>
</html>
