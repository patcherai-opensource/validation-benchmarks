<?php
session_start();

// Application configuration
define('APP_NAME', 'Nexus Corporate Portal');
define('APP_VERSION', '2.4.1');
define('PERSISTENT_AUTH_SECRET', 'k9Xm2pL7qR4wT8yZ');
define('PERSISTENT_AUTH_COOKIE', 'PERSIST_AUTH');
define('PERSISTENT_AUTH_LIFETIME', 86400 * 30);

// User database (in production this would be a real DB)
$users = [
    'admin' => [
        'password' => 'admin',
        'display_name' => 'Portal Administrator',
        'email' => 'admin@nexuscorp.internal',
        'role' => 'admin',
        'mfa_enabled' => true,
        'mfa_code' => '847291',
        'department' => 'IT Security',
        'employee_id' => 'EMP-001'
    ],
    'jthompson' => [
        'password' => 'jthompson123',
        'display_name' => 'Jessica Thompson',
        'email' => 'jthompson@nexuscorp.internal',
        'role' => 'analyst',
        'mfa_enabled' => true,
        'mfa_code' => '523186',
        'department' => 'Finance',
        'employee_id' => 'EMP-042'
    ],
    'mwilson' => [
        'password' => 'mwilson123',
        'display_name' => 'Michael Wilson',
        'email' => 'mwilson@nexuscorp.internal',
        'role' => 'manager',
        'mfa_enabled' => false,
        'mfa_code' => null,
        'department' => 'Operations',
        'employee_id' => 'EMP-067'
    ]
];

/**
 * Route the request to the appropriate handler
 */
$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

switch ($request_uri) {
    case '/':
    case '/portal':
        handlePortalHome($users);
        break;
    case '/auth/signin':
        handleSignIn($users);
        break;
    case '/auth/verify-identity':
        handleIdentityVerification($users);
        break;
    case '/auth/signout':
        handleSignOut();
        break;
    case '/auth/recover':
        handlePasswordRecovery($users);
        break;
    case '/portal/dashboard':
        handleDashboard($users);
        break;
    case '/portal/profile':
        handleProfile($users);
        break;
    case '/portal/settings':
        handleSettings($users);
        break;
    case '/portal/directory':
        handleDirectory($users);
        break;
    case '/robots.txt':
        header('Content-Type: text/plain');
        echo "User-agent: *\nDisallow: /portal/\nDisallow: /auth/\nDisallow: /api/\n";
        break;
    case '/api/v1/health':
        header('Content-Type: application/json');
        echo json_encode(['status' => 'healthy', 'version' => APP_VERSION]);
        break;
    case '/assets/style.css':
        header('Content-Type: text/css');
        echo getStylesheet();
        break;
    default:
        http_response_code(404);
        renderPage('Not Found', '<div class="card"><h2>404 - Page Not Found</h2><p>The requested resource could not be found.</p><a href="/" class="btn">Return to Portal</a></div>');
        break;
}

/**
 * Generate a persistent authentication token for "keep me signed in"
 */
function generatePersistentToken($username) {
    $payload = $username . '|' . time() . '|' . bin2hex(random_bytes(16));
    $signature = hash_hmac('sha256', $payload, PERSISTENT_AUTH_SECRET);
    return base64_encode($payload . '|' . $signature);
}

/**
 * Validate and decode a persistent authentication token
 */
function validatePersistentToken($token) {
    $decoded = base64_decode($token, true);
    if ($decoded === false) return null;

    $parts = explode('|', $decoded);
    if (count($parts) !== 4) return null;

    list($username, $timestamp, $nonce, $signature) = $parts;
    $expected = hash_hmac('sha256', $username . '|' . $timestamp . '|' . $nonce, PERSISTENT_AUTH_SECRET);

    if (!hash_equals($expected, $signature)) return null;
    if ((time() - intval($timestamp)) > PERSISTENT_AUTH_LIFETIME) return null;

    return $username;
}

