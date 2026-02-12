<?php
session_start();

$requestUri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

// Route handling
$routes = [
    '/' => 'handleDashboardRedirect',
    '/admin' => 'handleDashboardRedirect',
    '/admin/' => 'handleDashboardRedirect',
    '/admin/login' => 'handleLogin',
    '/admin/login/deeplink' => 'handleDeeplink',
    '/admin/dashboard' => 'handleDashboard',
    '/admin/translation' => 'handleTranslationList',
    '/admin/translation/export' => 'handleTranslationExport',
    '/admin/translation/import' => 'handleTranslationImport',
    '/admin/translation/cleanup' => 'handleTranslationCleanup',
    '/admin/asset/list' => 'handleAssetList',
    '/admin/document/list' => 'handleDocumentList',
    '/admin/user/list' => 'handleUserList',
    '/admin/settings' => 'handleSettings',
    '/admin/logout' => 'handleLogout',
];

// Normalize path
$requestUri = rtrim($requestUri, '/');
if ($requestUri === '') $requestUri = '/';

$handler = $routes[$requestUri] ?? null;

if ($handler === null) {
    // Try with trailing slash
    $handler = $routes[$requestUri . '/'] ?? null;
}

if ($handler === null) {
    http_response_code(404);
    echo json_encode(['success' => false, 'message' => 'Route not found']);
    exit;
}

$handler();

function getDbConnection() {
    $host = getenv('MYSQL_HOST') ?: '127.0.0.1';
    $user = getenv('MYSQL_USER') ?: 'user';
    $pass = getenv('MYSQL_PASSWORD') ?: 'password';
    $db = getenv('MYSQL_DATABASE') ?: 'pimcore';
    
    $conn = new mysqli($host, $user, $pass, $db);
    if ($conn->connect_error) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Database connection error']);
        exit;
    }
    return $conn;
}

function isAuthenticated() {
    return isset($_SESSION['pimcore_admin_sid']) && $_SESSION['pimcore_admin_sid'] === true;
}

function requireAuth() {
    if (!isAuthenticated()) {
        if (strpos($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json') !== false ||
            isset($_GET['_dc']) || isset($_GET['filter'])) {
            http_response_code(403);
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'message' => 'Session expired or unauthorized. Please log in.']);
            exit;
        }
        header('Location: /admin/login');
        exit;
    }
}

function handleDashboardRedirect() {
    if (isAuthenticated()) {
        header('Location: /admin/dashboard');
    } else {
        header('Location: /admin/login');
    }
    exit;
}

function handleLogin() {
    if ($_SERVER['REQUEST_METHOD'] === 'GET') {
        renderLoginPage();
        return;
    }
    
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $contentType = $_SERVER['CONTENT_TYPE'] ?? '';
        
        if (strpos($contentType, 'application/json') !== false) {
            $input = json_decode(file_get_contents('php://input'), true);
            $username = $input['username'] ?? '';
            $password = $input['password'] ?? '';
        } else {
            $username = $_POST['username'] ?? '';
            $password = $_POST['password'] ?? '';
        }
        
        if (empty($username) || empty($password)) {
            if (strpos($contentType, 'application/json') !== false) {
                header('Content-Type: application/json');
                echo json_encode(['success' => false, 'message' => 'Username and password are required']);
            } else {
                renderLoginPage('Username and password are required');
            }
            return;
        }
        
        $conn = getDbConnection();
        $stmt = $conn->prepare("SELECT id, username, password, name, admin FROM users WHERE username = ? AND active = 1");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();
        
        if ($result->num_rows === 1) {
            $user = $result->fetch_assoc();
            if (password_verify($password, $user['password'])) {
                $_SESSION['pimcore_admin_sid'] = true;
                $_SESSION['pimcore_user'] = [
                    'id' => $user['id'],
                    'username' => $user['username'],
                    'name' => $user['name'],
                    'admin' => $user['admin']
                ];
                
                if (strpos($contentType, 'application/json') !== false) {
                    header('Content-Type: application/json');
                    echo json_encode(['success' => true, 'token' => session_id()]);
                } else {
                    header('Location: /admin/dashboard');
                }
                $stmt->close();
                $conn->close();
                return;
            }
        }
        
        $stmt->close();
        $conn->close();
        
        if (strpos($contentType, 'application/json') !== false || strpos($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json') !== false) {
            http_response_code(401);
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'message' => 'Invalid credentials']);
        } else {
            renderLoginPage('Invalid credentials');
        }
        return;
    }
}

function handleDeeplink() {
    header('Content-Type: application/json');
    echo json_encode(['deeplink' => true, 'loginUrl' => '/admin/login']);
}

function handleLogout() {
    session_destroy();
    header('Location: /admin/login');
    exit;
}

function handleDashboard() {
    requireAuth();
    renderDashboard();
}

