<?php
session_start();

$action = isset($_GET['action']) ? $_GET['action'] : 'home';
$page = isset($_GET['page']) ? $_GET['page'] : 'HomePage';

function is_logged_in() {
    return isset($_SESSION['user_id']) && isset($_SESSION['username']);
}

function get_username() {
    return isset($_SESSION['username']) ? $_SESSION['username'] : '';
}

if ($action === 'login' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = isset($_POST['username']) ? trim($_POST['username']) : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';
    
    $users_file = __DIR__ . '/data/users.json';
    if (file_exists($users_file)) {
        $users = json_decode(file_get_contents($users_file), true);
        foreach ($users as $user) {
            if ($user['username'] === $username && password_verify($password, $user['password'])) {
                $_SESSION['user_id'] = $user['id'];
                $_SESSION['username'] = $user['username'];
                $_SESSION['role'] = $user['role'];
                header('Location: /?action=home');
                exit;
            }
        }
    }
    $login_error = 'Invalid username or password';
}

if ($action === 'logout') {
    session_destroy();
    header('Location: /');
    exit;
}

if ($action === 'register' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = isset($_POST['username']) ? trim($_POST['username']) : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';
    $email = isset($_POST['email']) ? trim($_POST['email']) : '';
    
    if (strlen($username) >= 3 && strlen($password) >= 6) {
        $users_file = __DIR__ . '/data/users.json';
        $users = file_exists($users_file) ? json_decode(file_get_contents($users_file), true) : [];
        
        $exists = false;
        foreach ($users as $user) {
            if ($user['username'] === $username) {
                $exists = true;
                break;
            }
        }
        
        if (!$exists) {
            $users[] = [
                'id' => count($users) + 1,
                'username' => $username,
                'email' => $email,
                'password' => password_hash($password, PASSWORD_DEFAULT),
                'role' => 'user'
            ];
            file_put_contents($users_file, json_encode($users, JSON_PRETTY_PRINT));
            $_SESSION['user_id'] = count($users);
            $_SESSION['username'] = $username;
            $_SESSION['role'] = 'user';
            header('Location: /?action=home');
            exit;
        } else {
            $register_error = 'Username already exists';
        }
    } else {
        $register_error = 'Username must be at least 3 characters and password at least 6 characters';
    }
}

$pages_file = __DIR__ . '/data/pages.json';
$pages = file_exists($pages_file) ? json_decode(file_get_contents($pages_file), true) : [];