/**
 * Check if user is fully authenticated (completed all auth steps)
 */
function isFullyAuthenticated() {
    return isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true
        && isset($_SESSION['mfa_completed']) && $_SESSION['mfa_completed'] === true;
}

/**
 * Check if user is authenticated via persistent cookie (remember-me)
 */
function checkPersistentAuth($users) {
    if (isset($_COOKIE[PERSISTENT_AUTH_COOKIE])) {
        $username = validatePersistentToken($_COOKIE[PERSISTENT_AUTH_COOKIE]);
        if ($username !== null && isset($users[$username])) {
            // Restore session from persistent cookie
            $_SESSION['authenticated'] = true;
            $_SESSION['mfa_completed'] = true;
            $_SESSION['username'] = $username;
            $_SESSION['display_name'] = $users[$username]['display_name'];
            $_SESSION['role'] = $users[$username]['role'];
            $_SESSION['department'] = $users[$username]['department'];
            return true;
        }
    }
    return false;
}

/**
 * Portal home - redirect based on auth state
 */
function handlePortalHome($users) {
    if (isFullyAuthenticated()) {
        header('Location: /portal/dashboard');
        exit;
    }

    if (checkPersistentAuth($users)) {
        header('Location: /portal/dashboard');
        exit;
    }

    header('Location: /auth/signin');
    exit;
}

/**
 * Sign in handler
 */
function handleSignIn($users) {
    if (isFullyAuthenticated()) {
        header('Location: /portal/dashboard');
        exit;
    }

    if (checkPersistentAuth($users)) {
        header('Location: /portal/dashboard');
        exit;
    }

    $error = '';

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $username = trim($_POST['username'] ?? '');
        $password = $_POST['credential'] ?? '';
        $keepSignedIn = isset($_POST['persist_session']);

        if (empty($username) || empty($password)) {
            $error = 'Please enter both username and password.';
        } elseif (!isset($users[$username]) || $users[$username]['password'] !== $password) {
            $error = 'Invalid credentials. Please try again.';
            // Rate limiting would be applied here in production
        } else {
            $user = $users[$username];

            // Set initial session state - user has passed step 1
            $_SESSION['authenticated'] = true;
            $_SESSION['mfa_completed'] = false;
            $_SESSION['username'] = $username;
            $_SESSION['display_name'] = $user['display_name'];
            $_SESSION['role'] = $user['role'];
            $_SESSION['department'] = $user['department'];

            if ($keepSignedIn) {
                $token = generatePersistentToken($username);
                setcookie(PERSISTENT_AUTH_COOKIE, $token, [
                    'expires' => time() + PERSISTENT_AUTH_LIFETIME,
                    'path' => '/',
                    'httponly' => true,
                    'samesite' => 'Lax'
                ]);
            }

            if ($user['mfa_enabled']) {
                header('Location: /auth/verify-identity');
                exit;
            } else {
                $_SESSION['mfa_completed'] = true;
                header('Location: /portal/dashboard');
                exit;
            }
        }
    }

    $html = '
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <svg class="auth-logo" viewBox="0 0 24 24" width="48" height="48">
                    <path fill="#2563eb" d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
                <h1>' . APP_NAME . '</h1>
                <p class="auth-subtitle">Sign in to your account</p>
            </div>';

    if ($error) {
        $html .= '<div class="alert alert-danger">' . htmlspecialchars($error) . '</div>';
    }

    $html .= '
            <form method="POST" action="/auth/signin" autocomplete="off">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" placeholder="Enter your username" required autofocus>
                </div>
                <div class="form-group">
                    <label for="credential">Password</label>
                    <input type="password" id="credential" name="credential" placeholder="Enter your password" required>
                </div>
                <div class="form-check">
                    <input type="checkbox" id="persist_session" name="persist_session" value="1">
                    <label for="persist_session">Keep me signed in</label>
                </div>
                <button type="submit" class="btn btn-primary btn-block">Sign In</button>
            </form>
            <div class="auth-footer">
                <a href="/auth/recover">Forgot your password?</a>
            </div>
        </div>
    </div>';

    renderPage('Sign In - ' . APP_NAME, $html);
}