function handleTranslationList() {
    requireAuth();
    
    $conn = getDbConnection();
    $type = $_GET['type'] ?? 'messages';
    $table = ($type === 'admin') ? 'translations_admin' : 'translations_messages';
    
    $page = max(1, intval($_GET['page'] ?? 1));
    $limit = min(100, max(10, intval($_GET['limit'] ?? 25)));
    $offset = ($page - 1) * $limit;
    
    $result = $conn->query("SELECT DISTINCT `key`, `type`, `creationDate`, `modificationDate` FROM `$table` ORDER BY `key` LIMIT $limit OFFSET $offset");
    
    $translations = [];
    if ($result) {
        while ($row = $result->fetch_assoc()) {
            $translations[] = $row;
        }
    }
    
    $countResult = $conn->query("SELECT COUNT(DISTINCT `key`) as total FROM `$table`");
    $total = $countResult->fetch_assoc()['total'];
    
    header('Content-Type: application/json');
    echo json_encode([
        'success' => true,
        'data' => $translations,
        'total' => (int)$total,
        'page' => $page,
        'limit' => $limit
    ]);
    
    $conn->close();
}

function handleTranslationExport() {
    requireAuth();
    
    $conn = getDbConnection();
    $type = $_GET['type'] ?? 'messages';
    $table = ($type === 'admin') ? 'translations_admin' : 'translations_messages';
    
    // Build base query
    $sql = "SELECT `key`, `language`, `text`, `type`, `creationDate`, `modificationDate` FROM `$table`";
    $conditionParts = [];
    
    // Process filter parameter - grid filter conditions
    $filterJson = isset($_GET['filter']) ? $_GET['filter'] : '';
    if (!empty($filterJson)) {
        $filters = json_decode($filterJson, true);
        if (is_array($filters)) {
            foreach ($filters as $filter) {
                $operator = 'LIKE';
                $fieldname = $filter['property'] ?? '';
                $value = $filter['value'] ?? '';
                $filterType = $filter['type'] ?? 'string';
                
                if (empty($fieldname)) {
                    continue;
                }
                
                if ($filterType === 'string') {
                    $operator = 'LIKE';
                    $quotedValue = $conn->real_escape_string('%' . $value . '%');
                    $condition = $fieldname . " " . $operator . " '" . $quotedValue . "'";
                } elseif ($filterType === 'numeric') {
                    $compOp = $filter['comparison'] ?? 'eq';
                    switch ($compOp) {
                        case 'lt': $operator = '<'; break;
                        case 'gt': $operator = '>'; break;
                        case 'eq': default: $operator = '='; break;
                    }
                    $condition = $fieldname . " " . $operator . " " . $conn->real_escape_string($value);
                } elseif ($filterType === 'date') {
                    $compOp = $filter['comparison'] ?? 'eq';
                    switch ($compOp) {
                        case 'lt': $operator = '<'; break;
                        case 'gt': $operator = '>'; break;
                        case 'eq': default: $operator = '='; break;
                    }
                    $condition = $fieldname . " " . $operator . " " . $conn->real_escape_string($value);
                } else {
                    $quotedValue = $conn->real_escape_string($value);
                    $condition = $fieldname . " = '" . $quotedValue . "'";
                }
                
                $conditionParts[] = $condition;
            }
        }
    }
    
    // Apply language filter
    $language = $_GET['language'] ?? '';
    if (!empty($language)) {
        $conditionParts[] = "`language` = '" . $conn->real_escape_string($language) . "'";
    }
    
    if (!empty($conditionParts)) {
        $sql .= " WHERE " . implode(" AND ", $conditionParts);
    }
    
    $sql .= " ORDER BY `key` ASC, `language` ASC";
    
    $result = $conn->query($sql);
    
    if ($result === false) {
        header('Content-Type: application/json');
        echo json_encode([
            'success' => false,
            'message' => 'Export failed'
        ]);
        $conn->close();
        return;
    }
    
    $rows = [];
    while ($row = $result->fetch_assoc()) {
        $rows[] = $row;
    }
    
    // Return as CSV download or JSON based on format parameter
    $format = $_GET['format'] ?? 'json';
    
    if ($format === 'csv') {
        header('Content-Type: text/csv; charset=utf-8');
        header('Content-Disposition: attachment; filename="translations_export.csv"');
        
        $output = fopen('php://output', 'w');
        if (!empty($rows)) {
            fputcsv($output, array_keys($rows[0]));
            foreach ($rows as $row) {
                fputcsv($output, $row);
            }
        }
        fclose($output);
    } else {
        header('Content-Type: application/json');
        echo json_encode([
            'success' => true,
            'data' => $rows,
            'total' => count($rows)
        ]);
    }
    
    $conn->close();
}

function handleTranslationImport() {
    requireAuth();
    
    header('Content-Type: application/json');
    echo json_encode([
        'success' => true,
        'message' => 'Import endpoint ready. Use POST with CSV file.'
    ]);
}

function handleTranslationCleanup() {
    requireAuth();
    
    header('Content-Type: application/json');
    echo json_encode([
        'success' => true,
        'message' => 'Cleanup completed',
        'removed' => 0
    ]);
}

