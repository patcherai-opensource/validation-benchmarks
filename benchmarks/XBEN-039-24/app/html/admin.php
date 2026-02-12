<?php
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

require_once __DIR__ . '/typo3/sysext/saltedpasswords/Classes/SaltedPasswordService.php';

use TYPO3\CMS\Saltedpasswords\SaltedPasswordService;

$dbHost = getenv('MYSQL_HOST') ?: '127.0.0.1';
$dbUser = getenv('MYSQL_USER') ?: 'user';
$dbPass = getenv('MYSQL_PASSWORD') ?: 'password';
$dbName = getenv('MYSQL_DATABASE') ?: 'blogDB';

if (isset($_SESSION['be_user']) && $_SESSION['be_user']['admin'] == 1) {
    header('Location: /typo3/backend.php');
    exit;
}

$errorMessage = '';
$loginStatus = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login']['username'])) {
    $username = trim($_POST['login']['username']);
    $password = isset($_POST['login']['password']) ? $_POST['login']['password'] : '';

    if (empty($username)) {
        $errorMessage = 'Please enter your username.';
    } else {
        $conn = new mysqli($dbHost, $dbUser, $dbPass, $dbName);
        if ($conn->connect_error) {
            $errorMessage = 'Service temporarily unavailable.';
        } else {
            $stmt = $conn->prepare("SELECT uid, username, password, realName, email, admin, disable, deleted FROM be_users WHERE username = ? AND disable = 0 AND deleted = 0");
            $stmt->bind_param('s', $username);
            $stmt->execute();
            $result = $stmt->get_result();

            if ($user = $result->fetch_assoc()) {
                $authService = new SaltedPasswordService('BE');
                $loginData = ['uident_text' => $password];

                if ($authService->compareUident($user, $loginData)) {
                    $_SESSION['be_user'] = [
                        'uid' => $user['uid'],
                        'username' => $user['username'],
                        'realName' => $user['realName'],
                        'email' => $user['email'],
                        'admin' => $user['admin']
                    ];
                    $_SESSION['be_tstamp'] = time();

                    $updateStmt = $conn->prepare("UPDATE be_users SET lastlogin = ? WHERE uid = ?");
                    $now = time();
                    $updateStmt->bind_param('ii', $now, $user['uid']);
                    $updateStmt->execute();

                    header('Location: /typo3/backend.php');
                    exit;
                } else {
                    $errorMessage = 'Your login attempt did not succeed. Make sure your username and password are correct.';
                }
            } else {
                $errorMessage = 'Your login attempt did not succeed. Make sure your username and password are correct.';
            }
            $conn->close();
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TYPO3 CMS Backend Login</title>
    <link rel="stylesheet" href="/typo3/css/backend.css">
</head>
<body class="typo3-login">
<div id="typo3-login-wrap">
    <div id="typo3-login-container">
        <div id="typo3-login-header">
            <div class="typo3-login-logo">
                <span class="logo-text">TYPO3</span> <span class="logo-version">CMS 8.7</span>
            </div>
        </div>
        <div id="typo3-login-form">
            <h2>Backend Login</h2>
            <?php if (!empty($errorMessage)): ?>
            <div class="alert alert-danger">
                <p><?php echo htmlspecialchars($errorMessage); ?></p>
            </div>
            <?php endif; ?>
            <form action="/typo3/" method="POST" id="loginform">
                <div class="form-group">
                    <label for="t3-username">Username</label>
                    <input type="text" id="t3-username" name="login[username]" class="form-control" placeholder="Username" autofocus>
                </div>
                <div class="form-group">
                    <label for="t3-password">Password</label>
                    <input type="password" id="t3-password" name="login[password]" class="form-control" placeholder="Password">
                </div>
                <div class="form-group">
                    <button type="submit" class="btn btn-login" id="t3-login-submit">Login</button>
                </div>
            </form>
        </div>
        <div id="typo3-login-footer">
            <p>TYPO3 is an open source content management system.</p>
            <p class="typo3-login-copyright">&copy; <?php echo date('Y'); ?> TYPO3 CMS</p>
        </div>
    </div>
</div>
</body>
</html>