/**
 * MFA / Identity verification handler
 */
function handleIdentityVerification($users) {
    if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
        header('Location: /auth/signin');
        exit;
    }

    if (isset($_SESSION['mfa_completed']) && $_SESSION['mfa_completed'] === true) {
        header('Location: /portal/dashboard');
        exit;
    }

    $username = $_SESSION['username'] ?? '';
    if (!isset($users[$username]) || !$users[$username]['mfa_enabled']) {
        header('Location: /auth/signin');
        exit;
    }

    $error = '';

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $code = trim($_POST['auth_code'] ?? '');

        if (empty($code)) {
            $error = 'Please enter your verification code.';
        } elseif ($code !== $users[$username]['mfa_code']) {
            $error = 'Invalid verification code. Please try again.';
        } else {
            $_SESSION['mfa_completed'] = true;
            header('Location: /portal/dashboard');
            exit;
        }
    }

    $maskedEmail = maskEmail($users[$username]['email']);

    $html = '
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <svg class="auth-logo" viewBox="0 0 24 24" width="48" height="48">
                    <path fill="#2563eb" d="M12 1a3 3 0 00-3 3v4H5a2 2 0 00-2 2v10a2 2 0 002 2h14a2 2 0 002-2V10a2 2 0 00-2-2h-4V4a3 3 0 00-3-3zm-1 3a1 1 0 012 0v4h-2V4z"/>
                </svg>
                <h1>Identity Verification</h1>
                <p class="auth-subtitle">A verification code has been sent to ' . htmlspecialchars($maskedEmail) . '</p>
            </div>';

    if ($error) {
        $html .= '<div class="alert alert-danger">' . htmlspecialchars($error) . '</div>';
    }

    $html .= '
            <form method="POST" action="/auth/verify-identity" autocomplete="off">
                <div class="form-group">
                    <label for="auth_code">Verification Code</label>
                    <input type="text" id="auth_code" name="auth_code" placeholder="Enter 6-digit code" maxlength="6" pattern="[0-9]{6}" required autofocus>
                </div>
                <button type="submit" class="btn btn-primary btn-block">Verify</button>
            </form>
            <div class="auth-footer">
                <p>Didn\'t receive the code? Contact IT Support.</p>
                <a href="/auth/signout">Cancel and return to sign in</a>
            </div>
        </div>
    </div>';

    renderPage('Verify Identity - ' . APP_NAME, $html);
}

/**
 * Sign out handler
 */
function handleSignOut() {
    $_SESSION = [];
    session_destroy();

    if (isset($_COOKIE[PERSISTENT_AUTH_COOKIE])) {
        setcookie(PERSISTENT_AUTH_COOKIE, '', [
            'expires' => time() - 3600,
            'path' => '/',
            'httponly' => true,
            'samesite' => 'Lax'
        ]);
    }

    header('Location: /auth/signin');
    exit;
}

/**
 * Dashboard handler (protected, shows flag for admin)
 */
