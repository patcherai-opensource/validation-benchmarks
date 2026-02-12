<?php
session_start();

$servername = $_ENV['DB_HOST'] ?? "127.0.0.1";
$username_db = $_ENV['DB_USER'] ?? "challenge";
$password_db = $_ENV['DB_PASSWORD'] ?? "challenge";
$dbname = $_ENV['DB_NAME'] ?? "challenge";

$error = '';

if (isset($_POST['action']) && $_POST['action'] === 'login') {
    $email = $_POST['Email'] ?? '';
    $password = $_POST['Password'] ?? '';

    $conn = new mysqli($servername, $username_db, $password_db, $dbname);
    if ($conn->connect_error) {
        $error = 'Database connection error.';
    } else {
        $stmt = $conn->prepare("SELECT ID, Email, FirstName, LastName, Password FROM Member WHERE Email = ?");
        $stmt->bind_param("s", $email);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows === 1) {
            $member = $result->fetch_assoc();
            if (password_verify($password, $member['Password'])) {
                $_SESSION['member_id'] = $member['ID'];
                $_SESSION['member_email'] = $member['Email'];
                $_SESSION['member_name'] = $member['FirstName'] . ' ' . $member['LastName'];
                $_SESSION['authenticated'] = true;

                header("Location: /admin/subsites/");
                exit;
            } else {
                $error = 'Invalid email or password.';
            }
        } else {
            $error = 'Invalid email or password.';
        }
        $stmt->close();
        $conn->close();
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log in to the CMS</title>
    <link rel="icon" href="/favicon.ico">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; background: #f5f5f5; color: #333; }
        .login-wrap { max-width: 400px; margin: 80px auto; padding: 40px; background: #fff; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }
        .login-wrap h1 { font-size: 20px; font-weight: 500; margin-bottom: 24px; color: #005a93; }
        .login-wrap .brand { text-align: center; margin-bottom: 24px; }
        .login-wrap .brand img { height: 32px; }
        .field { margin-bottom: 16px; }
        .field label { display: block; font-size: 13px; font-weight: 500; margin-bottom: 4px; color: #666; }
        .field input { width: 100%; padding: 8px 10px; border: 1px solid #ccc; border-radius: 3px; font-size: 14px; }
        .field input:focus { border-color: #005a93; outline: none; }
        .btn-primary { display: inline-block; padding: 8px 20px; background: #005a93; color: #fff; border: none; border-radius: 3px; font-size: 14px; cursor: pointer; }
        .btn-primary:hover { background: #004570; }
        .error-msg { color: #c00; font-size: 13px; margin-bottom: 12px; padding: 8px; background: #fff0f0; border: 1px solid #fcc; border-radius: 3px; }
        .footer-text { text-align: center; margin-top: 16px; font-size: 12px; color: #999; }
    </style>
</head>
<body>
    <div class="login-wrap">
        <div class="brand">
            <svg width="120" height="24" viewBox="0 0 120 24" xmlns="http://www.w3.org/2000/svg">
                <text x="0" y="18" font-family="Arial" font-size="16" font-weight="bold" fill="#005a93">SilverCMS</text>
            </svg>
        </div>
        <h1>Log in</h1>
        <?php if ($error): ?>
            <div class="error-msg"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>
        <form method="POST" action="/admin/login.php">
            <input type="hidden" name="action" value="login">
            <div class="field">
                <label for="Email">Email</label>
                <input type="email" name="Email" id="Email" required autofocus>
            </div>
            <div class="field">
                <label for="Password">Password</label>
                <input type="password" name="Password" id="Password" required>
            </div>
            <button type="submit" class="btn-primary">Log in</button>
        </form>
        <div class="footer-text">
            &copy; SilverCMS &mdash; Open Source Content Management
        </div>
    </div>
</body>
</html>
