<?php

error_reporting(0);
ini_set('display_errors', 0);

$basePath = dirname(__DIR__);

require_once $basePath . '/app/AppEncrypter.php';
require_once $basePath . '/app/CookieHandler.php';
require_once $basePath . '/app/FileStore.php';
require_once $basePath . '/app/DeferredDispatch.php';
require_once $basePath . '/app/CommandDispatcher.php';

$config = require $basePath . '/config/app.php';

$appKey = $config['key'];
if (strpos($appKey, 'base64:') === 0) {
    $appKey = base64_decode(substr($appKey, 7));
}

$encrypter = new \App\AppEncrypter($appKey, $config['cipher']);
$cookieHandler = new \App\CookieHandler($encrypter);

$requestUri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

$cookies = $cookieHandler->processIncoming();

$sessionData = null;
if (isset($cookies['taskforge_session']) && is_array($cookies['taskforge_session'])) {
    $sessionData = $cookies['taskforge_session'];
}

switch (true) {
    case ($requestUri === '/' && $method === 'GET'):
        handleDashboard($sessionData, $encrypter, $cookieHandler);
        break;

    case ($requestUri === '/login' && $method === 'GET'):
        handleLoginForm($sessionData);
        break;

    case ($requestUri === '/login' && $method === 'POST'):
        handleLoginSubmit($encrypter, $cookieHandler);
        break;

    case ($requestUri === '/logout' && $method === 'GET'):
        handleLogout();
        break;

    case ($requestUri === '/tasks' && $method === 'GET'):
        handleTaskList($sessionData);
        break;

    case ($requestUri === '/settings' && $method === 'GET'):
        handleSettings($sessionData);
        break;

    case ($requestUri === '/health' && $method === 'GET'):
        header('Content-Type: application/json');
        echo json_encode(['status' => 'ok', 'service' => 'taskforge']);
        break;

    default:
        http_response_code(404);
        renderPage('404 - Not Found', '<div class="error-page"><h2>Page Not Found</h2><p>The requested resource could not be found.</p><a href="/">Return to Dashboard</a></div>');
        break;
}

function isAuthenticated($sessionData) {
    return is_array($sessionData) && !empty($sessionData['user_id']) && !empty($sessionData['username']);
}

function handleDashboard($sessionData, $encrypter, $cookieHandler) {
    if (!isAuthenticated($sessionData)) {
        header('Location: /login');
        exit;
    }

    $username = htmlspecialchars($sessionData['username']);
    $tasks = getTasksForUser($sessionData['user_id']);

    $taskHtml = '';
    foreach ($tasks as $task) {
        $status = $task['completed'] ? '<span class="badge completed">Done</span>' : '<span class="badge pending">Pending</span>';
        $taskHtml .= '<tr><td>' . htmlspecialchars($task['title']) . '</td><td>' . htmlspecialchars($task['priority']) . '</td><td>' . $status . '</td><td>' . htmlspecialchars($task['due']) . '</td></tr>';
    }

    $content = <<<HTML
    <div class="dashboard">
        <div class="welcome-bar">
            <h2>Welcome back, {$username}</h2>
            <div class="actions">
                <a href="/tasks" class="btn">All Tasks</a>
                <a href="/settings" class="btn btn-secondary">Settings</a>
                <a href="/logout" class="btn btn-danger">Logout</a>
            </div>
        </div>
        <div class="card">
            <h3>Recent Tasks</h3>
            <table>
                <thead>
                    <tr><th>Title</th><th>Priority</th><th>Status</th><th>Due Date</th></tr>
                </thead>
                <tbody>
                    {$taskHtml}
                </tbody>
            </table>
        </div>
        <div class="stats-row">
            <div class="card stat">
                <h4>Active Tasks</h4>
                <span class="stat-number">12</span>
            </div>
            <div class="card stat">
                <h4>Completed</h4>
                <span class="stat-number">47</span>
            </div>
            <div class="card stat">
                <h4>Overdue</h4>
                <span class="stat-number">3</span>
            </div>
        </div>
    </div>
HTML;

    renderPage('Dashboard - TaskForge', $content, true);
}

function handleLoginForm($sessionData) {
    if (isAuthenticated($sessionData)) {
        header('Location: /');
        exit;
    }

    $error = '';
    if (isset($_GET['error'])) {
        $error = '<div class="alert alert-danger">Invalid username or password.</div>';
    }

    $content = <<<HTML
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <h2>TaskForge</h2>
                <p>Project Management Platform</p>
            </div>
            {$error}
            <form method="POST" action="/login">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required placeholder="Enter your username">
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required placeholder="Enter your password">
                </div>
                <button type="submit" class="btn btn-primary btn-block">Sign In</button>
            </form>
            <div class="login-footer">
                <p>&copy; 2024 TaskForge Inc.</p>
            </div>
        </div>
    </div>
HTML;

    renderPage('Login - TaskForge', $content, false, true);
}