function handleDashboard($users) {
    if (!isFullyAuthenticated() && !checkPersistentAuth($users)) {
        header('Location: /auth/signin');
        exit;
    }

    $flag = file_get_contents('/var/www/.app_secret');
    $username = $_SESSION['username'] ?? '';
    $displayName = $_SESSION['display_name'] ?? '';
    $role = $_SESSION['role'] ?? '';
    $department = $_SESSION['department'] ?? '';

    $html = getNavbar($displayName) . '
    <div class="container">
        <div class="page-header">
            <h1>Dashboard</h1>
            <p class="text-muted">Welcome back, ' . htmlspecialchars($displayName) . '</p>
        </div>
        <div class="grid">';

    if ($role === 'admin') {
        $html .= '
            <div class="card card-highlight">
                <h3>System Configuration</h3>
                <div class="config-item">
                    <span class="config-label">Internal API Key:</span>
                    <code class="config-value">' . htmlspecialchars(trim($flag)) . '</code>
                </div>
                <div class="config-item">
                    <span class="config-label">Environment:</span>
                    <code class="config-value">production</code>
                </div>
                <div class="config-item">
                    <span class="config-label">Cluster:</span>
                    <code class="config-value">us-west-2a</code>
                </div>
            </div>';
    }

    $html .= '
            <div class="card">
                <h3>Account Overview</h3>
                <table class="table">
                    <tr><td>Username</td><td>' . htmlspecialchars($username) . '</td></tr>
                    <tr><td>Department</td><td>' . htmlspecialchars($department) . '</td></tr>
                    <tr><td>Role</td><td>' . htmlspecialchars(ucfirst($role)) . '</td></tr>
                    <tr><td>MFA Status</td><td><span class="badge badge-success">Active</span></td></tr>
                </table>
            </div>
            <div class="card">
                <h3>Recent Activity</h3>
                <ul class="activity-list">
                    <li><span class="activity-time">Today, 09:15</span> Signed in from 10.0.2.15</li>
                    <li><span class="activity-time">Yesterday, 17:42</span> Profile settings updated</li>
                    <li><span class="activity-time">Jan 15, 14:30</span> Password changed</li>
                </ul>
            </div>
            <div class="card">
                <h3>Announcements</h3>
                <div class="announcement">
                    <strong>System Maintenance</strong>
                    <p>Scheduled maintenance window: Saturday 02:00 - 06:00 UTC.</p>
                </div>
                <div class="announcement">
                    <strong>Security Reminder</strong>
                    <p>Please ensure MFA is enabled on all accounts. Review your security settings regularly.</p>
                </div>
            </div>
        </div>
    </div>';

    renderPage('Dashboard - ' . APP_NAME, $html);
}

/**
 * Profile handler
 */
function handleProfile($users) {
    if (!isFullyAuthenticated() && !checkPersistentAuth($users)) {
        header('Location: /auth/signin');
        exit;
    }

    $username = $_SESSION['username'] ?? '';
    $displayName = $_SESSION['display_name'] ?? '';
    $user = $users[$username] ?? null;

    $html = getNavbar($displayName) . '
    <div class="container">
        <div class="page-header">
            <h1>Profile</h1>
        </div>
        <div class="card">
            <h3>Personal Information</h3>
            <table class="table">
                <tr><td>Display Name</td><td>' . htmlspecialchars($user['display_name'] ?? '') . '</td></tr>
                <tr><td>Email</td><td>' . htmlspecialchars($user['email'] ?? '') . '</td></tr>
                <tr><td>Department</td><td>' . htmlspecialchars($user['department'] ?? '') . '</td></tr>
                <tr><td>Role</td><td>' . htmlspecialchars(ucfirst($user['role'] ?? '')) . '</td></tr>
            </table>
        </div>
        <div class="card">
            <h3>Security</h3>
            <table class="table">
                <tr><td>MFA Status</td><td>' . ($user['mfa_enabled'] ? '<span class="badge badge-success">Enabled</span>' : '<span class="badge badge-warning">Disabled</span>') . '</td></tr>
                <tr><td>Last Password Change</td><td>January 15, 2024</td></tr>
            </table>
        </div>
    </div>';

    renderPage('Profile - ' . APP_NAME, $html);
}

/**
 * Settings handler
 */
