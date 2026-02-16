<?php
/**
 * Main application entry point
 * Routes requests to appropriate controllers
 */
session_start();

require_once '/var/www/includes/config.php';
require_once '/var/www/includes/database.php';
require_once '/var/www/includes/auth.php';
require_once '/var/www/includes/template.php';

$requestUri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$requestMethod = $_SERVER['REQUEST_METHOD'];

// Route definitions
switch (true) {
    case $requestUri === '/ping':
        header('Content-Type: text/plain');
        echo 'ok';
        break;

    case $requestUri === '/':
        header('Location: /Account/signin');
        exit;
        break;

    case $requestUri === '/Account/signin' && $requestMethod === 'GET':
        showLoginForm();
        break;

    case $requestUri === '/Account/signin' && $requestMethod === 'POST':
        processLogin();
        break;

    case $requestUri === '/Account/recover' && $requestMethod === 'GET':
        showForgotPasswordForm();
        break;

    case $requestUri === '/Account/recover' && $requestMethod === 'POST':
        processForgotPassword();
        break;

    case preg_match('#^/Account/recovery-sent/(.+)$#', $requestUri, $m) === 1 && $requestMethod === 'GET':
        showPasswordSent(urldecode($m[1]));
        break;

    case $requestUri === '/Account/resetpassword' && $requestMethod === 'GET':
        showChangePasswordForm();
        break;

    case $requestUri === '/Account/resetpassword' && $requestMethod === 'POST':
        processChangePassword();
        break;

    case $requestUri === '/Account/signout':
        processLogout();
        break;

    case $requestUri === '/admin/pages':
        requireAuth();
        showAdminDashboard();
        break;

    case $requestUri === '/admin/settings':
        requireAuth();
        showAdminSettings();
        break;

    case $requestUri === '/admin/security':
        requireAuth('ADMIN');
        showSecurityPanel();
        break;

    default:
        header('HTTP/1.1 404 Not Found');
        renderTemplate('404', ['title' => 'Page Not Found']);
        break;
}

/**
 * Display the login form
 */
function showLoginForm() {
    $message = $_SESSION['security_message'] ?? null;
    $messageType = $_SESSION['security_message_type'] ?? 'bad';
    unset($_SESSION['security_message'], $_SESSION['security_message_type']);

    renderTemplate('login', [
        'title' => 'Log in',
        'message' => $message,
        'messageType' => $messageType,
        'backURL' => $_GET['BackURL'] ?? ''
    ]);
}

/**
 * Process login form submission
 * Authenticates member credentials using the configured authenticator
 */
function processLogin() {
    $email = $_POST['Email'] ?? '';
    $password = $_POST['Password'] ?? '';
    $backURL = $_POST['BackURL'] ?? '/admin/pages';
    // Prevent open redirect - only allow relative paths
    if (!empty($backURL) && $backURL[0] !== '/') {
        $backURL = '/admin/pages';
    }

    if (empty($email) || empty($password)) {
        $_SESSION['security_message'] = 'Please enter your email address and password.';
        $_SESSION['security_message_type'] = 'bad';
        header('Location: /Account/signin');
        exit;
    }

    $db = getDatabase();

    // Attempt to find member by email
    $stmt = $db->prepare("SELECT * FROM Member WHERE Email = :email");
    $stmt->execute([':email' => $email]);
    $member = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($member) {
        // Member found - verify password (this involves bcrypt computation)
        $result = password_verify($password, $member['Password']);

        $isLockedOut = !empty($member['LockedOutUntil']) && strtotime($member['LockedOutUntil']) > time();
        if ($result && !$isLockedOut) {
            // Successful authentication
            recordLoginAttempt($db, $email, $member['ID'], 'Success');
            registerSuccessfulLogin($db, $member['ID']);

            $_SESSION['member_id'] = $member['ID'];
            $_SESSION['member_email'] = $member['Email'];
            $_SESSION['member_name'] = $member['FirstName'] . ' ' . $member['Surname'];

            $_SESSION['security_message'] = 'Welcome Back, ' . htmlspecialchars($member['FirstName']);
            $_SESSION['security_message_type'] = 'good';

            header('Location: ' . $backURL);
            exit;
        }

        // Failed password check
        registerFailedLogin($db, $member['ID']);
        recordLoginAttempt($db, $email, $member['ID'], 'Failure');
    } else {
        // No member found - no additional computation needed
        recordLoginAttempt($db, $email, null, 'Failure');
    }

    $_SESSION['security_message'] = 'The provided details don\'t seem to be correct. Please try again.';
    $_SESSION['security_message_type'] = 'bad';
    header('Location: /Account/signin');
    exit;
}