function handleAssetList() {
    requireAuth();
    
    $conn = getDbConnection();
    $parentId = intval($_GET['parentId'] ?? 0);
    
    $stmt = $conn->prepare("SELECT id, parentId, `type`, filename, path, mimetype, creationDate, modificationDate FROM assets WHERE parentId = ?");
    $stmt->bind_param("i", $parentId);
    $stmt->execute();
    $result = $stmt->get_result();
    
    $assets = [];
    while ($row = $result->fetch_assoc()) {
        $assets[] = $row;
    }
    
    header('Content-Type: application/json');
    echo json_encode([
        'success' => true,
        'data' => $assets,
        'total' => count($assets)
    ]);
    
    $stmt->close();
    $conn->close();
}

function handleDocumentList() {
    requireAuth();
    
    $conn = getDbConnection();
    $parentId = intval($_GET['parentId'] ?? 0);
    
    $stmt = $conn->prepare("SELECT id, parentId, `type`, `key`, path, published, creationDate, modificationDate FROM documents WHERE parentId = ?");
    $stmt->bind_param("i", $parentId);
    $stmt->execute();
    $result = $stmt->get_result();
    
    $documents = [];
    while ($row = $result->fetch_assoc()) {
        $documents[] = $row;
    }
    
    header('Content-Type: application/json');
    echo json_encode([
        'success' => true,
        'data' => $documents,
        'total' => count($documents)
    ]);
    
    $stmt->close();
    $conn->close();
}

function handleUserList() {
    requireAuth();
    
    $conn = getDbConnection();
    $result = $conn->query("SELECT id, username, name, email, admin, active, language, lastLogin FROM users");
    
    $users = [];
    while ($row = $result->fetch_assoc()) {
        $users[] = $row;
    }
    
    header('Content-Type: application/json');
    echo json_encode([
        'success' => true,
        'data' => $users,
        'total' => count($users)
    ]);
    
    $conn->close();
}

function handleSettings() {
    requireAuth();
    
    header('Content-Type: application/json');
    echo json_encode([
        'success' => true,
        'data' => [
            'timezone' => 'UTC',
            'languages' => ['en', 'de', 'fr'],
            'defaultLanguage' => 'en',
            'debug' => false,
            'version' => '10.5.20'
        ]
    ]);
}

function renderLoginPage($error = '') {
    ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore - Login</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body class="login-page">
<div class="login-container">
    <div class="login-header">
        <h1>pimcore</h1>
        <p class="version">Version 10.5.20</p>
    </div>
    <?php if ($error): ?>
    <div class="error-message"><?php echo htmlspecialchars($error); ?></div>
    <?php endif; ?>
    <form action="/admin/login" method="POST" class="login-form">
        <div class="form-group">
            <label for="username">Username</label>
            <input type="text" id="username" name="username" required autocomplete="username">
        </div>
        <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" name="password" required autocomplete="current-password">
        </div>
        <button type="submit" class="btn btn-primary">Login</button>
    </form>
</div>
</body>
</html>
    <?php
}

function renderDashboard() {
    $user = $_SESSION['pimcore_user'] ?? ['username' => 'unknown', 'name' => 'Unknown'];
    ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore - Admin Dashboard</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<div class="admin-layout">
    <nav class="sidebar">
        <div class="sidebar-header">
            <h2>pimcore</h2>
        </div>
        <ul class="nav-menu">
            <li><a href="/admin/dashboard" class="active">Dashboard</a></li>
            <li><a href="/admin/document/list">Documents</a></li>
            <li><a href="/admin/asset/list">Assets</a></li>
            <li>
                <span class="nav-section">Translations</span>
                <ul class="sub-menu">
                    <li><a href="/admin/translation?type=messages">Website</a></li>
                    <li><a href="/admin/translation?type=admin">Admin</a></li>
                    <li><a href="/admin/translation/export?type=messages&format=json">Export</a></li>
                </ul>
            </li>
            <li><a href="/admin/settings">Settings</a></li>
            <li><a href="/admin/user/list">Users</a></li>
        </ul>
        <div class="sidebar-footer">
            <span><?php echo htmlspecialchars($user['name']); ?></span>
            <a href="/admin/logout">Logout</a>
        </div>
    </nav>
    <main class="content">
        <h1>Dashboard</h1>
        <div class="dashboard-grid">
            <div class="card">
                <h3>Documents</h3>
                <p>Manage your website pages and content structure.</p>
            </div>
            <div class="card">
                <h3>Assets</h3>
                <p>Upload and manage media files and documents.</p>
            </div>
            <div class="card">
                <h3>Translations</h3>
                <p>Manage website and admin interface translations.</p>
            </div>
            <div class="card">
                <h3>Settings</h3>
                <p>Configure system settings and preferences.</p>
            </div>
        </div>
    </main>
</div>
</body>
</html>
    <?php
}