$current_page = null;
foreach ($pages as $p) {
    if ($p['slug'] === $page) {
        $current_page = $p;
        break;
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiEngine - <?php echo htmlspecialchars($page); ?></title>
    <link rel="stylesheet" href="/css/style.css">
    <link rel="stylesheet" href="/custom/css-presets/default.css" onerror="this.onerror=null;this.href='/css/default-theme.css';">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <a href="/">WikiEngine</a>
        </div>
        <div class="nav-links">
            <a href="/?page=HomePage">Home</a>
            <a href="/?page=Documentation">Docs</a>
            <a href="/?page=About">About</a>
            <?php if (is_logged_in()): ?>
                <a href="/?action=settings">Settings</a>
                <span class="user-info">Welcome, <?php echo htmlspecialchars(get_username()); ?></span>
                <a href="/?action=logout">Logout</a>
            <?php else: ?>
                <a href="/?action=login">Login</a>
                <a href="/?action=register">Register</a>
            <?php endif; ?>
        </div>
    </nav>

    <div class="container">
        <?php if ($action === 'login'): ?>
            <div class="auth-form">
                <h2>Login</h2>
                <?php if (isset($login_error)): ?>
                    <div class="error"><?php echo htmlspecialchars($login_error); ?></div>
                <?php endif; ?>
                <form method="POST" action="/?action=login">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Login</button>
                </form>
                <p>Don't have an account? <a href="/?action=register">Register here</a></p>
            </div>

        <?php elseif ($action === 'register'): ?>
            <div class="auth-form">
                <h2>Create Account</h2>
                <?php if (isset($register_error)): ?>
                    <div class="error"><?php echo htmlspecialchars($register_error); ?></div>
                <?php endif; ?>
                <form method="POST" action="/?action=register">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" required minlength="3">
                    </div>
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required minlength="6">
                    </div>
                    <button type="submit" class="btn btn-primary">Register</button>
                </form>
                <p>Already have an account? <a href="/?action=login">Login here</a></p>
            </div>

        <?php elseif ($action === 'settings' && is_logged_in()): ?>
            <div class="settings-page">
                <h2>User Settings</h2>
                <div class="settings-section">
                    <h3>Theme Customization</h3>
                    <p>Customize your wiki appearance with custom CSS presets.</p>
                    <div id="theme-manager">
                        <h4>Available Presets</h4>
                        <ul id="preset-list" class="preset-list">
                            <li>Loading presets...</li>
                        </ul>
                        <h4>Create Custom Preset</h4>
                        <form id="create-preset-form" class="preset-form">
                            <div class="form-group">
                                <label for="preset-name">Preset Name</label>
                                <input type="text" id="preset-name" name="presetName" placeholder="my-theme" required>
                                <small>Will be saved as [name].css</small>
                            </div>
                            <div class="form-group">
                                <label for="primary-color">Primary Color</label>
                                <input type="text" id="primary-color" name="primary-color" placeholder="#3498db" value="#3498db">
                            </div>
                            <div class="form-group">
                                <label for="secondary-color">Secondary Color</label>
                                <input type="text" id="secondary-color" name="secondary-color" placeholder="#2ecc71" value="#2ecc71">
                            </div>
                            <div class="form-group">
                                <label for="background-color">Background Color</label>
                                <input type="text" id="background-color" name="background-color" placeholder="#ffffff" value="#ffffff">
                            </div>
                            <div class="form-group">
                                <label for="text-color">Text Color</label>
                                <input type="text" id="text-color" name="text-color" placeholder="#333333" value="#333333">
                            </div>
                            <div class="form-group">
                                <label for="font-family">Font Family</label>
                                <input type="text" id="font-family" name="font-family" placeholder="Arial, sans-serif" value="Arial, sans-serif">
                            </div>
                            <button type="submit" class="btn btn-primary">Save Preset</button>
                        </form>
                        <div id="preset-result" class="preset-result"></div>
                    </div>
                </div>
            </div>
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    loadPresets();
                    
                    document.getElementById('create-preset-form').addEventListener('submit', function(e) {
                        e.preventDefault();
                        createPreset();
                    });
                });
                
                function loadPresets() {
                    fetch('/api/templates/custom-presets')
                        .then(response => response.json())
                        .then(data => {
                            const list = document.getElementById('preset-list');
                            if (data.presets && data.presets.length > 0) {
                                list.innerHTML = data.presets.map(p => 
                                    '<li><a href="/custom/css-presets/' + encodeURIComponent(p) + '">' + p + '</a></li>'
                                ).join('');
                            } else {
                                list.innerHTML = '<li>No custom presets found</li>';
                            }
                        })
                        .catch(err => {
                            document.getElementById('preset-list').innerHTML = '<li>Error loading presets</li>';
                        });
                }
                
                function createPreset() {
                    const form = document.getElementById('create-preset-form');
                    const formData = new FormData(form);
                    const presetName = formData.get('presetName');
                    const filename = presetName.endsWith('.css') ? presetName : presetName + '.css';
                    
                    fetch('/api/templates/custom-presets/' + encodeURIComponent(filename), {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        const result = document.getElementById('preset-result');
                        if (data.success) {
                            result.innerHTML = '<div class="success">Preset created successfully! <a href="/custom/css-presets/' + encodeURIComponent(filename) + '">View preset</a></div>';
                            loadPresets();
                        } else {
                            result.innerHTML = '<div class="error">' + (data.error || 'Failed to create preset') + '</div>';
                        }
                    })
                    .catch(err => {
                        document.getElementById('preset-result').innerHTML = '<div class="error">Error creating preset</div>';
                    });
                }
            </script>

        <?php else: ?>
            <div class="wiki-content">
                <?php if ($current_page): ?>
                    <h1><?php echo htmlspecialchars($current_page['title']); ?></h1>
                    <div class="page-content">
                        <?php echo $current_page['content']; ?>
                    </div>
                    <div class="page-meta">
                        <small>Last modified: <?php echo htmlspecialchars($current_page['modified']); ?></small>
                    </div>
                <?php else: ?>
                    <h1>Welcome to WikiEngine</h1>
                    <div class="page-content">
                        <p>WikiEngine is a collaborative documentation platform that allows teams to create and share knowledge.</p>
                        <h2>Features</h2>
                        <ul>
                            <li>Easy page creation and editing</li>
                            <li>User authentication and access control</li>
                            <li>Customizable themes and presets</li>
                            <li>Rich text formatting</li>
                        </ul>
                        <h2>Getting Started</h2>
                        <p>To get started, <a href="/?action=register">create an account</a> or <a href="/?action=login">login</a> if you already have one.</p>
                    </div>
                <?php endif; ?>
            </div>
        <?php endif; ?>
    </div>

    <footer class="footer">
        <p>&copy; 2024 WikiEngine. Powered by WikiEngine v4.5.3</p>
    </footer>
</body>
</html>