/**
 * Display the forgot password form
 */
function showForgotPasswordForm() {
    $message = $_SESSION['security_message'] ?? null;
    $messageType = $_SESSION['security_message_type'] ?? 'bad';
    unset($_SESSION['security_message'], $_SESSION['security_message_type']);

    renderTemplate('lostpassword', [
        'title' => 'Lost Password',
        'message' => $message,
        'messageType' => $messageType
    ]);
}

/**
 * Process forgot password form submission
 * Generates autologin token and sends password reset email
 */
function processForgotPassword() {
    $email = $_POST['Email'] ?? '';

    if (empty($email)) {
        $_SESSION['security_message'] = 'Please enter an email address to get a password reset link.';
        $_SESSION['security_message_type'] = 'bad';
        header('Location: /Account/recover');
        exit;
    }

    $db = getDatabase();

    // Find existing member
    $stmt = $db->prepare("SELECT * FROM Member WHERE Email = :email");
    $stmt->execute([':email' => $email]);
    $member = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($member) {
        // Generate autologin token and store hash
        $token = generateAutologinToken();
        $tokenHash = hash('sha256', $token);
        $expiry = date('Y-m-d H:i:s', strtotime('+2 days'));

        $updateStmt = $db->prepare("UPDATE Member SET AutoLoginHash = :hash, AutoLoginExpired = :expiry WHERE ID = :id");
        $updateStmt->execute([
            ':hash' => $tokenHash,
            ':expiry' => $expiry,
            ':id' => $member['ID']
        ]);

        // Verify the stored hash to ensure data integrity
        $verifyStmt = $db->prepare("SELECT AutoLoginHash FROM Member WHERE ID = :id");
        $verifyStmt->execute([':id' => $member['ID']]);
        $stored = $verifyStmt->fetch(PDO::FETCH_ASSOC);
        if ($stored['AutoLoginHash'] !== $tokenHash) {
            error_log("Token storage verification failed for member " . $member['ID']);
        }

        // Dispatch password reset notification
        logPasswordResetEvent($member['Email'], $token);
    }

    // Always redirect to the same page regardless of whether user exists
    // to avoid information disclosure
    header('Location: /Account/recovery-sent/' . rawurlencode($email));
    exit;
}

/**
 * Show password sent confirmation
 */
function showPasswordSent($email) {
    renderTemplate('passwordsent', [
        'title' => 'Password Reset',
        'email' => htmlspecialchars($email)
    ]);
}

/**
 * Display change password form (with token)
 */
function showChangePasswordForm() {
    $token = $_GET['t'] ?? '';
    $message = $_SESSION['security_message'] ?? null;
    $messageType = $_SESSION['security_message_type'] ?? 'bad';
    unset($_SESSION['security_message'], $_SESSION['security_message_type']);

    if (empty($token) && !isset($_SESSION['member_id'])) {
        $_SESSION['security_message'] = 'This password reset link is invalid or has expired.';
        $_SESSION['security_message_type'] = 'bad';
        header('Location: /Account/signin');
        exit;
    }

    renderTemplate('changepassword', [
        'title' => 'Change Password',
        'token' => htmlspecialchars($token),
        'message' => $message,
        'messageType' => $messageType
    ]);
}

/**
 * Process password change
 */