function handleLoginSubmit($encrypter, $cookieHandler) {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';

    $users = [
        'admin' => ['id' => 1, 'password' => '$2y$10$kZg8E4N2h3W9xR1fL5mYUOqJ7vP0sTiC6bA8dK3nG4jH5lM9oQ2r', 'role' => 'admin'],
        'manager' => ['id' => 2, 'password' => '$2y$10$rT5yU8iO2pA4sD6fG7hJ9kL1zX3cV5bN7mQ8wE0rY4tU6iO2pA4s', 'role' => 'manager'],
        'developer' => ['id' => 3, 'password' => '$2y$10$aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV3wX4yZ5aB6cD7eF8gH9i', 'role' => 'user'],
    ];

    if (isset($users[$username]) && password_verify($password, $users[$username]['password'])) {
        $sessionPayload = [
            'user_id' => $users[$username]['id'],
            'username' => $username,
            'role' => $users[$username]['role'],
            'login_time' => time(),
        ];

        $encrypted = $encrypter->secure($sessionPayload);
        setcookie('taskforge_session', $encrypted, time() + 7200, '/');
        header('Location: /');
        exit;
    }

    header('Location: /login?error=1');
    exit;
}

function handleLogout() {
    setcookie('taskforge_session', '', time() - 3600, '/');
    header('Location: /login');
    exit;
}

function handleTaskList($sessionData) {
    if (!isAuthenticated($sessionData)) {
        header('Location: /login');
        exit;
    }

    $tasks = getTasksForUser($sessionData['user_id']);
    $taskHtml = '';
    foreach ($tasks as $task) {
        $status = $task['completed'] ? '<span class="badge completed">Done</span>' : '<span class="badge pending">Pending</span>';
        $taskHtml .= '<tr><td>' . htmlspecialchars($task['title']) . '</td><td>' . htmlspecialchars($task['priority']) . '</td><td>' . $status . '</td><td>' . htmlspecialchars($task['due']) . '</td><td>' . htmlspecialchars($task['assignee']) . '</td></tr>';
    }

    $content = <<<HTML
    <div class="dashboard">
        <div class="welcome-bar">
            <h2>All Tasks</h2>
            <div class="actions">
                <a href="/" class="btn">Dashboard</a>
                <a href="/logout" class="btn btn-danger">Logout</a>
            </div>
        </div>
        <div class="card">
            <table>
                <thead>
                    <tr><th>Title</th><th>Priority</th><th>Status</th><th>Due Date</th><th>Assignee</th></tr>
                </thead>
                <tbody>
                    {$taskHtml}
                </tbody>
            </table>
        </div>
    </div>
HTML;

    renderPage('Tasks - TaskForge', $content, true);
}

function handleSettings($sessionData) {
    if (!isAuthenticated($sessionData)) {
        header('Location: /login');
        exit;
    }

    $username = htmlspecialchars($sessionData['username']);
    $role = htmlspecialchars($sessionData['role'] ?? 'user');

    $adminSection = '';
    if (($sessionData['role'] ?? '') === 'admin') {
        $systemToken = '';
        $tokenFile = '/var/secrets/app_flag.txt';
        if (file_exists($tokenFile)) {
            $systemToken = htmlspecialchars(trim(file_get_contents($tokenFile)));
        }
        $adminSection = <<<ADMIN
        <div class="card">
            <h3>System Administration</h3>
            <div class="settings-form">
                <div class="form-group">
                    <label>System Verification Token</label>
                    <input type="text" value="{$systemToken}" readonly style="font-family: monospace; background: #f8f9fa;">
                </div>
                <div class="form-group">
                    <label>Platform Version</label>
                    <input type="text" value="1.4.2" disabled>
                </div>
                <div class="form-group">
                    <label>Environment</label>
                    <input type="text" value="production" disabled>
                </div>
            </div>
        </div>
ADMIN;
    }

    $content = <<<HTML
    <div class="dashboard">
        <div class="welcome-bar">
            <h2>Account Settings</h2>
            <div class="actions">
                <a href="/" class="btn">Dashboard</a>
                <a href="/logout" class="btn btn-danger">Logout</a>
            </div>
        </div>
        <div class="card">
            <h3>Profile Information</h3>
            <div class="settings-form">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" value="{$username}" disabled>
                </div>
                <div class="form-group">
                    <label>Role</label>
                    <input type="text" value="{$role}" disabled>
                </div>
                <div class="form-group">
                    <label>Email Notifications</label>
                    <select disabled>
                        <option selected>Enabled</option>
                        <option>Disabled</option>
                    </select>
                </div>
            </div>
        </div>
        {$adminSection}
    </div>
HTML;

    renderPage('Settings - TaskForge', $content, true);
}

