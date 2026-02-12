<?php

error_reporting(0);
ini_set('display_errors', '0');

$config = require dirname(__DIR__) . '/bootstrap/app.php';

use App\Encryption\Encrypter;
use App\Http\Middleware\EncryptCookies;
use App\Http\Middleware\VerifyCsrfToken;

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

if ($uri === '/ping') {
    header('Content-Type: text/plain');
    echo 'pong';
    exit;
}

$encrypter = new Encrypter($config['key'], $config['cipher']);
$cookieMiddleware = new EncryptCookies($encrypter);
$csrfMiddleware = new VerifyCsrfToken($encrypter);

$decryptedCookies = $cookieMiddleware->handle($_COOKIE);

session_start();

if (!isset($_SESSION['_token'])) {
    $_SESSION['_token'] = bin2hex(random_bytes(20));
}

$request = [
    'method' => $method,
    'uri' => $uri,
    'post' => $_POST,
    'headers' => getallheaders(),
    'session' => $_SESSION,
    'cookies' => $decryptedCookies,
];

if ($uri === '/' || $uri === '') {
    renderDashboard($request, $encrypter, $csrfMiddleware);
    exit;
}

if ($uri === '/login' && $method === 'GET') {
    renderLogin($request, $encrypter);
    exit;
}

if ($uri === '/login' && $method === 'POST') {
    handleLogin($request, $encrypter, $csrfMiddleware);
    exit;
}

if ($uri === '/logout') {
    handleLogout();
    exit;
}

if ($uri === '/tasks' && $method === 'GET') {
    renderTasks($request, $encrypter);
    exit;
}

if ($uri === '/tasks/create' && $method === 'POST') {
    handleCreateTask($request, $encrypter, $csrfMiddleware);
    exit;
}

if ($uri === '/profile' && $method === 'GET') {
    renderProfile($request, $encrypter);
    exit;
}

if (preg_match('#^/tasks/(\d+)/complete$#', $uri, $matches) && $method === 'POST') {
    handleCompleteTask($request, $encrypter, $csrfMiddleware, (int)$matches[1]);
    exit;
}

http_response_code(404);
require dirname(__DIR__) . '/resources/views/404.php';
exit;


function getAuthUser($request) {
    $cookie = isset($request['cookies']['taskflow_session']) ? $request['cookies']['taskflow_session'] : null;
    if ($cookie && is_array($cookie) && isset($cookie['user_id'])) {
        return getUserById($cookie['user_id']);
    }
    return null;
}

function getUserById($id) {
    $users = [
        1 => ['id' => 1, 'name' => 'Admin', 'email' => 'admin@taskflow.local', 'role' => 'admin'],
        2 => ['id' => 2, 'name' => 'Jane Cooper', 'email' => 'jane@taskflow.local', 'role' => 'editor'],
        3 => ['id' => 3, 'name' => 'Bob Wilson', 'email' => 'bob@taskflow.local', 'role' => 'viewer'],
    ];
    return isset($users[$id]) ? $users[$id] : null;
}

function getUserByCredentials($email, $password) {
    $credentials = [
        'admin@taskflow.local' => ['password' => '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'id' => 1],
        'jane@taskflow.local' => ['password' => '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'id' => 2],
        'bob@taskflow.local' => ['password' => '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'id' => 3],
    ];
    if (isset($credentials[$email]) && password_verify($password, $credentials[$email]['password'])) {
        return getUserById($credentials[$email]['id']);
    }
    return null;
}

function getTasks() {
    return [
        ['id' => 1, 'title' => 'Review Q4 financial report', 'status' => 'pending', 'priority' => 'high', 'assigned' => 'Admin', 'due' => '2024-01-15'],
        ['id' => 2, 'title' => 'Update API documentation', 'status' => 'in_progress', 'priority' => 'medium', 'assigned' => 'Jane Cooper', 'due' => '2024-01-20'],
        ['id' => 3, 'title' => 'Deploy v2.3.1 hotfix', 'status' => 'completed', 'priority' => 'critical', 'assigned' => 'Admin', 'due' => '2024-01-10'],
        ['id' => 4, 'title' => 'Onboard new team members', 'status' => 'pending', 'priority' => 'low', 'assigned' => 'Bob Wilson', 'due' => '2024-02-01'],
        ['id' => 5, 'title' => 'Security audit preparation', 'status' => 'in_progress', 'priority' => 'high', 'assigned' => 'Admin', 'due' => '2024-01-25'],
    ];
}

function renderDashboard($request, $encrypter, $csrfMiddleware) {
    $user = getAuthUser($request);
    $tasks = getTasks();
    $csrfToken = $_SESSION['_token'];
    $xsrfCookie = $csrfMiddleware->addCookieToResponse(null, $csrfToken);
    setcookie('XSRF-TOKEN', $xsrfCookie, time() + 7200, '/');
    require dirname(__DIR__) . '/resources/views/dashboard.php';
}

function renderLogin($request, $encrypter) {
    $user = getAuthUser($request);
    if ($user) {
        header('Location: /');
        exit;
    }
    $csrfToken = $_SESSION['_token'];
    require dirname(__DIR__) . '/resources/views/login.php';
}

function handleLogin($request, $encrypter, $csrfMiddleware) {
    $email = isset($_POST['email']) ? $_POST['email'] : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';

    $user = getUserByCredentials($email, $password);

    if ($user) {
        $sessionData = ['user_id' => $user['id'], 'logged_in_at' => time()];
        $encrypted = $encrypter->encrypt($sessionData);
        setcookie('taskflow_session', $encrypted, time() + 7200, '/', '', false, true);

        $csrfToken = $_SESSION['_token'];
        $xsrfCookie = $csrfMiddleware->addCookieToResponse(null, $csrfToken);
        setcookie('XSRF-TOKEN', $xsrfCookie, time() + 7200, '/');

        header('Location: /');
        exit;
    }

    $error = 'Invalid credentials. Please try again.';
    $csrfToken = $_SESSION['_token'];
    require dirname(__DIR__) . '/resources/views/login.php';
}

function handleLogout() {
    setcookie('taskflow_session', '', time() - 3600, '/');
    setcookie('XSRF-TOKEN', '', time() - 3600, '/');
    session_destroy();
    header('Location: /login');
    exit;
}

function renderTasks($request, $encrypter) {
    $user = getAuthUser($request);
    if (!$user) {
        header('Location: /login');
        exit;
    }
    $tasks = getTasks();
    $csrfToken = $_SESSION['_token'];
    require dirname(__DIR__) . '/resources/views/tasks.php';
}

function handleCreateTask($request, $encrypter, $csrfMiddleware) {
    $user = getAuthUser($request);
    if (!$user) {
        http_response_code(403);
        echo json_encode(['error' => 'Unauthorized']);
        exit;
    }
    echo json_encode(['status' => 'ok', 'message' => 'Task created successfully']);
    exit;
}

function renderProfile($request, $encrypter) {
    $user = getAuthUser($request);
    if (!$user) {
        header('Location: /login');
        exit;
    }
    require dirname(__DIR__) . '/resources/views/profile.php';
}

function handleCompleteTask($request, $encrypter, $csrfMiddleware, $taskId) {
    $user = getAuthUser($request);
    if (!$user) {
        http_response_code(403);
        echo json_encode(['error' => 'Unauthorized']);
        exit;
    }
    echo json_encode(['status' => 'ok', 'message' => "Task {$taskId} marked as complete"]);
    exit;
}
