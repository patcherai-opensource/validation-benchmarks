<?php
/**
 * myKnowledgeBase Admin Backend
 *
 * @package   myKnowledgeBase
 */

session_start();

define('MKB_ROOT_DIR', dirname(__DIR__));
define('MKB_IMAGES_DIR', MKB_ROOT_DIR . '/images/');

require_once MKB_ROOT_DIR . '/includes/config.php';
require_once MKB_ROOT_DIR . '/includes/functions.php';
require_once MKB_ROOT_DIR . '/includes/TopicImage.php';

$action = isset($_GET['action']) ? $_GET['action'] : 'dashboard';

// Handle login
if ($action === 'login' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = isset($_POST['username']) ? trim($_POST['username']) : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';

    if (isset($mkb_admin_users[$username])) {
        $user = $mkb_admin_users[$username];
        if (password_verify($password, $user['password_hash'])) {
            $_SESSION['admin_authenticated'] = true;
            $_SESSION['admin_user'] = $username;
            $_SESSION['admin_display_name'] = $user['display_name'];
            $_SESSION['admin_role'] = $user['role'];
            header('Location: /admin/?action=dashboard');
            exit();
        }
    }
    $login_error = 'Invalid username or password.';
}

// Handle logout
if ($action === 'logout') {
    session_destroy();
    header('Location: /admin/');
    exit();
}

// If not authenticated, show login
if (!mkb_is_admin_logged_in()) {
    $action = 'login';
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>myKnowledgeBase - Administration</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
<nav class="navbar">
    <div class="container">
        <a class="navbar-brand" href="/admin/">myKnowledgeBase Admin</a>
        <div class="navbar-links">
            <a href="/">View Site</a>
            <?php if (mkb_is_admin_logged_in()): ?>
                <a href="/admin/?action=logout">Logout (<?php echo htmlspecialchars($_SESSION['admin_display_name']); ?>)</a>
            <?php endif; ?>
        </div>
    </div>
</nav>

<?php if ($action === 'login'): ?>
<div class="container">
    <div class="login-container">
        <div class="card">
            <h1>Admin Login</h1>
            <?php if (isset($login_error)): ?>
                <div class="alert alert-danger"><?php echo htmlspecialchars($login_error); ?></div>
            <?php endif; ?>
            <form method="post" action="/admin/?action=login">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" name="username" id="username" class="form-control" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" name="password" id="password" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%">Sign In</button>
            </form>
        </div>
    </div>
</div>
<?php else: ?>

<div class="admin-layout">
    <div class="admin-sidebar">
        <div class="sidebar-header">Navigation</div>
        <a href="/admin/?action=dashboard" <?php echo $action === 'dashboard' ? 'class="active"' : ''; ?>>Dashboard</a>
        <a href="/admin/?action=topics" <?php echo in_array($action, ['topics','addtopic','savetopic','edittopic','updatetopic']) ? 'class="active"' : ''; ?>>Topics</a>
        <a href="/admin/?action=faqs" <?php echo $action === 'faqs' ? 'class="active"' : ''; ?>>FAQ Entries</a>
        <a href="/admin/?action=configuration" <?php echo $action === 'configuration' ? 'class="active"' : ''; ?>>Configuration</a>
        <a href="/admin/?action=system" <?php echo $action === 'system' ? 'class="active"' : ''; ?>>System Info</a>
    </div>

    <div class="admin-main">
    <?php
    switch ($action) {
        case 'dashboard':
            include __DIR__ . '/pages/dashboard.php';
            break;
        case 'topics':
            include __DIR__ . '/pages/topics.php';
            break;
        case 'addtopic':
            include __DIR__ . '/pages/topic.add.php';
            break;
        case 'savetopic':
            include __DIR__ . '/pages/topic.save.php';
            break;
        case 'edittopic':
            include __DIR__ . '/pages/topic.edit.php';
            break;
        case 'updatetopic':
            include __DIR__ . '/pages/topic.update.php';
            break;
        case 'faqs':
            include __DIR__ . '/pages/faqs.php';
            break;
        case 'configuration':
            include __DIR__ . '/pages/configuration.php';
            break;
        case 'system':
            include __DIR__ . '/pages/system.php';
            break;
        default:
            include __DIR__ . '/pages/dashboard.php';
            break;
    }
    ?>
    </div>
</div>

<?php endif; ?>

<footer class="footer">
    <div class="container">
        <p>&copy; 2024 myKnowledgeBase Administration v3.2.5</p>
    </div>
</footer>
</body>
</html>