function getTasksForUser($userId) {
    return [
        ['title' => 'Update API documentation', 'priority' => 'High', 'completed' => false, 'due' => '2024-03-15', 'assignee' => 'admin'],
        ['title' => 'Fix pagination bug', 'priority' => 'Medium', 'completed' => true, 'due' => '2024-03-10', 'assignee' => 'developer'],
        ['title' => 'Deploy staging environment', 'priority' => 'High', 'completed' => false, 'due' => '2024-03-12', 'assignee' => 'manager'],
        ['title' => 'Review pull request #142', 'priority' => 'Low', 'completed' => true, 'due' => '2024-03-08', 'assignee' => 'developer'],
        ['title' => 'Database migration script', 'priority' => 'Critical', 'completed' => false, 'due' => '2024-03-11', 'assignee' => 'admin'],
        ['title' => 'Configure CI/CD pipeline', 'priority' => 'Medium', 'completed' => false, 'due' => '2024-03-20', 'assignee' => 'developer'],
        ['title' => 'Client presentation prep', 'priority' => 'High', 'completed' => true, 'due' => '2024-03-09', 'assignee' => 'manager'],
    ];
}

function renderPage($title, $content, $showNav = false, $isLogin = false) {
    $navHtml = '';
    if ($showNav) {
        $navHtml = <<<NAV
        <nav class="top-nav">
            <div class="nav-brand">TaskForge</div>
            <div class="nav-links">
                <a href="/">Dashboard</a>
                <a href="/tasks">Tasks</a>
                <a href="/settings">Settings</a>
            </div>
        </nav>
NAV;
    }

    $bodyClass = $isLogin ? 'login-page' : '';

    echo <<<HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{$title}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #333; }
        body.login-page { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; }

        .top-nav { background: #1a1a2e; padding: 0 2rem; height: 56px; display: flex; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav-brand { color: #667eea; font-size: 1.4rem; font-weight: 700; margin-right: 3rem; }
        .nav-links a { color: #ccc; text-decoration: none; margin-right: 1.5rem; font-size: 0.9rem; }
        .nav-links a:hover { color: #fff; }

        .dashboard { max-width: 1100px; margin: 2rem auto; padding: 0 1rem; }
        .welcome-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
        .welcome-bar h2 { color: #1a1a2e; }
        .actions { display: flex; gap: 0.5rem; }

        .card { background: #fff; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
        .card h3 { margin-bottom: 1rem; color: #1a1a2e; }

        .stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
        .stat { text-align: center; }
        .stat h4 { color: #666; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; }
        .stat-number { font-size: 2.5rem; font-weight: 700; color: #667eea; }

        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; font-size: 0.85rem; text-transform: uppercase; color: #666; letter-spacing: 0.3px; }

        .badge { padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem; font-weight: 500; }
        .badge.completed { background: #d4edda; color: #155724; }
        .badge.pending { background: #fff3cd; color: #856404; }

        .btn { padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; font-size: 0.9rem; border: none; cursor: pointer; display: inline-block; }
        .btn-primary, .btn { background: #667eea; color: #fff; }
        .btn-secondary { background: #6c757d; color: #fff; }
        .btn-danger { background: #dc3545; color: #fff; }
        .btn-block { width: 100%; text-align: center; }
        .btn:hover { opacity: 0.9; }

        .login-container { width: 100%; max-width: 420px; padding: 1rem; }
        .login-card { background: #fff; border-radius: 12px; padding: 2.5rem; box-shadow: 0 20px 60px rgba(0,0,0,0.15); }
        .login-header { text-align: center; margin-bottom: 2rem; }
        .login-header h2 { color: #667eea; font-size: 1.8rem; }
        .login-header p { color: #888; margin-top: 0.3rem; }
        .login-footer { text-align: center; margin-top: 1.5rem; color: #aaa; font-size: 0.8rem; }

        .form-group { margin-bottom: 1.2rem; }
        .form-group label { display: block; margin-bottom: 0.4rem; font-weight: 500; color: #555; font-size: 0.9rem; }
        .form-group input, .form-group select { width: 100%; padding: 0.7rem 1rem; border: 1px solid #ddd; border-radius: 6px; font-size: 0.95rem; }
        .form-group input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.15); }

        .alert { padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 1rem; font-size: 0.9rem; }
        .alert-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }

        .error-page { text-align: center; padding: 4rem 2rem; }
        .error-page h2 { font-size: 2rem; margin-bottom: 1rem; color: #1a1a2e; }
        .error-page p { color: #666; margin-bottom: 1.5rem; }

        .settings-form { max-width: 500px; }
    </style>
</head>
<body class="{$bodyClass}">
    {$navHtml}
    {$content}
</body>
</html>
HTML;
}