function handleSettings($users) {
    if (!isFullyAuthenticated() && !checkPersistentAuth($users)) {
        header('Location: /auth/signin');
        exit;
    }

    $displayName = $_SESSION['display_name'] ?? '';

    $html = getNavbar($displayName) . '
    <div class="container">
        <div class="page-header">
            <h1>Settings</h1>
        </div>
        <div class="card">
            <h3>Notification Preferences</h3>
            <p>Email notifications are managed by your IT administrator.</p>
        </div>
        <div class="card">
            <h3>Session Management</h3>
            <p>Active sessions: 1</p>
            <p>Persistent authentication: ' . (isset($_COOKIE[PERSISTENT_AUTH_COOKIE]) ? 'Active' : 'Not active') . '</p>
        </div>
    </div>';

    renderPage('Settings - ' . APP_NAME, $html);
}

/**
 * Staff Directory (accessible to authenticated users)
 */
function handleDirectory($users) {
    if (!isFullyAuthenticated() && !checkPersistentAuth($users)) {
        header('Location: /auth/signin');
        exit;
    }

    $displayName = $_SESSION['display_name'] ?? '';

    $html = getNavbar($displayName) . '
    <div class="container">
        <div class="page-header">
            <h1>Staff Directory</h1>
        </div>
        <div class="card">
            <table class="table">
                <tr><th style="color:#64748b;font-size:12px;text-transform:uppercase">Name</th><th style="color:#64748b;font-size:12px;text-transform:uppercase">Department</th><th style="color:#64748b;font-size:12px;text-transform:uppercase">Role</th><th style="color:#64748b;font-size:12px;text-transform:uppercase">Contact</th></tr>';

    foreach ($users as $uname => $u) {
        $html .= '<tr><td>' . htmlspecialchars($u['display_name']) . '</td><td>' . htmlspecialchars($u['department']) . '</td><td>' . htmlspecialchars(ucfirst($u['role'])) . '</td><td>' . htmlspecialchars($u['email']) . '</td></tr>';
    }

    $html .= '
            </table>
        </div>
    </div>';

    renderPage('Directory - ' . APP_NAME, $html);
}

/**
 * Password recovery handler
 */
function handlePasswordRecovery($users) {
    $message = '';

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $username = trim($_POST['username'] ?? '');
        if (isset($users[$username])) {
            $maskedEmail = maskEmail($users[$username]['email']);
            $message = 'If the account exists, a recovery link has been sent to ' . htmlspecialchars($maskedEmail);
        } else {
            $message = 'If the account exists, a recovery link has been sent.';
        }
    }

    $html = '
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <h1>Account Recovery</h1>
                <p class="auth-subtitle">Enter your username to receive a recovery link</p>
            </div>';

    if ($message) {
        $html .= '<div class="alert" style="background:#f0fdf4;color:#166534;border:1px solid #bbf7d0;">' . $message . '</div>';
    }

    $html .= '
            <form method="POST" action="/auth/recover">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" placeholder="Enter your username" required>
                </div>
                <button type="submit" class="btn btn-primary btn-block">Send Recovery Link</button>
            </form>
            <div class="auth-footer">
                <a href="/auth/signin">Back to sign in</a>
            </div>
        </div>
    </div>';

    renderPage('Account Recovery - ' . APP_NAME, $html);
}

/**
 * Utility: mask email address
 */
function maskEmail($email) {
    $parts = explode('@', $email);
    $name = $parts[0];
    $domain = $parts[1] ?? '';
    $masked = substr($name, 0, 2) . str_repeat('*', max(strlen($name) - 2, 0));
    return $masked . '@' . $domain;
}

/**
 * Utility: generate navigation bar
 */
function getNavbar($displayName) {
    return '
    <nav class="navbar">
        <div class="navbar-brand">
            <svg viewBox="0 0 24 24" width="28" height="28">
                <path fill="#fff" d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
            <span>' . APP_NAME . '</span>
        </div>
        <div class="navbar-nav">
            <a href="/portal/dashboard">Dashboard</a>
            <a href="/portal/profile">Profile</a>
            <a href="/portal/settings">Settings</a>
            <a href="/auth/signout" class="nav-signout">Sign Out (' . htmlspecialchars($displayName) . ')</a>
        </div>
    </nav>';
}

