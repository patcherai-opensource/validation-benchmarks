<?php
/**
 * Teampass - User identification
 * Handles web-based authentication
 */

session_start();
require_once __DIR__ . '/../includes/config.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /');
    exit;
}

$login = isset($_POST['login']) ? trim($_POST['login']) : '';
$pw = isset($_POST['pw']) ? $_POST['pw'] : '';

if (empty($login) || empty($pw)) {
    $_SESSION['error'] = 'Please fill in all fields.';
    header('Location: /');
    exit;
}

$conn = getDbConnection();
if (!$conn) {
    $_SESSION['error'] = 'A system error occurred. Please try again later.';
    header('Location: /');
    exit;
}

// Use prepared statement for web authentication
$stmt = $conn->prepare("SELECT id, login, pw, admin, name, lastname, disabled FROM teampass_users WHERE login = ?");
$stmt->bind_param("s", $login);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 1) {
    $user = $result->fetch_assoc();

    if ((int)$user['disabled'] === 1) {
        $_SESSION['error'] = 'Account is disabled. Contact your administrator.';
        $stmt->close();
        $conn->close();
        header('Location: /');
        exit;
    }

    if (password_verify($pw, $user['pw'])) {
        // Log successful authentication
        $logStmt = $conn->prepare("INSERT INTO teampass_log_system (type, label, qui) VALUES ('user_connection', 'User authenticated via web', ?)");
        $logStmt->bind_param("s", $login);
        $logStmt->execute();
        $logStmt->close();

        $_SESSION['user_id'] = $user['id'];
        $_SESSION['user_login'] = $user['login'];
        $_SESSION['user_admin'] = $user['admin'];
        $_SESSION['user_name'] = $user['name'] . ' ' . $user['lastname'];
        $_SESSION['authenticated'] = true;

        $stmt->close();
        $conn->close();
        header('Location: /sources/items.php');
        exit;
    } else {
        $_SESSION['error'] = 'Authentication failed.';
    }
} else {
    $_SESSION['error'] = 'Authentication failed.';
}

$stmt->close();
$conn->close();
header('Location: /');
exit;