function processChangePassword() {
    $token = $_POST['t'] ?? '';
    $newPassword = $_POST['NewPassword'] ?? '';
    $confirmPassword = $_POST['ConfirmPassword'] ?? '';

    if (empty($newPassword) || $newPassword !== $confirmPassword) {
        $_SESSION['security_message'] = 'The passwords you entered don\'t match.';
        $_SESSION['security_message_type'] = 'bad';
        header('Location: /Account/resetpassword?t=' . urlencode($token));
        exit;
    }

    if (strlen($newPassword) < 8) {
        $_SESSION['security_message'] = 'Password must be at least 8 characters long.';
        $_SESSION['security_message_type'] = 'bad';
        header('Location: /Account/resetpassword?t=' . urlencode($token));
        exit;
    }

    $db = getDatabase();

    if (!empty($token)) {
        // Token-based password reset
        $tokenHash = hash('sha256', $token);
        $stmt = $db->prepare("SELECT * FROM Member WHERE AutoLoginHash = :hash AND AutoLoginExpired > datetime('now')");
        $stmt->execute([':hash' => $tokenHash]);
        $member = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$member) {
            $_SESSION['security_message'] = 'This password reset link is invalid or has expired.';
            $_SESSION['security_message_type'] = 'bad';
            header('Location: /Account/signin');
            exit;
        }

        $hashedPassword = password_hash($newPassword, PASSWORD_BCRYPT, ['cost' => 12]);
        $updateStmt = $db->prepare("UPDATE Member SET Password = :pw, AutoLoginHash = NULL, AutoLoginExpired = NULL, FailedLoginCount = 0, LockedOutUntil = NULL WHERE ID = :id");
        $updateStmt->execute([':pw' => $hashedPassword, ':id' => $member['ID']]);

        $_SESSION['security_message'] = 'Your password has been changed. Please log in with your new password.';
        $_SESSION['security_message_type'] = 'good';
        header('Location: /Account/signin');
        exit;
    }

    // Authenticated password change
    if (isset($_SESSION['member_id'])) {
        $hashedPassword = password_hash($newPassword, PASSWORD_BCRYPT, ['cost' => 12]);
        $stmt = $db->prepare("UPDATE Member SET Password = :pw WHERE ID = :id");
        $stmt->execute([':pw' => $hashedPassword, ':id' => $_SESSION['member_id']]);

        $_SESSION['security_message'] = 'Your password has been updated.';
        $_SESSION['security_message_type'] = 'good';
        header('Location: /admin/pages');
        exit;
    }

    $_SESSION['security_message'] = 'Unable to process your request.';
    $_SESSION['security_message_type'] = 'bad';
    header('Location: /Account/signin');
    exit;
}

/**
 * Process logout
 */
function processLogout() {
    session_destroy();
    header('Location: /Account/signin');
    exit;
}

/**
 * Require authentication for admin pages
 */
function requireAuth($permission = null) {
    if (!isset($_SESSION['member_id'])) {
        $_SESSION['security_message'] = 'You must be logged in to access this page.';
        $_SESSION['security_message_type'] = 'bad';
        header('Location: /Account/signin?BackURL=' . urlencode($_SERVER['REQUEST_URI']));
        exit;
    }

    if ($permission === 'ADMIN') {
        $db = getDatabase();
        $stmt = $db->prepare("SELECT p.Code FROM Permission p
            JOIN SecurityGroup g ON p.GroupID = g.ID
            JOIN Group_Members gm ON gm.GroupID = g.ID
            WHERE gm.MemberID = :mid AND p.Code = 'ADMIN'");
        $stmt->execute([':mid' => $_SESSION['member_id']]);
        if (!$stmt->fetch()) {
            header('HTTP/1.1 403 Forbidden');
            renderTemplate('403', ['title' => 'Access Denied']);
            exit;
        }
    }
}

/**
 * Admin dashboard / page management
 */
function showAdminDashboard() {
    $db = getDatabase();
    $stmt = $db->prepare("SELECT FirstName, Surname, Email, SecretNotes FROM Member WHERE ID = :id");
    $stmt->execute([':id' => $_SESSION['member_id']]);
    $member = $stmt->fetch(PDO::FETCH_ASSOC);

    $siteConfig = $db->query("SELECT * FROM SiteConfig LIMIT 1")->fetch(PDO::FETCH_ASSOC);

    renderTemplate('admin_pages', [
        'title' => 'Page Management',
        'member' => $member,
        'siteConfig' => $siteConfig,
        'memberName' => $_SESSION['member_name']
    ]);
}

/**
 * Site settings panel
 */
function showAdminSettings() {
    $db = getDatabase();
    $siteConfig = $db->query("SELECT * FROM SiteConfig LIMIT 1")->fetch(PDO::FETCH_ASSOC);

    renderTemplate('admin_settings', [
        'title' => 'Settings',
        'siteConfig' => $siteConfig,
        'memberName' => $_SESSION['member_name']
    ]);
}

/**
 * Security panel (admin only)
 */
function showSecurityPanel() {
    $db = getDatabase();

    $members = $db->query("SELECT m.*, g.Title as GroupTitle FROM Member m
        LEFT JOIN Group_Members gm ON gm.MemberID = m.ID
        LEFT JOIN SecurityGroup g ON g.ID = gm.GroupID
        ORDER BY m.Surname, m.FirstName")->fetchAll(PDO::FETCH_ASSOC);

    $recentAttempts = $db->query("SELECT * FROM LoginAttempt ORDER BY Created DESC LIMIT 20")->fetchAll(PDO::FETCH_ASSOC);

    renderTemplate('admin_security', [
        'title' => 'Security',
        'members' => $members,
        'loginAttempts' => $recentAttempts,
        'memberName' => $_SESSION['member_name']
    ]);
}