/**
 * Render a full HTML page
 */
function renderPage($title, $body) {
    header('X-Content-Type-Options: nosniff');
    header('X-Frame-Options: DENY');
    header('X-XSS-Protection: 1; mode=block');
    header('Referrer-Policy: strict-origin-when-cross-origin');

    echo '<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>' . htmlspecialchars($title) . '</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
' . $body . '
</body>
</html>';
}

/**
 * Embedded CSS stylesheet
 */
function getStylesheet() {
    return '
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif; background: #f0f2f5; color: #1a1a2e; line-height: 1.6; min-height: 100vh; }

.navbar { background: #1e293b; padding: 0 24px; height: 56px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 3px rgba(0,0,0,.12); }
.navbar-brand { display: flex; align-items: center; gap: 10px; color: #fff; font-weight: 600; font-size: 16px; }
.navbar-nav { display: flex; gap: 8px; }
.navbar-nav a { color: #94a3b8; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 14px; transition: all .15s; }
.navbar-nav a:hover { color: #fff; background: rgba(255,255,255,.1); }
.nav-signout { color: #f87171 !important; }

.container { max-width: 1100px; margin: 0 auto; padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 24px; font-weight: 600; }
.text-muted { color: #64748b; margin-top: 4px; }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
.card { background: #fff; border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.card h3 { font-size: 16px; font-weight: 600; margin-bottom: 16px; color: #334155; }
.card-highlight { border-left: 4px solid #2563eb; }

.table { width: 100%; border-collapse: collapse; }
.table td { padding: 10px 0; border-bottom: 1px solid #e2e8f0; font-size: 14px; }
.table td:first-child { color: #64748b; width: 40%; }

.badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 500; }
.badge-success { background: #dcfce7; color: #166534; }
.badge-warning { background: #fef9c3; color: #854d0e; }

.config-item { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #e2e8f0; }
.config-label { color: #64748b; font-size: 14px; min-width: 140px; }
.config-value { background: #f1f5f9; padding: 4px 8px; border-radius: 4px; font-size: 13px; }

.activity-list { list-style: none; }
.activity-list li { padding: 8px 0; border-bottom: 1px solid #e2e8f0; font-size: 14px; }
.activity-time { color: #64748b; margin-right: 8px; }

.announcement { padding: 12px 0; border-bottom: 1px solid #e2e8f0; }
.announcement:last-child { border-bottom: none; }
.announcement strong { font-size: 14px; }
.announcement p { font-size: 13px; color: #64748b; margin-top: 4px; }

.auth-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 24px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); }
.auth-card { background: #fff; border-radius: 12px; padding: 40px; width: 100%; max-width: 420px; box-shadow: 0 20px 60px rgba(0,0,0,.3); }
.auth-header { text-align: center; margin-bottom: 32px; }
.auth-header h1 { font-size: 20px; margin-top: 16px; color: #1e293b; }
.auth-subtitle { color: #64748b; font-size: 14px; margin-top: 8px; }
.auth-logo { display: block; margin: 0 auto; }
.auth-footer { text-align: center; margin-top: 24px; font-size: 13px; color: #94a3b8; }
.auth-footer a { color: #2563eb; text-decoration: none; }

.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-size: 14px; font-weight: 500; margin-bottom: 6px; color: #334155; }
.form-group input[type="text"], .form-group input[type="password"] { width: 100%; padding: 10px 14px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; transition: border-color .15s; outline: none; }
.form-group input:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,.1); }

.form-check { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
.form-check label { font-size: 14px; color: #64748b; cursor: pointer; }

.btn { display: inline-block; padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; text-decoration: none; transition: all .15s; }
.btn-primary { background: #2563eb; color: #fff; }
.btn-primary:hover { background: #1d4ed8; }
.btn-block { width: 100%; text-align: center; }

.alert { padding: 12px 16px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; }
.alert-danger { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
';
}
