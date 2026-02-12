<?php
/**
 * SilverStripe CMS Front Controller
 * Routes requests to appropriate controllers
 */

require_once '/var/www/includes/database.php';
require_once '/var/www/includes/MemberAuthenticator.php';
require_once '/var/www/includes/session.php';

$requestUri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$requestUri = rtrim($requestUri, '/');

if (empty($requestUri)) {
    $requestUri = '/';
}

$method = $_SERVER['REQUEST_METHOD'];

switch (true) {
    case $requestUri === '/' || $requestUri === '/home':
        include '/var/www/templates/home.php';
        break;

    case $requestUri === '/about':
        include '/var/www/templates/about.php';
        break;

    case $requestUri === '/Security/login':
        handleLogin($method);
        break;

    case $requestUri === '/Security/lostpassword':
        handleLostPassword($method);
        break;

    case $requestUri === '/Security/logout':
        handleLogout();
        break;

    case $requestUri === '/admin':
    case $requestUri === '/admin/pages':
        handleAdmin();
        break;

    case $requestUri === '/admin/settings':
        handleAdminSettings();
        break;

    case $requestUri === '/admin/notes':
        handleAdminNotes();
        break;

    case $requestUri === '/ping':
        header('Content-Type: text/plain');
        echo 'ok';
        break;

    default:
        header('HTTP/1.1 404 Not Found');
        include '/var/www/templates/error_404.php';
        break;
}

function handleLogin($method) {
    $error = '';
    $backURL = isset($_GET['BackURL']) ? $_GET['BackURL'] : '/admin';

    if ($method === 'POST') {
        $data = [
            'Email' => isset($_POST['Email']) ? $_POST['Email'] : '',
            'Password' => isset($_POST['Password']) ? $_POST['Password'] : ''
        ];

        $member = MemberAuthenticator::authenticate($data);

        if ($member) {
            ss_login_member($member['ID']);
            header('Location: ' . $backURL);
            exit;
        } else {
            $error = 'The provided details don\'t seem to be correct. Please try again.';
        }
    }

    include '/var/www/templates/login.php';
}

function handleLostPassword($method) {
    $message = '';
    $error = '';

    if ($method === 'POST') {
        $email = isset($_POST['Email']) ? trim($_POST['Email']) : '';

        if (!empty($email)) {
            $member = MemberAuthenticator::findMemberByEmail($email);

            // Always show the same message regardless of whether the member exists
            $message = 'If an account exists for the provided email, a password reset link has been sent.';
        } else {
            $error = 'Please enter your email address.';
        }
    }

    include '/var/www/templates/lostpassword.php';
}

function handleLogout() {
    ss_logout_member();
    header('Location: /');
    exit;
}

function handleAdmin() {
    $member = ss_require_login();
    include '/var/www/templates/admin_dashboard.php';
}

function handleAdminSettings() {
    $member = ss_require_admin();

    $db = SS_Database::getConn();
    $config = $db->querySingle("SELECT * FROM SiteConfig WHERE ID = 1", true);

    include '/var/www/templates/admin_settings.php';
}

function handleAdminNotes() {
    $member = ss_require_admin();

    $db = SS_Database::getConn();
    $stmt = $db->prepare("SELECT n.*, m.FirstName, m.Surname FROM AdminNote n JOIN Member m ON n.MemberID = m.ID WHERE n.MemberID = :mid ORDER BY n.Created DESC");
    $stmt->bindValue(':mid', $member['ID'], SQLITE3_INTEGER);
    $result = $stmt->execute();

    $notes = [];
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $notes[] = $row;
    }

    include '/var/www/templates/admin_notes.php';
}
?>